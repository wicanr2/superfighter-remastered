"""獨立核對同角原生主色盤、雙色 HD、同狀態切換及舊程式回退。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame,original_image,viewport,source_y
from verify_victory_capture import check_sprite_sources

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--victory',action='store_true')
    p.add_argument('--original-root',type=Path,default=Path('/orig'))
    p.add_argument('--background',type=Path,default=Path('/project/workplace/hd-rooftop-study'))
    a=p.parse_args();root=a.output;receipt=json.loads((root/'receipt.json').read_text())
    if a.victory:
        assert receipt['scope']=='first-victory-message' and receipt['attacker']==1 and receipt['player0']==4
        assert receipt['script_sha256']==sha(root/'desktop_match_smoke.py')
        groups=['victory'];last='after-victory';expected_original=False
    else:
        assert receipt['script_sha256']==sha(root/'duplicate_palette_smoke.py')
        groups=['idle','walk'];last='after-release';expected_original=receipt['expected_original']
    events={x['name']:x['state']for x in receipt['events']}
    reference=(a.background/'reference.idx').read_bytes()
    frames={name:read_frame(root,name+'.png',reference,a.original_root)for name in events}
    source=(a.original_root/'SFMAN05.DAT').read_bytes();col=(a.original_root/'MAN.COL').read_bytes()
    assert sha(a.original_root/'MAN.COL')=='7153214bf444684179b5296ad1c4dfc874385cbf6e2d5e0c215c13e711749ce5'
    base=[[v*4+v//16 for v in source[0xac8+i*3:0xac8+(i+1)*3]]for i in range(16)]
    alt=[[v*4+v//16 for v in col[192+i*3:192+(i+1)*3]]for i in range(16)]
    for name,f in frames.items():
        assert events[name]['core']['fighters']==[4,4] and not events[name]['core']['training']['modified']
        assert f[1][192:208]==base and f[1][224:240]==alt
        check_sprite_sources(a.original_root,f[2])
    checks=[]
    for prefix in groups:
        names=[prefix+'-'+mode for mode in ('hd','original','restored')]
        hd,original,restored=[frames[n]for n in names]
        assert hd[:3]==original[:3]==restored[:3]
        for field in ('core','presentation','settings','assigned'):
            assert events[names[0]][field]==events[names[1]][field]==events[names[2]][field]
        assert all(events[n]['core']['paused']for n in names)
        assert [events[n]['hd_active']for n in names]==[not expected_original,False,not expected_original]
        assert viewport(original[-1]).tobytes()==original_image(original[0],original[1],original[2]).tobytes()
        assert viewport(hd[-1]).tobytes()==viewport(restored[-1]).tobytes()
        colour_counts=[0,0]
        for ordinal,(meta,indices,coverage)in enumerate(hd[3]):
            sprite=meta.get('sprite')
            if not sprite or sprite.get('effect'):continue
            player=sprite['player'];start=sprite['palette_base']
            for i,owner in enumerate(hd[4]):
                if owner!=ordinal or not coverage[i]or not 7<=indices[i]-start<=10:continue
                y=source_y(i//320,hd[2])
                if y is None:continue
                for dy in range(3):
                    for dx in range(3):
                        red,green,blue=hd[-1].getpixel((80+i%320*3+dx,y+dy))
                        colour_counts[player]+=int((blue>=green+10 and blue>red+20)if player==0 else(green>blue+20 and green>red+20))
        assert all(n>200 for n in colour_counts),colour_counts
        if expected_original:assert viewport(hd[-1]).tobytes()==viewport(original[-1]).tobytes()
        checks.append({'phase':prefix,'blue_first_player_clothing_pixels':colour_counts[0],'green_second_player_clothing_pixels':colour_counts[1],'restored_HD_identical':True,'same_original_state':True,'expected_original':expected_original})
    assert events[last]['core']['steps']>events[groups[0]+'-hd']['core']['steps']
    assert events[last]['hd_active']!=expected_original
    if not a.victory:
        assert events[last]['core']['key_values']==[0,0]
        assert events['walk-hd']['presentation']['actors'][1]['x']<events['idle-hd']['presentation']['actors'][1]['x']
    else:
        assert not events[last]['presentation'].get('victory')
        assert events[last]['presentation']['hud']['state']['display_wins']==[0,1]
    result={'kind':'independent native duplicate Frank source palettes and HD colour separation','captures':len(events),'checks':checks,'victory':a.victory,'binary_sha256':receipt['binary_sha256'],'receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in ('verify_character_capture.py','verify_victory_capture.py','hud_reference.py','shadow_reference.py','round_reference.py','display_reference.py','victory_reference.py')},
            'files':{q.name:sha(q)for q in root.iterdir()if q.is_file()and q.name not in ('duplicate-comparison.json','animation-comparison.json')and not q.name.startswith('capture.png')},
            'limits':'exact original palette identities and sampled Linux colour separation; RGB transfer is HD approximation, not material segmentation or original-pixel parity; other native scenes and all animation unproven'}
    (root/'duplicate-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('dependencies','files')},ensure_ascii=False))

if __name__=='__main__':main()
