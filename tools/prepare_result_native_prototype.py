"""由正式來源複本建立 048 原生結果原型，原參照只在 workplace。"""
import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess

import build_desktop
from prepare_title_native_prototype import replace, sha, snapshot

ROOT = Path('/project')


def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=('prepare', 'build'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert out.is_relative_to(ROOT/'workplace')
    original = build_desktop.compiled_inputs(ROOT)
    if a.stage == 'prepare':
        from PIL import Image
        from recognize_result_source import ResultSources
        assert not out.exists() and out.parent.stat().st_uid == os.getuid() == 1000
        out.mkdir()
        references = ResultSources(ROOT/'workplace/orig')
        def encoded(image):
            return {'Width': image.width, 'Height': image.height, 'RGB': base64.b64encode(image.tobytes()).decode()}
        reference = {'Inputs': references.inputs, 'Paper': base64.b64encode(references.paper.tobytes()).decode()}
        for name in ('left', 'right', 'outcomes', 'flags', 'names'):
            reference[name.capitalize()] = [encoded(image) for image in getattr(references, name)]
        dump(out/'result-reference.json', reference)
        paths = [ROOT/'assets/hd/candidates'/name for name in ('selection-portraits-source.json', 'result-portraits-source.json', 'result-source.json')]
        normal, losers, first = [json.loads(path.read_text()) for path in paths]
        rows = []
        paper = next(row for row in first['records'] if row['id'] == 'paper')
        for key, row in [('paper', paper)]+[(f'left-{i}', row) for i, row in enumerate(normal['records'])]+[(f'right-{i}', row) for i, row in enumerate(losers['records'])]:
            path = ROOT/'assets/hd/candidates'/row['file']
            assert sha(path) == row['sha256']
            rows.append({'Key': key, 'File': path.name, 'SHA': sha(path), 'Width': row['size'][0], 'Height': row['size'][1], 'Private': False})
        # 兩面旗幟只取既有純 HD 比較中的向量重畫，不複製原 FLAG 像素。
        preview = ROOT/'docs/screenshots/result-newspaper-candidate.png'
        assert sha(preview) == first['preview']['sha256']
        for i, box in enumerate(((150, 820, 475, 985), (1130, 820, 1455, 985))):
            path = out/f'flag-hd-{i}.png'
            Image.open(preview).convert('RGB').crop(box).save(path)
            rows.append({'Key': f'flag-{i}', 'File': path.name, 'SHA': sha(path), 'Width': 325, 'Height': 165, 'Private': True})
        assert len(rows) == 25
        dump(out/'result-art.json', {'ReferenceSHA': sha(out/'result-reference.json'), 'Art': rows})
        source = out/'source'
        source.mkdir()
        for name in ('go.mod', 'go.sum', 'VERSION'):
            shutil.copyfile(ROOT/name, source/name)
        for name in ('cmd', 'internal'):
            shutil.copytree(ROOT/name, source/name)
        (out/'go.work').write_text('go 1.24.0\n\nuse (\n ./source\n ../dosgolem-source\n)\n')
        template = ROOT/'tools/result-native-prototype/desktop.go.in'
        text = template.read_text()
        assert text.count('@RECIPE_SHA@') == 1
        (source/'internal/desktop/result_prototype.go').write_text(text.replace('@RECIPE_SHA@', sha(out/'result-art.json')))
        desktop = source/'internal/desktop/game.go'
        replace(desktop, 'type Game struct {\n', 'type Game struct {\n\tresultPrototype *resultPrototypeAssets\n\tresultPrototypeHD bool\n\tresultPrototypeView *resultPrototypeState\n')
        replace(desktop, '\treturn g, nil\n}', '\tg.resultPrototype = loadResultPrototype(opts.Root)\n\treturn g, nil\n}')
        replace(desktop, '\tg.hdActive = false\n', '\tg.hdActive = false\n\tg.resultPrototypeHD = false\n\tg.resultPrototypeView = nil\n')
        replace(desktop, '\tdst = window\n', '\tg.resultPrototypeView = g.resultPrototypeState()\n\tif g.hdEnabled && mapped && len(frame.Pixels) == 0 && g.drawResultPrototype(dst, g.resultPrototypeView) {\n\t\tg.resultPrototypeHD = true; g.hdActive = true; g.hdReason = "結果報紙候選，尚未定版"\n\t}\n\tdst = window\n')
        replace(desktop, '\t\tHDReason           string                `json:"hd_reason"`', '\t\tResultPrototype *resultPrototypeState `json:"result_prototype,omitempty"`\n\t\tResultPrototypeHD bool `json:"result_hd_prototype"`\n\t\tResultArtLoaded bool `json:"result_art_loaded"`\n\t\tHDReason           string                `json:"hd_reason"`')
        replace(desktop, 'HDReason: g.hdReason,', 'HDReason: g.hdReason, ResultPrototype: g.resultPrototypeState(), ResultPrototypeHD: g.resultPrototypeHD, ResultArtLoaded: g.resultPrototype != nil && g.resultPrototype.loaded,')
        replace(desktop, 'HDCharactersActive: g.hdActive && g.hdCharacters != nil,', 'HDCharactersActive: g.hdActive && g.hdCharacters != nil && !g.resultPrototypeHD,')
        replace(desktop, '"hd_enabled": g.hdEnabled,', '"result_hd_prototype": g.resultPrototypeHD, "result_prototype": g.resultPrototypeView, "hd_enabled": g.hdEnabled,')
        marker = '\t\tif e == nil && g.opts.Observe != "" && len(frame.Pixels) == 64000 {'
        replace(desktop, marker, '\t\tif e == nil && g.opts.Observe != "" {\n\t\t\tvar data []byte\n\t\t\tdata, e = json.Marshal(palette)\n\t\t\tif e == nil { e = os.WriteFile(path+".prototype-palette.json", data, 0600) }\n\t\t}\n'+marker)
        dependencies = [Path(__file__), template, ROOT/'tools/build_desktop.py', ROOT/'tools/prepare_title_native_prototype.py', ROOT/'tools/recognize_result_source.py', ROOT/'tools/export_result_source.py', ROOT/'tools/hd_source_probe.py', *paths, preview]
        recipe = {'kind': 'disposable 048 copied module, no production promotion', 'original_compiled_inputs': original,
            'recipe_inputs': {str(p.relative_to(ROOT)): sha(p) for p in dependencies}, 'source_snapshot': snapshot(source),
            'workspace_sha256': sha(out/'go.work'), 'reference_sha256': sha(out/'result-reference.json'),
            'art_recipe_sha256': sha(out/'result-art.json'), 'private_flag_SHA256': {row['File']: row['SHA'] for row in rows if row['Private']},
            'limits': 'result source reconstruction + candidate art; two flag artworks only; not formal format, approved visuals or all-character validation'}
        dump(out/'recipe.json', recipe)
        print(json.dumps({'source_files': len(recipe['source_snapshot']), 'formal_compiled_inputs': len(original), 'artwork_files': len(rows), 'reference_bytes': (out/'result-reference.json').stat().st_size}))
        return
    recipe = json.loads((out/'recipe.json').read_text())
    source = out/'source'
    assert recipe['original_compiled_inputs'] == original and snapshot(source) == recipe['source_snapshot']
    assert sha(out/'go.work') == recipe['workspace_sha256'] and sha(out/'result-reference.json') == recipe['reference_sha256']
    assert sha(out/'result-art.json') == recipe['art_recipe_sha256']
    for name, digest in recipe['recipe_inputs'].items():
        assert sha(ROOT/name) == digest
    binary = out/'superfighter-result-prototype-linux-amd64'
    assert not binary.exists()
    version = (source/'VERSION').read_text().strip()
    env = dict(os.environ, GOWORK=str(out/'go.work'), CGO_ENABLED='1', GOOS='linux', GOARCH='amd64')
    command = ['go', 'build', '-p', '1', '-mod=readonly', '-buildvcs=false', '-trimpath', '-ldflags', '-X main.version='+version, '-o', str(binary), './cmd/superfighter']
    subprocess.run(command, cwd=source, env=env, check=True)
    assert snapshot(source) == recipe['source_snapshot'] and build_desktop.compiled_inputs(ROOT) == original
    result = {'kind': 'isolated Linux result prototype compiler receipt', 'command': command, 'version': version,
        'go_version': subprocess.check_output(['go', 'version'], text=True).strip(), 'recipe_sha256': sha(out/'recipe.json'),
        'binary_sha256': sha(binary), 'source_snapshot': recipe['source_snapshot'],
        'limits': 'not promoted to bin, dist-all, release or production; no Windows/macOS acceptance'}
    dump(out/'build.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'source_snapshot'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
