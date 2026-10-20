"""獨立核對正常捲動來源，輸出保留原版前景的私有 HD 背景比較稿。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from display_reference import geometry
from verify_character_geometry import verify_sprite
from verify_stage_sources import decode

ROOT = Path('/project')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def indexed(indices, palette, size):
    assert len(indices) == size[0] * size[1]
    im = Image.frombytes('P', size, indices)
    im.putpalette(bytes(value for colour in palette for value in colour))
    return im.convert('RGB')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original-root', type=Path, default=Path('/orig'))
    parser.add_argument('--revisions', action='store_true', help='只在私有比較稿試用兩份未定版修稿')
    args = parser.parse_args()
    assert args.evidence.is_dir() and not args.output.exists()
    assert args.output.parent.is_dir() and args.output.parent.stat().st_uid == 1000
    receipt = json.loads((args.evidence / 'receipt.json').read_text())
    assert receipt['script_sha256'] == sha(args.evidence / 'background_scroll_receipt.go')
    source_manifest = ROOT / 'workplace/source-manifest.json'
    assert receipt['source_manifest_sha256'] == sha(source_manifest)
    originals = {x['name']: x['sha256'] for x in json.loads(source_manifest.read_text())['files']}
    catalog = json.loads((ROOT / 'assets/hd/catalog.json').read_text())
    catalog = {x['file']: x for x in catalog['files']}
    art_records = json.loads((ROOT / 'assets/hd/candidates/backgrounds-source.json').read_text())['records']
    art = {row['source_file']: ROOT / 'assets/hd/candidates' / row['file'] for row in art_records}
    art['I5.XGB'] = ROOT / 'assets/hd/candidates/dojo.png'
    art['I2.XGB'] = ROOT / 'assets/hd/backgrounds/rooftop.png'
    revision_source = None
    if args.revisions:
        revision_source = ROOT / 'assets/hd/candidates/background-revisions-source.json'
        revisions = json.loads(revision_source.read_text())['records']
        assert len(revisions) == 2
        for row in revisions:
            assert row['source_file'] in ('I10.XGB', 'I8.XGB')
            assert row['status'] == 'candidate revision; not selected or integrated'
            candidate = ROOT / 'assets/hd/candidates' / row['file']
            assert sha(candidate) == row['sha256']
            art[row['source_file']] = candidate
    assert len(art) == len(receipt['stages']) == 11
    assert len({x['scene'] for x in receipt['stages']}) == 11
    args.output.mkdir()
    results = []
    files = {}
    source_files = {}
    total_sprites = 0
    overview = Image.new('RGB', (1440, 4 * 236), '#131b27')
    overview_draw = ImageDraw.Draw(overview)
    for row in receipt['stages']:
        player = row['player1']
        folder = args.evidence / f'versus-00-{player:02d}'
        assert row['player0'] == 0 and row['scene'] == player and not row['training_modified']
        assert json.loads((folder / 'receipt.json').read_text()) == row
        original = args.original_root / row['source']
        assert sha(original) == originals[row['source']] == row['source_sha256']
        reference, background_palette = decode(original.read_bytes())
        assert (folder / 'reference.idx').read_bytes() == reference
        assert (folder / 'palette.rgb').read_bytes() == background_palette
        candidate = art[row['source']]
        registered = catalog[str(candidate.relative_to(ROOT / 'assets/hd'))]
        assert sha(candidate) == registered['sha256']
        with Image.open(candidate) as im:
            assert list(im.size) == registered['size']
            assert im.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            # 顯示用正規化，原 PNG 不改寫。不是 GPU 線性採樣逐點 parity。
            panorama = im.convert('RGB').resize((1440, 612), Image.Resampling.BILINEAR)
        ox, oy = (row['scene'] % 3) * 480, (row['scene'] // 3) * 236
        overview.paste(panorama.resize((480, 204), Image.Resampling.LANCZOS), (ox, oy + 32))
        overview_draw.text((ox + 10, oy + 10), f'DRAFT scene {row["scene"]}: {row["source"]}; not integrated', fill='white')
        stage_dir = args.output / f'scene-{row["scene"]:02d}'
        stage_dir.mkdir()
        samples = []
        last_steps = 0
        for sample in row['samples']:
            name = sample['name']
            frame = json.loads((folder / (name + '.frame.json')).read_text())
            palette = json.loads((folder / (name + '.palette.json')).read_text())
            assert len(palette) == 256 and all(len(c) == 3 and all(0 <= v <= 255 for v in c) for c in palette)
            assert bytes(v for c in palette[:128] for v in c) == background_palette
            assert frame['scene'] == row['scene'] and frame['layers_complete']
            assert not frame['training']['modified'] and not frame.get('round_message') and not frame.get('victory')
            assert frame['steps'] == sample['steps'] >= last_steps
            last_steps = frame['steps']
            assert frame['background_sha256'] == digest(reference) == sample['background_sha256']
            camera = frame['camera_x']
            assert camera == sample['camera_x'] and 0 <= camera <= 160
            raw = (folder / (name + '.idx')).read_bytes()
            tail = (folder / (name + '.vram-tail')).read_bytes()
            display = (folder / (name + '.display.idx')).read_bytes()
            assert len(raw) == 64000 and len(tail) == 1536
            scan = frame['scanout']
            start, pitch, height = geometry(scan['crtc'])
            assert (start, pitch, height) == (scan['start_byte'], scan['pitch_byte'], scan['height'])
            assert scan['width'] == pitch == 320 and start % 320 == 0
            source_top = start // 320
            assert source_top + height <= 204
            ram = raw + tail
            assert display == ram[start:start + height * 320]
            layers = []
            composed = bytearray(64000)
            foreground = Image.new('RGBA', (320, 200))
            sprites = []
            for ordinal, meta in enumerate(frame['layers']):
                indices = (folder / f'{name}.layer-{ordinal:02d}.idx').read_bytes()
                mask = (folder / f'{name}.layer-{ordinal:02d}.mask').read_bytes()
                assert len(indices) == len(mask) == 64000 and set(mask) <= {0, 1}
                if ordinal == 0:
                    assert meta.get('background') and mask == bytes([1]) * 64000
                    expected = b''.join(reference[y * 480 + camera:y * 480 + camera + 320] for y in range(200))
                    assert indices == expected == (folder / (name + '.background.idx')).read_bytes()
                else:
                    layer = indexed(indices, palette, (320, 200)).convert('RGBA')
                    layer.putalpha(Image.frombytes('L', (320, 200), mask).point([0, 255] + [255] * 254))
                    foreground.alpha_composite(layer)
                if meta.get('sprite'):
                    assert not meta['sprite'].get('effect')
                    sprites.append(verify_sprite(args.original_root, meta['sprite'], indices, mask))
                for i, coverage in enumerate(mask):
                    if coverage:
                        composed[i] = indices[i]
                layers.append((indices, mask))
            assert bytes(composed) == raw and len(sprites) == 2
            total_sprites += len(sprites)
            # 顯示窗使用的尾列仍逐點吻合原背景，不憑低色號猜前景。
            for y in range(200, source_top + height):
                assert ram[y * 320:(y + 1) * 320] == reference[y * 480 + camera:y * 480 + camera + 320]
            original_image = indexed(display, palette, (320, height)).resize((960, height * 3), Image.Resampling.NEAREST)
            full_candidate = panorama.crop((camera * 3, 0, camera * 3 + 960, 612)).convert('RGBA')
            full_candidate.alpha_composite(foreground.resize((960, 600), Image.Resampling.NEAREST), (0, 0))
            cropped = full_candidate.crop((0, source_top * 3, 960, (source_top + height) * 3)).convert('RGB')
            comparison = Image.new('RGB', (1920, 44 + height * 3), '#131b27')
            comparison.paste(original_image, (0, 44))
            comparison.paste(cropped, (960, 44))
            draw = ImageDraw.Draw(comparison)
            draw.text((12, 10), f'ORIGINAL  scene={row["scene"]}  {row["source"]}  camera={camera}  step={frame["steps"]}', fill='white')
            draw.text((972, 10), 'DRAFT HD BACKGROUND + ORIGINAL FOREGROUND; software study, not native integration', fill='white')
            path = stage_dir / (name + '.png')
            comparison.save(path)
            files[str(path.relative_to(args.output))] = sha(path)
            samples.append({'name': name, 'camera_x': camera, 'steps': frame['steps'], 'source_top': source_top,
                            'visible_height': height, 'frame_sha256': sha(folder / (name + '.frame.json')),
                            'display_sha256': digest(display), 'CPU_composition_matches': True,
                            'original_sprite_sources': sprites, 'output': str(path.relative_to(args.output))})
        assert len(samples) == 8 and [x['name'] for x in samples][0] == 'idle'
        assert [x['name'] for x in row['phases']] == ['left', 'right']
        assert all(x['health'] == [124, 124] for x in row['phases'])
        observed = sorted({camera for phase in row['phases'] for camera in phase['cameras']})
        assert all(0 <= camera <= 160 for camera in observed)
        results.append({'scene': row['scene'], 'source': row['source'], 'source_sha256': sha(original),
                        'candidate': str(candidate.relative_to(ROOT)), 'candidate_sha256': sha(candidate),
                        'observed_camera_values': observed, 'sampled_camera_values': sorted({x['camera_x'] for x in samples}),
                        'samples': samples})
        for p in folder.iterdir():
            if p.is_file():
                source_files[str(p.relative_to(args.evidence))] = sha(p)
    overview.save(args.output / 'overview-hd.png')
    files['overview-hd.png'] = sha(args.output / 'overview-hd.png')
    report = {'kind': 'independent original scroll/CPU verification and disposable HD-background comparison',
              'source_receipt_sha256': sha(args.evidence / 'receipt.json'), 'verifier_sha256': sha(Path(__file__)),
              'revision_source_sha256': sha(revision_source) if revision_source else None,
              'dependencies': {name: sha(Path(__file__).with_name(name)) for name in
                               ('display_reference.py', 'verify_character_geometry.py', 'verify_stage_sources.py')},
              'stages': results, 'captures': sum(len(x['samples']) for x in results), 'sprites': total_sprites,
              'files': files, 'source_files': source_files,
              'limits': 'normal versus simultaneous walking samples; source camera observations are exact, HD bilinear panorama is a visual approximation; original foreground retained; not production loading, GPU, all-camera image captures, single-player order or full HD; released capture means input source cleared, not a neutral-poll assertion'}
    (args.output / 'comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'scenes': len(results), 'captures': report['captures'], 'sprites': total_sprites,
                      'camera_ranges': [(x['scene'], min(x['observed_camera_values']), max(x['observed_camera_values'])) for x in results]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
