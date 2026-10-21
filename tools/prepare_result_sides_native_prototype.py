"""複製已驗七面旗幟版本，另建保留玩家位置的雙側結果原型。"""
import argparse
import base64
import json
from pathlib import Path
import shutil
import sys

import prepare_result_native_prototype as base
from prepare_title_native_prototype import sha, snapshot

ROOT=Path('/project')


def dump(p,value):
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=('prepare','build'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--parent',type=Path,default=ROOT/'workplace/result-native-prototype-v2')
    a=p.parse_args(); out=a.output.resolve(); parent=a.parent.resolve()
    assert out.is_relative_to(ROOT/'workplace')
    if a.stage=='build':
        assert json.loads((out/'recipe.json').read_text())['variant']=='both-result-sides'
        sys.argv=['prepare_result_native_prototype.py','build','--output',str(out)];base.main();return
    from recognize_result_sides import ResultSideSources
    assert not out.exists() and out.parent.stat().st_uid==1000
    recipe=json.loads((parent/'recipe.json').read_text())
    assert recipe['variant']=='seven-source-colour-flags' and snapshot(parent/'source')==recipe['source_snapshot']
    assert sha(parent/'result-reference.json')==recipe['reference_sha256']
    assert sha(parent/'result-art.json')==recipe['art_recipe_sha256']
    out.mkdir();shutil.copytree(parent/'source',out/'source')
    shutil.copyfile(parent/'go.work',out/'go.work')
    for filename in ('recipe.json','result-art.json','result-reference.json'):
        shutil.copyfile(parent/filename,out/('parent-'+filename))
    refs=ResultSideSources(ROOT/'workplace/orig')
    encoded=lambda im:{'Width':im.width,'Height':im.height,'RGB':base64.b64encode(im.tobytes()).decode()}
    reference={'Inputs':refs.inputs,'Paper':base64.b64encode(refs.paper.tobytes()).decode()}
    for name in ('left','right','outcomes','flags','names'):
        reference[name.capitalize()]=[encoded(im)for im in getattr(refs,name)]
    old_reference=json.loads((parent/'result-reference.json').read_text())
    assert reference['Left'][:11]==old_reference['Left'] and reference['Right'][:11]==old_reference['Right']
    for name in ('Inputs','Paper','Outcomes','Flags','Names'):assert reference[name]==old_reference[name]
    dump(out/'result-reference.json',reference)
    assert (out/'result-reference.json').stat().st_size<2*1024*1024
    art=json.loads((parent/'result-art.json').read_text());assert len(art['Art'])==30
    art['ReferenceSHA']=sha(out/'result-reference.json');dump(out/'result-art.json',art)
    template=ROOT/'tools/result-native-prototype/desktop_sides.go.in';text=template.read_text()
    assert text.count('@RECIPE_SHA@')==1
    (out/'source/internal/desktop/result_prototype.go').write_text(text.replace('@RECIPE_SHA@',sha(out/'result-art.json')))
    recipe.update(variant='both-result-sides',parent_directory=str(parent.relative_to(ROOT)),
        parent_recipe_sha256=sha(out/'parent-recipe.json'),parent_art_sha256=sha(out/'parent-result-art.json'),
        parent_reference_sha256=sha(out/'parent-result-reference.json'),reference_sha256=sha(out/'result-reference.json'),
        art_recipe_sha256=sha(out/'result-art.json'),source_snapshot=snapshot(out/'source'),
        workspace_sha256=sha(out/'go.work'),inactive_parent_flags={},
        limits='new disposable side-aware result prototype; original player positions retained, no production promotion')
    recipe['recipe_inputs'].update({str(p.relative_to(ROOT)):sha(p)for p in(Path(__file__),template,ROOT/'tools/recognize_result_sides.py')})
    old=json.loads((out/'parent-recipe.json').read_text())['source_snapshot']
    assert [name for name,h in old.items()if recipe['source_snapshot'][name]!=h]==['internal/desktop/result_prototype.go']
    dump(out/'recipe.json',recipe)
    print(json.dumps({'variant':recipe['variant'],'source_files':len(recipe['source_snapshot']),
        'reference_bytes':(out/'result-reference.json').stat().st_size,'artwork_files':30,'formal_inputs':46}))


if __name__=='__main__':main()
