"""獨立重組四人特殊光效的原生完整畫格、切換與缺件回退。"""
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
    assert receipt['script_sha256']==sha(root/'remaining_effects_smoke.py')
    reference=(a.background/'reference.idx').read_bytes();events={x['name']:x['state'] for x in receipt['events']}
    character=receipt['character'];assert character in (3,6,9,10)
    assert len(events)==2+3*len(receipt['groups']) and all(not e['core']['training']['modified'] and e['core']['fighters']==[character,4] for e in events.values())
    frames={name:read_frame(root,name+'.png',reference,a.original_root) for name in events}
    assert events['normal-hd']['hd_active'] and events['after-effects']['hd_active']
    results=[]
    labels={3:['cyan-charge','gold-arc'],6:['gold-wave'],9:['cyan-projectile','cyan-rings'],10:['orange-wave']}[character]
    family=receipt.get('family_filter','')
    if family:
        assert family in labels
        labels=[family]
    assert [x['label']for x in receipt['groups']]==labels
    for group in receipt['groups']:
        slots=group['effect_slots'];label=group['label']
        names=[label+'-'+mode for mode in ('hd','original','restored')]
        hd,original,restored=[frames[n] for n in names]
        assert hd[:3]==original[:3]==restored[:3]
        for field in ('core','presentation','settings','assigned'):
            assert events[names[0]][field]==events[names[1]][field]==events[names[2]][field]
        assert all(events[n]['core']['paused'] for n in names)
        assert viewport(original[-1]).tobytes()==original_image(original[0],original[1],original[2]).tobytes()
        assert viewport(hd[-1]).tobytes()==viewport(restored[-1]).tobytes()
        expected=not receipt['expected_original']
        assert [events[n]['hd_active'] for n in names]==[expected,False,expected]
        target=[(i,m,idx,mask)for i,(m,idx,mask)in enumerate(hd[3])if m.get('sprite',{}).get('effect') and m['sprite']['character']==character and m['sprite']['slot'] in slots]
        assert len(target)==1
        ordinal,meta,indices,coverage=target[0]
        proof=verify_sprite(a.original_root,meta['sprite'],indices,coverage)
        data=(a.original_root/f'SFMAN{character+1:02d}.DAT').read_bytes();sprite=meta['sprite']
        expected_palette=[[v*4+v//16 for v in data[0xaf8+i*3:0xaf8+(i+1)*3]]for i in range(16)]
        assert hd[1][sprite['palette_base']:sprite['palette_base']+16]==expected_palette
        changed=0;coloured=0
        for i,owner in enumerate(hd[4]):
            if owner!=ordinal:continue
            y=source_y(i//320,hd[2])
            if y is None:continue
            for dy in range(3):
                for dx in range(3):
                    point=(80+i%320*3+dx,y+dy)
                    rgb=hd[-1].getpixel(point);red,green,blue=rgb
                    changed+=rgb!=original[-1].getpixel(point)
                    coloured+=int((red>blue+25 and green>blue+20)if label.startswith(('gold','orange')) else(blue>red+20 and green>red+8))
        if expected:assert changed>20 and coloured>20,(changed,coloured)
        else:assert viewport(hd[-1]).tobytes()==viewport(original[-1]).tobytes()
        assert events['after-effects']['core']['steps']>events[names[0]]['core']['steps']
        results.append({'label':label,'slots':slots,'colour_family_pixels':coloured,'original_source':proof,'visible_effect_pixels_changed':changed,'mode_restoration_exact':True,'expected_original':receipt['expected_original']})
    assert not any(l.get('sprite',{}).get('effect') for l in events['after-effects']['presentation']['layers'])
    result={'kind':'independent native four-character effect family and old-pack whole-frame fallback','character':character,'effects':results,'captures':len(events),'binary_sha256':receipt['binary_sha256'],'receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in ('verify_character_capture.py','verify_character_geometry.py','hud_reference.py','shadow_reference.py','round_reference.py','display_reference.py','victory_reference.py')},
            'files':{q.name:sha(q)for q in root.iterdir()if q.is_file() and q.name!='comparison.json' and not q.name.startswith('capture.png')},
            'limits':'four first-player Linux effect families and paused switching; 21 source keys tested separately, not all GPU animation; not full animation, every effect, actual audio, Wine/native OS hardware or physical controllers'}
    (root/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('dependencies','files')},ensure_ascii=False))

if __name__=='__main__':main()
