#!/usr/bin/env python3
"""Materialize the pre-evaluation public-source API review (no benchmark tests).

The curated decisions below are research inputs, not evaluator-derived repairs.
They assess whether an existing source binding can be re-exported without a body
or signature change. They do not certify behavioral equivalence.
"""
from __future__ import annotations
import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'harness'))
from featureliftbench.direct_source_extraction import SourceIndex, sha

# task prefix -> API -> (decision, candidate/source symbol, reason, evidence ranges)
# Evidence is relative to the pinned full source tree, with inclusive line bounds.
REVIEWS = {
 'coverage': {
  'SourceSelector': ('adaptation_required', 'coverage.inorout.InOrOut',
   'InOrOut requires CoverageConfig, warn/debug and namespace settings. Its selection method accepts a frame, while skip_reason accepts modulename. Constructor and method adaptation are required.',
   [('coverage/inorout.py', 180, 218), ('coverage/inorout.py', 396, 455)]),
 },
 'dateutil': {
  'ZoneResolver': ('adaptation_required', 'dateutil.zoneinfo.ZoneInfoFile',
   'ZoneInfoFile loads a tar stream and exposes get(name, default). It has no load_zone(name, tzdata) or register_alias API with alias-cycle handling.',
   [('src/dateutil/zoneinfo/__init__.py', 30, 68)]),
  'parse_tzfile': ('adaptation_required', 'dateutil.tz.tz.tzfile._read_tzfile',
   'The upstream parser is an instance method taking a file object and constructing timezone data, not a bytes-to-metadata-dict function.',
   [('src/dateutil/tz/tz.py', 488, 530)]),
  'UnknownZoneError': ('adaptation_required', 'dateutil.zoneinfo.ZoneInfoFile.get',
   'Missing names return the supplied default; the contract needs a named error for missing names and alias cycles. An exception alias alone cannot change this control flow.',
   [('src/dateutil/zoneinfo/__init__.py', 54, 68)]),
  'InvalidTZFileError': ('adaptation_required', 'dateutil.tz.tz.tzfile._read_tzfile',
   'No source binding with this name was found in the indexed runtime files. The parser raises builtin ValueError for bad magic; this protocol does not synthesize exception classes, translate exceptions, or invent builtin aliases.',
   [('src/dateutil/tz/tz.py', 488, 510)]),
 },
 'flake8': {
  'OptionSpec': ('adaptation_required', 'flake8.options.manager.Option',
   'Option is an argparse registration object; its first positional arguments are option names, while OptionSpec starts with dest, parse_from_config and default. Renaming does not preserve argument meaning.',
   [('src/flake8/options/manager.py', 41, 100)]),
  'PluginSpec': ('adaptation_required', 'flake8.plugins.finder.LoadedPlugin',
   'LoadedPlugin holds plugin, obj and parameters; Plugin holds package/version/entry_point. Neither has the requested name/codes/checker_type/options constructor.',
   [('src/flake8/plugins/finder.py', 30, 69)]),
  'classify_plugins': ('adaptation_required', 'flake8.plugins.finder._classify_plugins',
   'The existing function requires LoadedPlugin objects and a second PluginOptions argument; the requested function takes only a list of PluginSpec.',
   [('src/flake8/plugins/finder.py', 310, 352)]),
  'apply_select_ignore': ('adaptation_required', 'flake8.plugins.finder._classify_plugins',
   'No standalone select/ignore function with the contract interface was found. Classification uses loaded objects and opts.enable_extensions; producing the declared filtering API needs new wiring.',
   [('src/flake8/plugins/finder.py', 310, 335)]),
  'OptionManager': ('existing_binding_interface_mismatch', 'flake8.options.manager.OptionManager',
   'Same-name export exists, but the upstream constructor requires keyword-only version, plugin_versions, parents and formatter_names; the contract permits OptionManager(). Keep the unchanged export and disclose mismatch.',
   [('src/flake8/options/manager.py', 207, 243)]),
 },
 'hatch': {
  'normalize_project_metadata': ('adaptation_required', 'hatchling.metadata.core.ProjectMetadata',
   'ProjectMetadata needs root/plugin_manager/config and exposes properties. The contract takes a project dict and returns a normalized dict; this requires orchestration and output construction.',
   [('backend/src/hatchling/metadata/core.py', 39, 63), ('backend/src/hatchling/metadata/core.py', 399, 436)]),
  'select_environment': ('adaptation_required', 'hatch.project.config._populate_default_env_values',
   'The relevant helper mutates data/config with seen/active traversal state. It is not the requested (envs, name) -> dict API.',
   [('src/hatch/project/config.py', 688, 729)]),
  'MetadataValidationError': ('adaptation_required', 'hatchling.metadata.core.CoreMetadata.classifiers',
   'No source exception with this name was found. Classifier validation raises ValueError and TypeError; the reviewed source-only alias policy does not create a new exception binding or translate errors.',
   [('backend/src/hatchling/metadata/core.py', 948, 995)]),
 },
 'httpx': {
  'build_request': ('adaptation_required', 'httpx._client.BaseClient.build_request',
   'The inherited source method needs self and reads client defaults. The target is a free function accepting base_url/default_params/default_headers/default_cookies; fixing entrypoint discovery cannot construct that state or adapt the signature.',
   [('httpx/_client.py', 319, 368), ('httpx/_client.py', 564, 565)]),
 },
 'poetry_core': {
  'DependencySpec': ('adaptation_required', 'poetry.core.packages.dependency.Dependency',
   'Dependency requires constraint and accepts groups, not the target optional constraint plus group/marker fields. Direct renaming cannot supply the requested data model.',
   [('src/poetry/core/packages/dependency.py', 38, 75)]),
  'parse_project_dependencies': ('adaptation_required', 'poetry.core.factory.Factory._configure_package_dependency_groups',
   'Factory configures a ProjectPackage using separate poetry and dependency-group structures; the target returns a dict of standalone groups from one project dict.',
   [('src/poetry/core/factory.py', 455, 515)]),
  'resolve_group': ('adaptation_required', 'poetry.core.packages.dependency_group.DependencyGroup._resolve_included_dependency_groups',
   'The source method traverses stored group objects; the target accepts a name, group dict and seen set and requires circular-include ValueError handling.',
   [('src/poetry/core/packages/dependency_group.py', 107, 123), ('src/poetry/core/packages/dependency_group.py', 156, 164)]),
  'DependencyGroup': ('existing_binding_interface_mismatch', 'poetry.core.packages.dependency_group.DependencyGroup',
   'The source constructor has keyword-only optional/mixed_dynamic and initializes its own dependencies. The target accepts dependencies and includes constructor fields. Same-name discovery is not interface compatibility.',
   [('src/poetry/core/packages/dependency_group.py', 19, 29)]),
 },
 'pytest': {
  'MarkerRegistry': ('adaptation_required', '_pytest.config.Config',
   'The source stores marker lines in Config ini state. No source class exposes the requested standalone from_ini/from_lines/names/description registry API.',
   [('src/_pytest/config/__init__.py', 1546, 1586)]),
  'parse_linelist': ('adaptation_required', '_pytest.config.Config._getini',
   'Linelist conversion exists inside a type-dispatch branch on Config state; extracting that branch into a new value-taking function exceeds direct re-export.',
   [('src/_pytest/config/__init__.py', 1594, 1636)]),
  'split_marker_line': ('adaptation_required', '_pytest.mark.pytest_cmdline_main',
   'Marker splitting is inline in the display loop, not a standalone line-to-tuple source function; lifting the statements into an API would synthesize a function.',
   [('src/_pytest/mark/__init__.py', 121, 131)]),
 },
 'python_decouple': {
  'RepositoryDict': ('adaptation_required', 'decouple.RepositoryEmpty',
   'RepositoryEmpty discards source and always reports no keys. It is not a dict repository. Exporting builtin dict would invent an implementation choice outside the source-binding policy.',
   [('decouple.py', 110, 118)]),
  'Config': ('existing_binding_interface_mismatch', 'decouple.Config',
   'The target accepts environ=None; source Config only accepts repository and directly reads os.environ. A same-name export does not support injecting the declared environment.',
   [('decouple.py', 61, 89)]),
  'Csv': ('existing_binding_default_difference', 'decouple.Csv',
   'Both bindings exist, but target strip defaults to a single space and source strip defaults to string.whitespace. No default change is performed.',
   [('decouple.py', 257, 285)]),
  'Choices': ('existing_binding_interface_mismatch', 'decouple.Choices',
   'Target choices is the first argument; upstream first argument is flat and choices is a different Django-style option. Positional flat lists can work, but keyword choices has different meaning.',
   [('decouple.py', 289, 307)]),
 },
 'readme_renderer': {
  'render_readme': ('adaptation_required', 'readme_renderer.markdown.render',
   'The source renders markdown with a variant and returns str or None. The target dispatches on media type and returns (html, warnings), requiring dispatch and output adaptation.',
   [('readme_renderer/markdown.py', 76, 102)]),
 },
 'requests_cache': {
  'create_cache_key': ('direct_alias', 'requests_cache.cache_keys.create_key',
   'A name-only candidate: source create_key already accepts a request object plus cache-key keyword options and returns a digest string. Re-export unchanged as create_cache_key. This does not certify arbitrary request-like objects: normalize_request expects copy() and mutable fields, and dependencies may violate isolation.',
   [('requests_cache/cache_keys.py', 55, 94), ('requests_cache/cache_keys.py', 114, 142)]),
  'CachePolicy': ('adaptation_required', 'requests_cache.policy.directives.CacheDirectives',
   'CacheDirectives holds parsed directives, not should_store/expiration_seconds/reason. Its from_headers lacks default/now. The policy object and decision logic need adaptation.',
   [('requests_cache/policy/directives.py', 12, 47)]),
  'get_expiration': ('adaptation_required', 'requests_cache.policy.expiration.get_expiration_datetime',
   'The source accepts an expiration value and returns an absolute datetime; even get_expiration_seconds accepts a value rather than headers/default/now. Header precedence and return adaptation are needed.',
   [('requests_cache/policy/expiration.py', 22, 63)]),
  'create_key': ('existing_binding_interface_mismatch', 'requests_cache.cache_keys.create_key',
   'The target takes method and url as explicit fields. Upstream create_key instead requires a request object. Its suitability as create_cache_key does not make this same-name export compatible.',
   [('requests_cache/cache_keys.py', 55, 82)]),
  'normalize_body': ('existing_binding_interface_mismatch', 'requests_cache.cache_keys.normalize_body',
   'The target takes body and headers; source takes a prepared request and required ignored_parameters, then reads request.body/headers.',
   [('requests_cache/cache_keys.py', 168, 198)]),
  'normalize_headers': ('existing_binding_input_domain_difference', 'requests_cache.cache_keys.normalize_headers',
   'The target signature permits headers=None; source immediately calls headers.items(). Export is retained unchanged, with this public-source discrepancy disclosed.',
   [('requests_cache/cache_keys.py', 145, 157)]),
 },
 'setuptools_scm': {
  'version_from_scm': ('adaptation_required', 'setuptools_scm._get_version.get_version',
   'get_version accepts SCM configuration and root, but no tag/distance/dirty/node keyword inputs. It invokes the SCM versioning pipeline; the requested no-subprocess function needs construction and formatting of supplied SCM state.',
   [('setuptools-scm/src/setuptools_scm/_get_version.py', 34, 80)]),
 },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to overwrite a review; use a versioned path.')
    suite = json.loads((args.suite / 'prepared_suite.json').read_text())
    tasks = {}
    for old in suite['tasks']:
        tid = old['task_id']
        spec = json.loads((ROOT / 'benchmark/tasks' / tid / 'metadata.json').read_text())['public_spec']
        import hashlib
        if hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest() != old['public_spec_sha256']:
            raise SystemExit('Public contract changed: ' + tid)
        curated = REVIEWS.get(tid.split('__')[0], {}) if old.get('unresolved_api') else {}
        row = {k: old[k] for k in ['source_snapshot_id', 'source_archive_sha256', 'public_spec_sha256', 'lift_type']}
        row.update(aliases={}, api_reviews={}, original_unmapped_api=old['unresolved_api'],
                   original_export_mappings=old['export_mappings'],
                   review_scope='all_required_top_level_apis_in_11_flagged_tasks' if curated else 'automatic_name_mapping_only_not_interface_audit')
        source = (args.suite / 'sources' / old['source_snapshot_id']).resolve()
        if curated:
            idx = SourceIndex(source)
            for api in spec['required_api']:
                name = api['path'].split('.')[1]
                if name in curated:
                    decision, symbol, reason, spans = curated[name]
                else:
                    # Existing exports are documented without asserting correctness.
                    value = old['export_mappings'].get(name)
                    if not value:
                        raise ValueError('Missing curated decision: ' + tid + '/' + name)
                    module, attrs = value
                    path = idx.modules[module]
                    node = next((n for n in ast.walk(idx.tree(module)) if getattr(n, 'name', '') == attrs[0]), None) if attrs else None
                    spans = [(str(path.relative_to(source)), node.lineno if node else 1, node.end_lineno if node else 1)]
                    decision, symbol = 'existing_binding_not_behaviorally_validated', '.'.join([module, *attrs])
                    reason = 'The declared top-level source binding is present. No body or signature edits are applied; this records availability only, not behavioral equivalence or isolation success.'
                evidence = []
                for path, start, end in spans:
                    f = source / path
                    if not (1 <= start <= end <= len(f.read_text().splitlines())):
                        raise ValueError('Invalid source evidence range: ' + path)
                    evidence.append({'path': path, 'start_line': start, 'end_line': end, 'sha256': sha(f)})
                row['api_reviews'][name] = {'decision': decision, 'source_symbol': symbol,
                    'target_api': api, 'reason': reason, 'source_evidence': evidence}
                if decision == 'direct_alias':
                    row['aliases'][name] = symbol
            assert set(old['unresolved_api']) <= set(row['api_reviews'])
        tasks[tid] = row
    result = {'schema': 'featureliftbench.dse_public_api_review.v1',
        'created_date': '2026-09-26', 'reviewer': 'assistant-assisted public-contract and pinned-source review',
        'selection_sha256': suite['selection_sha256'], 'original_suite_sha256': sha(args.suite / 'prepared_suite.json'),
        'review_builder_sha256': sha(Path(__file__)),
        'policy': 'Only source top-level name aliases; no wrappers, builtins invented as implementations, exception translation, state construction, argument conversion, test inspection or feedback repair.',
        'scope_limit': '11 tasks with originally unmapped names were manually reviewed. Remaining 29 have name-coverage records only. Neither category certifies behavior.',
        'entrypoint_parser_repairs': ['Explicit package __init__ locations', 'Single statically named base-class method resolution'],
        'functional_results_consulted': False, 'benchmark_tests_or_reference_consulted': False,
        'tasks': tasks}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'tasks': len(tasks), 'reviewed_tasks': sum(bool(r['api_reviews']) for r in tasks.values()),
        'originally_unmapped_apis': sum(len(r['original_unmapped_api']) for r in tasks.values()),
        'direct_aliases': sum(len(r['aliases']) for r in tasks.values())}))


if __name__ == '__main__':
    main()
