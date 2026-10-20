"""獨立核對原生場邊雙向翻轉、原檔 CPU 層及新舊程式的切換。"""
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
    assert receipt['script_sha256']==sha(root/'edge_clipping_smoke.py')
    states={x['name']:x['state']for x in receipt['events']};names=['edge-hd','edge-original','edge-restored']
    assert set(states)=={'normal-hd','after-edge',*names}
    assert all(not s['core']['training']['modified'] and s['core']['fighters']==[receipt['player0'],4] for s in states.values())
    reference=(a.background/'reference.idx').read_bytes()
    frames={name:read_frame(root,name+'.png',reference,a.original_root)for name in states}
    hd,original,restored=[frames[n]for n in names]
    assert hd[:3]==original[:3]==restored[:3]
    for field in ('core','presentation','settings','assigned'):
        assert states[names[0]][field]==states[names[1]][field]==states[names[2]][field]
    assert all(states[n]['core']['paused']for n in names)
    assert viewport(original[-1]).tobytes()==original_image(original[0],original[1],original[2]).tobytes()
    assert viewport(hd[-1]).tobytes()==viewport(restored[-1]).tobytes()
    enabled=not receipt['expected_original']
    assert [states[n]['hd_active']for n in names]==[enabled,False,enabled]
    if not enabled:
        assert '翻轉或裁切未吻合' in states[names[0]]['hd_reason']
        assert viewport(hd[-1]).tobytes()==viewport(original[-1]).tobytes()
    target=[(i,m,idx,mask)for i,(m,idx,mask)in enumerate(hd[3])if m.get('sprite') and m['sprite']['flags']&192==192 and m['sprite']['right_clip']>0]
    assert len(target)==1
    ordinal,meta,indices,coverage=target[0];proof=verify_sprite(a.original_root,meta['sprite'],indices,coverage)
    changed=0
    for i,owner in enumerate(hd[4]):
        if owner!=ordinal:continue
        y=source_y(i//320,hd[2])
        if y is None:continue
        for dy in range(3):
            for dx in range(3):
                point=(80+i%320*3+dx,y+dy)
                changed+=hd[-1].getpixel(point)!=original[-1].getpixel(point)
    if enabled:assert changed>100
    assert states['normal-hd']['hd_active'] and states['after-edge']['hd_active']
    assert states['after-edge']['core']['steps']>states[names[0]]['core']['steps']
    assert states['after-edge']['core']['key_values'][0]==0
    result={'kind':'independent normal native clipped mirrored throw and restoration','source':proof,'visible_character_pixels_changed':changed,'expected_original':receipt['expected_original'],'same_original_state':True,'restored_HD_identical':True,'continued_after_release':True,'captures':len(states),'version':states[names[0]]['version'],'binary_sha256':receipt['binary_sha256'],'receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in ('verify_character_capture.py','verify_character_geometry.py','hud_reference.py','shadow_reference.py','round_reference.py','display_reference.py','victory_reference.py')},
            'files':{q.name:sha(q)for q in root.iterdir()if q.is_file()and q.name!='comparison.json'and not q.name.startswith('capture.png')},
            'limits':'requested Linux normal edge sample and paused switching; no every clipping combination, all animations, alternate palettes, Wine/native hardware or physical controller claim'}
    (root/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('dependencies','files')},ensure_ascii=False))

if __name__=='__main__':main()
