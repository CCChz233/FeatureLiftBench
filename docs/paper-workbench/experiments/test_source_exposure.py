"""Regression checks for observable exposure; no benchmark or model execution."""
import tempfile
import unittest
from pathlib import Path
from diagnose_source_exposure import SourceIndex, content_confirmed, pairs_in, read_kind


class ExposureTests(unittest.TestCase):
    text = 'def resolve_feature(value):\n    return normalize_input(value)\n'
    target = 'pkg/core.py'
    observation = {'is_error': False, 'exit_code': 0,
                   'metadata': {'working_dir': '/flb/workspace/repo'}}

    def check(self, command, expected, observation=None, text=None):
        action = {'kind': 'TerminalAction', 'command': command}
        self.assertEqual(bool(content_confirmed(action, observation or self.observation,
            self.target, pairs_in(self.text), self.text if text is None else text)), expected)

    def test_literal_and_relative_reads(self):
        self.check('cat /flb/workspace/repo/pkg/core.py', True)
        self.check("cd /flb/workspace && sed -n '1,80p' repo/pkg/core.py", True)
        self.check('cat pkg/core.py', True)
        self.check('cat core.py', True, {'metadata': {'working_dir':'/flb/workspace/repo/pkg'}})

    def test_wrong_file_or_artifact_is_not_source(self):
        self.check('cat /flb/workspace/output/pkg/core.py', False)
        self.check('cat core.py', False)
        self.check('echo pkg/core.py; cat /flb/workspace/output/pkg/core.py', False)
        self.check('cat pkg/core.py', False, {'metadata': {'working_dir':'/flb/workspace/output'}})

    def test_failure_copy_filename_and_execution_are_not_exposure(self):
        self.check('cat pkg/core.py', False, {'is_error':True})
        self.check('cat pkg/core.py', False, {'exit_code':1})
        self.check('cat pkg/core.py', False, text='pkg/core.py')
        self.check('find pkg/core.py', False)
        self.check('cp pkg/core.py output/; cat pkg/core.py', False)
        self.check('python pkg/core.py', False)
        self.check('cat pkg/core.py > output.py', False)

    def test_editor_and_truncation(self):
        a={'kind':'FileEditorAction','command':'view','path':'/flb/workspace/repo/pkg/core.py'}
        self.assertTrue(content_confirmed(a,{},self.target,pairs_in(self.text),self.text))
        self.assertFalse(content_confirmed(a,{},self.target,pairs_in(self.text),self.text.splitlines()[0]))
        self.assertEqual(pairs_in('1\tdef resolve_feature(value):\n2\t    return normalize_input(value)'),pairs_in(self.text))

    def test_search_is_separate(self):
        a={'kind':'TerminalAction','command':"grep -n 'resolve_feature' pkg/core.py"}
        self.assertEqual(read_kind(a,self.observation,self.target),'search_snippet')
        self.assertTrue(content_confirmed(a,self.observation,self.target,pairs_in(self.text),self.text))

    def test_static_reexport_and_nested_nonbinding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p=root/'src/pkg';p.mkdir(parents=True)
            (p/'__init__.py').write_text('from .core import resolve_feature\n',encoding='utf-8')
            (p/'core.py').write_text(self.text+'\ndef outer():\n    def hidden(): pass\n',encoding='utf-8')
            index=SourceIndex(root)
            self.assertEqual(index.resolve('pkg.resolve_feature'),'src/pkg/core.py')
            self.assertIsNone(index.resolve('pkg.core.hidden'))
            self.assertIsNone(index.resolve('../outside.py'))


if __name__=='__main__': unittest.main()
