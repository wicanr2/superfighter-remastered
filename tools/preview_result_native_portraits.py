"""將已通過獨立核對的正常原生結果裁成敗者總覽，不使用原貌畫素。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/project')
BOX = (722, 166, 989, 433)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and not a.output.with_suffix('.json').exists()
    names = json.loads((ROOT/'assets/hd/candidates/result-portraits-source.json').read_text())['records']
    chosen = {}
    for q in a.cases:
        q = q.resolve()
        comparison = json.loads((q/'comparison.json').read_text())
        receipt = json.loads((q/'receipt.json').read_text())
        assert comparison['status'] == 'passed' and not comparison['fallback']
        assert comparison['receipt_sha256'] == sha(q/'receipt.json')
        assert comparison['GPU_identity_and_orientation_matches'] == 2
        assert comparison['files']['result-hd.png'] == sha(q/'result-hd.png')
        event = next(e for e in receipt['events'] if e['name'] == 'result-hd')
        assert event['state']['result_hd_prototype']
        index = event['state']['result_prototype']['characters'][1]
        assert any(r['side']=='right' and r['character']==index and r['mirrored'] for r in comparison['GPU_ranking'])
        chosen.setdefault(index, (q, comparison, receipt))
    assert set(chosen) == set(range(11)), sorted(chosen)
    font_path = ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    heading = ImageFont.truetype(str(font_path), 24)
    label = ImageFont.truetype(str(font_path), 19)
    picture = Image.new('RGB', (1152, 1052), '#151c28')
    draw = ImageDraw.Draw(picture)
    title = '十一名敗者的正常原生 HD 原型取樣，尚未正式整合'
    assert draw.textbbox((0, 0), title, font=heading)[2] < picture.width-24
    draw.text((12, 8), title, font=heading, fill='white')
    records = []
    for index in range(11):
        q, comparison, receipt = chosen[index]
        x, y = index%4*288+10, 54+index//4*310
        row = names[index]
        text = f"{row['name']}／來源 {index}"
        assert draw.textbbox((0,0), text, font=label)[2] <= 267
        draw.text((x,y), text, font=label, fill='white')
        source = Image.open(q/'result-hd.png').convert('RGB')
        assert source.size == (1120,820)
        picture.paste(source.crop(BOX), (x,y+32))
        records.append({'index':index, 'id':row['id'], 'name':row['name'],
            'capture':str((q/'result-hd.png').relative_to(ROOT)), 'capture_sha256':sha(q/'result-hd.png'),
            'comparison':str((q/'comparison.json').relative_to(ROOT)), 'comparison_sha256':sha(q/'comparison.json'),
            'receipt_sha256':sha(q/'receipt.json'), 'crop':list(BOX), 'destination':[x,y+32],
            'binary_sha256':receipt['binary_sha256']})
    draw.text((12, 1012), '全部由正常雙打結果擷取；原貌對照留本機，表情與傷勢仍為重畫近似。', font=label, fill='white')
    picture.save(a.output)
    data={'kind':'eleven normal native defeated portrait crops; isolated prototype, not static art or formal integration',
        'file':a.output.name, 'sha256':sha(a.output), 'size':list(picture.size), 'records':records,
        'builder_sha256':sha(Path(__file__)), 'font_sha256':sha(font_path)}
    a.output.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='records'},ensure_ascii=False))


if __name__ == '__main__':
    main()
