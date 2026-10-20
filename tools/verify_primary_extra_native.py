"""獨立核對鬼丸主色盤額外圖像的原生呈現及舊程式整格原貌。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from display_reference import geometry
from verify_character_capture import read_frame, original_image, viewport, source_y
from verify_character_geometry import verify_sprite


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    p.add_argument('--original-root', type=Path, default=Path('/orig'))
    a = p.parse_args()
    root = a.output
    receipt = json.loads((root / 'receipt.json').read_text())
    assert receipt['script_sha256'] == sha(root / 'primary_extra_smoke.py')
    old = receipt['expected_original']
    reference = Path('/project/workplace/hd-rooftop-study/reference.idx').read_bytes()
    events = {x['name']: x['state'] for x in receipt['events']}
    assert len(events) == 5 and all(s['core']['fighters'] == [5, 4] and not s['core']['training']['modified'] for s in events.values())
    assert events['normal-hd']['hd_active'] and events['after-effects']['hd_active']
    for name in ('normal-hd', 'after-effects'):
        read_frame(root, name + '.png', reference, a.original_root)
    names = ['primary-weapon-' + mode for mode in ('hd', 'original', 'restored')]
    assert [events[n]['hd_active'] for n in names] == [not old, False, not old]
    for field in ('core', 'presentation', 'settings', 'assigned'):
        assert all(events[n][field] == events[names[0]][field] for n in names)
    assert all(events[n]['core']['paused'] for n in names)
    frames = []
    proof = None
    for name in names:
        if not old:
            f = read_frame(root, name + '.png', reference, a.original_root)
        else:
            base = root / (name + '.png')
            raw = Path(str(base) + '.idx').read_bytes()
            palette = json.loads(Path(str(base) + '.palette.json').read_text())
            # 舊版只在完整分層時輸出 frame.json；不完整狀態保存在同次 observe 收據。
            frame = dict(events[name]['presentation'])
            capture = json.loads(Path(str(base) + '.capture.json').read_text())
            assert capture['presentation_serial'] == frame['serial'] and capture['presentation_steps'] == frame['steps']
            assert capture['core'] == events[name]['core'] and capture['scanout'] == frame['scanout']
            assert not frame['layers_complete'] and frame['layer_error'] == '特效色盤未對應'
            scan = frame['scanout']
            start, pitch, height = geometry(scan['crtc'])
            assert (start, pitch, height) == (scan['start_byte'], scan['pitch_byte'], scan['height'])
            vram = raw + Path(str(base) + '.vram-tail').read_bytes()
            visible = Path(str(base) + '.display.idx').read_bytes()
            assert visible == b''.join(vram[start+y*pitch:start+y*pitch+320] for y in range(height))
            frame['_visible'] = visible
            f = (raw, palette, frame, None, None, Image.open(base).convert('RGB'))
        frames.append(f)
    hd, original, restored = frames
    assert hd[:3] == original[:3] == restored[:3]
    assert viewport(original[-1]).tobytes() == original_image(original[0], original[1], original[2]).tobytes()
    assert viewport(hd[-1]).tobytes() == viewport(restored[-1]).tobytes()
    changed = orange = 0
    if old:
        assert receipt['groups'][0]['effect_slots'] == []
        assert viewport(hd[-1]).tobytes() == viewport(original[-1]).tobytes()
    else:
        assert receipt['groups'][0]['effect_slots'] == [35]
        target = [(i, m['sprite'], idx, mask) for i, (m, idx, mask) in enumerate(hd[3]) if m.get('sprite', {}).get('effect')]
        assert len(target) == 1
        ordinal, sprite, indices, mask = target[0]
        assert sprite['character'] == 5 and sprite['slot'] == 35 and sprite['palette_base'] == 0xc0
        proof = verify_sprite(a.original_root, sprite, indices, mask)
        data = (a.original_root / 'SFMAN06.DAT').read_bytes()
        wanted = [[v*4+v//16 for v in data[0xac8+i*3:0xac8+(i+1)*3]] for i in range(16)]
        assert hd[1][0xc0:0xd0] == wanted
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
                    orange += red > green+20 and green > blue+10
        assert changed > 20 and orange > 20, (changed, orange)
    assert events['after-effects']['core']['steps'] > events[names[0]]['core']['steps']
    assert not any(l.get('sprite', {}).get('effect') for l in events['after-effects']['presentation']['layers'])
    result = {'kind': 'independent normal native primary-palette extra and old binary fallback',
              'captures': 5, 'expected_original': old, 'same_original_state': True, 'restored_HD_identical': True,
              'continued_after_release': True, 'original_source': proof, 'visible_extra_pixels_changed': changed,
              'orange_pixels': orange, 'binary_sha256': receipt['binary_sha256'], 'receipt_sha256': sha(root / 'receipt.json'),
              'verifier_sha256': sha(Path(__file__)),
              'dependencies': {name: sha(Path(__file__).with_name(name)) for name in ('verify_character_capture.py', 'verify_character_geometry.py', 'hud_reference.py', 'shadow_reference.py', 'round_reference.py', 'display_reference.py', 'victory_reference.py')},
              'files': {q.name: sha(q) for q in root.iterdir() if q.is_file() and q.name != 'comparison.json' and not q.name.startswith('capture.png')},
              'limits': 'first-player Linux normal path only; original P2 and same-character sources tested separately; not all extra sprites, all animations, native Windows/macOS, audio or physical controllers'}
    (root / 'comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('files', 'dependencies')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
