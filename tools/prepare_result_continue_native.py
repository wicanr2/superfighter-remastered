"""048 DRAFT：另建單打繼續介面的隔離原生副本，保持正式來源與舊原型。"""
import argparse
import base64
import json
from pathlib import Path
import shutil
import sys

import prepare_result_native_prototype as base
from prepare_title_native_prototype import sha, snapshot

ROOT = Path('/project')


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def change(text,old,new):
    assert text.count(old) == 1,old[:100]
    return text.replace(old,new)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=('prepare','build'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--parent',type=Path,default=ROOT/'workplace/result-native-prototype-v3')
    args = p.parse_args(); out=args.output.resolve(); parent=args.parent.resolve()
    assert out.is_relative_to(ROOT/'workplace')
    if args.stage == 'build':
        assert json.loads((out/'recipe.json').read_text())['variant'] == 'normal-single-continue'
        sys.argv = ['prepare_result_native_prototype.py','build','--output',str(out)]
        base.main(); return
    from recognize_result_continue import ResultContinueSources, OUTLINES
    assert not out.exists() and out.parent.stat().st_uid == 1000
    recipe = json.loads((parent/'recipe.json').read_text())
    assert recipe['variant'] == 'both-result-sides' and snapshot(parent/'source') == recipe['source_snapshot']
    for file,key in (('result-reference.json','reference_sha256'),('result-art.json','art_recipe_sha256')):
        assert sha(parent/file) == recipe[key]
    out.mkdir(); shutil.copytree(parent/'source',out/'source'); shutil.copyfile(parent/'go.work',out/'go.work')
    for name in ('recipe.json','result-reference.json','result-art.json'):
        shutil.copyfile(parent/name,out/('parent-'+name))
    references = ResultContinueSources(ROOT/'workplace/orig')
    refs = json.loads((parent/'result-reference.json').read_text())
    refs['Inputs'] = references.inputs
    refs['Continue'] = {'Panel':{'Width':129,'Height':57,'RGB':base64.b64encode(references.panel.tobytes()).decode()},
        'Indices':base64.b64encode(references.panel_indices).decode(),'Outlines':OUTLINES,
        'Colours':sorted(references.highlight_colours),'Erase':references.erase_colour}
    dump(out/'result-reference.json',refs); assert (out/'result-reference.json').stat().st_size < 2*1024*1024
    art = json.loads((parent/'result-art.json').read_text()); assert len(art['Art']) == 30
    art['ReferenceSHA'] = sha(out/'result-reference.json'); dump(out/'result-art.json',art)
    source = out/'source/internal/desktop/result_prototype.go'
    text = source.read_text()
    text = change(text,'type resultReferences struct { Inputs map[string]string;', 'type resultReferences struct { Continue resultContinueReferences; Inputs map[string]string;')
    text = change(text,'    Characters [2]int `json:"characters"`','    Continue *resultContinueState `json:"continue,omitempty"`\n    Characters [2]int `json:"characters"`')
    text = change(text,sha(parent/'result-art.json'),sha(out/'result-art.json'))
    text = change(text,'len(a.refs.Inputs)!=7','len(a.refs.Inputs)!=9')
    marker='    artRoot:=os.Getenv("KDZZ_RESULT_PROTOTYPE_ART")'
    text = change(text,marker,'    c:=a.refs.Continue;if c.Panel.Width!=129||c.Panel.Height!=57||len(c.Panel.RGB)!=129*57*3||len(c.Indices)!=129*57||len(c.Colours)!=4||c.Outlines!=([2][4]int{{112,150,152,174},{168,150,208,174}}){return nil}\n'+marker)
    old='    digest:=resultDigest(rgb);if digest==a.lastSHA{return a.lastState};a.lastSHA=digest;a.lastState=nil\n    s:=&resultPrototypeState{OriginalSHA:digest}'
    new='''    digest:=fmt.Sprintf("%s/%s/%d",resultDigest(rgb),resultDigest(display.Indices),g.core.Status().Mode)
    if digest==a.lastSHA{return a.lastState};a.lastSHA=digest
    a.lastState=a.identifyPlainResult(rgb)
    // Core status mode is only exposed during battle. Full SH reconstruction identifies this UI.
    if a.lastState==nil{a.lastState=a.identifyContinueResult(rgb,display.Indices,palette)}
    return a.lastState
}
func (a *resultPrototypeAssets) identifyPlainResult(rgb []byte) *resultPrototypeState {
    s:=&resultPrototypeState{OriginalSHA:resultDigest(rgb)}'''
    text = change(text,old,new)
    text = change(text,'if !bytes.Equal(expected,rgb){return nil};a.lastState=s;return s','if !bytes.Equal(expected,rgb){return nil};return s')
    text = change(text,'    return true\n}', '    g.drawContinuePrototype(dst,s.Continue)\n    return true\n}')
    source.write_text(text)
    template = ROOT/'tools/result-native-prototype/desktop_continue.go.in'
    shutil.copyfile(template,out/'source/internal/desktop/result_continue_prototype.go')
    recipe.update(variant='normal-single-continue',parent_directory=str(parent.relative_to(ROOT)),
        parent_recipe_sha256=sha(out/'parent-recipe.json'),reference_sha256=sha(out/'result-reference.json'),
        art_recipe_sha256=sha(out/'result-art.json'),source_snapshot=snapshot(out/'source'),workspace_sha256=sha(out/'go.work'),
        limits='single loss continuation in disposable copy only; panel, lettering and outline are new vector/font approximations, no formal API, production or asset-format promotion')
    recipe['recipe_inputs'].update({str(path.relative_to(ROOT)):sha(path) for path in (Path(__file__),template,ROOT/'tools/recognize_result_continue.py')})
    before=json.loads((out/'parent-recipe.json').read_text())['source_snapshot']
    assert [name for name,h in before.items() if recipe['source_snapshot'][name] != h] == ['internal/desktop/result_prototype.go']
    assert set(recipe['source_snapshot'])-set(before) == {'internal/desktop/result_continue_prototype.go'}
    dump(out/'recipe.json',recipe)
    print(json.dumps({'variant':recipe['variant'],'copied_sources':len(recipe['source_snapshot']),
        'private_reference_bytes':(out/'result-reference.json').stat().st_size,'art_files':30,'formal_inputs':46}))


if __name__ == '__main__':
    main()
