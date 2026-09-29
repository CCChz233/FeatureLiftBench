"""Preview Fig.6 as a sample-selection chain and an audited behavior-drift case.

Always writes to an isolated preview directory; does not replace manuscript assets.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from figure_common import render
import paper_style
from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from failure_analysis import counts
from paper_inputs import ROOT

TASK = 'schema__nested_validate_core__hard3_001'
MODEL = 'deepseek-v4-pro'
RUN = ROOT / 'experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1' / TASK


def read_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def verify_case():
    """Check the frozen contract, archived classification, source exposure and demo."""
    classification = next(r for r in read_rows(
        ROOT / 'docs/paper-workbench/data/failure_analysis_20260916/classifications.csv')
        if r['task_id'] == TASK and r['model'] == MODEL)
    assert classification['root_cause_primary'] == 'behavior_drift'
    assert classification['evidence_eligibility'] == 'valid_agent_evidence'
    assert classification['entrypoint_explicit_read'] == '1'
    source_read = next(r for r in read_rows(
        ROOT / 'reports/paper_analysis/source_exposure/diagnosis/exposure_events.csv')
        if r['task_id'] == TASK and r['model'] == MODEL
        and r['evidence_kind'] == 'explicit_read')
    contract = RUN / 'workspace/TASK.md'
    assert 'A callable And step transforms the value' in contract.read_text()
    submission = RUN / 'submission/featurelifted/__init__.py'
    source = submission.read_text()
    excerpt = '                if s(data):\n                    return data'
    assert excerpt in source
    # A fresh numeric example derived from B003, not an evaluator test input.
    # Run only the inspected archived artifact, without upstream imports.
    demo = '''import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('case_submission', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
actual = module.And(int, lambda n: n + 1).validate(40)
print(json.dumps({'input': 40, 'expected_from_B003': 41, 'actual': actual}))
'''
    result = subprocess.run([sys.executable, '-I', '-B', '-c', demo, str(submission)],
                            check=True, text=True, capture_output=True, timeout=20)
    outcome = json.loads(result.stdout)
    assert outcome['actual'] == 40
    return {
        'task_id': TASK, 'model': MODEL, 'clause': 'B003', 'lift_type': 'Adapted',
        'classification': classification, 'source_read_action_step': source_read['action_step'],
        'source_read_file': source_read['file'],
        'source_read_observation_sha256': source_read['observation_sha256'],
        'submission_path': str(submission.relative_to(ROOT)),
        'submission_sha256': hashlib.sha256(submission.read_bytes()).hexdigest(),
        'excerpt_start_line': source[:source.index(excerpt)].count('\n') + 1,
        'contract_path': str(contract.relative_to(ROOT)),
        'contract_sha256': hashlib.sha256(contract.read_bytes()).hexdigest(),
        'demonstration': outcome,
        'demonstration_origin': 'New numeric input derived from public clause B003; not a benchmark test.',
        'review_scope': 'Existing author-integrated classification; local assistant evidence check, not new human review.',
        'claim_boundary': 'A confirmed source read does not establish complete localization or comprehension.',
        'case_boundary': 'The example demonstrates noncompliance with the requested callable transformation semantics; it does not claim these semantics are identical to the upstream library.',
    }


def draw():
    data = counts()
    case = verify_case()
    exposure = read_rows(ROOT / 'reports/paper_analysis/source_exposure/diagnosis/run_exposure.csv')
    failed = [r for r in exposure if r['outcome'] in ('public_failure', 'hidden_failure')]
    exposed = [r for r in failed if r['entrypoint_explicit_read'] == '1']
    assert len(failed) == 303 and len(exposed) == data['candidates'] == 241
    assert data['excluded'] == 13 and data['valid'] == 228
    drift = data['pooled']['behavior_drift']
    assert drift == 201
    ink, muted, blue, orange = '#23313C', '#657783', '#286B91', '#BA5A28'
    fig = plt.figure(figsize=(7.2, 4.2))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 720), ylim=(0, 420))
    ax.set_axis_off()
    texts = []

    def text(x, y, value, size=9, color=ink, weight='normal', **kwargs):
        item = ax.text(x, y, value, fontsize=size, color=color,
                       fontweight=weight, va='center', **kwargs)
        texts.append(item)
        return item

    def box(x, y, w, h, face, edge='none'):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle='round,pad=0,rounding_size=5',
                     facecolor=face, edgecolor=edge, linewidth=.6))

    def arrow(x, top, bottom):
        ax.add_patch(FancyArrowPatch((x, top), (x, bottom), arrowstyle='-|>',
                     mutation_scale=8, linewidth=.85, color='#9AACB8'))

    text(20, 395, '(a) Failure evidence', 10, weight='bold')
    text(275, 395, '(b) API present, behavior differs', 10, weight='bold')
    ax.plot([251, 251], [25, 377], color='#DEE6EC', linewidth=.8)

    for y, number, label, fill, color in [
        (307, len(failed), 'Behavioral-first\nfailures', '#F0F4F7', ink),
        (216, len(exposed), 'Confirmed reads of\nentrypoint source', '#EAF2F7', blue),
        (125, data['valid'], 'Retained for\nfailure analysis', '#EAF2F7', blue),
        (34, drift, 'API exists;\nbehavior differs', '#FAECE3', orange),
    ]:
        box(20, y, 214, 55, fill)
        text(34, y + 28, str(number), 23, color, 'bold')
        text(109, y + 28, label, 8.2, color)
    arrow(60, 303, 275)
    text(84, 290, f'{len(exposed)/len(failed):.1%}', 11, blue, 'bold')
    text(144, 290, '241 / 303', 7.5, muted)
    arrow(60, 212, 184)
    text(84, 198, '13 excluded*', 8, muted)
    arrow(60, 121, 94)
    text(84, 108, f'{drift/data["valid"]:.1%}', 11, orange, 'bold')
    text(144, 108, '201 / 228', 7.5, muted)
    text(20, 17, '* Contract/evaluator mismatch candidates', 6.8, muted)

    text(275, 370, 'Schema task  ·  DeepSeek V4 Pro  ·  confirmed source read', 7.8, muted)
    box(275, 293, 425, 59, '#EDF4F8')
    text(288, 338, 'REQUIRED  ·  PUBLIC CLAUSE B003', 7.6, blue, 'bold')
    text(288, 314, 'Each callable step must pass on its transformed value.', 9)

    box(275, 193, 425, 84, '#F4F6F8')
    text(288, 261, 'SUBMITTED IMPLEMENTATION  ·  EXCERPT', 7.6, muted, 'bold')
    text(290, 238, 'if s(data):', 10, fontfamily='DejaVu Sans Mono')
    ax.add_patch(Rectangle((287, 206), 169, 23, facecolor='#F9E3D4', edgecolor='none'))
    text(290, 218, '    return data', 10, orange, fontfamily='DejaVu Sans Mono')
    text(472, 231, 'Checks the result, then\nreturns the original value.', 8, muted)

    text(275, 171, 'NEW EXAMPLE FROM THE PUBLIC CONTRACT', 7.6, muted, 'bold')
    text(275, 148, 'And(int, lambda n: n + 1).validate(40)', 9,
         fontfamily='DejaVu Sans Mono')
    box(275, 57, 201, 64, '#EDF4F8')
    box(489, 57, 211, 64, '#FAECE3')
    text(288, 106, 'EXPECTED', 7.5, blue, 'bold')
    text(502, 106, 'ACTUAL SUBMISSION', 7.5, orange, 'bold')
    text(288, 80, str(case['demonstration']['expected_from_B003']), 21, blue, 'bold')
    text(502, 80, str(case['demonstration']['actual']), 21, orange, 'bold')
    text(332, 80, 'transformed', 8, muted)
    text(546, 80, 'unchanged', 8, muted)
    text(275, 32, 'The transformation result is discarded.', 9, orange)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in texts:
        bounds = item.get_window_extent(renderer)
        assert fig.bbox.contains(bounds.x0, bounds.y0), item.get_text()
        assert fig.bbox.contains(bounds.x1, bounds.y1), item.get_text()
    output = Path(paper_style.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    case['flow'] = {'behavioral_first_failures': len(failed), 'confirmed_reads': len(exposed),
                    'excluded': data['excluded'], 'retained': data['valid'], 'behavior_drift': drift}
    (output / 'evidence.json').write_text(json.dumps(case, indent=2) + '\n')
    for path in paper_style.save_figure(fig, 'fig6_evidence_case', formats=('pdf', 'svg', 'png')):
        print(path)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=paper_style.FIGURES_DIR / 'output/fig6_evidence_case')
    args = parser.parse_args()
    render([draw], args.output_dir)
