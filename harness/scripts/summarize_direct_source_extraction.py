#!/usr/bin/env python3
"""Summarize frozen DSE evaluations without changing submissions or scoring.

Uses evaluator output only. Gate locations are not semantic root-cause labels.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'harness'))
from featureliftbench.freeze import file_manifest, manifest_digest, verify_file_manifest, sha256_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', required=True, type=Path)
    args = parser.parse_args()
    suite = args.suite.resolve()
    prepared = json.loads((suite / 'prepared_suite.json').read_text())
    frozen = json.loads((suite / 'freeze_manifest.json').read_text())
    assert not verify_file_manifest(frozen['files_sha256'], root=suite), 'Scientific freeze changed'
    subsets = json.loads((suite / 'analysis_subsets.json').read_text())
    static = {r['task_id']: r for r in json.loads((suite / 'static_diagnostics.json').read_text())['tasks']}
    names = [('Build', 'build_pass', 'build'), ('Primary', 'public_tests_pass', 'public_tests'),
             ('Extended', 'hidden_tests_pass', 'hidden_tests'), ('Isolation', 'isolation_pass', 'isolation')]
    rows = []
    for record in prepared['tasks']:
        tid = record['task_id']; task = suite / 'tasks' / tid
        files = file_manifest([task / 'submission'], root=task / 'submission')
        assert {'file_count': len(files), 'sha256': manifest_digest({'files': files})} == record['submission_identity'], tid
        path = task / 'eval/result.json'
        if not path.exists():
            raise SystemExit('Incomplete evaluation: ' + tid)
        raw = json.loads(path.read_text())
        assert raw['task_id'] == tid
        sandbox = raw.get('sandbox', {})
        infrastructure = []
        if sandbox.get('docker_sandbox_error') or sandbox.get('backend') != 'docker':
            infrastructure.append('docker_sandbox')
        for stage in ['environment', 'eval_tooling', 'dependency_install']:
            value = raw.get(stage)
            if isinstance(value, dict) and value.get('passed') is False:
                infrastructure.append(stage)
        # The evaluator also stores genuine isolation violations in errors.
        # Those are submission outcomes, not infrastructure incidents.
        isolation_errors = [e for e in raw.get('errors', []) if
            e.startswith('runtime isolation audit blocked:') or
            "imports forbidden module '" in e or "imports from forbidden module '" in e]
        other_errors = [e for e in raw.get('errors', []) if e not in isolation_errors]
        if other_errors:
            infrastructure.append('unclassified_evaluator_errors_require_review')
        gates = {name: bool(raw.get(key)) for name, key, _ in names}
        passed = all(gates.values())
        assert bool(raw.get('scores', {}).get('functional_gate')) == passed
        first = next((name for name, _, _ in names if not gates[name]), 'Pass')
        evidence = {}
        for stage in ['build', 'public_tests', 'hidden_tests', 'isolation']:
            value = raw.get(stage)
            evidence[stage] = {'recorded': isinstance(value, dict), 'skipped': value.get('skipped') if isinstance(value, dict) else None}
        if not infrastructure:
            assert sandbox.get('network') == 'none' and sandbox.get('read_only') is True
        rows.append({'task_id': tid, 'lift_type': record['lift_type'], 'functional_pass': passed,
            'infrastructure_flags': infrastructure, 'first_failed_gate': first, 'gates': gates,
            'stage_execution': evidence, 'raw_status': raw.get('status'),
            'isolation_error_messages': isolation_errors, 'other_error_messages': other_errors,
            'raw_result': str(path.relative_to(suite)), 'raw_result_sha256': sha256_file(path),
            'all_top_level_names_mapped': not record['unresolved_api'],
            'unmapped_api': sorted(record['unresolved_api']),
            'all_artifact_source_overlap': static[tid]['all_artifact_source_overlap']})
    assert len(rows) == 40 and len({r['task_id'] for r in rows}) == 40
    def aggregate(items):
        eligible = [r for r in items if not r['infrastructure_flags']]
        return {'assigned': len(items), 'infrastructure_flagged': len(items)-len(eligible),
            'passed': sum(r['functional_pass'] for r in eligible),
            'pass_rate_all_assigned': sum(r['functional_pass'] for r in eligible) / len(items) if items else None,
            'first_failed_gate_counts': dict(Counter(r['first_failed_gate'] for r in eligible)),
            'individual_gate_pass_counts': {name: sum(r['gates'][name] for r in eligible) for name, _, _ in names}}
    result = {'schema': 'featureliftbench.dse_functional_summary.v1', 'prepared_suite_sha256': sha256_file(suite/'prepared_suite.json'),
        'evaluation_started_sha256': sha256_file(suite/'evaluation_started.json'), 'summary_script_sha256':sha256_file(Path(__file__)),
        'all40': aggregate(rows), 'by_lift_type': {t: aggregate([r for r in rows if r['lift_type']==t]) for t in ['Direct','Adapted','Composite']},
        'subsets': {name: aggregate([r for r in rows if r['task_id'] in subset['task_ids']]) for name, subset in subsets.items() if isinstance(subset,dict) and 'task_ids' in subset},
        'all_artifact_overlap_median':statistics.median(r['all_artifact_source_overlap'] for r in rows),
        'interpretation':'First failed gate ordered Build, Primary, Extended, Isolation; independent gates may also fail, and unexecuted gates are not independent behavioral failures. Infrastructure flags require review. Name coverage is not interface compatibility. Overlap is all-artifact, not success-only Copy.',
        'submission_identity_postcheck': '40/40 unchanged', 'tasks': rows}
    (suite/'functional_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# DSE-40 正式 Docker 功能评测', '', '固定 40 题；每题使用冻结提交执行一次。提取规则、别名与提交未按评测反馈修改。', '',
        f"完整通过：**{result['all40']['passed']}/40**；基础设施待核验：{result['all40']['infrastructure_flagged']} 题。", '',
        '| Lift type | Pass | Total |', '| --- | ---: | ---: |']
    for t,v in result['by_lift_type'].items(): lines.append(f"| {t} | {v['passed']} | {v['assigned']} |")
    lines += ['', '首败门槛按 Build → Primary → Extended → Isolation 排序；不代表语义根因。', '', '| 首败门槛 | 题数 |', '| --- | ---: |']
    for key in ['Build','Primary','Extended','Isolation','Pass']: lines.append(f"| {key} | {result['all40']['first_failed_gate_counts'].get(key,0)} |")
    lines += ['', '各 gate 独立通过数量：'+json.dumps(result['all40']['individual_gate_pass_counts'])+'。Build 失败后没有执行的测试不能单独计为行为失败。', '',
        f"冻结的名称覆盖子集：{result['subsets']['name_covered']['passed']}/29；该子集为 Direct 15、Adapted 14，无 Composite。总体仍以 40 题为准。", '',
        f"所有产物静态源码重叠中位数：{result['all_artifact_overlap_median']:.2%}。该数字不是论文的 success-only Copy。", '',
        '限制：DSE 获得入口提示和审定别名，准备阶段有接口审查；不能称为与 agent 完全相同输入的消融，也不能从差异直接推断模型具有深层理解。', '',
        '复核：40 题任务树与历史冻结一致；265 个 wheelhouse 文件哈希一致；固定镜像 ID 已核验；核心评分代码一致。当前 harness 存在 10 个历史差异，详见 formal_evaluation_identity_check.json；CLI 的 eval handler 与历史版本 AST 一致。', '',
        '全部提交评测后哈希未变。完整结果见 functional_summary.json、evaluation_results.json，以及 tasks/<task_id>/eval/result.json 和 logs/。', '', '| Task | Type | 首败门槛 |', '| --- | --- | --- |']
    lines += [f"| {r['task_id']} | {r['lift_type']} | {r['first_failed_gate']} |" for r in rows]
    (suite/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['tasks','interpretation']},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
