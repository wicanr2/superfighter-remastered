"""獨立重組鳳凰拳腳光效的原生完整畫格、切換與缺件回退。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame,original_image,viewport,source_y
from verify_character_geometry import verify_sprite

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--original-root',type=Path,default=Path('/orig'))
    p.add_argument('--background',type=Path,default=Path('/project/workplace/hd-rooftop-study'))
    a=p.parse_args();root=a.output;receipt=json.loads((root/'receipt.json').read_text())
    assert receipt['script_sha256']==sha(root/'phoenix_effects_smoke.py')
    reference=(a.background/'reference.idx').read_bytes();events={x['name']:x['state'] for x in receipt['events']}
    assert len(events)==8 and all(not e['core']['training']['modified'] and e['core']['fighters']==[3,4] for e in events.values())
    frames={name:read_frame(root,name+'.png',reference,a.original_root) for name in events}
    assert events['normal-hd']['hd_active'] and events['after-effects']['hd_active']
    results=[]
    for slot in (60,58):
        names=[f'effect-{slot}-{mode}' for mode in ('hd','original','restored')]
        hd,original,restored=[frames[n] for n in names]
        assert hd[:3]==original[:3]==restored[:3]
        for field in ('core','presentation','settings','assigned'):
            assert events[names[0]][field]==events[names[1]][field]==events[names[2]][field]
        assert all(events[n]['core']['paused'] for n in names)
        assert viewport(original[-1]).tobytes()==original_image(original[0],original[1],original[2]).tobytes()
        assert viewport(hd[-1]).tobytes()==viewport(restored[-1]).tobytes()
        expected=not receipt['expected_original']
        assert [events[n]['hd_active'] for n in names]==[expected,False,expected]
        target=[(i,m,idx,mask)for i,(m,idx,mask)in enumerate(hd[3])if m.get('sprite',{}).get('effect') and m['sprite']['character']==3 and m['sprite']['slot']==slot]
        assert len(target)==1
        ordinal,meta,indices,coverage=target[0]
        proof=verify_sprite(a.original_root,meta['sprite'],indices,coverage)
        changed=0
        for i,owner in enumerate(hd[4]):
            if owner!=ordinal:continue
            y=source_y(i//320,hd[2])
            if y is None:continue
            for dy in range(3):
                for dx in range(3):
                    point=(80+i%320*3+dx,y+dy)
                    changed+=hd[-1].getpixel(point)!=original[-1].getpixel(point)
        if expected:assert changed>20
        else:assert viewport(hd[-1]).tobytes()==viewport(original[-1]).tobytes()
        assert events['after-effects']['core']['steps']>events[names[0]]['core']['steps']
        results.append({'slot':slot,'original_source':proof,'visible_effect_pixels_changed':changed,'mode_restoration_exact':True,'expected_original':receipt['expected_original']})
    assert not any(l.get('sprite',{}).get('effect') for l in events['after-effects']['presentation']['layers'])
    result={'kind':'independent native ordinary Phoenix effects and old-pack whole-frame fallback','effects':results,'captures':8,'binary_sha256':receipt['binary_sha256'],'receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in ('verify_character_capture.py','verify_character_geometry.py','hud_reference.py','shadow_reference.py','round_reference.py','display_reference.py','victory_reference.py')},
            'files':{q.name:sha(q)for q in root.iterdir()if q.is_file() and q.name!='comparison.json' and not q.name.startswith('capture.png')},
            'limits':'two normal first-player Linux effects and paused switching only; not full animation, every effect, actual audio, Wine/native OS hardware or physical controllers'}
    (root/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('dependencies','files')},ensure_ascii=False))

if __name__=='__main__':main()
