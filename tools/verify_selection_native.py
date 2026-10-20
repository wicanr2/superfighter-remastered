"""獨立核對隔離原生選角肖像：原來源、兩側方向、框外像素與同狀態切換。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat

import build_desktop
from prepare_title_native_prototype import snapshot
from verify_character_capture import read_frame

ROOT = Path('/project')
BOXES = [(113, 109, 380, 376), (722, 109, 989, 376)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--build', type=Path, required=True)
    a = p.parse_args()
    root = a.output
    receipt = json.loads((root/'receipt.json').read_text())
    recipe = json.loads((a.build/'recipe.json').read_text())
    build = json.loads((a.build/'build.json').read_text())
    assert sha(root/'selection_native_smoke.py') == receipt['script_sha256']
    assert sha(a.build/'superfighter-selection-prototype-linux-amd64') == build['binary_sha256'] == receipt['binary_sha256']
    assert sha(a.build/'recipe.json') == build['recipe_sha256']
    assert snapshot(a.build/'source') == recipe['source_snapshot'] == build['source_snapshot']
    assert build_desktop.compiled_inputs(ROOT) == recipe['original_compiled_inputs']
    for name, digest in recipe['recipe_inputs'].items():
        assert sha(ROOT/name) == digest
    source_path = ROOT/'assets/hd/candidates/selection-portraits-source.json'
    assert sha(source_path) == receipt['portrait_source_sha256']
    source = json.loads(source_path.read_text())
    assert sha(ROOT/'assets/hd/characters/manifest.json') == receipt['character_manifest_sha256']
    archive = Path('/orig/BIGFIG.XBB')
    assert sha(archive) == source['source_sha256'] == '4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477'
    big = archive.read_bytes()
    assert len(big) == 11*8689
    references = {}
    for index, row in enumerate(source['records']):
        image = ROOT/'assets/hd/candidates'/row['file']
        assert row['index'] == index and sha(image) == row['sha256']
        portrait = Image.open(image).convert('RGB').resize((267, 267), Image.Resampling.BILINEAR)
        references[index, False] = portrait
        references[index, True] = ImageOps.mirror(portrait)
    events = {x['name']: x['state'] for x in receipt['events']}
    assert len(events) == (15 if receipt['fallback'] else 29)
    selections, pictures, sources, palette_bytes = {}, {}, {}, {}
    source_checks, ranking = [], []
    for name, state in events.items():
        path = root/(name+'.png')
        meta = json.loads(Path(str(path)+'.capture.json').read_text())
        assert meta['core'] == state['core'] and state['core']['paused']
        assert not state['core']['training']['modified']
        assert meta['selection_prototype'] == state.get('selection_prototype')
        assert meta['selection_hd_prototype'] == state['selection_hd_prototype']
        raw = Path(str(path)+'.display.idx').read_bytes()
        rgb = Path(str(path)+'.selected.rgb').read_bytes()
        colours = json.loads(Path(str(path)+'.prototype-palette.json').read_text())
        height = meta['selected_height']
        assert meta['selected_width'] == 320 and len(raw) == 320*height
        assert len(rgb) == 320*height*3 and rgb == bytes(c for value in raw for c in colours[value])
        sources[name], palette_bytes[name] = raw, Path(str(path)+'.prototype-palette.json').read_bytes()
        picture = Image.open(path).convert('RGB')
        assert picture.size == (1120, 820)
        pictures[name] = picture
        view = state.get('selection_prototype')
        if view is None:
            assert not state['selection_hd_prototype']
            continue
        assert height == 200 and meta['original_source'] == 'selection-filtered-original'
        assert meta['active_rect'] == {'Min': {'X': 80, 'Y': 64}, 'Max': {'X': 1040, 'Y': 664}}
        assert hashlib.sha256(raw).hexdigest() == view['original_sha256']
        assert view['boxes'] == [[11, 15, 100, 104], [214, 15, 303, 104]]
        assert view['player'] == state['core']['selection']['player']
        assert view['cursor'] == state['core']['selection']['cursor'] == view['portraits'][view['player']]
        if view['player'] == 1:
            assert view['portraits'][0] == 10
        active = state['hd_enabled'] and not receipt['fallback']
        assert state['selection_hd_prototype'] == state['hd_active'] == active
        original = Image.frombytes('RGB', (320, 200), rgb).resize((960, 600), Image.Resampling.NEAREST)
        actual = picture.crop((80, 64, 1040, 664))
        outside = actual.copy()
        for side, character in enumerate(view['portraits']):
            if character < 0:
                continue
            record = big[character*8689:(character+1)*8689]
            bank = 160+side*32
            assert colours[bank:bank+32] == [[v*4+v//16 for v in record[i:i+3]] for i in range(0, 96, 3)]
            for y in range(89):
                for x in range(89):
                    dx = 11+x if side == 0 else 302-x
                    assert raw[(15+y)*320+dx] == bank+record[768+y*89+x], (name, side, x, y)
            source_checks.append({'name': name, 'side': side, 'character': character, 'original_pixels': 89*89})
            box = BOXES[side]
            local = tuple(value-offset for value, offset in zip(box, (80, 64, 80, 64)))
            candidate = picture.crop(box)
            if active:
                # GPU minification uses mipmaps. Rank identity/orientation against all painted
                # candidates; do not claim Pillow sampling equals the GPU pixel for pixel.
                distances = {key: sum(ImageStat.Stat(ImageChops.difference(candidate, reference)).mean)/3
                             for key, reference in references.items()}
                best = min(distances, key=distances.get)
                assert best == (character, side == 1), (name, side, character, best, distances)
                assert candidate.tobytes() != original.crop(local).tobytes()
                ranking.append({'name': name, 'side': side, 'character': character, 'mirrored': side == 1,
                                'nearest_candidate_mean_RGB_difference': distances[best],
                                'next_candidate_mean_RGB_difference': sorted(distances.values())[1]})
                outside.paste(original.crop(local), local[:2])
        assert outside.tobytes() == original.tobytes(), (name, 'pixels outside HD portrait boxes changed')
        selections[name] = view
    expected = [0, 8, 9, 10] if receipt['fallback'] else list(range(11))
    for side in (0, 1):
        assert [selections[f'p{side}-{i:02d}-hd']['portraits'][side] for i in expected] == expected
    for label in ('p0-08', 'p1-10'):
        names = [label+'-'+mode for mode in ('hd', 'original', 'restored')]
        for field in ('core', 'presentation', 'settings', 'assigned'):
            assert all(events[n][field] == events[names[0]][field] for n in names)
        assert len({sources[n] for n in names}) == len({palette_bytes[n] for n in names}) == 1
        assert pictures[names[0]].crop((80, 64, 1040, 664)).tobytes() == pictures[names[2]].crop((80, 64, 1040, 664)).tobytes()
        original = Image.frombytes('RGB', (320, 200), Path(str(root/(names[1]+'.png'))+'.selected.rgb').read_bytes()).resize((960, 600), Image.Resampling.NEAREST)
        assert pictures[names[1]].crop((80, 64, 1040, 664)).tobytes() == original.tobytes()
    assert len(source_checks) == (20 if receipt['fallback'] else 41)
    assert len(ranking) == (0 if receipt['fallback'] else 38)
    title = events['title-original']
    assert not title['hd_active'] and not title.get('selection_prototype')
    assert hashlib.sha256(sources['title-original']).hexdigest() == 'b7dc57aad9dc678a83f8742225e1e94b2f1bad82ce815cb4fd8f2daf42032bdb'
    title_rgb = Path(str(root/'title-original.png')+'.selected.rgb').read_bytes()
    assert pictures['title-original'].crop((80, 64, 1040, 664)).tobytes() == Image.frombytes('RGB', (320, 200), title_rgb).resize((960, 600), Image.Resampling.NEAREST).tobytes()
    battle = events['battle-after-selection']
    assert battle['core']['battle'] and battle['core']['mode'] == 1 and battle['core']['fighters'] == [10, 4]
    assert 'selection' not in battle['core'] and not battle.get('selection_prototype') and not battle['selection_hd_prototype'] and battle['hd_active']
    read_frame(root, 'battle-after-selection.png', (ROOT/'workplace/hd-rooftop-study/reference.idx').read_bytes(), Path('/orig'))
    result = {'kind': 'independent isolated native two-sided selection portrait review', 'status': 'passed',
              'captures': len(events), 'fallback': receipt['fallback'], 'original_portrait_reconstructions': len(source_checks),
              'GPU_identity_and_orientation_matches': len(ranking), 'source_checks': source_checks, 'GPU_ranking': ranking,
              'outside_portrait_boxes_identical': True, 'paused_state_equal': True, 'restored_HD_identical': True,
              'title_original_and_selection_cleared_on_battle': True, 'formal_compiled_inputs_unchanged': len(recipe['original_compiled_inputs']),
              'receipt_sha256': sha(root/'receipt.json'), 'build_sha256': sha(a.build/'build.json'), 'verifier_sha256': sha(Path(__file__)),
              'dependencies': {name: sha(Path(__file__).with_name(name)) for name in
                               ('build_desktop.py', 'prepare_title_native_prototype.py', 'verify_character_capture.py', 'hud_reference.py', 'shadow_reference.py', 'round_reference.py', 'display_reference.py', 'victory_reference.py')},
              'files': {p.name: sha(p) for p in sorted(root.glob('*.png*')) if not p.name.startswith('capture.png')},
              'limits': 'Linux copied module, versus only; GPU candidate/orientation ranking is not exact sampling parity; backdrop and small portraits original; no formal layout/format, complete HD, single-player or hardware controller acceptance'}
    report = root/'comparison.json'
    assert not report.exists()
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('files', 'dependencies', 'source_checks', 'GPU_ranking')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
