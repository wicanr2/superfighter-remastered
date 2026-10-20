"""獨立核對特殊動作普通輸入、第二色盤及完整 CPU 層，輸出私有原圖參考。"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image, ImageDraw

from verify_character_geometry import verify_sprite

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def key(s):
    return f'{s["character"]}:{s.get("source_bank","normal")}:{int(s.get("effect",False))}:{s["slot"]}'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--characters',type=Path,default=Path('/project/assets/hd/characters'))
    p.add_argument('--original-root',type=Path,default=Path('/orig'))
    a=p.parse_args();root=a.output
    receipt=json.loads((root/'receipt.json').read_text())
    assert receipt['script_sha256']==sha(root/'special_effects_receipt.go')
    assert receipt['sequence_sha256']==sha(root/'sequence.json')
    assert receipt['character_manifest_sha256']==sha(a.characters/'manifest.json')
    for name,want in receipt['inputs'].items():
        assert sha(Path('/project')/name)==want,name
    manifest=json.loads((a.characters/'manifest.json').read_text())
    available={f'{s["character"]}:{s.get("source_bank","normal")}:{s.get("palette_bank",0)}:{s["slot"]}' for s in manifest['poses']}
    inputs=json.loads(Path('/project/workplace/source-manifest.json').read_text())
    source_files={x['name']:x['sha256'] for x in inputs['files']}
    sources={}
    for character in range(11):
        path=a.original_root/f'SFMAN{character+1:02d}.DAT'
        assert sha(path)==source_files[path.name]
        sources[character]=path.read_bytes()
    count=0;summary=[];effect_evidence=[];geometry_mismatches=[]
    expected=list(range(11)) if receipt.get('requested_character',-1)==-1 else [receipt['requested_character']]
    assert [x['character'] for x in receipt['cases']]==expected
    for row in receipt['cases']:
        character=row['character'];directory=root/f'character-{character:02d}'
        case=json.loads((directory/'receipt.json').read_text())
        assert {k:v for k,v in case.items() if k!='trace'}==row
        assert case['opponent']==4 and not case['training_modified']
        observed=set();missing=set();reasons=Counter();last_serial=last_steps=0
        trace=case['trace'];by_serial={}
        phase_names=[x['name'] for x in receipt['phases']]
        assert len(phase_names)==len(set(phase_names))
        observed_phases={x['phase'] for x in trace}
        assert observed_phases<=set(phase_names)
        assert [phase_names.index(x['phase'])for x in trace]==sorted(phase_names.index(x['phase'])for x in trace)
        assert phase_names[0] in observed_phases and phase_names[-1] in observed_phases
        for event in trace:
            assert event['serial']>last_serial and event['steps']>last_steps
            last_serial,last_steps=event['serial'],event['steps'];by_serial[last_serial]=event
            assert sorted(s['player'] for s in event['sprites'] if not s.get('effect'))==[0,1]
            absent=[]
            for s in event['sprites']:
                assert s['character']==[character,4][s['player']] and s.get('source_bank','normal')=='normal'
                data=sources[s['character']];seg,off=struct.unpack_from('<HH',data,0xb28+s['slot']*4)
                at=0xc48+seg*16+off;width,height=data[at:at+2];end=at+2+(width+1)//2*height
                assert width==s['width'] and height==s['height'] and end<=len(data)
                assert hashlib.sha256(data[at:end]).hexdigest()==s['source_sha256']
                k=key(s);observed.add(k)
                if k not in available:missing.add(k);absent.append(k)
            assert absent==(event['missing_keys'] or [])
            reasons[event['reason']]+=1
        assert dict(reasons)==case['reasons'] and sorted(observed)==case['observed_keys'] and sorted(missing)==case['missing_keys']
        for sample in case['samples']:
            stem=sample['stem'];frame=json.loads((directory/(stem+'.frame.json')).read_text())
            colors=json.loads((directory/(stem+'.palette.json')).read_text())
            assert frame['layers_complete'] and not frame['training']['modified']
            assert sample['serial']==frame['serial'] and sample['steps']==frame['steps']
            assert sample['reason']==by_serial[frame['serial']]['reason']
            combined=bytearray(64000)
            for i,layer in enumerate(frame['layers']):
                indices=(directory/f'{stem}.layer-{i:02d}.idx').read_bytes()
                mask=(directory/f'{stem}.layer-{i:02d}.mask').read_bytes()
                assert len(indices)==len(mask)==64000 and set(mask)<={0,1}
                for pos,covered in enumerate(mask):
                    if covered:combined[pos]=indices[pos]
                s=layer.get('sprite')
                if not s:continue
                try:
                    proof=verify_sprite(a.original_root,s,indices,mask)
                except AssertionError as exc:
                    geometry_mismatches.append({'character':character,'sample':stem,'sprite':s,'reason':str(exc)})
                    continue
                if s.get('effect'):
                    assert s['palette_base']==0xc0+s['player']*32+16
                    data=sources[s['character']]
                    expected_palette=[[v*4+v//16 for v in data[0xaf8+i*3:0xaf8+(i+1)*3]] for i in range(16)]
                    assert colors[s['palette_base']:s['palette_base']+16]==expected_palette
                    proof['capture']=str(directory.relative_to(root))+'/'+stem
                    effect_evidence.append(proof)
            assert combined==(directory/(stem+'.idx')).read_bytes()
        summary.append({'character':character,'sampled_frames':len(trace),'selected_frames':sum(x['selected'] for x in trace),'reasons':dict(reasons),'missing_keys':sorted(missing),'phases_without_sampled_draw':sorted(set(phase_names)-observed_phases)})
        count+=len(trace)
    assert not geometry_mismatches,geometry_mismatches
    unique={}
    for item in effect_evidence:
        sprite=item['sprite'];unique[(sprite['character'],sprite['slot'])]=item
    reference=None
    if unique:
        columns=5;rows=(len(unique)+columns-1)//columns
        sheet=Image.new('RGBA',(columns*240,rows*320),(18,24,34,255));draw=ImageDraw.Draw(sheet)
        for ordinal,((character,slot),item)in enumerate(sorted(unique.items())):
            data=sources[character];at=item['source_file_offset'];width,height=data[at:at+2];stride=(width+1)//2
            colours=[tuple(v*4+v//16 for v in data[0xaf8+i*3:0xaf8+(i+1)*3]) for i in range(16)]
            sprite_image=Image.new('RGBA',(width,height))
            for y in range(height):
                for x in range(width):
                    b=data[at+2+y*stride+x//2];v=b>>4 if x%2==0 else b&15
                    if v:sprite_image.putpixel((x,y),colours[v]+(255,))
            x0=ordinal%columns*240;y0=ordinal//columns*320
            scaled=sprite_image.resize((width*3,height*3),Image.Resampling.NEAREST)
            sheet.alpha_composite(scaled,(x0+(240-scaled.width)//2,y0+35+(265-scaled.height)//2))
            draw.text((x0+8,y0+8),f'C{character} slot {slot}: {width}x{height}',fill='white')
        sheet.save(root/'effects-reference.png');reference=sha(root/'effects-reference.png')
    result={'kind':'independent normal keyboard special-action source and selection sampling','cases':summary,'sampled_frames':count,'effects':effect_evidence,'unresolved_geometry_samples':geometry_mismatches,
            'reference_png_sha256':reference,'unique_effect_keys':[list(x)for x in sorted(unique)],'source_receipt_sha256':sha(root/'receipt.json'),'verifier_sha256':sha(Path(__file__)),'sprite_verifier_sha256':sha(Path(__file__).with_name('verify_character_geometry.py')),
            'limits':'source identities and saved CPU layer reconstruction; selector outcomes are recorded diagnostics, not independently proven GPU appearance, full animations, all inputs, controlled RNG parity or native GUI acceptance'}
    (root/'source-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sampled_frames':count,'cases':summary,'effect_samples':len(effect_evidence),'unique_effect_keys':[list(x)for x in sorted(unique)],'unresolved_geometry_samples':len(geometry_mismatches)},ensure_ascii=False))

if __name__=='__main__':main()
