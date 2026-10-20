"""沿既有已驗圖集重用兩組來源，加入嵐的四組新 WIN 畫稿及七十二入口。"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct

from PIL import Image
from prepare_hd_characters import atlas_regions

ROOT=Path('/project')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,default=ROOT/'assets/hd/characters')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists() and a.output.parent.stat().st_uid==1000
    w=ROOT/'workplace';review=json.loads((w/'hd-first-pass-v1/lan-evidence-review-v2.json').read_text());assert review['status']=='READY'
    original=w/'orig/HHWIN.FIG';assert sha(original)=='ac2cac7c82882a7cbf4abc17fb28b4d722dc798cf6e94234117c929f7c371589'
    data=original.read_bytes();base=json.loads((a.base/'manifest.json').read_text());m=copy.deepcopy(base)
    assert m['version']==3 and len(m['poses'])==1411 and len(m['atlases'])==65
    assert not any(x['character']==6 and x.get('source_bank')=='victory' for x in m['sources'])
    refs=json.loads((w/'remaining-victory-source-v1/manifest.json').read_text())
    ref=next(x for x in refs['records'] if x['character']==6);assert len(ref['cells'])==6
    art=w/'hd-first-pass-v1/lan-win-four-v1.png';assert sha(art)=='5b6a313c5443ad0ef373165549b820a5ff0e5f8456cd347f1b2499fc803a5a48'
    im=Image.open(art);assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
    regions=atlas_regions(im,2,2);assert len(regions)==4
    choices={}
    for cell in ref['cells']:
        if cell['ordinal']<2:
            matches=[x for x in m['poses'] if x['character']==6 and not x.get('source_bank') and not x.get('palette_bank') and x['source_sha256']==cell['source_sha256']]
            assert matches and len({(x['atlas'],tuple(x['rect'])) for x in matches})==1
            item=matches[0];choices[cell['source_sha256']]=(item['atlas'],item['rect'])
        else:choices[cell['source_sha256']]=('lan-win.png',regions[cell['ordinal']-2]['rect'])
    m['atlases'].append({'file':'lan-win.png','sha256':sha(art),'width':im.width,'height':im.height})
    m['sources'].append({'character':6,'source_bank':'victory','file':'HHWIN.FIG','sha256':sha(original)})
    for slot in range(72):
        seg,off=struct.unpack_from('<HH',data,0x60+slot*4);at=0x180+seg*16+off
        assert at>=0x180 and at+2<=len(data)
        width,height=data[at:at+2];end=at+2+(width+1)//2*height;assert width and height and end<=len(data)
        digest=hashlib.sha256(data[at:end]).hexdigest();atlas,rect=choices[digest]
        m['poses'].append({'character':6,'source_bank':'victory','slot':slot,'width':width,'height':height,'source_offset':at,'source_sha256':digest,'atlas':atlas,'rect':rect})
    assert m['poses'][:len(base['poses'])]==base['poses'] and len(m['poses'])==1483
    assert sum(x['width']*x['height'] for x in m['atlases'])<=100*1024*1024
    m['evidence'].append('docs/spec/037-lan-victory.md')
    a.output.mkdir()
    for src in a.base.iterdir():
        if src.name=='manifest.json':continue
        assert src.is_file() and not src.is_symlink();shutil.copyfile(src,a.output/src.name)
        assert sha(src)==sha(a.output/src.name)
    shutil.copyfile(art,a.output/'lan-win.png')
    provenance={'kind':'LAN victory registration with exact source reuse','tool_sha256':sha(Path(__file__)),
                'base_manifest_sha256':sha(a.base/'manifest.json'),'source_sha256':sha(original),'image_sha256':sha(art),
                'request':json.loads((w/'hd-first-pass-v1/lan-four-request-v1.json').read_text()),
                'reused_source_ordinals':[0,1],'new_source_ordinals':[2,3,4,5],'regions':regions,
                'limits':'six registered sources; normal runtime samples 0/3/4/5, not complete animation or second player',
                'rights':'user authorized generated HD art and mapping metadata in repository; original references remain local'}
    (a.output/'lan-victory-source.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    (a.output/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'poses':len(m['poses']),'atlases':len(m['atlases']),'sources':len(m['sources']),'manifest_sha256':sha(a.output/'manifest.json')}))

if __name__=='__main__':main()
