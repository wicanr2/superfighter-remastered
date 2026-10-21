"""裁取已核對的三種正常原生結果標題；原圖／分類公式不收進公開圖。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/project')
BOX = (464, 109, 659, 616)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', nargs='+', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and not a.output.with_suffix('.json').exists()
    chosen = {}
    for q in a.cases:
        q = q.resolve()
        receipt = json.loads((q/'receipt.json').read_text())
        comparison = json.loads((q/'comparison.json').read_text())
        assert comparison['status'] == 'passed' and not comparison['fallback']
        assert comparison['receipt_sha256'] == sha(q/'receipt.json')
        assert comparison['files']['result-hd.png'] == sha(q/'result-hd.png')
        state = next(e['state'] for e in receipt['events'] if e['name'] == 'result-hd')
        assert state['result_hd_prototype']
        index = state['result_prototype']['outcome_record']
        assert comparison['outcome_record'] == index == receipt['outcome_record']
        chosen.setdefault(index, q)
    assert set(chosen) == {0,1,2}, sorted(chosen)
    labels = ['壓倒勝','逆轉勝','險勝']
    font_path = ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    heading = ImageFont.truetype(str(font_path),22)
    font = ImageFont.truetype(str(font_path),18)
    picture = Image.new('RGB',(660,650),'#151c28')
    draw = ImageDraw.Draw(picture)
    draw.text((12,8),'三種結果的正常原生 HD 取樣，尚未正式整合',font=heading,fill='white')
    records=[]
    for i in range(3):
        q=chosen[i]; x=12+i*220
        label=f'來源 {i}／{labels[i]}'
        assert draw.textbbox((0,0),label,font=font)[2] <= 195
        draw.text((x,40),label,font=font,fill='white')
        capture=Image.open(q/'result-hd.png').convert('RGB')
        assert capture.size==(1120,820)
        picture.paste(capture.crop(BOX),(x,70))
        records.append({'index':i,'label':labels[i],'capture':str((q/'result-hd.png').relative_to(ROOT)),
            'capture_sha256':sha(q/'result-hd.png'),'comparison':str((q/'comparison.json').relative_to(ROOT)),
            'comparison_sha256':sha(q/'comparison.json'),'receipt_sha256':sha(q/'receipt.json'),
            'binary_sha256':json.loads((q/'receipt.json').read_text())['binary_sha256'],
            'crop':list(BOX),'destination':[x,70]})
    draw.text((12,606),'來源依原版完整結果辨識，不代表分類公式或正式版驗收。',font=font,fill='white')
    picture.save(a.output)
    data={'kind':'three observed normal native result heading crops; isolated prototype, not static source art or formal integration',
        'file':a.output.name,'sha256':sha(a.output),'size':list(picture.size),'records':records,
        'builder_sha256':sha(Path(__file__)),'font_sha256':sha(font_path)}
    a.output.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='records'},ensure_ascii=False))


if __name__=='__main__':
    main()
