"""核對 SELMAN 正常來源，製作純 HD 靜態選角比較，不更動遊戲或滑鼠區域。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from hd_source_probe import decode_candidate

ROOT = Path('/project')
SELMAN_SHA = '9b40caeee1eff32370a6826e1362087ae1da086237731f06de905d696b6c195a'
BIG_SHA = '4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477'
NAMES = ['斬', '薩爾可夫', '子彈', '鳳凰', '法蘭克', '鬼丸', '嵐', '金太極', '蜘蛛女', '小丑', '印第安喬']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def put_json(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def original_checks(captures):
    """只容許已量測的八格框線；不以容錯掩蓋其他來源差異。"""
    source = ROOT/'workplace/orig/SELMAN.CPM'
    big_path = ROOT/'workplace/orig/BIGFIG.XBB'
    assert sha(source) == SELMAN_SHA and sha(big_path) == BIG_SHA
    w, h, palette, base = decode_candidate(source.read_bytes())
    assert (w, h, len(base), len(palette)) == (320, 200, 64000, 768)
    big = big_path.read_bytes()
    borders = set()
    for column in range(8):
        x0, x1 = 28+33*column, 60+33*column
        borders.update(y*320+x for y in range(150, 183) for x in range(x0, x1+1)
                       if x in (x0, x1) or y in (150, 182))
    records = []
    for meta_path in sorted(captures.glob('*.png.capture.json')):
        meta = json.loads(meta_path.read_text())
        view = meta.get('selection_prototype')
        if view is None:
            continue
        prefix = str(meta_path).removesuffix('.capture.json')
        raw = Path(prefix+'.display.idx').read_bytes()
        colours = json.loads(Path(prefix+'.prototype-palette.json').read_text())
        assert len(raw) == len(base)
        assert colours[:160] == [[v*4+v//16 for v in palette[i:i+3]] for i in range(0, 480, 3)]
        expected = bytearray(base)
        for side, character in enumerate(view['portraits']):
            if character < 0:
                continue
            record = big[character*8689:(character+1)*8689]
            bank = 160+side*32
            assert colours[bank:bank+32] == [[v*4+v//16 for v in record[i:i+3]] for i in range(0, 96, 3)]
            for y in range(89):
                for x in range(89):
                    dx = 11+x if side == 0 else 302-x
                    expected[(15+y)*320+dx] = bank+record[768+y*89+x]
        differences = [i for i, (a, b) in enumerate(zip(expected, raw)) if a != b]
        assert all(i in borders and raw[i] in (240, 241) for i in differences), meta_path.name
        for i in differences:
            expected[i] = raw[i]
        assert bytes(expected) == raw
        assert Path(prefix+'.selected.rgb').read_bytes() == bytes(c for v in expected for c in colours[v])
        records.append({'capture': meta_path.name, 'portraits': view['portraits'],
                        'selector_border_pixels': len(differences), 'index_sha256': hashlib.sha256(raw).hexdigest()})
    assert len(records) == 27, len(records)
    return {'SELMAN.CPM_sha256': SELMAN_SHA, 'BIGFIG.XBB_sha256': BIG_SHA,
            'logical_size': [320, 200], 'source_records': records,
            'method': 'full SELMAN + BIGFIG + measured eight selector perimeters; original RGB reconstructed',
            'limits': 'retained border pixels observed, no claim about unobserved redraw timing'}


def screen(art, logo, vs, columns):
    """只讀新 HD 素材，絕不讀取原版像素作公開輸出。"""
    scale = 4
    im = Image.new('RGBA', (1280, 800), (79, 79, 79, 255))
    draw = ImageDraw.Draw(im)
    # 原位置框線以原生幾何重畫；沒有從 SELMAN 複製像素。
    for x in (9, 212):
        draw.rectangle((x*scale, 13*scale, (x+93)*scale, 106*scale), fill='#120e0a')
        draw.rectangle((x*scale, 13*scale, (x+91)*scale, 104*scale), fill='#e4ba2e', outline='#fff4ac', width=4)
        draw.rectangle(((x+2)*scale, 15*scale, (x+89)*scale, 102*scale), fill='#b90000')
    logo = logo.crop(logo.getchannel('A').point(lambda v: 255 if v >= 16 else 0).getbbox())
    gray = ImageOps.grayscale(logo).convert('RGBA')
    gray.putalpha(logo.getchannel('A').point(lambda a: int(a*.48)))
    gray = gray.resize((1100, 270), Image.Resampling.LANCZOS)
    im.alpha_composite(gray, (64, 280))
    # 保留兩側原肖像範圍與鏡像方向；此靜態比較選蜘蛛女／印第安喬。
    im.alpha_composite(art[8].resize((356, 356), Image.Resampling.LANCZOS), (44, 60))
    im.alpha_composite(ImageOps.mirror(art[10]).resize((356, 356), Image.Resampling.LANCZOS), (856, 60))
    vs = vs.crop(vs.getchannel('A').point(lambda v: 255 if v >= 16 else 0).getbbox())
    im.alpha_composite(vs.resize((340, 204), Image.Resampling.LANCZOS), (450, 172))
    y, left, span = 600, 112, 1056
    for i in range(columns):
        x0, x1 = left+round(i*span/columns), left+round((i+1)*span/columns)
        size = x1-x0-4
        im.alpha_composite(art[i].resize((size, size), Image.Resampling.LANCZOS), (x0+2, y+2))
        ImageDraw.Draw(im).rectangle((x0, y, x1-1, y+size+3), outline='#151515', width=3)
    if columns == 11:
        for i, colour in ((8, '#ffcf35'), (10, '#57dfff')):
            x0, x1 = left+round(i*span/columns), left+round((i+1)*span/columns)
            ImageDraw.Draw(im).rectangle((x0, y, x1-1, y+x1-x0-1), outline=colour, width=5)
    return im.convert('RGB')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--captures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert a.output.is_dir() and not (a.output/'receipt.json').exists()
    checks = original_checks(a.captures)
    source_path = ROOT/'assets/hd/candidates/selection-portraits-source.json'
    records = json.loads(source_path.read_text())['records']
    inputs = [source_path, ROOT/'assets/hd/candidates/title-logo-v1.png', ROOT/'assets/hd/candidates/selection-vs-v1.png']
    vs_source = ROOT/'assets/hd/candidates/selection-vs-source.json'
    assert sha(inputs[2]) == json.loads(vs_source.read_text())['sha256']
    art = []
    for row in records:
        path = ROOT/'assets/hd/candidates'/row['file']
        assert sha(path) == row['sha256']
        inputs.append(path)
        art.append(Image.open(path).convert('RGBA'))
    logo, vs = (Image.open(p).convert('RGBA') for p in inputs[1:3])
    inputs.append(vs_source)
    font_path = ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    font = ImageFont.truetype(str(font_path), 24)
    sheets = []
    for count, title in ((8, 'A：保留八格位置，三名魔王沿用既有姓名按鈕'),
                         (11, 'B：十一格並列，需另外調整滑鼠區域與焦點')):
        card = Image.new('RGB', (1280, 960), '#111924')
        card.paste(screen(art, logo, vs, count), (0, 48))
        d = ImageDraw.Draw(card)
        d.text((18, 8), title, font=font, fill='white')
        for i, name in enumerate(NAMES):
            x = 12+round(i*1256/11)
            d.rounded_rectangle((x, 855, x+108, 896), radius=5, fill='#28384a', outline='#718199')
            box = d.textbbox((0, 0), name, font=font)
            d.text((x+(108-box[2])/2, 857), name, font=font, fill='white')
        d.text((18, 914), '靜態 HD 構圖比較，非遊戲截圖；按鈕不可操作，尚未定版。', font=font, fill='#f4c962')
        card.save(a.output/f'layout-{count}.png')
        sheets.append(card)
    public = Image.new('RGB', (1280, 1920))
    for i, card in enumerate(sheets):
        public.paste(card, (0, i*960))
    target = ROOT/'docs/screenshots/selection-layout-candidates.png'
    assert not target.exists()
    public.save(target)
    put_json(a.output/'receipt.json', {'passed': True, 'kind': 'static HD layout comparison, not runtime',
        'renderer_sha256': sha(Path(__file__)), 'source_checks': checks,
        'HD_inputs': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        'font_sha256': sha(font_path), 'output': str(target.relative_to(ROOT)), 'output_sha256': sha(target),
        'limits': 'new art and vector geometry only in public preview; no changed game paths, hit areas or release'})
    source_file = ROOT/'docs/screenshots/source.json'
    screenshots = json.loads(source_file.read_text())
    assert not any(row['file'] == target.name for row in screenshots['prototype_captures'])
    screenshots['prototype_captures'].append({'kind': 'static pure HD layout comparison; not native capture',
        'file': target.name, 'sha256': sha(target), 'source': 'assets/hd/candidates/selection-vs-source.json',
        'source_sha256': sha(vs_source), 'HD_inputs': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        'renderer': 'tools/preview_selection_screen.py', 'renderer_sha256': sha(Path(__file__)),
        'receipt_sha256': sha(a.output/'receipt.json'), 'platform': 'Pillow 11.3.0 in Docker; static preview only',
        'authorization': 'existing B art style and HD upload request; no repository visibility change',
        'limits': 'new art and vector geometry; no original pixels, no interactive buttons or formal UI approval'})
    put_json(source_file, screenshots)
    print(json.dumps({'passed': True, 'source_captures': len(checks['source_records']),
                      'preview_sha256': sha(target)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
