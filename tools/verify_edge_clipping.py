"""以原 i64 bytes 與正常 CPU 層，獨立審查雙向翻轉的場邊來源起點。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def predict(s,data,mirror_source_pair):
    seg,off=struct.unpack_from('<HH',data,0xb28+s['slot']*4);at=0xc48+seg*16+off
    width,height=data[at:at+2];stride=(width+1)//2;packed=data[at+2:at+2+stride*height]
    assert (width,height)==(s['width'],s['height'])
    assert hashlib.sha256(data[at:at+2+len(packed)]).hexdigest()==s['source_sha256']
    left=(s['left_clip']+1)//2;right=(s['right_clip']+1)//2
    pairs=stride-left-right;rows=height-s['top_clip']
    startx=max(s['x'],0)+width-s['left_clip']-s['right_clip'];starty=max(s['y'],0)+rows
    indices=bytearray(64000);mask=bytearray(64000)
    for y in range(rows):
        for p in range(pairs):
            value=packed[y*stride+mirror_source_pair+p]
            for nibble in range(2):
                v=value>>4 if nibble==0 else value&15;x=startx-p*2-nibble;dest_y=starty-y
                if v and 0<=x<320 and 0<=dest_y<200:indices[dest_y*320+x]=v|s['palette_base'];mask[dest_y*320+x]=1
    origin=(startx+mirror_source_pair*2+1-width,starty+1-height)
    clip=(max(0,startx-pairs*2+1),max(0,max(s['y'],0)+1),min(320,startx+1),min(200,starty+1))
    return indices,mask,origin,clip,packed,at

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--research',type=Path,required=True);p.add_argument('--original-root',type=Path,default=Path('/orig'));a=p.parse_args()
    root=Path('/project');source=a.original_root/'SFMAN05.DAT';assert sha(source)=='b5b77d590420b92db2d265aa89483de70d58193caf442fd41eba338eb111d653'
    ida=json.loads((a.research/'ida.json').read_text());assert ida['tool']=='IDA 9.4' and ida['input_sha256']==sha(a.original_root/'SF.EXE')
    old=json.loads((root/'workplace/ida-hd-draw-v2.json').read_text())
    for f in ida['functions']:
        prior=next(x for x in old['functions']if x['original_name']==f['original_name'])
        assert [(x['ida_linear'],x['bytes'],x['operand'])for x in f['instructions']]==[(x['ida_linear'],x['bytes'],x['operand'])for x in prior['instructions']]
        assert len(f['incoming'])==6
    instructions={x['ida_linear']:x for f in ida['functions']for x in f['instructions']}
    assert [instructions[x]['bytes']for x in ('0x14729','0x1472b','0x1472d','0x1472f')]==['8ac3','8adf','32ff','03f3']
    assert [instructions[x]['bytes']for x in ('0x14854','0x14856','0x14858')]==['8ac7','32ff','03f3']
    cases=json.loads((root/'workplace/hd-motion-coverage-v1/source-comparison.json').read_text())['unresolved_geometry_samples'];proofs=[]
    for case in cases:
        directory=root/'workplace/hd-motion-coverage-v1'/f'character-{case["character"]:02d}';stem=case['sample'];frame=json.loads((directory/(stem+'.frame.json')).read_text())
        s=case['sprite'];assert s['flags']&192==192 and s['left_clip']==0 and s['right_clip']in (1,9)
        target=next(i for i,l in enumerate(frame['layers'])if l.get('sprite')==s)
        actual=(directory/f'{stem}.layer-{target:02d}.idx').read_bytes();coverage=(directory/f'{stem}.layer-{target:02d}.mask').read_bytes()
        result=predict(s,source.read_bytes(),(s['left_clip']+1)//2);indices,mask,origin,clip,packed,at=result
        assert mask==coverage and all(not m or actual[i]==indices[i]for i,m in enumerate(mask))
        width,height=s['width'],s['height'];transformed=bytearray(64000);transformed_mask=bytearray(64000)
        for y in range(height):
            for x in range(width):
                b=packed[y*((width+1)//2)+x//2];v=b>>4 if x%2==0 else b&15;dx=origin[0]+width-1-x;dy=origin[1]+height-1-y
                if v and clip[0]<=dx<clip[2] and clip[1]<=dy<clip[3]:transformed[dy*320+dx]=v|s['palette_base'];transformed_mask[dy*320+dx]=1
        assert transformed==indices and transformed_mask==mask
        old_indices,old_mask,*_=predict(s,source.read_bytes(),(s['right_clip']+1)//2)
        mismatches=sum(old_mask[i]!=coverage[i]or coverage[i]and old_indices[i]!=actual[i]for i in range(64000));assert mismatches>0
        proofs.append({'character':case['character'],'sample':stem,'sprite':s,'source_file_offset':at,'written_pixels':sum(mask),'old_mismatched_pixels':mismatches,'origin':origin,'clip':clip,'CPU_coverage_and_pixels_match':True,'full_image_transform_match':True,'frame_sha256':sha(directory/(stem+'.frame.json'))})
    report={'status':'READY','tool':'independent Python source replay and IDA 9.4 database export','source_sha256':sha(source),'EXE_sha256':sha(a.original_root/'SF.EXE'),'ida_export_sha256':sha(a.research/'ida.json'),'source_database_sha256':sha(root/'workplace/sf-hd-draw-v2.i64'),'verifier_sha256':sha(Path(__file__)),'cases':proofs,'limits':'four saved normal samples, two Frank sources, right clip 1/9; no all-clipping, alternate palette, native GPU or full-animation claim'}
    (a.research/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'READY','cases':[{k:v for k,v in x.items()if k!='sprite'}for x in proofs]},ensure_ascii=False))

if __name__=='__main__':main()
