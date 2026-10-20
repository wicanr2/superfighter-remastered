"""核對目前核心正常結果生命週期及完整來源識別，保留轉場與篡改拒絕。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from recognize_result_source import ResultSources
from verify_title_menu import no_palette_cpm
from verify_title_lifecycle import border
from hd_source_probe import decode_candidate

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    out = a.output
    target = out/'source-review.json'
    assert not target.exists()
    receipt = json.loads((out/'receipt.json').read_text())
    assert sha(out/'result_core_receipt.go') == receipt['script_sha256'] == sha(ROOT/'tools/result_core_receipt.go')
    assert receipt['dosgolem_manifest_sha256'] == sha(ROOT/'workplace/dosgolem-patched-manifest.json')
    for name, digest in receipt['inputs'].items():
        assert sha(ROOT/'workplace/orig'/name) == digest
    source = ResultSources(ROOT/'workplace/orig')
    states = {}
    events = {e['name']: e for e in receipt['events']}
    for name, event in events.items():
        raw = (out/(name+'.rgb')).read_bytes()
        indices = (out/(name+'.idx')).read_bytes()
        palette = json.loads((out/(name+'.palette.json')).read_text())
        display = json.loads((out/(name+'.display.json')).read_text())
        assert event['width'] == 320 and event['height'] == 200
        assert display['width'] == 320 and display['pitch_byte'] == 320
        if name in ('normal-battle', 'knockout-0', 'next-round', 'knockout-1', 'after-match-inputs'):
            # 015 已確認的 CRTC 對戰視區，與 legacy ScreenRGB 的 200 列不同。
            assert display['height'] == 192 and display['start_byte'] in (2560, 3840) and len(indices) == 61440
        else:
            assert display['height'] == 200 and display['start_byte'] == 0
            assert len(indices) == 64000 and raw == bytes(c for v in indices for c in palette[v])
        assert hashlib.sha256(raw).hexdigest() == event['live_rgb_sha256']
        assert not event['core']['training']['modified'] and not event['core']['training']['active']
        states[name] = source.identify(raw)
        if name.startswith('result-stable-') or name == 'post-match-wait':
            state = states[name]
            assert state is not None and (state.left_character, state.right_character, state.outcome_record) == (0, 4, 0)
            assert state.flag_records == (0, 1) and state.name_positions == (42, 232)
            assert not event['core']['battle'] and event['cached_frame_pixels'] == 0
        else:
            assert states[name] is None, name
    assert len(events) == 13
    assert events['knockout-0']['core']['health'][1] == events['knockout-1']['core']['health'][1] == 0
    assert events['next-round']['core']['health'] == [124, 124] and events['next-round']['core']['battle']
    # 原標題完整來源核對，不能只以「離開戰鬥」當返回成功。
    _, _, title_palette, title = decode_candidate((ROOT/'workplace/orig/TITLE.CPM').read_bytes())
    overlay = no_palette_cpm((ROOT/'workplace/orig/SFNAME.CPM').read_bytes())
    expected = bytearray(title)
    for at, value in enumerate(overlay):
        if value:
            expected[(at//285+96)*320+at%285+18] = value
    # 沿 046 已驗的原框線繪製順序；命中範圍不能當作繪製矩形。
    actual = (out/'return-to-title.idx').read_bytes()
    executable = (ROOT/'workplace/orig/SF.EXE').read_bytes()
    image = executable[struct.unpack_from('<H', executable, 8)[0]*16:]
    rectangles = [struct.unpack_from('<4H', image, 0xac10+i*8) for i in range(4)]
    matching = []
    for selected, rectangle in enumerate(rectangles):
        candidate = bytearray(expected)
        border(candidate, rectangle)
        if bytes(candidate) == actual:
            matching.append(selected)
    assert len(matching) == 1, 'returned title does not match a complete source reconstruction'
    actual_palette = json.loads((out/'return-to-title.palette.json').read_text())
    title_colours = [[v*4+v//16 for v in title_palette[i:i+3]] for i in range(0, 768, 3)]
    assert all(actual_palette[i] == title_colours[i] for i in range(256) if i not in (*range(7, 15), 51))
    phases = [shift for shift in range(8) if all(actual_palette[7+i] == title_colours[7+(i+shift)%8] for i in range(8))]
    assert len(phases) == 1
    accepted = (out/'result-stable-0.rgb').read_bytes()
    reject = []
    for label, x, y in (('background', 0, 0), ('left-portrait', 20, 40), ('right-portrait', 220, 40),
                        ('outcome', 140, 30), ('left-flag', 40, 165), ('right-flag', 240, 165),
                        ('left-name', 45, 137), ('right-name', 240, 137)):
        mutated = bytearray(accepted)
        mutated[(y*320+x)*3] ^= 1
        assert source.identify(bytes(mutated)) is None, label
        reject.append(label)
    assert source.identify(accepted[:-1]) is None and source.identify(accepted+b'\0') is None
    proof = {'status': 'passed', 'kind': 'current normal public-Core result lifecycle; not native GUI or HD acceptance',
        'result_sources': {name: state.record() if state else None for name, state in states.items()},
        'captures': 13, 'complete_result_reconstructions': 7, 'rejected_modified_regions': reject,
        'truncated_and_extended_rejected': True, 'return_title_full_index_reconstruction': True,
        'returned_title_selected': matching[0], 'returned_title_palette_phase': phases[0],
        'receipt_sha256': sha(out/'receipt.json'), 'probe_sha256': sha(ROOT/'tools/result_core_receipt.go'),
        'verifier_sha256': sha(Path(__file__)), 'source_identifier_sha256': sha(ROOT/'tools/recognize_result_source.py'),
        'dependencies': {n: sha(ROOT/'tools'/n) for n in ('hd_source_probe.py', 'export_result_source.py', 'verify_title_menu.py', 'verify_title_lifecycle.py')},
        'original_inputs': source.inputs,
        'limits': 'one normal Jaan/Frank result, unmodified input only; no fixed RNG parity, all-character result classification, flags table, native GUI, HD pixels or production integration'}
    (out/'source-review.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('result_sources','dependencies','original_inputs')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
