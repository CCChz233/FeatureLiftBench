"""Rebuild marked LaTeX tables from saved evidence, without running experiments.

Run `python docs/paper/writing/update_tables.py` to update tables only.
Run with --check to verify that the editable paper's tables match the evidence.
Prose outside BEGIN/END GENERATED TABLE markers is never changed.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median

from known_defect_sensitivity import RESULTS, ANNOTATIONS, ROOT, FREEZE, PREDECESSOR_FREEZE, MODELS, EXCLUDED_IDS, boolean, read_csv

PAPER = Path(__file__).resolve().parents[1]
FINAL = ROOT / 'reports/paper_analysis/python150_paper_analysis_final'
FREEZE_PATH = ROOT / 'artifacts/research_analysis/python200_prime/current_benchmark_freeze.json'
STATS_PATH = FINAL / 'json/stats.json'
AUDIT = ROOT / 'reports/paper_analysis/python150_offline_audit_20260908'
CROSS_AUDIT_PATH = AUDIT / 'cross_version_summary.json'
DEFECT_AUDIT_PATH = AUDIT / 'defect_review.json'
CHAPTER2_PATH = PAPER / 'writing/chapter2_evidence.json'
SHORT = dict(zip(MODELS, ['Pro', 'Flash', 'Luna', 'GLM', 'Qwen', 'OSS']))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def table(label, caption, columns, headers, rows, note=''):
    out = [r'\begin{table}[tbp]', rf' \caption{{{caption}}}', rf' \label{{tab:{label}}}',
           r' \centering\small', r' \setlength{\tabcolsep}{4pt}',
           rf' \begin{{tabular}}{{@{{}}{columns}@{{}}}}', r' \toprule',
           ' ' + ' & '.join(headers) + r' \\', r' \midrule']
    out.extend(' '+(' & '.join(map(str, row))+r' \\' if isinstance(row, list) else row) for row in rows)
    out += [r' \bottomrule', r' \end{tabular}']
    if note:
        out += [r' \par\smallskip\begin{minipage}{\linewidth}\footnotesize', ' '+note, r' \end{minipage}']
    return '\n'.join(out + [r'\end{table}'])


def wilson(p, n):
    z = 1.959963984540054
    a = p/n
    d = 1+z*z/n
    c = (a+z*z/(2*n))/d
    h = z*math.sqrt(a*(1-a)/n+z*z/(4*n*n))/d
    return c-h, c+h


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    rows = read_csv(RESULTS)
    f = read_json(FREEZE_PATH)
    stats = read_json(STATS_PATH)
    cross_audit = read_json(CROSS_AUDIT_PATH)
    defect_audit = read_json(DEFECT_AUDIT_PATH)
    chapter2 = read_json(CHAPTER2_PATH)
    for source in chapter2['source_files']:
        assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], source['path']
    assert chapter2['strata'] == {
        'python150': {'tasks': 150, 'repositories': 126, 'snapshots': 132},
        'hard50': {'tasks': 50, 'repositories': 50, 'snapshots': 50},
        'complete': {'tasks': 200, 'repositories': 176, 'snapshots': 182},
    }
    assert chapter2['repair_llm_review_tasks'] == 38
    assert chapter2['repair_maintainer_proxy_adjudication_tasks'] == 6
    # The content-alignment caption is conditional on the separate offline audit.
    assert cross_audit['release_freeze'] == FREEZE
    assert cross_audit['changed_task_count'] == 24
    assert all(cross_audit['replacement_exactly_covers_changes'].values())
    assert cross_audit['row_checks']['agent_prompt_matches_rendered_v2']['true'] == 900
    assert cross_audit['row_checks']['recorded_capsule_matches_local_v2']['true'] == 838
    assert defect_audit['verdict_counts'] == {'supported_candidate': 6, 'ambiguous_candidate': 1}
    assert {c['task_id'] for c in defect_audit['cases']} == set(EXCLUDED_IDS)
    for audit in [cross_audit, defect_audit]:
        for source in audit['source_files']:
            assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], source['path']
    groups = {m: [r for r in rows if r['model']==m] for m in MODELS}
    assert len(rows)==900 and len({(r['model'], r['task_id']) for r in rows})==900
    assert all(len(v)==150 for v in groups.values())
    assert Counter(r['freeze_id'] for r in rows)=={FREEZE:522,PREDECESSOR_FREEZE:378}
    tasks = {r['task_id']:r for r in groups[MODELS[0]]}
    assert all({r['task_id'] for r in v}==set(tasks) for v in groups.values())
    assert len(f['tasks'])==200
    assert set(tasks)=={t for t,v in f['tasks'].items() if v['stratum']=='python150'}
    for r in rows:
        assert boolean(r['functional_pass']) == (boolean(r['usable_submission']) and all(boolean(r[k]) for k in ['build_pass','public_pass','hidden_pass','isolation_pass']))
        assert r['hard3']==tasks[r['task_id']]['hard3'] and r['lift_type']==tasks[r['task_id']]['lift_type']
    repos = {g:{v['source_repo_id'] for v in f['tasks'].values() if v['stratum']==g} for g in ['python150','hard50']}
    assert len(repos['python150'])==126 and len(repos['hard50'])==50 and not (repos['python150']&repos['hard50'])
    g = f['gates']
    assert g['task_validation']==200 and g['source_mapping']==200 and g['oracle_runs']=='600/600' and g['oracle_stable_tasks']=='200/200'
    out = {}
    composition=[]
    for hard, title in [(False,'Core-100'),(True,'hard3-50')]:
        rr=[r for r in tasks.values() if boolean(r['hard3'])==hard]
        composition.append([title,*[sum(r['lift_type']==k for r in rr) for k in ['Direct','Adapted','Composite']],len(rr)])
    composition += [r'\midrule',['Python-150',56,76,18,150]]
    first=table('dataset', 'Dataset composition and recorded validation coverage. hard3 is inside Python-150; the additional Hard-50 extension is separate.', 'lrrrr', ['Construction group','Direct','Adapted','Composite','Tasks'],composition)
    at=first.index(r' \end{tabular}')+len(r' \end{tabular}')
    panels=r'''
 \par\medskip
 \begin{tabular}{@{}lrrr@{}}
 \toprule
 Release stratum & Tasks & Repositories & Snapshots \\
 \midrule
 Python-150 & 150 & 126 & 132 \\
 Additional Hard-50 & 50 & 50 & 50 \\
 Complete release & 200 & 176 & 182 \\
 \bottomrule
 \end{tabular}
 \par\medskip
 \begin{tabularx}{\linewidth}{@{}lrX@{}}
 \toprule
 Validation evidence & Coverage & Scope \\
 \midrule
 Task/specification checks & 200/200 & Recorded mechanical checks \\
 Source mappings & 200/200 & Pinned source identities \\
 Oracle executions & 600/600 & Three passing runs per task \\
 Stable oracle fingerprints & 200/200 & Recorded repeatability \\
 Repair-scope LLM review & 38 tasks & Recorded repair scope \\
 Maintainer-proxy adjudication & 6 tasks & Coding-agent scope judgments \\
 \bottomrule
 \end{tabularx}
 \par\smallskip\begin{minipage}{\linewidth}\footnotesize
 No complete independent semantic audit is established by these counts.
 \end{minipage}'''
    out['dataset']=first[:at]+panels+first[at:]
    config_rows=[]
    for m in MODELS:
        modes=Counter()
        for r in groups[m]:
            suite='python150-prime-v2-main-r1' if m==MODELS[0] else 'python200-prime-v2-main-r1'
            p=ROOT/'experiments/python/openhands'/m/suite/r['task_id']/'run.json'
            run=read_json(p)
            c=run['agent_config']
            assert c['context_window_tokens']==131072 and c['reserved_output_tokens']==8192
            assert str(c['native_tool_calling']).lower()=='true'
            modes[c['openhands_condenser_mode']]+=1
            if c['openhands_condenser_mode']=='token':
                assert c['openhands_condenser_trigger_tokens']==122880 and c['openhands_condenser_target_tokens']==61440
                assert c['openhands_condenser_max_events']==1000000 and c['openhands_condenser_keep_first']==4
        expected='token' if m in MODELS[:2] else 'default'
        assert modes=={expected:150},(m,modes)
        fc=Counter(r['freeze_id'] for r in groups[m])
        config_rows.append([SHORT[m],expected,'122,880 / 61,440' if expected=='token' else 'Unspecified',fc[FREEZE],fc[PREDECESSOR_FREEZE]])
    out['config']=table('config','Recorded configurations and Python-150 run provenance. Counts refer to retained run-freeze IDs, not just the release label.','llcrr',['Backend','Condenser','Trigger / target','v2','Prior'],config_rows,
        r'Common envelope: OpenHands CLI 1.16.0; 120 steps; 131,072 context tokens with 8,192 reserved; 3,600 s timeout; native tool calling; no Main token cap. Evaluator: Python 3.11.14, Linux/amd64. Token condenser: keep first four events; maximum 1,000,000 events. Default does not specify token thresholds in these records. v2 = \texttt{6c20ff03\ldots}; Prior = \texttt{0b106842\ldots}. All rows report image tag suffix \texttt{212930ea}.')
    mainrows=[];sen=[];funnel=[];gates=[];compact=[]
    old={r['label']:r for r in read_csv(FINAL/'csv/main_table.csv')}
    stage=['functional_pass','missing_submission','build_failure','public_failure','hidden_failure','isolation_failure']
    for m,rr in groups.items():
        label=SHORT[m];passed=[r for r in rr if boolean(r['functional_pass'])]
        n=len(passed);empty=sum(not boolean(r['usable_submission']) for r in rr)
        ci=wilson(n,150)
        core=sum(not boolean(r['hard3']) for r in passed);hard=n-core
        assert int(old[label]['n_pass'])==n and int(old[label]['empty'])==empty
        mainrows.append([label,n,f'{100*n/150:.1f} [{100*ci[0]:.1f}, {100*ci[1]:.1f}]',core,hard,empty])
        assert all(not boolean(r['functional_pass']) for r in rr if r['task_id'] in EXCLUDED_IDS)
        sen.append([label,f'{n}/150',f'{100*n/150:.1f}',f'{n}/143',f'{100*n/143:.1f}'])
        stages=Counter(r['first_failure_stage'] for r in rr)
        assert set(stages)<=set(stage),(label,stages)
        funnel.append([label,*[stages[k] for k in stage]])
        delivered=[r for r in rr if boolean(r['usable_submission'])]
        flags=[sum(not boolean(r[k]) for r in delivered) for k in ['build_pass','public_pass','hidden_pass','isolation_pass']]
        residual=sum(all(boolean(r[k]) for k in ['build_pass','public_pass','hidden_pass']) and not boolean(r['isolation_pass']) for r in delivered)
        gates.append([label,len(delivered),*flags,residual])
        vals=[sum(float(r['rres']) for r in passed)/n,median(float(r['rres']) for r in passed),median(float(r['copied_fraction']) for r in passed)]
        assert all(abs(v-float(old[label][k]))<0.00051 for v,k in zip(vals,['rres_mean','rres_median','copy_median']))
        compact.append([label,n,*[f'{v:.3f}' for v in vals]])
    out['main']=table('main',r'Functional outcomes on the content-aligned Python-150 task inputs. Rates and Wilson intervals are percentages. Empty submissions remain failures; retained run identities and profile differences are disclosed in Table~\ref{tab:config}.','lrrrrr',['Backend','Pass / 150',r'Rate [95\% CI]','Core / 100','hard3 / 50','Empty'],mainrows)
    out['sensitivity']=table('sensitivity','Post hoc exclusion of the same seven provisionally flagged tasks for every backend. This sensitivity view does not replace the main task set.','lrrrr',['Backend','Main pass',r'Rate (\%)','Exclusion pass',r'Rate (\%)'],sen,
        'All configurations fail all seven flagged tasks. Numerators therefore remain unchanged; only the denominator changes from 150 to 143. Task flags are AI-assisted and non-exhaustive.')
    out['funnel']=table('funnel','Mutually exclusive first outcomes; every row sums to 150.','lrrrrrr',['Backend','Pass','Missing','Build','Public','Hidden','Isolation'],funnel)
    totals=['Total',*[sum(r[i] for r in gates) for i in range(1,7)]]
    out['gates']=table('independent-gates','Non-exclusive failed gate flags among delivered artifacts. Counts can overlap.','lrrrrrr',['Backend','Delivered','Build','Public','Hidden','Isolation','Residual'],gates+[r'\midrule',totals], 'Residual requires Build, Public, and Hidden to pass while Isolation fails.')
    out['compactness']=table('compactness',"Descriptive footprint on each backend's passing artifacts. Rows use different task sets.",'lrrrr',['Backend','Passes','Mean RRES','Median RRES','Median copy'],compact)
    bins=Counter((sum(boolean(r['functional_pass']) for r in rows if r['task_id']==t),boolean(v['hard3'])) for t,v in tasks.items())
    diffrows=[[i,bins[i,False],bins[i,True],bins[i,False]+bins[i,True]] for i in range(7)]
    assert [r[3] for r in diffrows]==[v['total'] for v in stats['spectrum6']['bins']]
    out['difficulty']=table('difficulty','Tasks by number of passing backends in the six retained campaigns.','rrrr',['Passing backends','Core','hard3','Total'],diffrows+[r'\midrule',['Total',100,50,150]])
    pairs=[]
    for key in ['paired_pro_luna','paired_flash_luna']:
        st=stats[key];aa={r['task_id']:r for r in groups[st['a']] if boolean(r['functional_pass'])};bb={r['task_id']:r for r in groups[st['b']] if boolean(r['functional_pass'])}
        common=aa.keys()&bb.keys();assert len(common)==st['n']
        for d,suffix in [(aa,'a'),(bb,'b')]:
            assert abs(median(float(d[t]['rres']) for t in common)-st['rres_median_'+suffix])<1e-6
            assert abs(median(float(d[t]['copied_fraction']) for t in common)-st['median_'+suffix])<1e-6
        pair=st['label_a']+' / '+st['label_b']
        pairs.append([pair,st['n'],f"{st['rres_median_a']:.3f} / {st['rres_median_b']:.3f}",f"{st['median_a']:.3f} / {st['median_b']:.3f}"])
    out['paired']=table('paired','Paired medians on common passing tasks; values follow the backend order in the first column.','lrcc',['Pair','Tasks','RRES medians','Copy medians'],pairs,
        r'Copy-fraction Wilcoxon tests: Pro/Luna $p=1.18\times10^{-13}$, rank-biserial $r=0.881$ (76 higher Pro, 18 higher Luna, three ties); Flash/Luna $p=4.24\times10^{-13}$, $r=0.885$ (75/14/three). These test results concern copying, not RRES.')
    lr=[]
    for r in read_csv(FINAL/'csv/logistic_params.csv'):
        if r['fit'] not in ['all6','strong3'] or r['term']=='Intercept' or r['term'].startswith('C(model)'):continue
        term='hard3 vs. Core' if r['term']=='hard3' else ('Adapted vs. Direct' if 'Adapted' in r['term'] else 'Composite vs. Direct')
        p=float(r['p']);ptext=f'{p:.3f}' if p>=.001 else rf'${p/10**math.floor(math.log10(p)):.2f}\times10^{{{math.floor(math.log10(p))}}}$'
        lr.append(['All six' if r['fit']=='all6' else 'Pro/Flash/Luna',term,f"{float(r['or']):.3f}",f"{float(r['std_err']):.3f}",ptext])
    out['logistic']=table('logistic','Construction and lift-type associations from the saved logistic fits. Backend covariates are included; standard errors are clustered by task.','llrrr',['Fit','Contrast','Odds ratio','SE (log odds)','$p$'],lr)
    ext=[]
    for m in MODELS[1:]:
        base=ROOT/'experiments/python/openhands'/m/'python200-prime-v2-main-r1'
        counts=Counter()
        for t,v in f['tasks'].items():
            path=base/t/'eval/result.json'
            if path.exists():
                raw=read_json(path)
                if all(raw.get(k,False) for k in ['build_pass','public_tests_pass','hidden_tests_pass','isolation_pass']):counts[v['stratum']]+=1
        n=counts['python150'];h=counts['hard50'];assert n==sum(boolean(r['functional_pass']) for r in groups[m])
        ext.append([SHORT[m],f'{n}/150',f'{h}/50',f'{n+h}/200 ({(n+h)/2:.1f}\\%)'])
    assert [int(r[3].split('/')[0]) for r in ext]==[157,144,98,86,61]
    out['extension']=table('extension','Supplementary functional outcomes in five assembled 200-task campaigns. The additional Hard-50 is outside the Python-150 input audit.','lrrr',['Backend','Python-150','Additional Hard-50','Combined'],ext)
    annotations=read_csv(ANNOTATIONS)
    kept=[r for r in annotations if r['task_id'] not in EXCLUDED_IDS]
    assert len(annotations)==77 and len(kept)==63
    # Preserve the existing first-pass taxonomy, without relabeling any row.
    ca=Counter((r['model'],r['root_cause_primary']) for r in kept)
    cats=[('Behavioral drift','behavior_drift'),('Contract/API completion','contract_api_completion'),('Packaging/modularization','packaging_modularization')]
    # Taxonomy values are checked against the actual export below.
    print('Retained annotation categories:',dict(Counter(r['root_cause_primary'] for r in kept)))
    ar=[]
    for title,key in cats:
        a=ca[MODELS[0],key];b=ca[MODELS[1],key];ar.append([title,a,b,a+b])
    assert sum(r[3] for r in ar)==63,ca
    out['semantic']=table('semantic','Provisional AI-assisted L1 symptoms on Pro/Flash artifact failures. These are not independently validated root-cause proportions.','lrrr',['Symptom','Pro','Flash','Total'],ar+[r'\midrule',['Total',28,35,63]])
    tex=(PAPER/'main.tex').read_text(encoding='utf-8')
    for key,val in out.items():
        pattern=r'(% BEGIN GENERATED TABLE: '+re.escape(key)+r'\n).*?(% END GENERATED TABLE: '+re.escape(key)+')'
        tex,n=re.subn(pattern,lambda m:m[1]+val+'\n'+m[2],tex,flags=re.S)
        assert n==1,(key,n)
    # Four generated data tables plus one authored related-work comparison.
    assert len(re.findall(r'\\begin\{table\}',tex.split(r'\appendix')[0]))==5
    assert tex.count(r'\label{tab:positioning}')==1
    assert tex.count(r'\begin{figure}')==5
    before=(PAPER/'main.tex').read_text(encoding='utf-8')
    if args.check:
        assert tex==before,'Generated tables differ: rerun without --check.'
    else:
        (PAPER/'main.tex').write_text(tex,encoding='utf-8')
    sources=[RESULTS,ANNOTATIONS,FREEZE_PATH,STATS_PATH,FINAL/'csv/main_table.csv',FINAL/'csv/logistic_params.csv',CROSS_AUDIT_PATH,DEFECT_AUDIT_PATH,CHAPTER2_PATH]
    qa={'status':'verified_with_input_audit_and_environment_annotation_caveats','rows':900,'tasks':150,'models':6,'run_profiles_checked':900,'main_tables':5,'main_generated_data_tables':4,'main_authored_literature_tables':1,'appendix_tables':8,'figure_placeholders':5,
        'input_audit':{'aligned_initial_prompts':900,'aligned_recorded_capsules':838,'oracle_runtime_image_identity_unreconciled':True},
        'run_freeze_counts':dict(Counter(r['freeze_id'] for r in rows)), 'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
    if not args.check:(PAPER/'writing/table_validation.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
    print(('Checked' if args.check else 'Updated')+f' {len(out)} tables; 900 result/profile records; no agent evaluations.')


if __name__=='__main__':main()
