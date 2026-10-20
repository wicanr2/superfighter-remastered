"""只在 workplace 產生隔離的 046 原生原型，不修改正式程式或素材格式。"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    return {str(p.relative_to(path)):sha(p)for p in sorted(path.rglob('*'))if p.is_file()}


def replace(path,old,new):
    source=path.read_text();assert source.count(old)==1,(str(path),old)
    path.write_text(source.replace(old,new))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('prepare','build'))
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();out=a.output.resolve();assert out.is_relative_to(ROOT/'workplace')
    spec=importlib.util.spec_from_file_location('desktop_build',ROOT/'tools/build_desktop.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original_inputs=module.compiled_inputs(ROOT)
    if a.stage=='prepare':
        assert not out.exists() and out.parent.stat().st_uid==os.getuid()==1000
        out.mkdir();source=out/'source';source.mkdir()
        for name in('go.mod','go.sum','VERSION'):shutil.copyfile(ROOT/name,source/name)
        for name in('cmd','internal'):shutil.copytree(ROOT/name,source/name)
        (out/'go.work').write_text('go 1.24.0\n\nuse (\n ./source\n ../dosgolem-source\n)\n')
        templates=ROOT/'tools/title-native-prototype'
        shutil.copyfile(templates/'core.go.in',source/'internal/gamecore/title_prototype.go')
        shutil.copyfile(templates/'desktop.go.in',source/'internal/desktop/title_prototype.go')
        core=source/'internal/gamecore/core.go'
        replace(core,'type Status struct {\n','type Status struct {\n\tTitlePrototype *TitlePrototypeState `json:"title_prototype,omitempty"`\n\tTitlePrototypeStage string `json:"title_prototype_stage"`\n\tTitlePrototypeInput TitlePrototypeInput `json:"title_prototype_input"`\n')
        replace(core,'type Core struct {\n','type Core struct {\n\ttitlePrototype *titlePrototypeRecording\n')
        replace(core,'\tc.installSelection()\n','\tc.installSelection()\n\tc.installTitlePrototype(root)\n')
        replace(core,'\treturn s\n}\nfunc (c *Core) RGB()', '\ts.TitlePrototype = c.TitlePrototype()\n\tif c.titlePrototype != nil { s.TitlePrototypeStage = c.titlePrototype.stage; s.TitlePrototypeInput = c.titlePrototype.input }\n\tif s.Battle { s.TitlePrototypeStage = "battle" }\n\treturn s\n}\nfunc (c *Core) RGB()')
        desktop=source/'internal/desktop/game.go'
        replace(desktop,'type Game struct {\n','type Game struct {\n\ttitlePrototypePaint *titlePrototypePaint\n\ttitlePrototypeActive bool\n\ttitlePrototypePhase int\n')
        replace(desktop,'\treturn g, nil\n}', '\tg.titlePrototypePaint = loadTitlePrototypePaint()\n\tif g.titlePrototypePaint != nil { g.notice = "標題 HD 隔離原型；材質分區尚未定版。" }\n\treturn g, nil\n}')
        replace(desktop,'\tg.hdActive = false\n','\tg.hdActive = false\n\tg.titlePrototypeActive = false\n\tg.titlePrototypePhase = -1\n')
        replace(desktop,'\tif !mapped && displayError != "" {', '\tif g.hdEnabled && mapped && len(frame.Pixels) == 0 {\n\t\tif title := g.core.TitlePrototype(); title != nil && g.drawTitlePrototype(dst, title) {\n\t\t\tcharactersDrawn = true; backgroundOnly = false; g.hdActive = true; g.titlePrototypeActive = true; g.titlePrototypePhase = title.Phase; g.hdReason = "標題 HD 隔離原型；材質假說"\n\t\t}\n\t}\n\tif !mapped && displayError != "" {')
        replace(desktop,'\t\tHDReason           string                `json:"hd_reason"`','\t\tTitlePrototypeHD bool `json:"title_hd_prototype"`\n\t\tHDReason           string                `json:"hd_reason"`')
        replace(desktop,'HDReason: g.hdReason,','HDReason: g.hdReason, TitlePrototypeHD: g.titlePrototypeActive,')
        replace(desktop,'HDCharactersActive: g.hdActive && g.hdCharacters != nil,','HDCharactersActive: g.hdActive && g.hdCharacters != nil && !g.titlePrototypeActive,')
        replace(desktop,'"hd_enabled": g.hdEnabled,','"title_hd_prototype": g.titlePrototypeActive, "title_prototype_phase": g.titlePrototypePhase, "hd_enabled": g.hdEnabled,')
        marker='\t\tif e == nil && g.opts.Observe != "" && len(frame.Pixels) == 64000 {'
        extra='''
        if e == nil && g.opts.Observe != "" {
            var data []byte
            data, e = json.Marshal(palette)
            if e == nil { e = os.WriteFile(path+".prototype-palette.json", data, 0600) }
            if title := g.core.TitlePrototype(); title != nil && e == nil {
                data, e = json.MarshalIndent(title, "", "  ")
                if e == nil { e = os.WriteFile(path+".title.json", data, 0600) }
                if e == nil { e = os.WriteFile(path+".title.idx", title.Pixels, 0600) }
            }
        }
'''
        replace(desktop,marker,extra+marker)
        recipe={'kind':'disposable 046 native prototype; no production promotion','original_compiled_inputs':original_inputs,
                'recipe_inputs':{str(p.relative_to(ROOT)):sha(p)for p in(Path(__file__),templates/'core.go.in',templates/'desktop.go.in')},
                'source_snapshot':snapshot(source),'workspace_sha256':sha(out/'go.work'),
                'limits':'private copied module only; original assets, rules, public API and packages unchanged; material segmentation remains hypothesis'}
        (out/'recipe.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'stage':'prepared','source_files':len(recipe['source_snapshot']),'formal_compiled_inputs':len(original_inputs)}))
        return
    recipe=json.loads((out/'recipe.json').read_text());source=out/'source'
    assert recipe['original_compiled_inputs']==original_inputs and snapshot(source)==recipe['source_snapshot']
    assert sha(out/'go.work')==recipe['workspace_sha256']
    for name,digest in recipe['recipe_inputs'].items():assert sha(ROOT/name)==digest
    version=(source/'VERSION').read_text().strip();binary=out/'superfighter-title-prototype-linux-amd64'
    assert not binary.exists()
    env=dict(os.environ,GOWORK=str(out/'go.work'),CGO_ENABLED='1',GOOS='linux',GOARCH='amd64')
    command=['go','build','-p','1','-mod=readonly','-buildvcs=false','-trimpath','-ldflags','-X main.version='+version,'-o',str(binary),'./cmd/superfighter']
    subprocess.run(command,cwd=source,env=env,check=True)
    assert snapshot(source)==recipe['source_snapshot'] and module.compiled_inputs(ROOT)==original_inputs
    result={'kind':'isolated Linux native prototype compiler receipt','command':command,'version':version,
            'go_version':subprocess.check_output(['go','version'],text=True).strip(),'recipe_sha256':sha(out/'recipe.json'),
            'workspace_sha256':sha(out/'go.work'),'binary_sha256':sha(binary),'source_snapshot':recipe['source_snapshot'],
            'limits':'not promoted to workplace/bin, dist-all, release or production; not Windows/macOS acceptance'}
    (out/'build.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='source_snapshot'},ensure_ascii=False))


if __name__=='__main__':
    main()
