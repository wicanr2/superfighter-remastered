"""在新隔離副本接七面旗幟，保留第一版結果原型與所有歷史輸入。"""
import argparse
import json
from pathlib import Path
import sys

import prepare_result_native_prototype as base
from prepare_title_native_prototype import replace, sha, snapshot

ROOT = Path('/project')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=('prepare', 'build'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    if a.stage == 'build':
        recipe = json.loads((out/'recipe.json').read_text())
        assert recipe['variant'] == 'seven-source-colour-flags'
        sys.argv = ['prepare_result_native_prototype.py', 'build', '--output', str(out)]
        base.main()
        return
    assert not out.exists()
    sys.argv = ['prepare_result_native_prototype.py', 'prepare', '--output', str(out)]
    base.main()
    recipe_path, art_path = out/'recipe.json', out/'result-art.json'
    old_recipe = recipe_path.read_bytes()
    old_art = art_path.read_bytes()
    (out/'parent-recipe.json').write_bytes(old_recipe)
    (out/'parent-art.json').write_bytes(old_art)
    recipe = json.loads(old_recipe)
    art = json.loads(old_art)
    old_snapshot = dict(recipe['source_snapshot'])
    flags_path = ROOT/'assets/hd/candidates/result-flags-source.json'
    flags = json.loads(flags_path.read_text())
    assert [r['index'] for r in flags['records']] == list(range(7))
    old_flags = [r for r in art['Art'] if r['Key'].startswith('flag-')]
    assert len(old_flags) == 2 and all(r['Private'] for r in old_flags)
    art['Art'] = [r for r in art['Art'] if not r['Key'].startswith('flag-')]
    for row in flags['records']:
        path = ROOT/'assets/hd/candidates'/row['file']
        assert sha(path) == row['sha256'] and row['size'] == [1300, 660]
        art['Art'].append({'Key': f"flag-{row['index']}", 'File': path.name, 'SHA': sha(path),
                          'Width': 1300, 'Height': 660, 'Private': False})
    assert len(art['Art']) == 30
    art_path.write_text(json.dumps(art, ensure_ascii=False, indent=2)+'\n')
    source = out/'source/internal/desktop/result_prototype.go'
    replace(source, sha(out/'parent-art.json'), sha(art_path))
    replace(source, 'len(pending)!=25', 'len(pending)!=30')
    replace(source, 's.Flags[0]>1||s.Flags[1]>1', 's.Flags[0]>6||s.Flags[1]>6')
    recipe['variant'] = 'seven-source-colour-flags'
    recipe['parent_recipe_sha256'] = sha(out/'parent-recipe.json')
    recipe['parent_art_sha256'] = sha(out/'parent-art.json')
    recipe['inactive_parent_flags'] = recipe['private_flag_SHA256']
    recipe['private_flag_SHA256'] = {}
    recipe['art_recipe_sha256'] = sha(art_path)
    recipe['source_snapshot'] = snapshot(out/'source')
    changed = [name for name, digest in old_snapshot.items() if digest != recipe['source_snapshot'][name]]
    assert changed == ['internal/desktop/result_prototype.go']
    recipe['changed_parent_source_files'] = changed
    recipe['recipe_inputs'].update({str(p.relative_to(ROOT)): sha(p) for p in (Path(__file__), flags_path)})
    recipe['limits'] = 'new disposable seven-flag variant; source reconstruction unchanged; not production format, art approval or all-character result acceptance'
    recipe_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'variant': recipe['variant'], 'artwork_files': len(art['Art']),
                      'changed_parent_source_files': changed, 'formal_compiled_inputs': len(recipe['original_compiled_inputs'])}))


if __name__ == '__main__':
    main()
