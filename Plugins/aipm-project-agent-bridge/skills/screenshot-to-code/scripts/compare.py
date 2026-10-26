"""Create diagnostic screenshot differences. Exit 0 means measured, never accepted."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image, ImageChops, ImageDraw, ImageStat


def load_rgb(path):
    with Image.open(path) as source:
        source.load()
        return Image.alpha_composite(Image.new('RGBA', source.size, 'white'), source.convert('RGBA')).convert('RGB')


def boxes(path, size, reason=False):
    if path is None:
        return []
    records = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('Region/mask document must be a JSON list')
    ids = set()
    for record in records:
        box = record.get('box')
        if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
            raise ValueError('Each box must contain four integer raster coordinates')
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= size[0] and 0 <= y0 < y1 <= size[1]):
            raise ValueError('Box is outside image dimensions or empty')
        if reason:
            if not isinstance(record.get('reason'), str) or not record['reason'].strip():
                raise ValueError('Every mask needs a nonempty reason')
        else:
            key = record.get('id')
            if not isinstance(key, str) or not key or key in ids:
                raise ValueError('Every region needs a unique nonempty id')
            ids.add(key)
    return records


def metrics(diff, include, threshold):
    count = include.histogram()[255]
    if not count:
        raise ValueError('No comparable pixels remain')
    channels = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    changed = maximum.point(lambda v: 255 if v > threshold else 0)
    changed = ImageChops.multiply(changed, include)
    return {'pixels': count, 'changed_percent': round(100 * changed.histogram()[255] / count, 6),
            'mean_absolute_error': round(sum(ImageStat.Stat(diff, include).mean) / 3, 6),
            'max_channel_error': max(i for i, n in enumerate(maximum.histogram(mask=include)) if n)}


def compare(reference, actual, out, threshold=8, regions=None, masks=None):
    if not 0 <= threshold <= 255:
        raise ValueError('Threshold must be between 0 and 255')
    ref, cand = load_rgb(reference), load_rgb(actual)
    if ref.size != cand.size:
        raise ValueError(f'Image dimensions differ: {ref.size} vs {cand.size}; recapture, do not resize')
    if out.resolve() in [reference.resolve(), actual.resolve()]:
        raise ValueError('Output directory must not replace an input')
    region_records, mask_records = boxes(regions, ref.size), boxes(masks, ref.size, True)
    include = Image.new('L', ref.size, 255)
    for record in mask_records:
        include.paste(0, tuple(record['box']))
    diff = ImageChops.difference(ref, cand)
    raw = metrics(diff, Image.new('L', ref.size, 255), threshold)
    unmasked = metrics(diff, include, threshold)
    regional = []
    for record in region_records:
        box = tuple(record['box'])
        regional.append({'id': record['id'], 'box': record['box'],
                         **metrics(diff.crop(box), Image.new('L', diff.crop(box).size, 255), threshold),
                         'mask_applied': False})
    data = {'schema_version': 1, 'quality_status': 'NOT_ASSESSED',
            'note': 'Diagnostic pixel error is not semantic, functional, accessibility, or perceptual acceptance.',
            'raster_pixels': list(ref.size), 'threshold': threshold, 'alpha_background': '#ffffff',
            'reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
            'actual_sha256': hashlib.sha256(actual.read_bytes()).hexdigest(),
            'global': raw, 'unmasked': unmasked,
            'masked_percent': round(100 * (1 - unmasked['pixels'] / raw['pixels']), 6),
            'masks': mask_records, 'regions': regional}
    out.mkdir(parents=True, exist_ok=True)
    # Never allow the fixed artifact names to overwrite either source image.
    targets = [out / name for name in ['metrics.json', 'overlay.png', 'heatmap.png', 'side-by-side.png']]
    if any(p.resolve() in [reference.resolve(), actual.resolve()] for p in targets):
        raise ValueError('Artifact path would overwrite an input')
    Image.blend(ref, cand, .5).save(out / 'overlay.png')
    channels = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    Image.merge('RGB', (maximum, Image.new('L', ref.size), Image.new('L', ref.size))).save(out / 'heatmap.png')
    side = Image.new('RGB', (ref.width * 2, ref.height), 'white')
    side.paste(ref, (0, 0)); side.paste(cand, (ref.width, 0)); side.save(out / 'side-by-side.png')
    (out / 'metrics.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference', type=Path); p.add_argument('actual', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--threshold', type=int, default=8)
    p.add_argument('--regions', type=Path); p.add_argument('--masks', type=Path)
    args = p.parse_args()
    try:
        result = compare(args.reference, args.actual, args.out, args.threshold, args.regions, args.masks)
    except (OSError, ValueError, TypeError, AttributeError) as e:
        p.exit(2, f'Comparison failed: {e}\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
