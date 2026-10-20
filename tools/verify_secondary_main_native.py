"""獨立重組兩側主角色第二色盤原生擷取，核對切換與舊程式回退。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame, original_image, viewport, source_y
from verify_character_geometry import verify_sprite


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--original-root', type=Path, default=Path('/orig'))
    a = p.parse_args()
    root = a.output
    receipt = json.loads((root / 'receipt.json').read_text())
    assert receipt['script_sha256'] == sha(root / 'secondary_main_smoke.py')
    old = receipt['expected_original']
    events = {x['name']: x['state'] for x in receipt['events']}
    assert len(events) == 8
    assert all(s['core']['fighters'] == [3, 4] and not s['core']['training']['modified'] for s in events.values())
    reference = Path('/project/workplace/hd-rooftop-study/reference.idx').read_bytes()
    assert events['normal-hd']['hd_active'] and events['after-effects']['hd_active']
    for name in ('normal-hd', 'after-effects'):
        read_frame(root, name + '.png', reference, a.original_root)
    proofs = []
    for label, player, character, slot in [('phoenix-cyan', 0, 3, 48), ('frank-cyan', 1, 4, 54)]:
        names = [label + '-' + mode for mode in ('hd', 'original', 'restored')]
        assert [events[n]['hd_active'] for n in names] == [not old, False, not old]
        for field in ('core', 'presentation', 'settings', 'assigned'):
            assert all(events[n][field] == events[names[0]][field] for n in names)
        assert all(events[n]['core']['paused'] for n in names)
        hd, original, restored = [read_frame(root, n + '.png', reference, a.original_root) for n in names]
        assert hd[:3] == original[:3] == restored[:3]
        assert viewport(original[-1]).tobytes() == original_image(original[0], original[1], original[2]).tobytes()
        assert viewport(hd[-1]).tobytes() == viewport(restored[-1]).tobytes()
        targets = [(i, m['sprite'], idx, mask) for i, (m, idx, mask) in enumerate(hd[3])
                   if m.get('sprite', {}).get('player') == player and not m['sprite'].get('effect')]
        assert len(targets) == 1
        ordinal, sprite, indices, mask = targets[0]
        assert (sprite['character'], sprite['slot'], sprite['palette_base']) == (character, slot, 0xd0 + player * 32)
        proof = verify_sprite(a.original_root, sprite, indices, mask)
        data = (a.original_root / f'SFMAN{character+1:02d}.DAT').read_bytes()
        wanted = [[v*4+v//16 for v in data[0xaf8+i*3:0xaf8+(i+1)*3]] for i in range(16)]
        assert hd[1][sprite['palette_base']:sprite['palette_base']+16] == wanted
        changed = cyan = 0
        for at, owner in enumerate(hd[4]):
            if owner != ordinal:
                continue
            y = source_y(at // 320, hd[2])
            if y is None:
                continue
            for dy in range(3):
                for dx in range(3):
                    point = (80+at%320*3+dx, y+dy)
                    rgb = hd[-1].getpixel(point)
                    changed += rgb != original[-1].getpixel(point)
                    red, green, blue = rgb
                    cyan += blue > red+15 and green > red+10
        if old:
            assert viewport(hd[-1]).tobytes() == viewport(original[-1]).tobytes()
            assert changed == 0
        else:
            assert changed > 20 and cyan > 20, (label, changed, cyan)
        proofs.append({'label': label, 'original_source': proof, 'visible_main_pixels_changed': changed, 'cyan_pixels': cyan})
    assert events['after-effects']['core']['steps'] > events['frank-cyan-hd']['core']['steps']
    assert events['after-effects']['core']['key_values'] == [0, 0]
    result = {'kind': 'independent native secondary-main palette and old program fallback',
              'captures': 8, 'expected_original': old, 'same_original_state': True,
              'restored_HD_identical': True, 'continued_after_release': True, 'proofs': proofs,
              'binary_sha256': receipt['binary_sha256'], 'receipt_sha256': sha(root / 'receipt.json'),
              'verifier_sha256': sha(Path(__file__)),
              'dependencies': {name: sha(Path(__file__).with_name(name)) for name in ('verify_character_capture.py', 'verify_character_geometry.py', 'hud_reference.py', 'shadow_reference.py', 'round_reference.py', 'display_reference.py', 'victory_reference.py')},
              'files': {q.name: sha(q) for q in root.iterdir() if q.is_file() and q.name != 'comparison.json' and not q.name.startswith('capture.png')},
              'limits': 'Linux 3/4 normal versus, sources 48/54 only; RGB approximation, not full animation or other platforms'}
    (root / 'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('files', 'dependencies', 'proofs')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
