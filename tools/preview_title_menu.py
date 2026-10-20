"""以未修改的候選 PNG 呈現主選單比較稿，不連接遊戲或原輸入。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    root=Path('/project');art=root/'assets/hd/candidates'
    font=root/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    person=Image.open(art/'title-person-v1.png').convert('RGBA')
    logo=Image.open(art/'title-logo-v1.png').convert('RGBA')
    # 只改繪製矩形，不另存改過的原 PNG。
    bounds=logo.getchannel('A').point(lambda value:255 if value>=16 else 0).getbbox()
    preview=Image.new('RGBA',(1600,1000),(0,0,0,255))
    preview.alpha_composite(person.resize((1600,1000),Image.Resampling.LANCZOS))
    logo_rect=(18*5,96*5,303*5,165*5)
    preview.alpha_composite(logo.crop(bounds).resize((logo_rect[2]-logo_rect[0],logo_rect[3]-logo_rect[1]),Image.Resampling.LANCZOS),logo_rect[:2])
    draw=ImageDraw.Draw(preview);label_font=ImageFont.truetype(str(font),48)
    button_rects=[]
    for i,label in enumerate(('單　打','雙　打','設　定','結　束')):
        left=(27+i*70)*5;top=174*5;right=left+54*5;bottom=189*5
        button_rects.append([left,top,right,bottom])
        draw.rectangle((left,top,right-1,bottom-1),fill=(79,57,102),outline=(187,155,216),width=3)
        draw.line((left+4,bottom-5,right-5,bottom-5),fill=(42,22,65),width=3)
        if i==0:draw.rectangle((left,top,right-1,bottom-1),outline=(251,235,170),width=4)
        box=draw.textbbox((0,0),label,font=label_font)
        x=(left+right-(box[2]-box[0]))//2-box[0];y=(top+bottom-(box[3]-box[1]))//2-box[1]
        assert left<=x+box[0]<x+box[2]<=right and top<=y+box[1]<y+box[3]<=bottom
        draw.text((x,y),label,font=label_font,fill=(250,239,255))
    preview.convert('RGB').save(a.output/'title-menu-candidate.png')
    original=Image.open(root/'workplace/title-menu-source-v2/original-title-reference.png').convert('RGB')
    compare=Image.new('RGB',(3200,1080),(12,14,22));d=ImageDraw.Draw(compare)
    d.text((30,15),'原版正常標題',font=ImageFont.truetype(str(font),36),fill='white')
    d.text((1630,15),'HD 候選，尚未接入；未重現原色盤動畫',font=ImageFont.truetype(str(font),36),fill='white')
    compare.paste(original.resize((1600,1000),Image.Resampling.NEAREST),(0,80));compare.paste(preview.convert('RGB'),(1600,80));compare.save(a.output/'private-comparison.png')
    receipt={'kind':'disposable static title/menu layout; not native capture or approved layout','inputs':{str(p.relative_to(root)):sha(p)for p in(art/'title-person-v1.png',art/'title-logo-v1.png',font,Path(__file__))},'person_canvas':[1600,1000],'logo_alpha_threshold_for_draw_bounds':16,'logo_draw_bounds':bounds,'logo_destination':logo_rect,'button_rects':button_rects,'font_size':48,'limits':'候選人物及字標按原布局矩形繪製，比例有調整；未接核心、游標、按鈕事件、設定或原色盤動畫','outputs':{p.name:sha(p)for p in a.output.iterdir()if p.is_file()}}
    (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':
    main()
