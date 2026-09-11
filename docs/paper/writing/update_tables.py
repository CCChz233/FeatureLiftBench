"""Rebuild marked LaTeX tables and compact result text from saved evidence.

Run `python docs/paper/writing/update_tables.py` to update tables only.
Run with --check to verify that the editable paper's tables match the evidence.
Prose outside BEGIN/END GENERATED TABLE or TEXT markers is never changed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median
import sys
from comprehensive_table import comprehensive_table

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import (RESULTS, ROOT, PAPER, FREEZE_PATH, STATS_PATH,
                          CHAPTER2_PATH, MANIFEST_PATH, MODELS, SHORT,
                          boolean, read_csv, read_json, input_path, run_directory)


def table(label, caption, columns, headers, rows, note='', *, flexible=False):
    out = [r'\begin{table}[tbp]', rf' \caption{{{caption}}}', rf' \label{{tab:{label}}}',
           r' \centering\small', r' \setlength{\tabcolsep}{4pt}',
           r' \renewcommand{\arraystretch}{1.12}',
           (rf' \begin{{tabularx}}{{\linewidth}}{{@{{}}{columns}@{{}}}}' if flexible else rf' \begin{{tabular}}{{@{{}}{columns}@{{}}}}'), r' \toprule',
           ' ' + ' & '.join(headers) + r' \\', r' \midrule']
    out.extend(' '+(' & '.join(map(str, row))+r' \\' if isinstance(row, list) else row) for row in rows)
    out += [r' \bottomrule', r' \end{tabularx}' if flexible else r' \end{tabular}']
    if note:
        out += [r' \par\smallskip\begin{minipage}{\linewidth}\footnotesize', ' '+note, r' \end{minipage}']
    return '\n'.join(out + [r'\end{table}'])


def quantile(values, q):
    """Linear interpolation, matching the saved analysis's quantile convention."""
    values = sorted(values)
    at = q * (len(values) - 1)
    lo, hi = math.floor(at), math.ceil(at)
    return values[lo] * (hi-at) + values[hi] * (at-lo) if lo != hi else values[lo]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    rows = read_csv(RESULTS)
    f = read_json(FREEZE_PATH)
    stats = read_json(STATS_PATH)
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
    groups = {m: [r for r in rows if r['model']==m] for m in MODELS}
    assert len(rows)==900 and len({(r['model'], r['task_id']) for r in rows})==900
    assert all(len(v)==150 for v in groups.values())
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
    lift_counts=Counter(r['lift_type'] for r in tasks.values())
    assert lift_counts=={'Direct':56,'Adapted':76,'Composite':18}
    out['dataset']=('Among the 150 evaluated tasks, '+str(lift_counts['Direct'])+' are Direct, '
        +str(lift_counts['Adapted'])+' Adapted, and '+str(lift_counts['Composite'])+' Composite. '
        'These labels describe the requested transformation, not difficulty tiers.')
    config_rows=[]
    for m in MODELS:
        modes=Counter()
        for r in groups[m]:
            p=run_directory(m)/r['task_id']/'run.json'
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
        config_rows.append([SHORT[m],expected,'122,880 / 61,440' if expected=='token' else 'Unspecified',len(groups[m])])
    funnel=[];gates=[]
    old={r['label']:r for r in read_csv(input_path('main_summary'))}
    stage=['functional_pass','missing_submission','build_failure','public_failure','hidden_failure','isolation_failure']
    for m,rr in groups.items():
        label=SHORT[m];passed=[r for r in rr if boolean(r['functional_pass'])]
        n=len(passed);empty=sum(not boolean(r['usable_submission']) for r in rr)
        assert int(old[label]['n_pass'])==n and int(old[label]['empty'])==empty
        stages=Counter(r['first_failure_stage'] for r in rr)
        assert set(stages)<=set(stage),(label,stages)
        funnel.append([label,*[stages[k] for k in stage]])
        delivered=[r for r in rr if boolean(r['usable_submission'])]
        flags=[sum(not boolean(r[k]) for r in delivered) for k in ['build_pass','public_pass','hidden_pass','isolation_pass']]
        residual=sum(all(boolean(r[k]) for k in ['build_pass','public_pass','hidden_pass']) and not boolean(r['isolation_pass']) for r in delivered)
        gates.append([label,len(delivered),*flags,residual])
        vals=[sum(float(r['rres']) for r in passed)/n,median(float(r['rres']) for r in passed),median(float(r['copied_fraction']) for r in passed)]
        assert all(abs(v-float(old[label][k]))<0.00051 for v,k in zip(vals,['rres_mean','rres_median','copy_median']))
        for field,prefix in [('rres','rres'),('copied_fraction','copy')]:
            vv=[float(r[field]) for r in passed]
            q1,q3=quantile(vv,.25),quantile(vv,.75)
            assert abs(q1-float(old[label][prefix+'_q1']))<.00051
            assert abs(q3-float(old[label][prefix+'_q3']))<.00051
    out['main']=comprehensive_table(groups, MODELS, SHORT)
    out['funnel']=table('funnel','Mutually exclusive first outcomes; every row sums to 150.','lrrrrrr',['Backend','Pass','Missing','Build','Public','Hidden','Isolation'],funnel,
        r'Missing means no usable submission. Remaining failures are assigned to the first failed gate in Build--Public--Hidden--Isolation order; gate columns count failures, not passes.')
    totals=['Total',*[sum(r[i] for r in gates) for i in range(1,7)]]
    out['gates']=table('independent-gates','Non-exclusive failed gate flags among delivered artifacts. Counts can overlap.','lrrrrrr',['Backend','Delivered','Build','Public','Hidden','Isolation','Residual'],gates+[r'\midrule',totals],
        'Delivered gives each row\'s denominator. A failed flag may follow an earlier loading failure and does not imply that the corresponding tests executed. Residual requires Build, Public, and Hidden to pass while Isolation fails.')
    bins=Counter(sum(boolean(r['functional_pass']) for r in rows if r['task_id']==t) for t in tasks)
    assert [bins[i] for i in range(7)]==[v['total'] for v in stats['spectrum6']['bins']]
    spectrum=[[i,bins[i],f'{100*bins[i]/150:.1f}'] for i in range(7)]
    out['difficulty']=table('difficulty','Observed solve frequency across six configurations.','rrr',
        ['Passing configurations','Tasks',r'Share (\%)'],spectrum,
        'All 150 evaluated tasks are included. Counts reflect the recorded outcomes and do not define fixed difficulty tiers.')
    pairs=[]
    for key in ['paired_pro_luna','paired_flash_luna']:
        st=stats[key];aa={r['task_id']:r for r in groups[st['a']] if boolean(r['functional_pass'])};bb={r['task_id']:r for r in groups[st['b']] if boolean(r['functional_pass'])}
        common=aa.keys()&bb.keys();assert len(common)==st['n']
        for d,suffix in [(aa,'a'),(bb,'b')]:
            assert abs(median(float(d[t]['rres']) for t in common)-st['rres_median_'+suffix])<1e-6
            assert abs(median(float(d[t]['copied_fraction']) for t in common)-st['median_'+suffix])<1e-6
        if pairs:pairs.append(r'\midrule')
        pair=rf'$A$: {SHORT[st["a"]]}; $B$: {SHORT[st["b"]]} ({st["n"]} common passing tasks)'
        pairs.append(r'\multicolumn{7}{@{}l}{'+pair+r'} \\')
        for field,title in [('rres','RRES'),('copied_fraction','Copy')]:
            av=[float(aa[t][field]) for t in sorted(common)]
            bv=[float(bb[t][field]) for t in sorted(common)]
            delta=[a-b for a,b in zip(av,bv)]
            higher=sum(d>0 for d in delta); lower=sum(d<0 for d in delta); ties=sum(d==0 for d in delta)
            assert higher+lower+ties==st['n']
            if field=='copied_fraction':
                assert (higher,lower,ties)==(st['n_a_greater'],st['n_b_greater'],st['n_tie'])
                assert abs(median(delta)-st['median_diff'])<1e-6
            pairs.append([title,f'{median(av):.3f}',f'{median(bv):.3f}',f'{median(delta):+.3f}',higher,lower,ties])
    out['paired']=table('paired','Matched-task footprint: typical values and consistency of the difference.','lrrrrrr',['Metric','Median $A$','Median $B$',r'Median $\Delta$',r'$\Delta>0$',r'$\Delta<0$',r'$\Delta=0$'],pairs,
        r'$\Delta=A-B$ is computed per task before taking its median. The last three columns count tasks with positive, negative, or zero differences. RRES is artifact/reference Python LOC; Copy is the detected source-overlap fraction. Higher values do not imply better quality.')
    ext=[]
    for m in MODELS[1:]:
        base=run_directory(m)
        counts=Counter()
        for t,v in f['tasks'].items():
            path=base/t/'eval/result.json'
            if path.exists():
                raw=read_json(path)
                if all(raw.get(k,False) for k in ['build_pass','public_tests_pass','hidden_tests_pass','isolation_pass']):counts[v['stratum']]+=1
        n=counts['python150'];h=counts['hard50'];assert n==sum(boolean(r['functional_pass']) for r in groups[m])
        ext.append([SHORT[m],f'{n}/150',f'{h}/50',f'{n+h}/200 ({(n+h)/2:.1f}\\%)'])
    assert [int(r[3].split('/')[0]) for r in ext]==[157,144,98,86,61]
    out['extension']=('On the remaining 50 release tasks, the passing counts are '
        +', '.join(r[0]+' '+r[2] for r in ext[:-1])+', and '+ext[-1][0]+' '+ext[-1][2]+'. '
        r'These supplement the 150-task counts in Table~\ref{tab:main}; '
        'the saved campaigns retain the full 200-task results.')
    tex=(PAPER/'main.tex').read_text(encoding='utf-8')
    for key,val in out.items():
        kind='TEXT' if key in ['dataset','extension'] else 'TABLE'
        pattern=r'(% BEGIN GENERATED '+kind+': '+re.escape(key)+r'\n).*?(% END GENERATED '+kind+': '+re.escape(key)+')'
        tex,n=re.subn(pattern,lambda m:m[1]+val+'\n'+m[2],tex,flags=re.S)
        assert n==1,(key,n)
    # Two main data tables, one literature comparison, and four appendix
    # tables (the appendix structure table uses its own updater).
    assert len(re.findall(r'\\begin\{table\}',tex.split(r'\appendix')[0]))==3
    assert tex.count(r'\label{tab:structure}')==1
    assert re.findall(r'% BEGIN GENERATED TABLE: (\S+)',tex.split(r'\appendix')[0])==['main','paired']
    assert len(re.findall(r'\\begin\{table\}',tex.split(r'\appendix')[1]))==4
    assert tex.count(r'\label{tab:positioning}')==1
    assert tex.count(r'\begin{figure}')==5
    before=(PAPER/'main.tex').read_text(encoding='utf-8')
    if args.check:
        assert tex==before,'Generated tables differ: rerun without --check.'
    else:
        (PAPER/'main.tex').write_text(tex,encoding='utf-8')
    sources=[MANIFEST_PATH,RESULTS,FREEZE_PATH,STATS_PATH,input_path('main_summary'),CHAPTER2_PATH]
    qa={'status':'verified_current_paper_tables','rows':900,'tasks':150,'models':6,'run_profiles_checked':900,'main_tables':3,'main_generated_data_tables':2,'main_authored_literature_tables':1,'appendix_tables':4,'figure_placeholders':len(re.findall(r'\\figureplaceholder\{',tex)),'generated_text_blocks':2,
        'main_table_order':['main','paired','positioning'],
        'structure_table_updater':'writing/update_structure_results.py',
        'table_revision':'paper_workflow_cleanup_20260911',
        'detailed_profiles':[dict(zip(['backend','condenser','trigger_target','outcomes'],r)) for r in config_rows],
        'scope':'Current numeric tables and recorded run profiles; historical audits remain separate artifacts.',
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
    if not args.check:(PAPER/'writing/table_validation.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
    print(('Checked' if args.check else 'Updated')+' 5 tables and 2 text blocks; 900 result/profile records; no agent evaluations.')


if __name__=='__main__':main()
