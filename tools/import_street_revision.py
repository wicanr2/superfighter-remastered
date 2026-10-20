"""保存街道塗鴉修稿的原 PNG、精確請求與非破壞性候選分類。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops, ImageStat

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests', type=Path, required=True)
    parser.add_argument('--generated-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir() and a.output.parent.stat().st_uid == 1000
    requests = json.loads(a.requests.read_text())
    assert len(requests) == 2 and [x['selected'] for x in requests] == [False, True]
    destination = ROOT/'assets/hd/candidates'
    catalog_path = ROOT/'assets/hd/catalog.json'
    assert destination.stat().st_uid == catalog_path.stat().st_uid == 1000
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    assert len(previous) == 117 and catalog['pngs'] == 105
    for row in previous:
        p = ROOT/'assets/hd'/row['file']
        assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
    parent = destination/'street-i4.png'
    original = ROOT/'workplace/orig/I4.XGB'
    original_manifest = {x['name']: x['sha256'] for x in json.loads((ROOT/'workplace/source-manifest.json').read_text())['files']}
    parent_record = next(x for x in json.loads((destination/'backgrounds-source.json').read_text())['records'] if x['source_file'] == 'I4.XGB')
    assert sha(parent) == parent_record['sha256'] and sha(original) == original_manifest['I4.XGB']
    target = destination/'street-i4-v2.png'
    provenance = destination/'street-revision-source.json'
    assert not target.exists() and not provenance.exists()
    a.output.mkdir()
    history = []
    for request in requests:
        assert Path(request['generated']).name == request['generated']
        generated = a.generated_root/request['generated']
        assert generated.is_file() and not generated.is_symlink()
        with Image.open(generated) as image:
            image.verify()
        with Image.open(generated) as image:
            assert image.width >= 1600 and image.height >= 650 and abs(image.width/image.height-480/204) < .01
            assert image.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            size = list(image.size)
        local = a.output/('selected.png' if request['selected'] else 'rejected-first.png')
        shutil.copyfile(generated, local)
        history.append(dict(request, sha256=sha(local), size=size, local=local.name))
    selected = history[1]
    # 生成式局部修稿仍會重畫其他像素；量測差異，不宣稱區外 bytes 相同。
    old = Image.open(parent).convert('RGB')
    new = Image.open(a.output/'selected.png').convert('RGB')
    assert old.size == new.size
    difference = ImageChops.difference(old, new)
    outside = difference.copy()
    outside.paste((0, 0, 0), (950, 375, 1248, 435))
    metrics = {'same_dimensions': True, 'difference_bbox': difference.getbbox(),
               'mean_abs_RGB_difference': ImageStat.Stat(difference).mean,
               'outside_top_graffiti_mean_abs_RGB_difference': ImageStat.Stat(outside).mean,
               'outside_pixels_identical': outside.getbbox() is None,
               'limits': 'appearance review only; generated repaint does not preserve all non-text pixels exactly'}
    shutil.copyfile(a.output/'selected.png', target)
    source = {'kind': 'non-destructive street graffiti candidate revision, not production',
              'file': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size, 'size': selected['size'],
              'source_file': 'I4.XGB', 'source_sha256': sha(original),
              'parent_file': parent.name, 'parent_sha256': sha(parent),
              'tool': 'built-in image_gen', 'generated_source': selected['generated'],
              'prompt': selected['prompt'], 'transparent_background': False,
              'authorization': 'existing HD style B and generated-asset upload scope; repo visibility unchanged',
              'requested_text': 'SUPER STAR', 'interpretation_grade': 'strong inference from original graffiti glyphs, not decoded game text',
              'visual_review': '上排可辨讀 SUPER STAR，店名保持 SILVER SLIPPER / GRILL；下方塗鴉及完整構圖仍為候選，需依正常捲動畫面複核。',
              'repaint_metrics': metrics,
              'status': 'candidate revision; not selected or integrated',
              'limits': 'not exact glyph parity, native integration or formal collection format approval; previous PNG preserved'}
    provenance.write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n')
    catalog['files'].extend([
        {'file': str(target.relative_to(ROOT/'assets/hd')), 'sha256': sha(target), 'bytes': target.stat().st_size,
         'size': selected['size'], 'status': 'candidate-revision-not-integrated', 'tool': 'built-in imagegen',
         'generated_source': selected['generated'], 'source_file': 'I4.XGB'},
        {'file': str(provenance.relative_to(ROOT/'assets/hd')), 'sha256': sha(provenance), 'bytes': provenance.stat().st_size,
         'status': 'candidate-revision-provenance'}])
    catalog['pngs'] = 106
    assert catalog['files'][:117] == previous
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    for row in catalog['files']:
        p = ROOT/'assets/hd'/row['file']
        assert p.stat().st_uid == 1000 and sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
    (a.output/'history.json').write_text(json.dumps({'requests_sha256': sha(a.requests), 'importer_sha256': sha(Path(__file__)),
        'records': history, 'repaint_metrics': metrics, 'public_source_sha256': sha(provenance),
        'catalog_sha256': sha(catalog_path), 'previous_catalog_entries': previous}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'PNG_count': 106, 'catalog_entries': len(catalog['files']),
                      'payload_bytes': sum(x['bytes'] for x in catalog['files']), 'source_sha256': sha(provenance),
                      'repaint_metrics': metrics}, ensure_ascii=False))


if __name__ == '__main__':
    main()
