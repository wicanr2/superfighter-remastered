"""保留既有素材來源紀錄，更新 049 新增 PNG／清單的身分與總量。"""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path('/project/assets/hd')


def main():
    file = ROOT/'catalog.json'
    catalog = json.loads(file.read_text())
    manifest = json.loads((ROOT/'characters/manifest.json').read_text())
    active_atlases = {row['file'] for row in manifest['atlases']}
    existing = {row['file']: row for row in catalog['files']}
    additions = [ROOT/'screens.json', ROOT/'characters/spider-complete-source.json',
                 *sorted((ROOT/'characters').glob('spider-covered-poses-*.png')),
                 *sorted((ROOT/'candidates').glob('spider-covered-v3-*.png'))]
    for path in additions + [ROOT/'characters/manifest.json']:
        relative = str(path.relative_to(ROOT))
        row = existing.get(relative, dict(file=relative))
        row.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
        if path.suffix == '.png':
            with Image.open(path) as image:
                row['size'] = list(image.size)
            row['status'] = ('049 original generated input' if 'candidates/' in relative else
                             '049 current-character-atlas' if path.name in active_atlases else '049 pending costume choice')
            row['source_record'] = 'characters/spider-complete-source.json'
        else:
            row['status'] = '049 runtime mapping metadata'
        existing[relative] = row
    screens=json.loads((ROOT/'screens.json').read_text())
    backgrounds=json.loads((ROOT.parent.parent/'internal/hd/background-sources.json').read_text())
    for relative in {row['file'] for row in screens['images']}:
        existing[relative]['status']='049 integrated screen image; artistic approximation'
    for relative in {row['image_file'] for row in backgrounds}:
        existing[relative]['status']='049 integrated scene image; artistic approximation'
    catalog['files'] = list(existing.values())
    catalog['characters'].update(atlases=len(manifest['atlases']), registered_keys=len(manifest['poses']), sources=len(manifest['sources']), complete_HD=False)
    catalog['pngs'] = len(list(ROOT.rglob('*.png')))
    catalog['integration'] = '049 production wiring; verification scope in docs/spec/049-hd-batch-integration.md; Spider B approved; original-audio integration in 050; not full-game parity'
    file.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    for row in catalog['files']:
        path=ROOT/row['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],row['file']
    print(json.dumps(dict(records=len(catalog['files']),pngs=catalog['pngs'],characters=catalog['characters'])))


if __name__=='__main__':
    main()
