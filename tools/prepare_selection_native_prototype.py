"""由正式來源建立隔離的 047 選角肖像原型，不晉升或改正式格式。"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import build_desktop
from prepare_title_native_prototype import sha, snapshot, replace

ROOT = Path('/project')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=('prepare', 'build'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert out.is_relative_to(ROOT/'workplace')
    original = build_desktop.compiled_inputs(ROOT)
    if a.stage == 'prepare':
        assert not out.exists() and out.parent.stat().st_uid == os.getuid() == 1000
        out.mkdir()
        source = out/'source'
        source.mkdir()
        for name in ('go.mod', 'go.sum', 'VERSION'):
            shutil.copyfile(ROOT/name, source/name)
        for name in ('cmd', 'internal'):
            shutil.copytree(ROOT/name, source/name)
        (out/'go.work').write_text('go 1.24.0\n\nuse (\n ./source\n ../dosgolem-source\n)\n')
        template = ROOT/'tools/selection-native-prototype/desktop.go.in'
        shutil.copyfile(template, source/'internal/desktop/selection_prototype.go')
        desktop = source/'internal/desktop/game.go'
        replace(desktop, 'type Game struct {\n', 'type Game struct {\n\tselectionPrototype *selectionPrototypeAssets\n\tselectionPrototypeHD bool\n\tselectionPrototypeView *selectionPrototypeState\n')
        replace(desktop, '\treturn g, nil\n}', '\tg.selectionPrototype = loadSelectionPrototype(opts.Root)\n\treturn g, nil\n}')
        replace(desktop, '\tg.hdActive = false\n', '\tg.hdActive = false\n\tg.selectionPrototypeHD = false\n\tg.selectionPrototypeView = nil\n')
        replace(desktop, '\tdst = window\n', '\tg.selectionPrototypeView = g.selectionPrototypeState()\n\tif g.hdEnabled && mapped && len(frame.Pixels) == 0 && g.drawSelectionPrototype(dst, g.selectionPrototypeView) {\n\t\tg.selectionPrototypeHD = true; g.hdActive = true; g.hdReason = "選角肖像候選，尚未定版"\n\t}\n\tdst = window\n')
        replace(desktop, '\t\tHDReason           string                `json:"hd_reason"`', '\t\tSelectionPrototype *selectionPrototypeState `json:"selection_prototype,omitempty"`\n\t\tSelectionPrototypeHD bool `json:"selection_hd_prototype"`\n\t\tHDReason           string                `json:"hd_reason"`')
        replace(desktop, 'HDReason: g.hdReason,', 'HDReason: g.hdReason, SelectionPrototype: g.selectionPrototypeState(), SelectionPrototypeHD: g.selectionPrototypeHD,')
        replace(desktop, 'HDCharactersActive: g.hdActive && g.hdCharacters != nil,', 'HDCharactersActive: g.hdActive && g.hdCharacters != nil && !g.selectionPrototypeHD,')
        replace(desktop, '"hd_enabled": g.hdEnabled,', '"selection_hd_prototype": g.selectionPrototypeHD, "selection_prototype": g.selectionPrototypeView, "hd_enabled": g.hdEnabled,')
        marker = '\t\tif e == nil && g.opts.Observe != "" && len(frame.Pixels) == 64000 {'
        replace(desktop, marker, '\t\tif e == nil && g.opts.Observe != "" {\n\t\t\tvar data []byte\n\t\t\tdata, e = json.Marshal(palette)\n\t\t\tif e == nil { e = os.WriteFile(path+".prototype-palette.json", data, 0600) }\n\t\t}\n'+marker)
        paths = [Path(__file__), template, ROOT/'tools/prepare_title_native_prototype.py', ROOT/'tools/build_desktop.py']
        recipe = {'kind': 'disposable 047 copied module, no production promotion', 'original_compiled_inputs': original,
                  'recipe_inputs': {str(q.relative_to(ROOT)): sha(q) for q in paths}, 'source_snapshot': snapshot(source),
                  'workspace_sha256': sha(out/'go.work'), 'limits': 'large portraits only; original backdrop, small portraits and navigation preserved; no production format'}
        (out/'recipe.json').write_text(json.dumps(recipe, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({'source_files': len(recipe['source_snapshot']), 'formal_compiled_inputs': len(original)}))
        return
    recipe = json.loads((out/'recipe.json').read_text())
    source = out/'source'
    assert recipe['original_compiled_inputs'] == original and snapshot(source) == recipe['source_snapshot']
    assert sha(out/'go.work') == recipe['workspace_sha256']
    for name, digest in recipe['recipe_inputs'].items():
        assert sha(ROOT/name) == digest
    binary = out/'superfighter-selection-prototype-linux-amd64'
    assert not binary.exists()
    version = (source/'VERSION').read_text().strip()
    env = dict(os.environ, GOWORK=str(out/'go.work'), CGO_ENABLED='1', GOOS='linux', GOARCH='amd64')
    command = ['go', 'build', '-p', '1', '-mod=readonly', '-buildvcs=false', '-trimpath', '-ldflags', '-X main.version='+version, '-o', str(binary), './cmd/superfighter']
    subprocess.run(command, cwd=source, env=env, check=True)
    assert snapshot(source) == recipe['source_snapshot'] and build_desktop.compiled_inputs(ROOT) == original
    result = {'kind': 'isolated Linux selection portrait compiler receipt', 'command': command, 'version': version,
              'go_version': subprocess.check_output(['go', 'version'], text=True).strip(), 'recipe_sha256': sha(out/'recipe.json'),
              'binary_sha256': sha(binary), 'workspace_sha256': sha(out/'go.work'), 'source_snapshot': recipe['source_snapshot'],
              'limits': 'not promoted to workplace/bin, dist-all, release or production; not Windows/macOS acceptance'}
    (out/'build.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_snapshot'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
