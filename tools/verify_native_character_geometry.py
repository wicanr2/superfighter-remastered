"""獨立核對原生新幾何、CPU 角色層及原貌／HD 同狀態切換。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame,original_image,viewport,source_y
from verify_character_geometry import verify_sprite

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--original-root',type=Path,required=True);p.add_argument('--background',type=Path,required=True);a=p.parse_args()
    root=a.output;receipt=json.loads((root/'receipt.json').read_text());geometry=receipt['geometry']
    assert receipt['scope']=='first-victory-message' and geometry['captured'] and receipt['script_sha256']==sha(root/'desktop_match_smoke.py')
    events=geometry['events'];names=['geometry-hd','geometry-original','geometry-restored'];assert [e['name'] for e in events]==names
    reference=(a.background/'reference.idx').read_bytes();frames=[read_frame(root,n+'.png',reference,a.original_root) for n in names]
    assert frames[0][:3]==frames[1][:3]==frames[2][:3]
    for field in ('core','presentation','settings','assigned'):
        assert events[0]['state'][field]==events[1]['state'][field]==events[2]['state'][field],field
    assert all(e['state']['core']['paused'] for e in events)
    assert [e['state']['hd_active'] for e in events]==[True,False,True]
    assert viewport(frames[1][-1]).tobytes()==original_image(frames[1][0],frames[1][1],frames[1][2]).tobytes()
    assert viewport(frames[0][-1]).tobytes()==viewport(frames[2][-1]).tobytes()
    kind=geometry['kind'];subjects=[];changed=0
    for ordinal,(meta,indices,coverage) in enumerate(frames[0][3]):
        s=meta.get('sprite')
        if not s or s.get('effect') or not (s['flags']&192==192 if kind=='c0' else s['top_clip']>0):continue
        subjects.append(verify_sprite(a.original_root,s,indices,coverage))
        for i,owner in enumerate(frames[0][4]):
            if owner!=ordinal:continue
            y=source_y(i//320,frames[0][2])
            if y is None:continue
            for dy in range(3):
                for dx in range(3):
                    point=(80+(i%320)*3+dx,y+dy)
                    changed+=frames[0][-1].getpixel(point)!=frames[1][-1].getpixel(point)
    assert subjects and changed>100,(kind,changed)
    final=next(e['state'] for e in receipt['events'] if e['name']=='after-victory')
    assert final['core']['steps']>events[0]['state']['core']['steps'] and not final['presentation'].get('victory')
    result={'kind':'independent native HD character geometry and paused switch','geometry':kind,'subjects':subjects,'changed_character_pixels':changed,
            'same_original_state':True,'restored_HD_identical':True,'ordinary_next_round_after_resume':True,'version':events[0]['state'].get('version'),
            'binary_sha256':receipt['binary_sha256'],'verifier_sha256':sha(Path(__file__)),'source_verifier_sha256':sha(Path(__file__).with_name('verify_character_geometry.py')),
            'dependencies':{name:sha(Path(__file__).with_name(name)) for name in ('verify_character_capture.py','hud_reference.py','shadow_reference.py','round_reference.py','display_reference.py','victory_reference.py')},
            'files':{p.name:sha(p) for p in root.iterdir() if p.is_file() and (p.name=='receipt.json' or p.name.startswith('geometry-'))},
            'limits':'requested Linux normal knockout samples; no all animations, all palettes, Wine/native hardware or every clipping combination claim'}
    (root/'geometry-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))

if __name__=='__main__':main()
