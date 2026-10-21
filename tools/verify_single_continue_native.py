"""獨立核對隔離繼續介面的原來源、GPU 身分、原貌切換及離場清除。"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat

import build_desktop
from prepare_title_native_prototype import snapshot
from recognize_result_continue import ResultContinueSources
from verify_single_continue_core import sha, verify_destination

ROOT=Path('/project')
VIEW=(80,64,1040,664)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--build',type=Path,required=True)
    a=p.parse_args();q,b=a.output,a.build
    assert not (q/'comparison.json').exists()
    receipt=json.loads((q/'receipt.json').read_text())
    recipe=json.loads((b/'recipe.json').read_text());build=json.loads((b/'build.json').read_text())
    # Each run binds its immutable script copy; later harness input fixes do not rewrite old receipts.
    assert receipt['script_sha256']==sha(q/'single_continue_native_smoke.py')
    assert receipt['binary_sha256']==build['binary_sha256']==sha(b/'superfighter-result-prototype-linux-amd64')
    assert build['recipe_sha256']==sha(b/'recipe.json')
    assert recipe['source_snapshot']==build['source_snapshot']==snapshot(b/'source')
    assert recipe['original_compiled_inputs']==build_desktop.compiled_inputs(ROOT)
    assert recipe['variant']=='normal-single-continue'
    for name,digest in recipe['recipe_inputs'].items():assert sha(ROOT/name)==digest
    assert receipt['reference_sha256']==recipe['reference_sha256']==sha(b/'result-reference.json')
    assert receipt['art_recipe_sha256']==recipe['art_recipe_sha256']==sha(b/'result-art.json')
    assert receipt['knockout_rounds']==[0,1]
    opponent=receipt['opponent'];assert 0<=opponent<11
    source=ResultContinueSources(ROOT/'workplace/orig')
    states,pictures,originals,typed={},{},{},{}
    proofs,rankings=[],[]
    art=json.loads((b/'result-art.json').read_text())['Art']
    references={}
    for row in art:
        path=ROOT/'assets/hd/candidates'/row['File']
        assert not row['Private'] and sha(path)==row['SHA']
        im=Image.open(path).convert('RGB')
        if row['Key'].startswith(('left-','right-')):
            for mirror in (False,True):
                references[row['Key'],mirror]=(ImageOps.mirror(im) if mirror else im).resize((267,267),Image.Resampling.BILINEAR)
    for event in receipt['events']:
        name,state=event['name'],event['state'];path=q/(name+'.png')
        meta=json.loads(Path(str(path)+'.capture.json').read_text())
        assert state['core']['paused'] and meta['core']==state['core']
        assert not any(state['core']['training'][k] for k in ('requested','active','modified'))
        assert meta['result_hd_prototype']==state['result_hd_prototype']
        assert meta.get('result_prototype')==state.get('result_prototype')
        rgb=Path(str(path)+'.selected.rgb').read_bytes()
        indices=Path(str(path)+'.display.idx').read_bytes()
        palette=json.loads(Path(str(path)+'.prototype-palette.json').read_text())
        assert rgb==bytes(c for v in indices for c in palette[v])
        picture=Image.open(path).convert('RGB');assert picture.size==(1120,820)
        states[name],pictures[name],originals[name]=state,picture,rgb
        if name.startswith('continue-'):
            assert meta['selected_width']==320 and meta['selected_height']==200
            assert meta['active_rect']=={'Min':{'X':80,'Y':64},'Max':{'X':1040,'Y':664}}
            found=source.identify_continue(rgb,indices,palette);assert found is not None,name
            assert (found.left_character,found.right_character,found.winner_player,found.outcome_record)==(0,opponent,1,0)
            expected={'characters':[0,opponent],'winner_player':1,'outcome_record':0,'flag_records':list(found.flag_records),
                'name_positions':list(found.name_positions),'original_rgb_sha256':found.original_RGB_sha256,
                'continue':{'selected':found.selected,'highlight_rgb':list(found.highlight_rgb),
                'inactive_erased':found.inactive_erased,'original_indices_sha256':found.original_indices_sha256}}
            assert meta['result_prototype']==expected,(name,meta['result_prototype'],expected)
            typed[name]=expected
            active=not receipt['fallback'] and name!='continue-left-original'
            assert state['result_hd_prototype']==state['hd_active']==active
            assert not state['hd_characters_active']
            assert state['result_art_loaded']==(not receipt['fallback'])
            actual=picture.crop(VIEW)
            original=Image.frombytes('RGB',(320,200),rgb).resize((960,600),Image.Resampling.NEAREST)
            if active:
                assert actual.tobytes()!=original.tobytes()
                # Verify painted identity/orientation in unaffected portrait regions, not a duplicate renderer.
                for side,box,key in ((0,(134,166,401,433),'right-0'),(1,(722,166,989,433),'left-'+str(opponent))):
                    crop=picture.crop(box)
                    distances={k:sum(ImageStat.Stat(ImageChops.difference(crop,ref)).mean)/3 for k,ref in references.items()}
                    best=min(distances,key=distances.get);assert best==(key,side==1),(name,best)
                    rankings.append({'name':name,'side':side,'key':key,'mirror':side==1,'distance':distances[best]})
                panel=picture.crop((368,466,755,637))
                assert panel.tobytes()!=original.crop((288,402,675,573)).tobytes()
            else:
                assert actual.tobytes()==original.tobytes(),name
            proofs.append({'capture':name,'original':found.record(),'png_sha256':sha(path)})
        elif name=='after-continue-choice':
            assert source.identify_continue(rgb,indices,palette) is None
            assert not state.get('result_prototype') and not state['result_hd_prototype'] and not state['hd_active']
            assert picture.crop(VIEW).tobytes()==Image.frombytes('RGB',(320,200),rgb).resize((960,600),Image.Resampling.NEAREST).tobytes()
            destination=verify_destination(indices,palette,receipt['choice'])
        else:
            assert name=='single-battle' and state['core']['battle'] and state['core']['mode']==0 and state['core']['fighters']==[0,opponent]
            assert not state.get('result_prototype') and not state['result_hd_prototype']
    assert len(states)==8 and len(proofs)==6
    for field in ('core','presentation','settings','assigned','result_prototype'):
        assert states['continue-left-hd'][field]==states['continue-left-original'][field]==states['continue-left-restored'][field]
    assert len({originals[n] for n in ('continue-left-hd','continue-left-original','continue-left-restored')})==1
    assert pictures['continue-left-hd'].crop(VIEW).tobytes()==pictures['continue-left-restored'].crop(VIEW).tobytes()
    assert typed['continue-left-hd']['continue']['selected']==0
    assert not typed['continue-left-hd']['continue']['inactive_erased']
    assert typed['continue-right-hd']['continue']['selected']==1 and typed['continue-right-hd']['continue']['inactive_erased']
    assert typed['continue-left-after-toggle']['continue']['selected']==0 and typed['continue-left-after-toggle']['continue']['inactive_erased']
    assert typed['continue-chosen']['continue']['selected']==receipt['choice']
    result={'status':'passed','kind':'isolated Linux normal single continue HD, source reconstruction and destinations',
        'captures':len(states),'continue_full_reconstructions':len(proofs),'GPU_portrait_identity_matches':len(rankings),
        'choice':receipt['choice'],'opponent':opponent,'fallback':receipt['fallback'],'destination':destination,'proofs':proofs,'GPU_ranking':rankings,
        'restored_HD_identical':True,'paused_state_equal':True,'cleared_on_destination':True,
        'receipt_sha256':sha(q/'receipt.json'),'build_sha256':sha(b/'build.json'),'verifier_sha256':sha(Path(__file__)),
        'dependencies':{n:sha(ROOT/'tools'/n) for n in ('recognize_result_continue.py','recognize_result_sides.py','recognize_result_source.py','verify_single_continue_core.py')},
        'limits':'Jaan normal AI loss with the observed original opponent only; GPU identity is not pixel-sampling parity; vector panel/font are draft approximations, no formal release, all-character, single-player win, hardware or other-platform acceptance'}
    (q/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ('proofs','GPU_ranking','dependencies')},ensure_ascii=False))


if __name__=='__main__':main()
