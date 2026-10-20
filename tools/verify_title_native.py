"""獨立重組隔離原生標題來源，核對原貌、切換、生命週期及缺稿回退。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

from PIL import Image
from hd_source_probe import decode_candidate
from verify_title_menu import no_palette_cpm
from verify_title_lifecycle import border
from verify_character_capture import read_frame


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--cursor-source', type=Path, help='正常原版游標限界收據，cursor-only 必填')
    parser.add_argument('--report-name', default='comparison.json', help='新驗證器重審舊收據時另存報告，保留舊報告身分')
    a = parser.parse_args()
    root, project, original = a.output, Path('/project'), Path('/orig')
    receipt = json.loads((root/'receipt.json').read_text())
    build = json.loads((a.build/'build.json').read_text())
    recipe = json.loads((a.build/'recipe.json').read_text())
    assert sha(root/'title_native_smoke.py') == receipt['script_sha256']
    assert sha(a.build/'superfighter-title-prototype-linux-amd64') == receipt['binary_sha256'] == build['binary_sha256']
    assert sha(a.build/'recipe.json') == build['recipe_sha256']
    for name, digest in recipe['recipe_inputs'].items():
        assert sha(project/name) == digest, name
    for name, digest in build['source_snapshot'].items():
        assert sha(a.build/'source'/name) == digest, name
    spec = importlib.util.spec_from_file_location('desktop_build', project/'tools/build_desktop.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.compiled_inputs(project) == recipe['original_compiled_inputs']
    assert sha(project/'assets/hd/characters/manifest.json') == receipt['character_manifest_sha256']
    sources = {x['name']: x['sha256'] for x in json.loads((project/'workplace/source-manifest.json').read_text())['files']}
    for name in ('SF.EXE', 'TITLE.CPM', 'SFNAME.CPM'):
        assert sha(original/name) == sources[name]
    executable = (original/'SF.EXE').read_bytes()
    image = executable[struct.unpack_from('<H', executable, 8)[0]*16:]
    data = image[0xabd0:0xac50]
    boxes = [list(struct.unpack_from('<4H', data, 64+i*8)) for i in range(4)]
    width, height, raw_palette, base = decode_candidate((original/'TITLE.CPM').read_bytes())
    assert (width, height) == (320, 200)
    palette = [[v*4+v//16 for v in raw_palette[i:i+3]] for i in range(0, 768, 3)]
    base = bytearray(base)
    for at, value in enumerate(no_palette_cpm((original/'SFNAME.CPM').read_bytes())):
        if value:
            base[(at//285+96)*320+at%285+18] = value
    events = {x['name']: x['state'] for x in receipt['events']}
    cursor_only = receipt.get('cursor_only', False)
    cursor_sources = []
    if cursor_only:
        assert a.cursor_source is not None
        cursor_receipt = json.loads((a.cursor_source/'receipt.json').read_text())
        for name, digest in cursor_receipt['inputs'].items():
            source = Path(name) if name.startswith('/') else project/name
            assert sha(source) == digest
        assert sha(a.cursor_source/'title_cursor_receipt.go') == sha(project/'tools/title_cursor_receipt.go')
        targets = {'body': (150, 120), 'right-edge': (304, 100), 'bottom-edge': (150, 184)}
        for sample in cursor_receipt['samples']:
            at = a.cursor_source/sample['stem']
            raw = Path(str(at)+'.idx').read_bytes()
            colours = json.loads(Path(str(at)+'.palette.json').read_text())
            assert sha(Path(str(at)+'.idx')) == sample['sha256']
            x, y = targets[sample['phase']]
            assert sample['mouse'] == [x, y] and sample['offset'] == y*320+x and sample['hidden'] == 0
            assert sample['registers']['CS'] == 0x01b9 and sample['registers']['DS'] == 0x0bfa and sample['registers']['IP'] == 0x0359
            expected = bytearray(base)
            border(expected, boxes[sample['selected']])
            for row in range(16):
                black, white = struct.unpack_from('<H', data, row*2)[0], struct.unpack_from('<H', data, 32+row*2)[0]
                for column in range(16):
                    position = (sample['offset']+row*320+column)&65535
                    if position >= 64000:
                        continue
                    if not black&(1<<(15-column)):
                        expected[position] = 0
                    if white&(1<<(15-column)):
                        expected[position] = 255
            assert raw == expected
            assert all(colours[i] == palette[i] for i in range(256) if i not in (*range(7, 15), 51))
            assert any(all(colours[7+i] == palette[7+(i+phase)%8] for i in range(8)) for phase in range(8))
            cursor_sources.append({'phase': sample['phase'], 'mouse': sample['mouse'], 'source_sha256': sample['sha256']})
        assert len(cursor_sources) == 12 and {p['phase'] for p in cursor_sources} == set(targets)
    assert len(events) == (13 if cursor_only else 4 if receipt['fallback'] else 9)
    title_proofs, outside_proofs = [], []
    screenshots = {}
    for name, event in events.items():
        path = root/(name+'.png')
        capture = json.loads(Path(str(path)+'.capture.json').read_text())
        assert capture['core'] == event['core']
        assert capture['title_hd_prototype'] == event['title_hd_prototype']
        assert not event['core']['training']['modified'] and event['core']['paused']
        picture = Image.open(path).convert('RGB')
        rect = capture['active_rect']
        height = capture['selected_height']
        top = 64+(600-height*3)//2
        assert rect == {'Min': {'X': 80, 'Y': top}, 'Max': {'X': 1040, 'Y': top+height*3}}
        screenshots[name] = picture.crop((80, 64, 1040, 664))
        raw = Path(str(path)+'.display.idx').read_bytes()
        rgb = Path(str(path)+'.selected.rgb').read_bytes()
        colours = json.loads(Path(str(path)+'.prototype-palette.json').read_text())
        assert len(raw) == 320*height and len(rgb) == 320*height*3
        expected_rgb = bytes(v for index in raw for v in colours[index])
        assert rgb == expected_rgb
        title = event['core'].get('title_prototype')
        if title:
            assert height == 200
            assert title == json.loads(Path(str(path)+'.title.json').read_text())
            assert raw == Path(str(path)+'.title.idx').read_bytes()
            assert hashlib.sha256(raw).hexdigest() == title['original_sha256']
            assert title['button_boxes'] == boxes
            expected = bytearray(base)
            border(expected, boxes[title['selected']])
            cursor_points = {}
            if not title['cursor_hidden']:
                for y in range(16):
                    black = struct.unpack_from('<H', data, y*2)[0]
                    white = struct.unpack_from('<H', data, 32+y*2)[0]
                    for x in range(16):
                        at = (title['cursor_offset']+y*320+x)&65535
                        if at >= 64000:
                            continue
                        if not black&(1<<(15-x)):
                            expected[at] = 0
                            cursor_points[at] = 0
                        if white&(1<<(15-x)):
                            expected[at] = 255
                            cursor_points[at] = 255
            assert raw == expected, (name, 'whole source reconstruction')
            assert all(colours[i] == palette[i] for i in range(256) if i not in (*range(7, 15), 51))
            assert all(colours[7+i] == palette[7+(i+title['phase'])%8] for i in range(8))
            known_flash = [[v*4+v//16 for v in data[96+i*4:99+i*4]] for i in range(8)]
            assert colours[51] == title['flash_rgb'] and colours[51] in known_flash
            if event['title_hd_prototype']:
                assert capture['title_prototype_phase'] == title['phase']
                assert event['hd_active'] and event['hd_enabled']
                for at, index in cursor_points.items():
                    for dy in range(3):
                        for dx in range(3):
                            assert screenshots[name].getpixel((at%320*3+dx, at//320*3+dy)) == tuple(colours[index])
            title_proofs.append({'name': name, 'selected': title['selected'], 'phase': title['phase'],
                                 'source_sha256': sha(Path(str(path)+'.title.idx')),
                                 'cursor_pixels': len(cursor_points), 'prototype_HD': event['title_hd_prototype']})
        else:
            assert not capture['title_hd_prototype']
            assert not Path(str(path)+'.title.json').exists()
            outside_proofs.append(name)
        if not event['hd_active']:
            assert height == 200
            expected_picture = Image.frombytes('RGB', (320, height), rgb).resize((960, height*3), Image.Resampling.NEAREST)
            assert screenshots[name].tobytes() == expected_picture.tobytes(), (name, 'original viewport')
    trios = [['title-hd', 'title-original', 'title-restored']]
    if cursor_only:
        trios += [['cursor-'+label+'-'+mode for mode in ('hd', 'original', 'restored')]
                  for label in ('body', 'right-edge', 'bottom-edge')]
    for trio in trios:
        for field in ('core', 'presentation', 'settings', 'assigned'):
            assert all(events[n][field] == events[trio[0]][field] for n in trio)
        for suffix in ('.title.idx', '.prototype-palette.json'):
            assert len({Path(str(root/(n+'.png'))+suffix).read_bytes() for n in trio}) == 1
        assert screenshots[trio[0]].tobytes() == screenshots[trio[2]].tobytes()
    trio = trios[0]
    changed = sum(x != y for x, y in zip(screenshots[trio[0]].getdata(), screenshots[trio[1]].getdata()))
    if receipt['fallback']:
        assert changed == 0 and not receipt['observed_HD_phases']
        assert not any(x['prototype_HD'] for x in title_proofs)
        assert events['fallback-next-selection']['core']['title_prototype']['selected'] == 1
    elif cursor_only:
        assert changed > 100000
        for label, x, y in [('body', 150, 120), ('right-edge', 304, 100), ('bottom-edge', 150, 184)]:
            for mode in ('hd', 'original', 'restored'):
                name = 'cursor-'+label+'-'+mode
                title = events[name]['core']['title_prototype']
                assert not title['cursor_hidden'] and title['cursor_offset'] == y*320+x
                assert next(p['cursor_pixels'] for p in title_proofs if p['name'] == name) > 20
        selection = events['mouse-versus-selection']
        assert selection['core'].get('selection') and selection['core']['title_prototype_stage'] == 'selection'
        assert not selection['title_hd_prototype'] and not selection['hd_active']
    else:
        assert changed > 100000 and receipt['observed_HD_phases'] == list(range(8))
        assert events['settings-original']['core']['title_prototype_stage'] == 'settings'
        assert events['returned-title-hd']['title_hd_prototype']
        assert events['versus-selection-original']['core']['title_prototype_stage'] == 'selection'
        battle = events['battle-hd-after-title']
        assert battle['core']['battle'] and battle['core']['fighters'] == [0, 4] and battle['hd_active']
        reference = (project/'workplace/hd-rooftop-study/reference.idx').read_bytes()
        read_frame(root, 'battle-hd-after-title.png', reference, original)
    result = {'kind': 'independent isolated native title reconstruction and transition review', 'status': 'passed',
              'captures': len(events), 'fallback': receipt['fallback'], 'cursor_only': cursor_only, 'title_sources': title_proofs,
              'cursor_source_samples': cursor_sources,
              'cursor_source_receipt_sha256': sha(a.cursor_source/'receipt.json') if cursor_only else None,
              'outside_title': outside_proofs, 'changed_viewport_pixels': changed,
              'paused_state_equal': True, 'restored_pixels_equal': True, 'formal_compiled_inputs_unchanged': len(recipe['original_compiled_inputs']),
              'observed_HD_phases': receipt['observed_HD_phases'], 'receipt_sha256': sha(root/'receipt.json'),
              'build_sha256': sha(a.build/'build.json'), 'verifier_sha256': sha(Path(__file__)),
              'dependencies': {p.name: sha(p) for p in sorted(Path(__file__).parent.glob('*.py')) if p.name.startswith(('verify_', 'hd_source_probe', 'hud_reference', 'shadow_reference', 'round_reference', 'display_reference', 'victory_reference'))},
              'files': {p.name: sha(p) for p in sorted(root.glob('*.png*')) if not p.name.startswith('capture.png')},
              'limits': 'Linux disposable module only; observed eight phases are frontend observations, not eight saved images; no production integration, HD material approval, full game or physical controller acceptance'}
    assert Path(a.report_name).name == a.report_name and a.report_name.endswith('.json')
    report = root/a.report_name
    encoded = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    assert not report.exists() or report.read_text() == encoded, 'report changed: choose a new --report-name'
    report.write_text(encoded)
    print(json.dumps({k: v for k, v in result.items() if k not in ('dependencies', 'files', 'title_sources')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
