"""以原來源幾何重畫七面結果旗幟，保存新 SVG／PNG 候選，不拷貝點陣色號。"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from recognize_result_source import ResultSources

ROOT = Path('/project')
RED, BLUE, WHITE, DARK, GOLD = '#cf0830', '#6528eb', '#ffffff', '#383838', '#ffcb14'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def components(points, diagonal=False):
    points = set(points)
    out = []
    neighbours = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                  if (dx or dy) and (diagonal or abs(dx)+abs(dy) == 1)]
    while points:
        seed = min(points)
        points.remove(seed)
        part, todo = {seed}, [seed]
        while todo:
            x, y = todo.pop()
            for dx, dy in neighbours:
                q = x+dx, y+dy
                if q in points:
                    points.remove(q)
                    part.add(q)
                    todo.append(q)
        out.append(part)
    return out


def bounds(points):
    return [min(x for x, y in points), min(y for x, y in points),
            max(x for x, y in points)+1, max(y for x, y in points)+1]


def star_points(cx, cy, rx, ry):
    return [(cx+math.cos(-math.pi/2+i*math.pi/5)*rx*(1 if i%2 == 0 else .4),
             cy+math.sin(-math.pi/2+i*math.pi/5)*ry*(1 if i%2 == 0 else .4)) for i in range(10)]


def commands_for(index, original):
    commands = []
    layout = {}
    def rect(x, y, w, h, fill):
        commands.append({'type': 'rect', 'box': [x, y, x+w, y+h], 'fill': fill})
    def poly(points, fill):
        commands.append({'type': 'polygon', 'points': points, 'fill': fill})
    def ellipse(box, fill):
        commands.append({'type': 'ellipse', 'box': box, 'fill': fill})
    def line(x0, y0, x1, y1, width, fill):
        length = math.hypot(x1-x0, y1-y0)
        nx, ny = -(y1-y0)/length*width/2, (x1-x0)/length*width/2
        poly([(x0+nx, y0+ny), (x1+nx, y1+ny), (x1-nx, y1-ny), (x0-nx, y0-ny)], fill)
    def mask(colour):
        return {(x, y) for y in range(33) for x in range(65) if original.getpixel((x, y)) == colour}
    if index == 0:
        rect(0, 0, 65, 33, WHITE)
        box = bounds(mask((207, 8, 48)))
        ellipse(box, RED)
        layout['red_region_bounds'] = box
        layout['review'] = '紅色橢圓按來源紅區邊界重畫；粉紅點陣邊緣改由新抗鋸齒呈現。'
    elif index == 1:
        for i in range(13):
            rect(0, i*33/13, 65, 33/13, RED if i%2 == 0 else WHITE)
        box = bounds(mask((101, 40, 235)))
        rect(box[0], box[1], box[2]-box[0], box[3]-box[1], BLUE)
        points = {(x, y) for y in range(box[1], box[3]) for x in range(box[0], box[2])
                  if original.getpixel((x, y)) == (255, 255, 255)}
        dots = components(points)
        assert len(dots) == 98
        for part in dots:
            x0, y0, x1, y1 = bounds(part)
            poly(star_points((x0+x1)/2, (y0+y1)/2, .57, .57), WHITE)
        layout.update(canton_bounds=box, source_white_components=98,
                      review='保留原來源 98 個白色點位，以新小星重畫；不擅自改成現代標準星數。橫條由平滑向量重排。')
    elif index == 2:
        rect(0, 0, 65, 33, BLUE)
        line(0, 0, 65, 33, 5, WHITE)
        line(0, 33, 65, 0, 5, WHITE)
        line(0, 0, 65, 33, 2.5, RED)
        line(0, 33, 65, 0, 2.5, RED)
        rect(28, 0, 9, 33, WHITE)
        rect(0, 12, 65, 9, WHITE)
        rect(29, 0, 7, 33, RED)
        rect(0, 13, 65, 7, RED)
        layout['review'] = '保留紫藍底與紅白交叉；斜線寬度及交接處為向量近似，不稱原像素或法定比例。'
    elif index == 3:
        rect(0, 0, 65, 33, RED)
        parts = sorted(components(mask((255, 255, 255)), diagonal=True), key=lambda p: (-len(p), bounds(p)))
        assert len(parts) == 5
        marks = []
        for part in parts:
            x0, y0, x1, y1 = bounds(part)
            poly(star_points((x0+x1)/2, (y0+y1)/2, (x1-x0)/2, (y1-y0)/2), WHITE)
            marks.append({'pixels': len(part), 'bounds': [x0, y0, x1, y1]})
        layout.update(source_marks=marks, review='原資料是五個白色小圖記；保留白色及不規則位置，星形為新向量近似，未改成金黃或標準位置。')
    elif index == 4:
        for i, fill in enumerate((WHITE, BLUE, RED)):
            rect(0, i*11, 65, 11, fill)
        layout['review'] = '三等分色帶採來源白／紫藍／紅配色；未替換成其他旗幟版本。'
    elif index == 5:
        for i, fill in enumerate((RED, WHITE, DARK)):
            rect(0, i*11, 65, 11, fill)
        # 中央徽記另作平滑翼形與軀幹，沒有複製八列舊點陣輪廓。
        poly([(23, 21), (24, 18), (26, 15), (29, 15), (30.5, 13), (32, 15), (35, 15), (37, 18), (38, 21),
              (34, 19), (32, 18), (33, 21), (28, 21), (29, 18), (27, 19)], GOLD)
        poly([(30, 14), (30, 12.8), (31.4, 12.8), (32.3, 13.7), (31.5, 14.3)], GOLD)
        for x in (25.5, 27.0, 34.0, 35.5):
            line(x, 17.4, x, 19.3, .3, WHITE)
        layout.update(source_motif_bounds=bounds(mask((255, 203, 20))),
                      review='金色中央徽記另作翼形幾何近似；未還原徽章文字／細節，也不宣稱正確的國徽版本。')
    elif index == 6:
        rect(0, 0, 65, 33, WHITE)
        coloured = {(x, y) for y in range(33) for x in range(65)
                    if original.getpixel((x, y)) not in ((255, 255, 255), (56, 56, 56))}
        x0, y0, x1, y1 = bounds(coloured)
        cx, cy, rx, ry = (x0+x1)/2, (y0+y1)/2, (x1-x0)/2, (y1-y0)/2
        ellipse([x0, y0, x1, y1], BLUE)
        poly([(cx+math.cos(t*math.pi/100)*rx, cy+math.sin(t*math.pi/100)*ry)
              for t in range(100, 201)], RED)
        ellipse([cx-rx, cy-ry/2, cx, cy+ry/2], BLUE)
        ellipse([cx, cy-ry/2, cx+rx, cy+ry/2], RED)
        black = mask((56, 56, 56))
        groups = []
        for sx, sy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            quadrant = {(x, y) for x, y in black if (x >= 32) == bool(sx) and (y >= 16) == bool(sy)}
            by_p = {}
            for x, y in quadrant:
                p, q = (x-y, x+y) if sx != sy else (x+y, x-y)
                by_p.setdefault(p, set()).add(q)
            bands = []
            for p in sorted(by_p):
                if not bands or p > bands[-1][-1]+1:
                    bands.append([])
                bands[-1].append(p)
            assert len(bands) == 3
            segments = []
            for band in bands:
                qs = sorted(set().union(*(by_p[p] for p in band)))
                intervals = []
                for q in qs:
                    if not intervals or q > intervals[-1][-1]+1:
                        intervals.append([])
                    intervals[-1].append(q)
                for interval in intervals:
                    # 把量到的線帶改成平滑向量長條，保留中斷位置。
                    plo, phi = min(band)+.5, max(band)+1.5
                    qlo, qhi = min(interval)-.5, max(interval)+.5
                    if sx != sy:
                        qlo, qhi = qlo+1, qhi+1
                    def xy(p, q):
                        return ((p+q)/2, (q-p)/2) if sx != sy else ((p+q)/2, (p-q)/2)
                    poly([xy(plo, qlo), xy(phi, qlo), xy(phi, qhi), xy(plo, qhi)], DARK)
                segments.append(len(intervals))
            groups.append({'quadrant': [sx, sy], 'segments_per_bar': segments})
        layout.update(source_motif_bounds=[x0, y0, x1, y1], trigram_groups=groups,
                      review='四組卦線按原黑線投影保留完整／中斷配置；中央旋紋與曲線為新向量近似，未以標準國旗改正原圖。')
    return commands, layout


def svg(commands):
    elements = []
    for item in commands:
        fill = item['fill']
        if item['type'] == 'polygon':
            points = ' '.join(f'{x:.4f},{y:.4f}' for x, y in item['points'])
            elements.append(f'<polygon points="{points}" fill="{fill}"/>')
        else:
            x0, y0, x1, y1 = item['box']
            if item['type'] == 'rect':
                elements.append(f'<rect x="{x0:.4f}" y="{y0:.4f}" width="{x1-x0:.4f}" height="{y1-y0:.4f}" fill="{fill}"/>')
            else:
                elements.append(f'<ellipse cx="{(x0+x1)/2:.4f}" cy="{(y0+y1)/2:.4f}" rx="{(x1-x0)/2:.4f}" ry="{(y1-y0)/2:.4f}" fill="{fill}"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="660" viewBox="0 0 65 33">\n'+'\n'.join(elements)+'\n</svg>\n'


def rasterize(commands):
    im = Image.new('RGB', (2600, 1320), 'white')
    draw = ImageDraw.Draw(im)
    for item in commands:
        if item['type'] == 'polygon':
            draw.polygon([(round(x*40), round(y*40)) for x, y in item['points']], fill=item['fill'])
        else:
            box = [round(v*40) for v in item['box']]
            if item['type'] == 'rect':
                draw.rectangle(box, fill=item['fill'])
            else:
                draw.ellipse(box, fill=item['fill'])
    return im.resize((1300, 660), Image.Resampling.LANCZOS)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    destination = ROOT/'assets/hd/candidates'
    source_path = destination/'result-flags-source.json'
    preview = ROOT/'docs/screenshots/result-flag-candidates.png'
    assert not source_path.exists() and not preview.exists()
    source = ResultSources(ROOT/'workplace/orig')
    catalog_path = ROOT/'assets/hd/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    for row in previous:
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    assert all(p.stat().st_uid == 1000 for p in (destination, catalog_path, preview.parent))
    a.output.mkdir()
    public = Image.new('RGB', (1400, 1640), '#151d29')
    private = Image.new('RGB', (1400, 1640), '#151d29')
    font = ImageFont.truetype(str(ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'), 23)
    ImageDraw.Draw(public).text((18, 6), '七面結果旗幟 HD 向量候選，未接正式程式', font=font, fill='white')
    records = []
    for i, original in enumerate(source.flags):
        commands, layout = commands_for(i, original)
        png_path = destination/f'result-flag-{i:02d}-v1.png'
        svg_path = png_path.with_suffix('.svg')
        assert not png_path.exists() and not svg_path.exists()
        svg_path.write_text(svg(commands))
        image = rasterize(commands)
        image.save(png_path)
        x, y = i%2*700, 44+i//2*399
        label = f'FLAG.XBB 第 {i} 筆，65×33 → SVG／1300×660'
        ImageDraw.Draw(public).text((x+16, y+4), label, font=font, fill='white')
        public.paste(image.resize((650, 330), Image.Resampling.LANCZOS), (x+20, y+40))
        ImageDraw.Draw(private).text((x+16, y+4), f'RECORD {i} ORIGINAL / HD', font=font, fill='white')
        private.paste(original.resize((325, 165), Image.Resampling.NEAREST), (x+20, y+40))
        private.paste(image.resize((325, 165), Image.Resampling.LANCZOS), (x+345, y+40))
        records.append({'index': i, 'file': png_path.name, 'svg': svg_path.name, 'sha256': sha(png_path),
            'svg_sha256': sha(svg_path), 'size': [1300, 660], 'original_size': [65, 33],
            'source_file_offset': i*2147, 'original_RGB_sha256': hashlib.sha256(original.tobytes()).hexdigest(),
            'commands': commands, 'layout': layout, 'status': 'candidate-vector-art-not-approved-or-integrated'})
        for path in (png_path, svg_path):
            row = {'file': str(path.relative_to(ROOT/'assets/hd')), 'sha256': sha(path), 'bytes': path.stat().st_size,
                   'status': 'candidate-result-flag-vector-not-integrated', 'source_record': i, 'tool': 'project vector geometry + Pillow 11.3.0'}
            if path.suffix == '.png':
                row['size'] = [1300, 660]
            catalog['files'].append(row)
    public.save(preview)
    private.save(a.output/'original-vs-candidate.png')
    provenance = {'kind': 'seven new vector result flag candidates, source layout and palette retained where measured',
        'authorization': 'existing HD generation/upload scope; no visibility or formal release change',
        'source_file': 'FLAG.XBB', 'source_sha256': source.inputs['FLAG.XBB'], 'palette_source': 'FLAG.FIG',
        'palette_source_sha256': source.inputs['FLAG.FIG'], 'tool': 'project SVG primitives; Pillow 11.3.0 supersampling in Docker',
        'builder_sha256': sha(Path(__file__)), 'records': records,
        'preview': {'file': str(preview.relative_to(ROOT)), 'sha256': sha(preview)},
        'limits': 'new geometric approximations, not original bitmap copies, national flag standards, all-character flag assignment, visual approval or runtime integration'}
    source_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
    catalog['files'].append({'file': str(source_path.relative_to(ROOT/'assets/hd')), 'sha256': sha(source_path),
        'bytes': source_path.stat().st_size, 'status': 'candidate-result-flag-vector-provenance'})
    catalog['pngs'] += 7
    assert catalog['files'][:-15] == previous
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    path = ROOT/'docs/screenshots/source.json'
    screens = json.loads(path.read_text())
    screens['prototype_captures'].append({'kind': 'new SVG result-flag art contact sheet; not native capture',
        'file': preview.name, 'sha256': sha(preview), 'source': 'assets/hd/candidates/result-flags-source.json',
        'source_sha256': sha(source_path), 'renderer': 'tools/prepare_result_flag_art.py', 'renderer_sha256': sha(Path(__file__)),
        'platform': 'Pillow 11.3.0 in Docker; not runtime acceptance', 'authorization': 'existing user HD upload request',
        'limits': 'new vector artwork only; original flag images and comparison stay local'})
    path.write_text(json.dumps(screens, ensure_ascii=False, indent=2)+'\n')
    receipt = {'passed': True, 'previous_catalog_entries': previous, 'builder_sha256': sha(Path(__file__)),
        'source_sha256': sha(source_path), 'preview_sha256': sha(preview), 'private_comparison_sha256': sha(a.output/'original-vs-candidate.png'),
        'PNG_count': catalog['pngs'], 'catalog_entries': len(catalog['files']), 'asset_payload_bytes': sum(r['bytes'] for r in catalog['files'])}
    (a.output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'previous_catalog_entries'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
