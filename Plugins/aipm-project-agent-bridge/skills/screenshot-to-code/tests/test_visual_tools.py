"""Deterministic metric contracts; no model or network calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

class VisualToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.p = Path(self.temp.name)
        self.ref = self.p / 'ref.png'
        self.actual = self.p / 'actual.png'
        Image.new('RGB', (20, 10), 'white').save(self.ref)
        Image.new('RGB', (20, 10), 'white').save(self.actual)

    def tearDown(self):
        self.temp.cleanup()

    def run_diff(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/compare.py'), str(self.ref), str(self.actual), '--out', str(self.p / 'diff'), *args], capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})

    def result(self):
        return json.loads((self.p / 'diff/metrics.json').read_text())

    def test_identical_images_have_zero_error_and_artifacts(self):
        r = self.run_diff()
        self.assertEqual(r.returncode, 0, r.stderr)
        data = self.result()
        self.assertEqual(data['global']['changed_percent'], 0)
        self.assertEqual(data['global']['mean_absolute_error'], 0)
        self.assertEqual(data['quality_status'], 'NOT_ASSESSED')
        for name in ['overlay.png', 'heatmap.png', 'side-by-side.png']:
            self.assertTrue((self.p / 'diff' / name).is_file())

    def test_small_region_cannot_be_hidden_by_large_background(self):
        im = Image.open(self.actual)
        im.paste((0, 0, 0), (0, 0, 2, 2))
        im.save(self.actual)
        regions = self.p / 'regions.json'
        regions.write_text(json.dumps([{'id': 'button', 'box': [0, 0, 2, 2]}]))
        r = self.run_diff('--regions', str(regions))
        self.assertEqual(r.returncode, 0, r.stderr)
        data = self.result()
        self.assertEqual(data['global']['changed_percent'], 2)
        self.assertEqual(data['regions'][0]['changed_percent'], 100)

    def test_reject_size_mismatch_instead_of_resizing(self):
        Image.new('RGB', (10, 10), 'white').save(self.actual)
        r = self.run_diff()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('dimensions', r.stderr.lower())

    def test_overlapping_masks_count_once_and_keep_raw_score(self):
        Image.new('RGB', (20, 10), 'black').save(self.actual)
        masks = self.p / 'masks.json'
        masks.write_text(json.dumps([{'box': [0, 0, 10, 10], 'reason': 'clock'}, {'box': [0, 0, 10, 10], 'reason': 'clock overlap'}]))
        r = self.run_diff('--masks', str(masks))
        self.assertEqual(r.returncode, 0, r.stderr)
        data = self.result()
        self.assertEqual(data['global']['changed_percent'], 100)
        self.assertEqual(data['unmasked']['pixels'], 100)
        self.assertEqual(data['masked_percent'], 50)

    def test_full_mask_and_out_of_bounds_regions_fail(self):
        for box in [[0, 0, 20, 10], [-1, 0, 2, 2]]:
            masks = self.p / 'masks.json'
            masks.write_text(json.dumps([{'box': box, 'reason': 'dynamic'}]))
            self.assertNotEqual(self.run_diff('--masks', str(masks)).returncode, 0)

    def test_threshold_does_not_hide_mean_error(self):
        Image.new('RGB', (20, 10), (254, 254, 254)).save(self.actual)
        self.assertEqual(self.run_diff('--threshold', '2').returncode, 0)
        self.assertEqual(self.result()['global']['changed_percent'], 0)
        self.assertEqual(self.result()['global']['mean_absolute_error'], 1)

    def test_probe_records_hash_dimensions_and_sample(self):
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/probe.py'), str(self.ref), '--sample', '1,1'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data['samples'][0]['hex'], '#ffffff')
        self.assertEqual(data['raster_pixels'], [20, 10])
        self.assertEqual(len(data['sha256']), 64)

if __name__ == '__main__':
    unittest.main(verbosity=2)
