"""沿版本 3 增加正常已驗的鳳凰兩個第二色盤光效鍵，保留全部舊素材。"""
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
    art=ROOT/'workplace/phoenix-effects-art-v1'
    review=json.loads((art/'evidence-review.json').read_text());assert review['status']=='READY'
    for name,want in review['inputs'].items():assert sha(ROOT/name)==want,name
    assert sha(a.base/'manifest.json')==review['base_manifest_sha256']
    base=json.loads((a.base/'manifest.json').read_text());m=copy.deepcopy(base)
    assert m['version']==3 and len(m['poses'])==1483 and len(m['atlases'])==66
    data=(ROOT/'workplace/orig/SFMAN04.DAT').read_bytes()
    assert hashlib.sha256(data).hexdigest()=='2cd299e9c10814ae37bb044c2e3ae7adf940d8b1accd8feffa3844bbfb43356b'
    png=art/'phoenix-effects.png';im=Image.open(png)
    assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
    regions=atlas_regions(im,2,1);assert len(regions)==2
    m['atlases'].append({'file':'phoenix-effects.png','sha256':sha(png),'width':im.width,'height':im.height})
    for slot,region in zip((58,60),regions):
        assert not any(x['character']==3 and x.get('palette_bank',0)==1 and x['slot']==slot for x in m['poses'])
        seg,off=struct.unpack_from('<HH',data,0xb28+slot*4);at=0xc48+seg*16+off
        width,height=data[at:at+2];end=at+2+(width+1)//2*height
        m['poses'].append({'character':3,'palette_bank':1,'slot':slot,'width':width,'height':height,'source_offset':at,'source_sha256':hashlib.sha256(data[at:end]).hexdigest(),'atlas':'phoenix-effects.png','rect':region['rect']})
    m['evidence'].append('docs/spec/039-phoenix-effects.md')
    encoded=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode()
    assert len(encoded)<=512*1024 and sum(x['width']*x['height'] for x in m['atlases'])<=100*1024*1024
    assert m['poses'][:1483]==base['poses'] and len(m['poses'])==1485
    a.output.mkdir()
    for src in a.base.iterdir():
        assert src.is_file() and not src.is_symlink()
        if src.name=='manifest.json':continue
        shutil.copyfile(src,a.output/src.name);assert sha(src)==sha(a.output/src.name)
    shutil.copyfile(png,a.output/'phoenix-effects.png')
    (a.output/'manifest.json').write_bytes(encoded)
    provenance={'kind':'phoenix ordinary attack effects, original generated PNG preserved','tool_sha256':sha(Path(__file__)),'base_manifest_sha256':sha(a.base/'manifest.json'),'source_sha256':hashlib.sha256(data).hexdigest(),'request':json.loads((art/'request.json').read_text()),'image_sha256':sha(png),'evidence_review_sha256':sha(art/'evidence-review.json'),'regions':regions,'registered_effect_slots':[58,60],'limits':'two ordinary effect sources; not all specials, all animations or alternate palettes','rights':'user authorized generated HD assets in repository; original references and CPU sidecars local only'}
    (a.output/'phoenix-effects-source.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'poses':len(m['poses']),'atlases':len(m['atlases']),'manifest_bytes':len(encoded),'manifest_sha256':sha(a.output/'manifest.json')}))

if __name__=='__main__':main()
