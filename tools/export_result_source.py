"""匯出結果報紙來源並完整重組既有正常結果擷取；原圖只寫入 workplace。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image, ImageOps

from hd_source_probe import decode_candidate

ROOT = Path('/project')
INPUTS = {
    'SHIN.FIG': '28659c54fe5ce751c630424c3ef234717debd8aa9fe451eaab1d1e2639670845',
    'BIGFIG.XBB': '4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477',
    'LOSEFIG.XBB': 'b1b1781bc799dca14f3ce0f3b74e451e654bafe88341249a977a34ab909b159c',
    'WC.XBB': '774f14af079c7148fb05a5db21fdfb17abc0a658c9fcd9a82958166ebaf8b0e0',
    'FLAG.XBB': '87a5bf27cb516d1e5612252dd0a3dff5f3980c837ea4b96b644ece0257acc6d1',
    'FLAG.FIG': '64ad397ba0a29808b5e8dc147c456be6c1f26df6d94258a3d2340b0f2a2e51ce',
    'NAME.XBB': '60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgb_palette(raw):
    assert len(raw) % 3 == 0 and max(raw) <= 63
    return [tuple(v*4+v//16 for v in raw[i:i+3]) for i in range(0, len(raw), 3)]


def byte_sprites(raw):
    pos, records = 0, []
    while pos < len(raw):
        assert pos+2 <= len(raw)
        w, h = raw[pos:pos+2]
        end = pos+2+w*h
        assert w and h and end <= len(raw)
        records.append((pos, w, h, raw[pos+2:end]))
        pos = end
    assert pos == len(raw)
    return records


def raster(w, h, pixels, colours):
    assert len(pixels) == w*h and max(pixels) < len(colours)
    return Image.frombytes('RGB', (w, h), bytes(c for v in pixels for c in colours[v]))


def portrait(raw, index):
    assert len(raw) == 11*8689 and 0 <= index < 11
    data = raw[index*8689:(index+1)*8689]
    return raster(89, 89, data[768:768+89*89], rgb_palette(data[:96]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    files = {name: ROOT/'workplace/orig'/name for name in INPUTS}
    for name, digest in INPUTS.items():
        assert digest is None or sha(files[name]) == digest, name
    source_manifest = json.loads((ROOT/'workplace/source-manifest.json').read_text())
    for row in source_manifest['files']:
        if row['name'] == 'LOSEFIG.XBB':
            assert sha(files['LOSEFIG.XBB']) == row['sha256']
            break
    else:
        raise ValueError('missing original LOSEFIG manifest')
    a.output.mkdir()
    w, h, pal, bg = decode_candidate(files['SHIN.FIG'].read_bytes())
    assert (w, h) == (320, 200)
    colours = rgb_palette(pal)
    paper = raster(w, h, bg, colours)
    paper.save(a.output/'newspaper-reference.png')
    _, _, flag_pal, _ = decode_candidate(files['FLAG.FIG'].read_bytes())
    flags = byte_sprites(files['FLAG.XBB'].read_bytes())
    outcomes = byte_sprites(files['WC.XBB'].read_bytes())
    assert [(x[1], x[2]) for x in flags] == [(65, 33)]*7
    assert [(x[1], x[2]) for x in outcomes] == [(65, 169)]*3
    for i, (_, sw, sh, pixels) in enumerate(outcomes):
        raster(sw, sh, pixels, colours).save(a.output/f'outcome-{i}.png')
    for i, (_, sw, sh, pixels) in enumerate(flags):
        raster(sw, sh, pixels, rgb_palette(flag_pal)).save(a.output/f'flag-{i}.png')
    for i in range(11):
        portrait(files['LOSEFIG.XBB'].read_bytes(), i).save(a.output/f'loser-{i:02d}.png')
    # 既有正常完整雙打，斬勝法蘭克。只核對已取樣組合，不猜其他結果規則。
    reconstructed = paper.copy()
    reconstructed.paste(portrait(files['BIGFIG.XBB'].read_bytes(), 0), (18, 34))
    reconstructed.paste(ImageOps.mirror(portrait(files['LOSEFIG.XBB'].read_bytes(), 4)), (214, 34))
    reconstructed.paste(Image.open(a.output/'outcome-0.png'), (128, 15))
    reconstructed.paste(Image.open(a.output/'flag-0.png'), (30, 154))
    reconstructed.paste(Image.open(a.output/'flag-1.png'), (226, 154))
    names = files['NAME.XBB'].read_bytes()
    name_records = []
    for index, x in ((0, 42), (4, 232)):
        off = struct.unpack_from('<H', names, index*2)[0]
        nw, nh = names[off:off+2]
        pixels = names[off+2:off+2+nw*nh]
        assert len(pixels) == nw*nh and max(pixels) <= 6
        reconstructed.paste(raster(nw, nh, bytes(1 if v else 0 for v in pixels), [(219,)*3, (0,)*3]), (x, 134))
        name_records.append({'character': index, 'offset': off, 'size': [nw, nh], 'position': [x, 134]})
    capture = ROOT/'workplace/native-match-v2/result-newspaper.png.live.rgb'
    actual = capture.read_bytes()
    assert reconstructed.tobytes() == actual, 'full result RGB differs'
    reconstructed.save(a.output/'reconstructed.png')
    receipt = {'kind': 'original result source export and complete existing normal-capture reconstruction',
        'passed': True, 'tool': 'Pillow 11.3.0 in Docker', 'exporter_sha256': sha(Path(__file__)),
        'address_space': 'original file offsets and 320x200 screen coordinates, not runtime or IDA addresses',
        'inputs': {name: sha(path) for name, path in files.items()},
        'capture': str(capture.relative_to(ROOT)), 'capture_sha256': sha(capture),
        'normal_path_receipt_sha256': sha(ROOT/'workplace/native-match-v2/receipt.json'),
        'original_normal_path': 'two ordinary rounds, result newspaper and Return to title; existing native-match-v2',
        'portraits': [{'source': 'BIGFIG.XBB', 'character': 0, 'position': [18, 34], 'mirrored': False},
                     {'source': 'LOSEFIG.XBB', 'character': 4, 'position': [214, 34], 'mirrored': True}],
        'outcome': {'source': 'WC.XBB', 'record': 0, 'offset': 0, 'size': [65, 169], 'position': [128, 15]},
        'flags': [{'record': 0, 'position': [30, 154]}, {'record': 1, 'position': [226, 154]}],
        'names': name_records, 'files': {},
        'limits': 'one previously verified normal result, not new execution; no result classification rule or all-character result coverage'}
    receipt['files'] = {p.name: sha(p) for p in a.output.glob('*.png')}
    (a.output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'passed': True, 'full_original_RGB_pixels': 64000, 'source_files': receipt['inputs'],
                      'receipt_sha256': sha(a.output/'receipt.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
