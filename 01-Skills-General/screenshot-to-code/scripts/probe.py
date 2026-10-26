"""Inspect source raster pixels without pretending to identify fonts or CSS."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--sample', action='append', default=[], metavar='X,Y')
    args = p.parse_args()
    try:
        with Image.open(args.image) as original:
            im = original.convert('RGB')
            samples = []
            for value in args.sample:
                x, y = map(int, value.split(','))
                if not (0 <= x < im.width and 0 <= y < im.height):
                    raise ValueError('Sample outside image dimensions')
                rgb = im.getpixel((x, y))
                samples.append({'xy': [x, y], 'rgb': list(rgb), 'hex': '#%02x%02x%02x' % rgb})
            palette = im.copy()
            palette.thumbnail((256, 256))
            colors = palette.quantize(colors=12).convert('RGB').getcolors(65536) or []
            data = {'sha256': hashlib.sha256(args.image.read_bytes()).hexdigest(),
                    'raster_pixels': list(im.size), 'source_mode': original.mode,
                    'css_viewport': 'UNKNOWN', 'device_pixel_ratio': 'UNKNOWN',
                    'samples': samples, 'approximate_dominant_colors': [
                        {'hex': '#%02x%02x%02x' % c, 'sample_count': n} for n, c in sorted(colors, reverse=True)[:12]],
                    'note': 'Dominant colors are quantized diagnostics. CSS colors, fonts, scale and opacity require separate evidence.'}
        print(json.dumps(data, indent=2))
    except (OSError, ValueError) as e:
        p.exit(2, f'Inspection failed: {e}\n')

if __name__ == '__main__':
    main()
