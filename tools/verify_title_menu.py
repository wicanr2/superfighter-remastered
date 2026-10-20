"""獨立核對正常主選單取樣、TITLE.CPM 與無色盤 SFNAME.CPM 的完整合成。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image
from hd_source_probe import decode_candidate


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def no_palette_cpm(data):
    width, height, flag = struct.unpack_from('<HHB', data)
    assert (width, height, flag) == (285, 94, 0)
    marker, position, raw = data[5], 6, bytearray()
    while position < len(data):
        value = data[position]
        position += 1
        count = 1
        if value == marker:
            assert position + 2 <= len(data)
            count, value = data[position:position+2]
            position += 2
            assert count > 0
        assert len(raw) + count <= width * height
        raw.extend(bytes([value]) * count)
    assert len(raw) == width * height
    return bytes(raw)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    root = a.output
    r = Path('/project')
    receipt = json.loads((root/'receipt.json').read_text())
    for name, digest in receipt['inputs'].items():
        assert sha(r/name) == digest, name
    assert sha(root/'title_menu_receipt.go') == receipt['inputs']['tools/title_menu_receipt.go']
    sources = {x['name']: x['sha256'] for x in json.loads((r/'workplace/source-manifest.json').read_text())['files']}
    for name in ('SF.EXE', 'TITLE.CPM', 'SFNAME.CPM'):
        assert sha(Path('/orig')/name) == sources[name]
    width, height, palette, background = decode_candidate(Path('/orig/TITLE.CPM').read_bytes())
    assert (width, height) == (320, 200)
    palette = [[v*4+v//16 for v in palette[i:i+3]] for i in range(0,768,3)]
    overlay = no_palette_cpm(Path('/orig/SFNAME.CPM').read_bytes())
    candidates = {}
    for transparent in (True, False):
        combined = bytearray(background)
        for at, value in enumerate(overlay):
            if value or not transparent:
                combined[(at//285+96)*320+at%285+18] = value
        # 普通初始主選單的第一按鈕邊框；只主張下列實際取樣。
        for x in range(27,81):
            combined[174*320+x] = combined[188*320+x] = 51
        for y in range(175,188):
            combined[y*320+27] = combined[y*320+80] = 51
        candidates[transparent] = bytes(combined)
    samples = []
    rules = set()
    palette_phases = set()
    selected_border_colors = set()
    for case in receipt['cases']:
        name = case['name']
        assert case['mouse'] == [50+['single','versus','settings','exit'].index(name)*70,181]
        for sample in case['samples']:
            stem = sample['stem']
            directory = root/name
            raw = (directory/(stem+'.idx')).read_bytes()
            actual_palette = json.loads((directory/(stem+'.palette.json')).read_text())
            display = json.loads((directory/(stem+'.display.json')).read_text())
            state = json.loads((directory/(stem+'.state.json')).read_text())
            rgb = (directory/(stem+'.rgb')).read_bytes()
            assert display['width'] == 320 and display['height'] == 200 and display['start_byte'] == 0 and display['pitch_byte'] == 320
            assert len(raw) == 64000 and len(rgb) == 192000
            assert rgb == bytes(v for index in raw for v in actual_palette[index])
            assert sha(directory/(stem+'.rgb')) == sample['rgb_sha256']
            assert state['steps'] == sample['steps'] and not state['training']['modified']
            is_title = not stem.startswith('pressed')
            if is_title:
                assert all(actual_palette[i] == palette[i] for i in range(256) if i not in (*range(7,15),51))
                phases = [shift for shift in range(8) if all(actual_palette[7+i] == palette[7+(i+shift)%8] for i in range(8))]
                assert len(phases) == 1, 'title palette is not the source cyclic permutation'
                palette_phases.add(phases[0])
                selected_border_colors.add(tuple(actual_palette[51]))
                matched = [key for key, expected in candidates.items() if raw == expected]
                assert len(matched) == 1, (name, stem, 'title synthesis not unique or mismatched')
                rules.add(matched[0])
            samples.append({'case':name,'stem':stem,'steps':state['steps'],'title':is_title,'idx_sha256':sha(directory/(stem+'.idx')),'selection':state.get('selection')})
        if name in ('single','versus'):
            assert case['final_state'].get('selection') is not None and not case['terminal_error']
        elif name == 'exit':
            assert '回傳碼 0' in case['terminal_error']
        else:
            assert not case['final_state'].get('selection') and not case['terminal_error']
    assert len(rules)==1
    expected=candidates[next(iter(rules))]
    im=Image.frombytes('P',(320,200),expected);im.putpalette([v for color in palette for v in color])
    im.convert('RGB').save(root/'original-title-reference.png')
    result={'kind':'independent original title source reconstruction and four menu paths','status':'passed',
            'source_files':{name:sources[name]for name in('SF.EXE','TITLE.CPM','SFNAME.CPM')},
            'title_size':[320,200],'overlay_size':[285,94],'overlay_origin':[18,96],
            'zero_transparent':next(iter(rules)),'stable_title_samples':sum(x['title']for x in samples),
            'observed_logo_palette_rotations':sorted(palette_phases),
            'initial_border_rect':[27,174,81,189],'initial_border_index':51,
            'observed_border_RGB':sorted(selected_border_colors),
            'samples':samples,'receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'decoder_sha256':sha(r/'tools/hd_source_probe.py'),'limits':'normal four mouse actions and sampled palette phases only; border color origin, full animation, menu-state identifier, cursor, settings navigation, HD and native window acceptance not established'}
    (root/'source-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='samples'},ensure_ascii=False))


if __name__=='__main__':
    main()
