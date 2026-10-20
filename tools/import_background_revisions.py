"""將內建 imagegen 的背景修稿原 PNG 另存入 repo，保留舊稿及精確提示詞。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

ROOT = Path('/project')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests', type=Path, required=True)
    parser.add_argument('--generated-root', type=Path, required=True)
    args = parser.parse_args()
    requests = json.loads(args.requests.read_text())
    assert len(requests) == 2
    destination = ROOT / 'assets/hd/candidates'
    assert destination.is_dir() and destination.stat().st_uid == 1000
    record_path = destination / 'background-revisions-source.json'
    assert not record_path.exists()
    catalog_path = ROOT / 'assets/hd/catalog.json'
    assert catalog_path.stat().st_uid == 1000
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    assert len(previous) == 102 and catalog['pngs'] == 94
    source = {x['name']: x['sha256'] for x in json.loads((ROOT / 'workplace/source-manifest.json').read_text())['files']}
    parent_records = {x['source_file']: x for x in json.loads((destination / 'backgrounds-source.json').read_text())['records']}
    records = []
    for request in requests:
        assert set(request) == {'source', 'parent', 'file', 'generated', 'prompt', 'review'}
        assert Path(request['file']).name == request['file'] and request['file'].endswith('-v2.png')
        assert Path(request['generated']).name == request['generated']
        assert request['source'] in ('I10.XGB', 'I8.XGB')
        original = ROOT / 'workplace/orig' / request['source']
        parent = destination / request['parent']
        generated = args.generated_root / request['generated']
        assert original.is_file() and sha(original) == source[request['source']]
        assert parent.name == parent_records[request['source']]['file'] and sha(parent) == parent_records[request['source']]['sha256']
        assert generated.is_file() and not generated.is_symlink()
        assert not (destination / request['file']).exists()
        with Image.open(generated) as image:
            image.verify()
        with Image.open(generated) as image:
            assert image.width >= 1600 and image.height >= 650 and abs(image.width / image.height - 480 / 204) < .01
            assert image.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            size = list(image.size)
        records.append({'file': request['file'], 'sha256': sha(generated), 'bytes': generated.stat().st_size, 'size': size,
                        'source_file': request['source'], 'source_sha256': sha(original),
                        'parent_file': parent.name, 'parent_sha256': sha(parent), 'tool': 'built-in image_gen',
                        'prompt': request['prompt'], 'transparent_background': False,
                        'status': 'candidate revision; not selected or integrated', 'visual_review': request['review']})
    for request, record in zip(requests, records):
        target = destination / record['file']
        shutil.copyfile(args.generated_root / request['generated'], target)
        assert target.stat().st_uid == 1000 and sha(target) == record['sha256']
        catalog['files'].append({'file': str(target.relative_to(ROOT / 'assets/hd')), 'sha256': sha(target),
                                 'bytes': target.stat().st_size, 'size': record['size'], 'status': 'candidate-revision-not-integrated',
                                 'tool': 'built-in imagegen', 'generated_source': request['generated'], 'source_file': record['source_file']})
    record_path.write_text(json.dumps({'kind': 'non-destructive candidate background layout revisions; original references remain local',
                                      'authorization': 'existing user scope: complete HD in style B and upload generated assets; repo visibility unchanged',
                                      'requests_sha256': sha(args.requests), 'records': records,
                                      'limits': 'stage horizon improved but exact source layout still needs review; no production format approval or native integration'},
                                     ensure_ascii=False, indent=2) + '\n')
    catalog['files'].append({'file': str(record_path.relative_to(ROOT / 'assets/hd')), 'sha256': sha(record_path),
                             'bytes': record_path.stat().st_size, 'status': 'candidate-revision-provenance'})
    assert catalog['files'][:102] == previous
    catalog['pngs'] = 96
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    for x in catalog['files']:
        p = ROOT / 'assets/hd' / x['file']
        assert sha(p) == x['sha256'] and p.stat().st_size == x['bytes']
    print(json.dumps({'pngs': 96, 'payload_entries': len(catalog['files']),
                      'payload_bytes': sum(x['bytes'] for x in catalog['files']), 'records_sha256': sha(record_path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
