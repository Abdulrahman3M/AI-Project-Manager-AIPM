"""Offline structural regression tests. Does not execute Windows browser processes."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BrowserEnvironmentSkillTests(unittest.TestCase):
    def test_required_structure(self):
        for name in ['SKILL.md','PROMPT.md','VERSION','CHANGELOG.md',
                     'scripts/Browser-Environment.ps1','references/Browser-Compatibility.md',
                     'examples/Usage.md','troubleshooting/Common-Issues.md']:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_core_actions_and_constraints(self):
        code = (ROOT / 'scripts/Browser-Environment.ps1').read_text()
        for name in ['Create','Start','Status','Repair','Connect','Reset','-ConfirmReset',
                     '--remote-debugging-address=127.0.0.1','Get-NetTCPConnection',
                     'OwningProcess', 'userDataDirectory', 'CreateShortcut', '/json/version']:
            self.assertIn(name,code)
        for unsafe in ('Stop-Process -Name msedge','taskkill /IM msedge','Remove-Item -Recurse -Force'):
            self.assertNotIn(unsafe,code)

    def test_prompt_alignment(self):
        p=(ROOT/'PROMPT.md').read_text()
        for s in ('Profile 1','user data directory','example.com','screenshot','personal'):
            self.assertIn(s.lower(),p.lower())

    def test_skill_frontmatter(self):
        skill=(ROOT/'SKILL.md').read_text()
        self.assertRegex(skill,r'(?s)^---\nname: browser-environment-manager\ndescription: .+?\n---')
        self.assertEqual((ROOT/'VERSION').read_text().strip(),'1.0.0')

if __name__ == '__main__': unittest.main()
