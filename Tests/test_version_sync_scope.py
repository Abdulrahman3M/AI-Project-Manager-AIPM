from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_support import TEST_WORKSPACE


class ProductVersionSyncScopeTests(unittest.TestCase):
    def test_product_version_sync_updates_shared_platform_tui_and_plugin_release(self) -> None:
        with tempfile.TemporaryDirectory(prefix='aipm-version-sync-', dir=TEST_WORKSPACE) as temporary:
            root = Path(temporary)
            for relative in (
                'Maintenance-Tools', 'Versioning/Release-Notes',
                'TUI/AI-Project-Manager', 'Plugins/aipm-project-agent-bridge', 'docs/project/Release-Notes',
            ):
                (root / relative).mkdir(parents=True, exist_ok=True)
            source_script = Path(__file__).resolve().parents[1] / 'Maintenance-Tools/Sync-Product-Version.py'
            shutil.copy2(source_script, root / 'Maintenance-Tools/Sync-Product-Version.py')
            (root / 'Versioning/VERSION').write_text('1.11.14\n', encoding='utf-8')
            (root / 'Versioning/CHANGELOG.md').write_text('## [1.11.14] — Product update\n\n- Test.\n', encoding='utf-8')
            (root / 'Versioning/Release-Notes/v1.11.14.md').write_text('# v1.11.14\n', encoding='utf-8')
            (root / 'VERSION').write_text('1.11.13\n', encoding='utf-8')
            (root / 'TUI/AI-Project-Manager/VERSION').write_text('1.11.13\n', encoding='utf-8')
            (root / 'Plugins/VERSION').write_text('1.11.13\n', encoding='utf-8')
            (root / 'Plugins/aipm-project-agent-bridge/VERSION').write_text('1.11.13\n', encoding='utf-8')
            for relative in ('CHANGELOG.md', 'TUI/AI-Project-Manager/CHANGELOG.md', 'Plugins/CHANGELOG.md'):
                (root / relative).write_text('## [1.11.13] — Existing\n\n- Keep.\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(root / 'Maintenance-Tools/Sync-Product-Version.py')], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'VERSION').read_text(encoding='utf-8').strip(), '1.11.14')
            self.assertEqual((root / 'TUI/AI-Project-Manager/VERSION').read_text(encoding='utf-8').strip(), '1.11.14')
            self.assertEqual((root / 'Plugins/VERSION').read_text(encoding='utf-8').strip(), '1.11.14')
            self.assertEqual((root / 'Plugins/aipm-project-agent-bridge/VERSION').read_text(encoding='utf-8').strip(), '1.11.13')
            self.assertIn('## [1.11.14]', (root / 'Plugins/CHANGELOG.md').read_text(encoding='utf-8'))
            self.assertEqual((root / 'docs/project/Release-Notes/Release-Notes-v1.11.14.md').read_bytes(), (root / 'Versioning/Release-Notes/v1.11.14.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
