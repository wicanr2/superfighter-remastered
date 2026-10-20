"""保存 VS 生成原 PNG 與完整提示詞，不接入正式遊戲。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--generated-root', type=Path, required=True)
    a = p.parse_args()
    request = json.loads(a.request.read_text())
    generated = a.generated_root/Path(request['generated']).name
    target = ROOT/'assets/hd/candidates/selection-vs-v1.png'
    provenance = ROOT/'assets/hd/candidates/selection-vs-source.json'
    catalog_path = ROOT/'assets/hd/catalog.json'
    assert not target.exists() and not provenance.exists()
    assert target.parent.stat().st_uid == catalog_path.stat().st_uid == 1000
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    for row in previous:
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    assert sha(ROOT/'workplace/orig/SELMAN.CPM') == '9b40caeee1eff32370a6826e1362087ae1da086237731f06de905d696b6c195a'
    reference = ROOT/'workplace/selection-screen-preview-v1/vs-reference.png'
    with Image.open(generated) as image:
        image.verify()
    with Image.open(generated) as image:
        assert image.mode == 'RGBA' and image.width >= 1200 and image.height >= 800
        alpha = image.getchannel('A')
        assert alpha.getextrema() == (0, 255)
        size = list(image.size)
        bounds = alpha.point(lambda v: 255 if v >= 16 else 0).getbbox()
    shutil.copyfile(generated, target)
    assert sha(target) == sha(generated) and target.stat().st_uid == 1000
    record = {'kind': 'candidate HD VS lettering, not integrated', 'file': target.name,
        'sha256': sha(target), 'bytes': target.stat().st_size, 'size': size, 'alpha_16_bounds': list(bounds),
        'source_file': 'SELMAN.CPM', 'source_sha256': sha(ROOT/'workplace/orig/SELMAN.CPM'),
        'reference_logical_crop': [110, 40, 203, 98], 'reference_scale': 8,
        'reference_sha256': sha(reference), 'tool': 'built-in image_gen', 'model_version': 'not exposed by tool',
        'prompt': request['prompt'], 'transparent_background': True, 'generated_source': generated.name,
        'importer_sha256': sha(Path(__file__)),
        'review': '已目視紅底金邊 VS，S 曲線與 V 的比例為重繪近似；未視覺定版，沒有改寫生成原 bytes。',
        'rights': 'new generated derivative art; original game data stays local; repository visibility unchanged'}
    provenance.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    for path, status in ((target, 'candidate-selection-vs-not-integrated'), (provenance, 'candidate-selection-vs-provenance')):
        row = {'file': str(path.relative_to(ROOT/'assets/hd')), 'sha256': sha(path),
               'bytes': path.stat().st_size, 'status': status}
        if path == target:
            row.update(size=size, tool='built-in imagegen', generated_source=generated.name)
        catalog['files'].append(row)
    catalog['pngs'] += 1
    assert catalog['files'][:-2] == previous
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'file': str(target.relative_to(ROOT)), 'sha256': sha(target), 'size': size,
                      'PNG_count': catalog['pngs'], 'catalog_entries': len(catalog['files']),
                      'asset_payload_bytes': sum(row['bytes'] for row in catalog['files'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
