"""Offline, conservative content-confirmed source exposure over 900 saved runs.

No upstream code is imported or executed. A negative means not confirmed by
this detector, never that the agent did not locate/understand a capability.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
import re
import shlex
import posixpath
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/paper_analysis/source_exposure"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
READ = re.compile(r"\b(cat|sed|head|tail|less|more|awk|nl|rg|grep)\b")
SEARCH = re.compile(r"\b(rg|grep|find)\b")
WRITE = re.compile(r"\b(cp|mv|tee|apply_patch|pytest)\b|<<|write_text\(|open\([^\n]*['\"]w")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized(line):
    line = ANSI.sub("", line).strip()
    line = re.sub(r"^\d+\s*[:|\t]\s*", "", line)
    return " ".join(line.split())


def pairs_in(text):
    lines = [normalized(x) for x in text.splitlines()]
    return {(a, b) for a, b in zip(lines, lines[1:])
            if len(a) >= 12 and len(b) >= 12 and not a.startswith('#') and not b.startswith('#')}


class SourceIndex:
    def __init__(self, root):
        self.root = root
        self.modules = {}
        self.cache = {}
        for base in (root, root / 'src', root / 'lib'):
            if not base.is_dir(): continue
            for f in base.rglob('*.py'):
                rel = f.relative_to(base)
                if any(x.startswith('.') for x in rel.parts): continue
                parts = list(rel.with_suffix('').parts)
                if parts[-1] == '__init__': parts.pop()
                self.modules.setdefault('.'.join(parts), f)

    def tree(self, file):
        if file not in self.cache:
            try: self.cache[file] = ast.parse(file.read_text(encoding='utf-8-sig'))
            except (OSError, SyntaxError, UnicodeError): self.cache[file] = None
        return self.cache[file]

    def resolve(self, target, seen=()):
        if target in seen or len(seen) > 8: return None
        raw = target.removeprefix('repo/').replace('\\', '/')
        if '/' in raw or raw.endswith('.py'):
            f = self.root / raw
            if f.is_file() and f.resolve().is_relative_to(self.root.resolve()):
                return f.relative_to(self.root).as_posix()
            return None
        parts = target.split('.')
        for cut in range(len(parts), 0, -1):
            mod = '.'.join(parts[:cut]); f = self.modules.get(mod)
            if not f: continue
            attrs = parts[cut:]
            if not attrs: return f.relative_to(self.root).as_posix()
            tree = self.tree(f)
            if tree is None: return None
            name = attrs[0]
            def bindings(nodes):
                for node in nodes:
                    yield node
                    if isinstance(node, (ast.If, ast.Try)):
                        yield from bindings(node.body)
                        yield from bindings(node.orelse)
                        if isinstance(node, ast.Try):
                            yield from bindings(node.finalbody)
                            for handler in node.handlers: yield from bindings(handler.body)
            for node in bindings(tree.body):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                    if len(attrs) > 1 and not all(any(getattr(n,'name',None)==a for n in ast.walk(node)) for a in attrs[1:]):
                        continue
                    return f.relative_to(self.root).as_posix()
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    ts = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if len(attrs)==1 and any(isinstance(t,ast.Name) and t.id==name for t in ts):
                        return f.relative_to(self.root).as_posix()
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if (alias.asname or alias.name) != name: continue
                        base = mod.split('.') if f.name=='__init__.py' else mod.split('.')[:-1]
                        if node.level:
                            base = base[:len(base)-node.level+1]
                            imported = '.'.join(base + ([node.module] if node.module else []))
                        else: imported = node.module or ''
                        return self.resolve('.'.join(filter(None,[imported,alias.name,*attrs[1:]])), (*seen,target))
            return None
        return None


def read_kind(action, observation, target):
    """Resolve literal read operands inside the actual source mount, not artifacts.

    Deliberately skip loops, variable expansion and redirects. Observation cwd is
    the recorded terminal cwd; an explicit cd is processed before following reads.
    """
    if action.get('kind') == 'FileEditorAction':
        return 'explicit_read' if (action.get('command') == 'view' and
            posixpath.normpath(str(action.get('path','')).replace('\\','/')) ==
            '/flb/workspace/repo/' + target) else None
    if action.get('kind') != 'TerminalAction': return None
    command = str(action.get('command',''))
    if WRITE.search(command) or re.search(r'\b(for|while|eval)\b|\$|`|>', command): return None
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|<>')
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError: return None
    cwd = str(observation.get('metadata',{}).get('working_dir',''))
    segments = []; segment = []
    for token in tokens + [';']:
        if token in (';', '&&', '||', '|', '&'):
            if segment: segments.append(segment)
            segment = []
        else: segment.append(token)
    kinds = []
    for segment in segments:
        cmd = posixpath.basename(segment[0])
        if cmd == 'cd':
            # Relative cd starts from an unrecorded pre-command cwd: skip it.
            cwd = posixpath.normpath(segment[1]) if len(segment)==2 and segment[1].startswith('/') else ''
            continue
        if cmd not in ('cat','sed','head','tail','less','more','awk','nl','rg','grep'): continue
        for operand in segment[1:]:
            if operand.startswith('-') or not (operand.startswith('/') or cwd.startswith('/')): continue
            path = posixpath.normpath(operand if operand.startswith('/') else posixpath.join(cwd,operand))
            if path == '/flb/workspace/repo/' + target:
                kinds.append('search_snippet' if cmd in ('rg','grep') else 'explicit_read')
    return 'explicit_read' if 'explicit_read' in kinds else ('search_snippet' if kinds else None)


def content_confirmed(action, observation, target, source_pairs, text):
    """Exact adjacent source-line evidence plus a targeted read; intentionally incomplete."""
    if observation.get('is_error') or observation.get('exit_code', 0) not in (0, None): return False
    return bool(read_kind(action, observation, target)) and bool(source_pairs & pairs_in(text))


def save_csv(path, rows):
    if not rows: path.write_text('',encoding='utf-8'); return
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',type=Path,default=OUT/'preflight')
    parser.add_argument('--output',type=Path,default=OUT/'diagnosis')
    args=parser.parse_args(); out=args.output;out.mkdir(parents=True,exist_ok=True)
    targets=read(args.preflight/'targets.private.json')['tasks']
    with (args.preflight/'run_index.csv').open(encoding='utf-8',newline='') as f: runs=list(csv.DictReader(f))
    all_rows=[];events=[];mappings=[]
    for task_num,t in enumerate(targets,1):
        tid=t['task_id'];repo=ROOT/'benchmark/tasks'/tid/'repo';index=SourceIndex(repo)
        entry=set();support=set();closure=set();missing_entries=[];unresolved_support=[]
        for symbol in t['entrypoints_declared']:
            file=index.resolve(symbol)
            mappings.append({'task_id':tid,'symbol':symbol,'file':file or '', 'status':'statically_mapped' if file else 'unresolved'})
            if file:entry.add(file)
            else:missing_entries.append(symbol)
        for raw in t['required_source_files']:
            file=index.resolve(raw)
            if file:support.add(file)
            else:unresolved_support.append(raw)
        if t['closure_gold_path']:
            def paths(v):
                if isinstance(v,dict):
                    for k,x in v.items():
                        if k=='source_path' and isinstance(x,str):yield x
                        else:yield from paths(x)
                elif isinstance(v,list):
                    for x in v:yield from paths(x)
            for raw in paths(read(ROOT/t['closure_gold_path'])):
                f=index.resolve(raw)
                if f:closure.add(f)
        files=entry|support|closure;source_pairs={}
        for file in files:
            try:source_pairs[file]=pairs_in((repo/file).read_text(encoding='utf-8-sig'))
            except (OSError,UnicodeError):source_pairs[file]=set()
        for run in [r for r in runs if r['task_id']==tid]:
            path=ROOT/run['events_path'];actions={};seen=set();exposed={};explicit={};search_attempt=False;search_hit=False
            malformed=0;duplicates=0;orphan=0;step=0;matches=0;observations=0
            if path.is_file():
                for line in path.open(encoding='utf-8',errors='replace'):
                    try:e=json.loads(line)
                    except json.JSONDecodeError:malformed+=1;continue
                    eid=e.get('id')
                    if eid and eid in seen:duplicates+=1;continue
                    if eid:seen.add(eid)
                    if e.get('kind')=='ActionEvent':
                        step+=1;actions[eid]=(step,e.get('action') or {});continue
                    if e.get('kind')!='ObservationEvent':continue
                    observations+=1;pair=actions.get(e.get('action_id'))
                    if not pair:orphan+=1;continue
                    matches+=1;num,action=pair;o=e.get('observation') or {}
                    text='\n'.join(c.get('text','') for c in o.get('content',[]) if isinstance(c,dict))
                    cmd=str(action.get('command',''))
                    if SEARCH.search(cmd):
                        terms=[*entry,*t['entrypoints_declared']]
                        search_attempt|=any(x in cmd for x in terms)
                        if not o.get('is_error'):search_hit|=any(x in text for x in terms)
                    for file in files:
                        if file in explicit:continue
                        if content_confirmed(action,o,file,source_pairs[file],text):
                            kind=read_kind(action,o,file)
                            if file in exposed and kind!='explicit_read':continue
                            exposed.setdefault(file,num)
                            if kind=='explicit_read':explicit[file]=num
                            events.append({'model':run['model'],'task_id':tid,'file':file,'entrypoint_file':file in entry,
                                'support_file':file in support,'closure_file':file in closure,'action_step':num,
                                'action_id':e.get('action_id'),'observation_id':eid,'action_kind':action.get('kind'),'evidence_kind':kind,
                                'command_or_path':action.get('path') or cmd,
                                'matched_source_pair':json.dumps(sorted(source_pairs[file]&pairs_in(text))[0]),
                                'observation_sha256':hashlib.sha256(text.encode()).hexdigest()})
            hits=entry & exposed.keys()
            explicit_hits=entry & explicit.keys()
            status='paired_events_available' if matches and not malformed and not orphan else 'partial_or_unavailable'
            all_rows.append({'model':run['model'],'task_id':tid,'outcome':run['first_failure_stage'],
                'trace_status':status,'action_count':step,'observation_count':observations,'paired_observations':matches,
                'malformed_lines':malformed,'duplicate_events':duplicates,'orphan_observations':orphan,
                'declared_entrypoints':len(t['entrypoints_declared']),'mapped_entrypoint_files':len(entry),
                'unresolved_entrypoint_symbols':len(missing_entries),'search_attempt':int(search_attempt),'search_hit':int(search_hit),
                'entrypoint_content_exposed':int(bool(hits)),
                'entrypoint_explicit_read':int(bool(explicit_hits)),
                'first_explicit_read_action_step':min(explicit[f] for f in explicit_hits) if explicit_hits else '',
                'first_exposure_action_step':min(exposed[f] for f in hits) if hits else '',
                'entrypoint_files_exposed':len(hits),'support_raw_entries':len(t['required_source_files']),
                'support_mapped_files':len(support),'support_unresolved_entries':len(unresolved_support),
                'support_exposed_files':len(support&exposed.keys()),'has_closure_annotation':int(bool(t['closure_gold_path'])),
                'closure_mapped_files':len(closure),'closure_exposed_files':len(closure&exposed.keys())})
        if task_num%25==0:print(f'{task_num}/150 tasks; {len(all_rows)} runs',flush=True)
    assert len(all_rows)==900
    save_csv(out/'entrypoint_mapping.csv',mappings);save_csv(out/'exposure_events.csv',events);save_csv(out/'run_exposure.csv',all_rows)
    groups={'functional_pass':'Pass','public_failure':'Behavioral-first failure','hidden_failure':'Behavioral-first failure',
            'missing_submission':'Delivery/build failure','build_failure':'Delivery/build failure','isolation_failure':'Isolation-first failure'}
    summary=[]
    for model in ['ALL',*sorted({r['model'] for r in all_rows})]:
        for category in dict.fromkeys(groups.values()):
            rows=[r for r in all_rows if (model=='ALL' or r['model']==model) and groups[r['outcome']]==category]
            hits=[r for r in rows if r['entrypoint_explicit_read']]
            summary.append({'model':model,'outcome_group':category,'all_runs':len(rows),
                'paired_trace_runs':sum(r['trace_status']=='paired_events_available' for r in rows),
                'confirmed_explicit_read_runs':len(hits),'confirmed_explicit_read_percent':100*len(hits)/len(rows) if rows else '',
                'including_search_snippet_runs':sum(r['entrypoint_content_exposed'] for r in rows),
                'median_first_explicit_read_action_step':median(r['first_explicit_read_action_step'] for r in hits) if hits else ''})
    save_csv(out/'summary_by_model_outcome.csv',summary)
    print(json.dumps([r for r in summary if r['model']=='ALL'],indent=2))
    (out/'method.json').write_text(json.dumps({'runs':900,'scope':'Conservative file-content exposure, not symbol understanding or complete localization',
       'step':'one-based ActionEvent order; not the configured budget counter',
       'confirmation':'Successful literal source-mount read plus two adjacent non-comment normalized source lines, at least 12 characters each; search snippets reported separately',
       'negative':'No match means not confirmed, not absence of reading',
       'mapping':'Static dotted symbol/file mapping; unresolved declarations retained; semantic relevance not re-adjudicated',
       'limitations':['relative paths, search formatting, truncation, dynamic inspection and shell scripts may be missed',
       'content pair may lie outside entrypoint body; measures file exposure only',
       'paired events do not prove complete trajectory logging','no causal labels','closure scope remains annotated reference files'],
       'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__': main()
