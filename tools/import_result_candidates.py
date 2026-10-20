"""收錄報紙／法蘭克敗者生成原圖，製作純 HD 靜態結果比較。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def star(draw, cx, cy, radius):
    points = [(cx+math.cos(-math.pi/2+i*math.pi/5)*radius*(1 if i%2 == 0 else .4),
               cy+math.sin(-math.pi/2+i*math.pi/5)*radius*(1 if i%2 == 0 else .4)) for i in range(10)]
    draw.polygon(points, fill='white')


def preview(paper_path, loser_path):
    im = Image.open(paper_path).convert('RGB').resize((1600, 1000), Image.Resampling.LANCZOS)
    winner = ROOT/'assets/hd/candidates/selection-jaan-v1.png'
    im.paste(Image.open(winner).convert('RGB').resize((445, 445), Image.Resampling.LANCZOS), (90, 170))
    im.paste(ImageOps.mirror(Image.open(loser_path).convert('RGB')).resize((445, 445), Image.Resampling.LANCZOS), (1070, 170))
    draw = ImageDraw.Draw(im)
    font_path = ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    headline = ImageFont.truetype(str(font_path), 225)
    for i, glyph in enumerate('壓倒勝'):
        box = draw.textbbox((0, 0), glyph, font=headline, stroke_width=4)
        x = 802-(box[2]-box[0])/2-box[0]
        y = 75+i*280-box[1]
        draw.text((x, y), glyph, font=headline, stroke_width=4, fill='#111111', stroke_fill='#111111')
    name_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 62)
    for name, centre in (('JAAN', 315), ('FRANK', 1295)):
        box = draw.textbbox((0, 0), name, font=name_font)
        draw.text((centre-(box[2]-box[0])/2-box[0], 670-box[1]), name, font=name_font, fill='#111111')
    # 同取樣兩面國旗，以向量另畫；不複製 FLAG.XBB 像素。
    draw.rectangle((150, 770, 474, 934), fill='#ffffff')
    draw.ellipse((263, 803, 361, 901), fill='#cc0830')
    for i in range(13):
        top, bottom = 770+round(i*165/13), 770+round((i+1)*165/13)-1
        draw.rectangle((1130, top, 1454, bottom), fill='#c8102e' if i%2 == 0 else 'white')
    draw.rectangle((1130, 770, 1260, 858), fill='#28388c')
    for y in range(9):
        count = 6 if y%2 == 0 else 5
        for x in range(count):
            star(draw, 1140+x*22+(11 if count == 5 else 0), 776+y*9, 3.7)
    card = Image.new('RGB', (1600, 1100), '#131b27')
    card.paste(im, (0, 50))
    ui_font = ImageFont.truetype(str(font_path), 26)
    d = ImageDraw.Draw(card)
    d.text((18, 5), '結果報紙 HD 候選：斬勝法蘭克；靜態比較，非遊戲擷取', font=ui_font, fill='white')
    d.text((18, 1057), '細字印刷為紋理近似，標題另行排字；未定版、未接正式遊戲。', font=ui_font, fill='#f2cb67')
    return card


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--requests', type=Path, required=True)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--generated-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    reference = json.loads((a.references/'receipt.json').read_text())
    assert reference['passed'] and reference['exporter_sha256'] == sha(ROOT/'tools/export_result_source.py')
    for name, digest in reference['files'].items():
        assert sha(a.references/name) == digest
    requests = json.loads(a.requests.read_text())
    assert [row['id'] for row in requests] == ['paper', 'loser-frank']
    destination = ROOT/'assets/hd/candidates'
    catalog_path = ROOT/'assets/hd/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    for row in previous:
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    assert all(p.stat().st_uid == 1000 for p in (destination, catalog_path, ROOT/'docs/screenshots'))
    targets = [destination/'result-newspaper-v1.png', destination/'result-loser-frank-v1.png']
    source_path = destination/'result-source.json'
    target_preview = ROOT/'docs/screenshots/result-newspaper-candidate.png'
    assert not source_path.exists() and not target_preview.exists() and all(not p.exists() for p in targets)
    records = []
    for request, target in zip(requests, targets):
        original = a.generated_root/Path(request['generated']).name
        with Image.open(original) as im:
            im.verify()
        with Image.open(original) as im:
            assert im.width >= 1200 and im.height >= 900
            assert im.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            size = list(im.size)
        shutil.copyfile(original, target)
        assert sha(original) == sha(target) and target.stat().st_uid == 1000
        ref = a.references/('newspaper-reference.png' if request['id'] == 'paper' else 'loser-04.png')
        records.append({'id': request['id'], 'file': target.name, 'size': size, 'sha256': sha(target),
            'bytes': target.stat().st_size, 'tool': 'built-in image_gen', 'model_version': 'not exposed by tool',
            'prompt': request['prompt'], 'generated_source': original.name, 'transparent_background': False,
            'original_reference_sha256': sha(ref), 'source_file': 'SHIN.FIG' if request['id'] == 'paper' else 'LOSEFIG.XBB',
            'source_sha256': reference['inputs']['SHIN.FIG' if request['id'] == 'paper' else 'LOSEFIG.XBB'],
            'status': 'candidate-not-approved-or-integrated'})
        catalog['files'].append({'file': str(target.relative_to(ROOT/'assets/hd')), 'size': size, 'sha256': sha(target),
            'bytes': target.stat().st_size, 'status': 'candidate-result-not-integrated', 'tool': 'built-in imagegen',
            'generated_source': original.name})
    a.output.mkdir()
    preview(*targets).save(target_preview)
    provenance = {'kind': 'HD result newspaper and defeated Frank candidates; original references local only',
        'authorization': 'existing B style and generated-HD upload scope; visibility unchanged',
        'records': records, 'original_source_inputs': reference['inputs'], 'source_receipt_sha256': sha(a.references/'receipt.json'),
        'requests_sha256': sha(a.requests), 'importer_sha256': sha(Path(__file__)),
        'style_reference': {'file': 'selection-frank-v1.png', 'sha256': sha(destination/'selection-frank-v1.png')},
        'winner_reference': {'file': 'selection-jaan-v1.png', 'sha256': sha(destination/'selection-jaan-v1.png')},
        'preview': {'file': str(target_preview.relative_to(ROOT)), 'sha256': sha(target_preview)},
        'review': '底圖為新印刷紋理，細字不可當原文；框線位置為近似。法蘭克保留白髮與青藍衣緣，眼部腫傷／嘴角與原圖程度不同，未宣稱完全忠實。',
        'limits': 'only one defeated portrait; headline uses modern Traditional Chinese type, not original calligraphy; static layout, no formal result integration'}
    dump(source_path, provenance)
    catalog['files'].append({'file': str(source_path.relative_to(ROOT/'assets/hd')), 'sha256': sha(source_path),
        'bytes': source_path.stat().st_size, 'status': 'candidate-result-provenance'})
    catalog['pngs'] += 2
    assert catalog['files'][:-3] == previous
    dump(catalog_path, catalog)
    screen_source = ROOT/'docs/screenshots/source.json'
    screens = json.loads(screen_source.read_text())
    screens['prototype_captures'].append({'kind': 'static HD result art comparison; not native capture',
        'file': target_preview.name, 'sha256': sha(target_preview), 'source': 'assets/hd/candidates/result-source.json',
        'source_sha256': sha(source_path), 'renderer': 'tools/import_result_candidates.py', 'renderer_sha256': sha(Path(__file__)),
        'platform': 'Pillow 11.3.0 in Docker; no native platform acceptance',
        'authorization': 'existing user request for HD generation and repository upload',
        'limits': 'new HD and vector elements only; no original pixels or formal result UI'})
    dump(screen_source, screens)
    receipt = {'passed': True, 'importer_sha256': sha(Path(__file__)), 'previous_catalog_entries': previous,
        'source_sha256': sha(source_path), 'preview_sha256': sha(target_preview), 'PNG_count': catalog['pngs'],
        'catalog_entries': len(catalog['files']), 'asset_payload_bytes': sum(r['bytes'] for r in catalog['files'])}
    dump(a.output/'receipt.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'previous_catalog_entries'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
