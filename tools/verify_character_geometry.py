"""從正常擊倒原檔及 CPU 圖層，獨立核對雙向翻轉與頂部裁切。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from verify_character_capture import read_frame

ROOT=Path('/project')
CASES=[('c0','hd-first-pass-v1/native-lan-victory-v2','transition-0.png'),
       ('top','hd-first-pass-v1/native-kim-v1','knockout-0.png')]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify_sprite(original,sprite,indices,coverage):
    s=sprite;data=(original/f'SFMAN{s["character"]+1:02d}.DAT').read_bytes()
    segment,offset=struct.unpack_from('<HH',data,0xb28+s['slot']*4);at=0xc48+segment*16+offset
    width,height=data[at:at+2];stride=(width+1)//2;packed=data[at+2:at+2+stride*height]
    assert (width,height)==(s['width'],s['height']) and hashlib.sha256(data[at:at+2+len(packed)]).hexdigest()==s['source_sha256']
    left=(s['left_clip']+1)//2;right=(s['right_clip']+1)//2;top=s['top_clip'];rows=height-top;pairs=stride-left-right
    flipx=bool(s['flags']&64);flipy=bool(s['flags']&128)
    # 以已驗 blit 入口暫存器契約推算 CPU 目的位址，不呼叫 production Placement。
    startx=max(s['x'],0)+(width-s['left_clip']-s['right_clip'] if flipx else 0)
    starty=max(s['y'],0)+(rows if flipy else 0)
    expected=bytearray(64000);mask=bytearray(64000)
    for row in range(rows):
        source_row=row if flipy else row+top;source_pair=right if flipx and not flipy else left
        for pair in range(pairs):
            value=packed[source_row*stride+source_pair+pair]
            for nibble in range(2):
                v=value>>4 if nibble==0 else value&15
                x=startx+(-1 if flipx else 1)*(pair*2+nibble)
                y=starty+(-row if flipy else row)
                if v and 0<=x<320 and 0<=y<200:expected[y*320+x]=v|s['palette_base'];mask[y*320+x]=1
    assert mask==coverage,'CPU coverage differs from source blit prediction'
    assert all(not mask[i] or indices[i]==expected[i] for i in range(64000)),'CPU colours differ from source blit prediction'
    # 另驗完整來源矩形的連續影像翻轉與裁切，作為 HD 定位的獨立對照。
    originx=max(s['x'],0)-left*2;originy=max(s['y'],0)-top
    clip=[max(s['x'],0),max(s['y'],0),max(s['x'],0)+pairs*2,max(s['y'],0)+rows]
    if flipx:
        source_pair=left if flipy else right
        originx=startx+source_pair*2+1-width;clip[0]=startx-pairs*2+1;clip[2]=startx+1
    if flipy:
        originy=max(s['y'],0)+rows+1-height;clip[1]=max(s['y'],0)+1;clip[3]=max(s['y'],0)+rows+1
    transformed=bytearray(64000);transformed_mask=bytearray(64000)
    for row in range(height):
        for column in range(width):
            value=packed[row*stride+column//2];v=value>>4 if column%2==0 else value&15
            x=originx+(width-1-column if flipx else column);y=originy+(height-1-row if flipy else row)
            if v and max(0,clip[0])<=x<min(320,clip[2]) and max(0,clip[1])<=y<min(200,clip[3]):
                transformed[y*320+x]=v|s['palette_base'];transformed_mask[y*320+x]=1
    assert transformed_mask==mask and transformed==expected,'image transform differs from original blit'
    return {'sprite':s,'source_file':f'SFMAN{s["character"]+1:02d}.DAT','source_file_sha256':hashlib.sha256(data).hexdigest(),
            'source_file_offset':at,'written_pixels':sum(mask),'origin':[originx,originy],'clip':clip,'CPU_coverage_and_pixels_match':True,'image_transform_matches':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--original-root',type=Path,default=Path('/orig'));a=p.parse_args()
    a.output.mkdir(exist_ok=False)
    reference=(ROOT/'workplace/hd-rooftop-study/reference.idx').read_bytes();results=[]
    for kind,folder,name in CASES:
        directory=ROOT/'workplace'/folder;receipt=json.loads((directory/'receipt.json').read_text());assert receipt['scope']=='first-victory-message'
        assert receipt['inputs']=='X11 keyboard/mouse only; no memory, health, winner, position or RNG injection'
        frame=read_frame(directory,name,reference,a.original_root)
        assert not frame[2]['training']['modified']
        target=[(m,indices,mask) for m,indices,mask in frame[3] if m.get('sprite') and not m['sprite'].get('effect') and
                (m['sprite']['flags']&192==192 if kind=='c0' else m['sprite']['top_clip']>0)]
        assert len(target)==1
        meta,indices,mask=target[0];result=verify_sprite(a.original_root,meta['sprite'],indices,mask)
        result.update(kind=kind,capture=folder+'/'+name,receipt_sha256=digest(directory/'receipt.json'),frame_sha256=digest(directory/(name+'.frame.json')),
                      screenshot_sha256=digest(directory/name),old_HD_active=json.loads((directory/(name+'.capture.json')).read_text())['hd_active'])
        assert result['old_HD_active'] is False;results.append(result)
    result={'kind':'independent normal original character geometry review','cases':results,'source_EXE_sha256':digest(a.original_root/'SF.EXE'),
            'tool_sha256':digest(Path(__file__)),'original_CPU_static_reference':'workplace/ida-hd-draw-v2.json, IDA MZ linear sub_14665/sub_146E8/sub_1477E/sub_1480A; runtime locations separately in 008',
            'limits':'normal first-player Kim/Lan knockout against Frank, P2 source 27/28; not all clip combinations, palettes or complete HD'}
    (a.output/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
