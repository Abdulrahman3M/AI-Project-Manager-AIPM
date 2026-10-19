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

    def test_authorized_legacy_reconnect_contract(self):
        code = (ROOT / 'scripts/Browser-Environment.ps1').read_text()
        for expected in [
            'IB-Edge-Debug', 'Register-AuthorizedLegacyEnvironment',
            'Get-CommandLineSwitchValue', 'PROCESS_INSPECTION_UNAVAILABLE',
            'LISTENER_INSPECTION_UNAVAILABLE', 'Wait-DedicatedCDP',
            'STARTUP_TIMEOUT', 'PARENT_PROCESS_AMBIGUOUS',
            'PROFILE_VERIFICATION_REQUIRES_AGENT_TOOL'
        ]:
            self.assertIn(expected, code)

    def test_legacy_data_directory_is_narrowly_scoped(self):
        code = (ROOT / 'scripts/Browser-Environment.ps1').read_text()
        self.assertIn("$Name -ceq 'AI-Agent-Browser'", code)
        self.assertIn("'C:\\Users\\Abdoo\\AppData\\Local\\IB-Edge-Debug'", code)
        self.assertIn("'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'", code)
        self.assertNotIn('Stop-Process', code)

    def test_prompt_alignment(self):
        p=(ROOT/'PROMPT.md').read_text()
        for s in ('Profile 1','user data directory','example.com','screenshot','personal'):
            self.assertIn(s.lower(),p.lower())

    def test_skill_frontmatter(self):
        skill=(ROOT/'SKILL.md').read_text()
        self.assertRegex(skill,r'(?s)^---\nname: browser-environment-manager\ndescription: .+?\n---')
        self.assertEqual((ROOT/'VERSION').read_text().strip(),'1.1.0')

if __name__ == '__main__': unittest.main()
