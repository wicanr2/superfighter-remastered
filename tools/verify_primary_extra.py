"""獨立核對鬼丸主色盤額外 blit、來源指標及保存完整 CPU 畫格。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image, ImageDraw
from verify_stage_sources import decode

ROOT = Path('/project')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--original-root', type=Path, default=Path('/orig'))
    args = parser.parse_args()
    root = args.output
    receipt = json.loads((root / 'receipt.json').read_text())
    assert receipt['script_sha256'] == sha(root / 'primary_extra_draw_receipt.go')
    assert receipt['unimplemented'] in (None, [])
    player = receipt['player']
    same_character = receipt.get('same_character', False)
    assert player in (0, 1) and receipt['selected'] == ([5, 5] if same_character else ([5, 4] if player == 0 else [4, 5]))
    source_manifest = json.loads((ROOT / 'workplace/source-manifest.json').read_text())
    sources = {x['name']: x['sha256'] for x in source_manifest['files']}
    data = {}
    for name, wanted in receipt['inputs'].items():
        p = args.original_root / name
        assert sha(p) == wanted == sources[name]
        data[name] = p.read_bytes()
    extras = []
    for blit in receipt['records']:
        assert blit['pixel_differences'] == blit['mask_differences'] == 0
        assert blit['sources']
        for source in blit['sources']:
            character = source['character']
            assert character == receipt['selected'][source['player']]
            raw = data[f'SFMAN{character+1:02d}.DAT']
            segment, offset = struct.unpack_from('<HH', raw, 0xb28 + source['slot'] * 4)
            at = 0xc48 + segment * 16 + offset
            width, height = raw[at:at + 2]
            end = at + 2 + (width + 1) // 2 * height
            assert at == source['file_offset'] and (width, height) == (blit['width'], blit['height'])
            assert digest(raw[at:end]) == blit['source_sha256'] and source['bytes_match_source']
            linear = ((source['table_segment'] + source['base_segment']) & 65535) * 16 + source['table_offset']
            assert linear == blit['source_ds'] * 16 + blit['source_si']
        if blit['role'] == 'effect':
            assert blit['palette_base'] == 0xc0 + player * 32
            assert blit['runtime_return_ip'] == (0x4393 if player == 0 else 0x4523)
            assert all(s['player'] == player and s['character'] == 5 and s['slot'] == 35 for s in blit['sources'])
            raw = data['MAN.COL'] if same_character and player == 1 else data['SFMAN06.DAT']
            palette_at = 5 * 48 if same_character and player == 1 else 0xac8
            expected = [[v*4 + v//16 for v in raw[palette_at+i*3:palette_at+(i+1)*3]] for i in range(16)]
            assert blit['runtime_colors'] == expected
            extras.append(blit)
    assert len(receipt['records']) == 404 and len(receipt['frames']) == 200 and len(extras) == 4
    for blit in extras:
        if not blit.get('fixture'):
            continue
        stem = blit['fixture']
        source = (root / (stem + '.source.bin')).read_bytes()
        assert digest(source) == blit['source_sha256']
        before = (root / (stem + '.before.idx')).read_bytes()
        after = (root / (stem + '.after.idx')).read_bytes()
        mask = (root / (stem + '.mask')).read_bytes()
        assert len(before) == len(after) == len(mask) == 64000
        expected = bytearray(before)
        coverage = bytearray(64000)
        width, height = source[:2]
        stride = (width + 1) // 2
        left, right, top = (blit['left_clip'] + 1) // 2, (blit['right_clip'] + 1) // 2, blit['top_clip']
        rows, pairs = height - top, stride - left - right
        flipx, flipy = bool(blit['flags'] & 64), bool(blit['flags'] & 128)
        start = blit['destination_di'] + (width - blit['left_clip'] - blit['right_clip'] if flipx else 0) + (rows * 320 if flipy else 0)
        start &= 65535
        for row in range(rows):
            source_row = row if flipy else row + top
            source_pair = right if flipx and not flipy else left
            for pair in range(pairs):
                value = source[2 + source_row*stride + source_pair + pair]
                for n, colour in enumerate((value >> 4, value & 15)):
                    at = (blit['destination_es'] - receipt['composition_buffer_segment']) * 16 + start + (-row if flipy else row) * 320 + (-1 if flipx else 1) * (pair*2 + n)
                    if colour and 0 <= at < 64000:
                        expected[at] = colour | blit['palette_base']
                        coverage[at] = 1
        assert bytes(expected) == after and bytes(coverage) == mask
    captures = []
    background_file = 'I2.XGB' if receipt['selected'][1] == 4 else 'I3.XGB'
    reference, _ = decode((args.original_root / background_file).read_bytes())
    for frame in receipt['frames']:
        assert frame['matched'] and frame['coverage'] == 64000 and frame['differences'] == 0
        if not frame.get('fixture'):
            continue
        stem = frame['fixture']
        metadata = json.loads((root / (stem + '.layers.json')).read_text())
        combined = bytearray(64000)
        for ordinal, layer in enumerate(metadata):
            indices = (root / f'{stem}.layer-{ordinal:02d}.idx').read_bytes()
            coverage = (root / f'{stem}.layer-{ordinal:02d}.mask').read_bytes()
            assert len(indices) == len(coverage) == 64000 and set(coverage) <= {0, 1}
            if ordinal == 0:
                camera = frame['camera_x']
                assert coverage == bytes([1]) * 64000
                assert indices == b''.join(reference[y*480+camera:y*480+camera+320] for y in range(200))
            for i, written in enumerate(coverage):
                if written:
                    combined[i] = indices[i]
        assert bytes(combined) == (root / (stem + '.idx')).read_bytes()
        captures.append({'fixture': stem, 'steps': frame['steps'], 'layers': frame['layers'], 'CPU_layers_match': True})
    assert len(captures) == 1
    manifest = json.loads((ROOT / 'assets/hd/characters/manifest.json').read_text())
    pose = next(p for p in manifest['poses'] if p['character'] == 5 and p['slot'] == 35 and p.get('palette_bank', 0) == 0 and not p.get('source_bank'))
    assert pose['source_sha256'] == extras[0]['source_sha256']
    atlas_path = ROOT / 'assets/hd/characters' / pose['atlas']
    assert sha(atlas_path) == next(a['sha256'] for a in manifest['atlases'] if a['file'] == pose['atlas'])
    sprite = data['SFMAN06.DAT'][extras[0]['sources'][0]['file_offset']:]
    width, height = sprite[:2]
    colours = extras[0]['runtime_colors']
    original = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            b = sprite[2 + y*((width+1)//2) + x//2]
            value = b >> 4 if x % 2 == 0 else b & 15
            if value:
                original.putpixel((x, y), tuple(colours[value]) + (255,))
    with Image.open(atlas_path) as atlas:
        art = atlas.crop(tuple(pose['rect'])).resize((width*4, height*4), Image.Resampling.BICUBIC)
    compare = Image.new('RGBA', (480, 340), '#18212b')
    compare.alpha_composite(original.resize((width*4, height*4), Image.Resampling.NEAREST), (80, 50))
    compare.alpha_composite(art, (320, 50))
    draw = ImageDraw.Draw(compare)
    draw.text((15, 15), 'Original primary palette', fill='white')
    draw.text((255, 15), 'Existing HD source 35', fill='white')
    compare.save(root / 'extra-source-comparison.png')
    report = {'kind': 'independent original primary-palette extra sprite evidence, not production acceptance',
              'player': player, 'same_character': same_character, 'blits': 404, 'frames': 200, 'primary_extra_blits': 4, 'saved_captures': captures,
              'extra_source': {'character': 5, 'slot': 35, 'file': 'SFMAN06.DAT', 'file_offset': extras[0]['sources'][0]['file_offset'],
                               'width': width, 'height': height, 'source_sha256': extras[0]['source_sha256'], 'palette_base': extras[0]['palette_base'],
                               'runtime_return_ip': extras[0]['runtime_return_ip'], 'original_file_sha256': receipt['inputs']['SFMAN06.DAT']},
              'existing_pose': pose, 'receipt_sha256': sha(root / 'receipt.json'), 'verifier_sha256': sha(Path(__file__)),
              'HD_comparison_sha256': sha(root / 'extra-source-comparison.png'),
              'files': {p.name: sha(p) for p in root.iterdir() if p.is_file() and p.name not in ('source-review.json',)},
              'limits': 'declared normal keyboard path and literal pointers/palettes; not exact prior Core replay, all extra sources, all animations or native HD; HD art still needs visual review'}
    (root / 'source-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('player', 'blits', 'frames', 'primary_extra_blits', 'extra_source')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
