"""將已驗二十一鍵及六 PNG 原封加入 repo，保留舊美術及 catalog 項。"""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

ROOT = Path('/project')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source = ROOT / 'workplace/hd-characters-remaining-effects-v1'
    target = ROOT / 'assets/hd/characters'
    art = ROOT / 'workplace/remaining-special-audit-v1/art-v1'
    review = json.loads((art/'evidence-review.json').read_text())
    assert review['status'] == 'READY' and sha(target/'manifest.json') == review['base_manifest_sha256']
    old = json.loads((target/'manifest.json').read_text())
    new = json.loads((source/'manifest.json').read_text())
    assert new['poses'][:1495] == old['poses'] and len(new['poses']) == 1516 and len(new['atlases']) == 74
    assert target.stat().st_uid == 1000
    for p in target.iterdir():
        assert p.is_file() and p.stat().st_uid == 1000
        if p.name != 'manifest.json':
            assert sha(p) == sha(source/p.name)
    catalog_path = ROOT / 'assets/hd/catalog.json'
    assert catalog_path.stat().st_uid == 1000
    catalog = json.loads(catalog_path.read_text())
    before = json.loads(catalog_path.read_text())
    assert len(catalog['files']) == 107 and catalog['pngs'] == 97
    (art/'catalog-before.json').write_text(json.dumps(before, ensure_ascii=False, indent=2)+'\n')
    added = []
    for p in source.iterdir():
        q = target/p.name
        if q.exists() and p.name != 'manifest.json':
            continue
        shutil.copyfile(p, q)
        assert sha(p) == sha(q) and q.stat().st_uid == 1000
        relative = 'characters/'+p.name
        if p.name == 'manifest.json':
            entry = next(x for x in catalog['files'] if x['file'] == relative)
            entry.update(sha256=sha(q), bytes=q.stat().st_size, copied_from=str(p.relative_to(ROOT)))
        else:
            entry = {'file': relative, 'sha256': sha(q), 'bytes': q.stat().st_size,
                     'status': 'current-character-atlas' if p.suffix == '.png' else 'effect-provenance',
                     'copied_from': str(p.relative_to(ROOT)), 'tool': 'built-in imagegen'}
            if p.suffix == '.png':
                with Image.open(q) as image:
                    entry['size'] = list(image.size)
                    image.verify()
                entry['generated_source'] = str((art/p.name).relative_to(ROOT))
            catalog['files'].append(entry)
            added.append(relative)
    assert len(added) == 7
    catalog['characters'].update(atlases=74, registered_keys=1516)
    catalog['pngs'] = 103
    for previous, current in zip(before['files'], catalog['files']):
        if previous['file'] != 'characters/manifest.json':
            assert previous == current
    for x in catalog['files']:
        p = ROOT/'assets/hd'/x['file']
        assert sha(p) == x['sha256'] and p.stat().st_size == x['bytes']
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    result = {'pngs': catalog['pngs'], 'catalog_entries': len(catalog['files']),
              'catalog_payload_bytes': sum(x['bytes'] for x in catalog['files']),
              'asset_files': sum(x.is_file() for x in (ROOT/'assets/hd').rglob('*')),
              'manifest_sha256': sha(target/'manifest.json'), 'catalog_sha256': sha(catalog_path),
              'added': added, 'old_keys': 1495, 'new_keys': 1516, 'old_PNGs_unchanged': True}
    (art/'assets-promotion.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
