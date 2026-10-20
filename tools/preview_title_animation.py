"""原相位序列的 HD 材質分區比較；只產出候選，未接入原生程式。"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    a=p.parse_args();out=a.directory;r=Path('/project');art=r/'assets/hd/candidates'
    report_path=r/'workplace/title-demo-v2/source-review.json';report=json.loads(report_path.read_text())
    transfer=json.loads((out/'colour-transfer.json').read_text())
    assert transfer['proof_sha256']==sha(report_path) and transfer['source_material_mask']
    assert transfer['script_sha256']==sha(r/'tools/title_palette_preview.go')
    assert transfer['art_sha256']==sha(art/'title-logo-v1.png')
    logo=Image.open(art/'title-logo-v1.png').convert('RGBA')
    logos={}
    for frame in transfer['frames']:
        path=out/frame['file'];assert sha(path)==frame['sha256']
        image=Image.open(path).convert('RGBA');assert image.size==logo.size
        assert ImageChops.difference(image.getchannel('A'),logo.getchannel('A')).getbbox()is None
        logos[frame['phase']]=image
    assert logos[0].tobytes()==logo.tobytes(),'phase zero must preserve the complete original art'
    bounds=logo.getchannel('A').point(lambda value:255 if value>=16 else 0).getbbox()
    # 原動態材質最後一列為 39；雙線性材質投影在這條界線以下必須保持原稿。
    static_from=math.ceil(bounds[1]-.5+40.5*(bounds[3]-bounds[1])/69)
    static_rect=(0,static_from,logo.width,logo.height)
    assert all(image.crop(static_rect).tobytes()==logo.crop(static_rect).tobytes()for image in logos.values())
    assert len({hashlib.sha256(image.tobytes()).hexdigest()for image in logos.values()})==8
    person=Image.open(art/'title-person-v1.png').convert('RGBA').resize((1600,1000),Image.Resampling.LANCZOS)
    font_path=r/'internal/desktop/assets/NotoSansCJKtc-Regular.otf';font=ImageFont.truetype(str(font_path),48)
    def plate(phase,selected,outline):
        frame=Image.new('RGBA',(1600,1000),(0,0,0,255));frame.alpha_composite(person)
        frame.alpha_composite(logos[phase].crop(bounds).resize((1425,345),Image.Resampling.LANCZOS),(90,480))
        draw=ImageDraw.Draw(frame)
        for i,(left,top,right,bottom)in enumerate(report['button_tables']):
            rectangle=(left*5,top*5,(right+2)*5,bottom*5)
            x1,y1,x2,y2=rectangle
            draw.rectangle((x1,y1,x2-1,y2-1),fill=(79,57,102),outline=tuple(outline)if i==selected else(187,155,216),width=4 if i==selected else 3)
            text=('單　打','雙　打','設　定','結　束')[i];box=draw.textbbox((0,0),text,font=font)
            x=(x1+x2-(box[2]-box[0]))//2-box[0];y=(y1+y2-(box[3]-box[1]))//2-box[1]
            assert x1<=x+box[0]<x+box[2]<=x2 and y1<=y+box[1]<y+box[3]<=y2
            draw.text((x,y),text,font=font,fill=(250,239,255))
        return frame.convert('RGB')
    heading=ImageFont.truetype(str(font_path),28)
    sheet=Image.new('RGB',(1600,1200),(12,14,22));draw=ImageDraw.Draw(sheet)
    draw.text((20,12),'標題 HD 材質換色候選：原相位順序，尚未接入遊戲',font=heading,fill='white')
    frames=[];records=[]
    source_steps={x['stem']:x['steps']for x in json.loads((r/'workplace/title-demo-v2/receipt.json').read_text())['samples']}
    for i,original in enumerate(report['verified'][:16]):
        palette=json.loads((r/'workplace/title-demo-v2'/(original['stem']+'.palette.json')).read_text())
        phase=original['phase'];image=plate(phase,original['selected'],palette[51])
        path=out/f'title-frame-{i:02d}.png';assert not path.exists();image.save(path)
        x,y=(i%4)*400,80+(i//4)*280
        draw.text((x+8,y),f'{i+1:02d}　色盤相位 {phase}',font=ImageFont.truetype(str(font_path),20),fill=(210,216,230))
        sheet.paste(image.resize((400,250),Image.Resampling.LANCZOS),(x,y+28))
        frames.append(image.resize((800,500),Image.Resampling.LANCZOS))
        records.append({'source_stem':original['stem'],'phase':phase,'selected':original['selected'],'source_steps':source_steps[original['stem']],'file':path.name,'sha256':sha(path)})
    sheet.save(out/'phase-sheet.png')
    # 播放間隔只是比較稿速度；不推定原版 BIOS／硬體 wall-clock。
    frames[0].save(out/'title-candidate-local.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=False)
    with Image.open(out/'title-candidate-local.gif')as im:assert im.n_frames==16
    normal=r/'workplace/title-lifecycle-v5';normal_report=json.loads((normal/'source-review.json').read_text())
    selection=Image.new('RGB',(1600,1140),(12,14,22));draw=ImageDraw.Draw(selection);seen=set()
    for sample in normal_report['verified']:
        selected=sample['selected']
        if selected in seen:continue
        seen.add(selected);palette=json.loads((normal/(sample['stem']+'.palette.json')).read_text())
        frame=plate(sample['phase'],selected,palette[51]);x,y=(selected%2)*800,60+(selected//2)*560
        draw.text((x+12,y-40),('單打','雙打','設定','結束')[selected],font=heading,fill='white')
        selection.paste(frame.resize((800,500),Image.Resampling.LANCZOS),(x,y))
    assert seen==set(range(4));selection.save(out/'selection-sheet.png')
    result={'kind':'disposable HD title material-animation and selection comparison; not native integration',
            'transfer_sha256':sha(out/'colour-transfer.json'),'renderer_sha256':sha(Path(__file__)),
            'source_report_sha256':sha(report_path),'normal_report_sha256':sha(normal/'source-review.json'),
            'font_sha256':sha(font_path),'person_sha256':sha(art/'title-person-v1.png'),
            'frames':records,'alpha_preserved_in_all_phases':True,'phase_zero_preserves_original_art':True,
            'static_lower_logo_from_row':static_from,'static_lower_logo_preserved':True,'distinct_phases':8,
            'button_geometry_from_original_table':True,'local_GIF_frames':16,'local_GIF_duration_ms':100,
            'limits':'材質分區是由原圖投影至新畫稿的假說；沒有逐像素材質語意證明。GIF 有色盤量化且速度只供比較，未接原核心、輸入、游標或正式載入，不宣稱原生 HD 或 wall-clock parity',
            'outputs':{name:sha(out/name)for name in('phase-sheet.png','selection-sheet.png','title-candidate-local.gif')}}
    (out/'preview.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in('frames','outputs')},ensure_ascii=False))


if __name__=='__main__':
    main()
