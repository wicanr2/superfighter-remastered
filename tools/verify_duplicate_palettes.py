"""從原檔獨立重組十一種同角色雙打的色盤、角色及背景 CPU 層。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_geometry import verify_sprite
from verify_stage_sources import decode

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--original-root',type=Path,default=Path('/orig'))
    a=p.parse_args();r=Path('/project');root=a.output;receipt=json.loads((root/'receipt.json').read_text())
    assert receipt['script_sha256']==sha(root/'duplicate_palette_receipt.go')
    for name,want in receipt['inputs'].items():assert sha(r/name)==want,name
    col=(a.original_root/'MAN.COL').read_bytes();assert sha(a.original_root/'MAN.COL')==receipt['MAN_COL_sha256']
    assert len(col)==768 and max(col)<=63
    inventory={x['name']:x['sha256']for x in json.loads((r/'workplace/source-manifest.json').read_text())['files']}
    backgrounds={}
    for name,want in inventory.items():
        if not name.startswith('I')or not name.endswith('.XGB'):continue
        path=a.original_root/name;assert sha(path)==want
        pixels,palette=decode(path.read_bytes());backgrounds[digest(pixels)]=(name,pixels,palette)
    assert len(backgrounds)==11 and len(receipt['cases'])==11
    proofs=[];sprites=frames=0
    for character,case in enumerate(receipt['cases']):
        assert case['character']==character and case['MAN_COL_file_offset']==character*48
        directory=root/f'character-{character:02d}';assert json.loads((directory/'receipt.json').read_text())==case
        source=a.original_root/f'SFMAN{character+1:02d}.DAT';data=source.read_bytes()
        assert sha(source)==case['source_DAT_sha256']==inventory[source.name]
        base=[[v*4+v//16 for v in data[0xac8+i*3:0xac8+(i+1)*3]]for i in range(16)]
        alt=[[v*4+v//16 for v in col[character*48+i*3:character*48+(i+1)*3]]for i in range(16)]
        assert digest(json.dumps(base,separators=(',',':')).encode())==case['base_palette_sha256']
        assert digest(json.dumps(alt,separators=(',',':')).encode())==case['alternate_palette_sha256']
        assert base!=alt
        assert [s['name']for s in case['samples']]==['idle','walk']
        last_serial=last_steps=0
        for sample in case['samples']:
            stem=sample['name'];f=json.loads((directory/(stem+'.frame.json')).read_text())
            colors=json.loads((directory/(stem+'.palette.json')).read_text())
            assert colors[192:208]==base and colors[224:240]==alt
            assert f['serial']==sample['serial']>last_serial and f['steps']==sample['steps']>last_steps
            last_serial,last_steps=f['serial'],f['steps']
            assert f['layers_complete'] and not f['training']['modified'] and f.get('retained_background_rows',0)==0
            background,pixels,palette=backgrounds[f['background_sha256']]
            assert bytes(v for c in colors[:128]for v in c)==palette
            combined=bytearray(64000);players=[]
            for i,l in enumerate(f['layers']):
                indices=(directory/f'{stem}.layer-{i:02d}.idx').read_bytes();mask=(directory/f'{stem}.layer-{i:02d}.mask').read_bytes()
                assert len(indices)==len(mask)==64000 and set(mask)<={0,1}
                if i==0:
                    assert l['background'] and all(mask)
                    expected=b''.join(pixels[y*480+f['camera_x']:y*480+f['camera_x']+320]for y in range(200))
                    assert indices==expected
                for pos,covered in enumerate(mask):
                    if covered:combined[pos]=indices[pos]
                if 'sprite'in l:
                    s=l['sprite'];assert not s.get('effect')and s['character']==character
                    proof=verify_sprite(a.original_root,s,indices,mask);assert proof['CPU_coverage_and_pixels_match']
                    players.append(s['player']);sprites+=1
            assert sorted(players)==[0,1] and combined==(directory/(stem+'.idx')).read_bytes()
            assert sample['first_matches_DAT'] and sample['second_matches_MAN_COL'] and sample['palettes_distinct']
            frames+=1
        proofs.append({'character':character,'source':source.name,'MAN_COL_file_offset':character*48,'changed_palette_entries':sum(x!=y for x,y in zip(base,alt)),'source_DAT_sha256':sha(source),'samples':2,'first_palette_source_confirmed':True,'second_palette_source_confirmed':True,'complete_CPU_layers_confirmed':True})
    result={'kind':'independent normal duplicate palette and original layer source comparison','cases':proofs,'frames':frames,'sprites':sprites,'source_receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),
            'dependencies':{name:sha(Path(__file__).with_name(name))for name in ('verify_character_geometry.py','verify_stage_sources.py')},
            'limits':'normal eleven duplicates idle/walk and exact source palette tables; runtime loader branch and HD colour transfer need separate proof; not full animations or native HD integration'}
    (root/'source-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('dependencies','cases')},ensure_ascii=False))

if __name__=='__main__':main()
