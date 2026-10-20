"""保存十一人選角肖像生成原 PNG、來源與提示詞，另作候選預覽，不改正式格式。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--requests', type=Path, required=True)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--generated-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    references = json.loads((a.references/'references.json').read_text())
    requests = json.loads(a.requests.read_text())
    assert len(requests) == len(references['records']) == 11
    assert [r['id'] for r in requests] == [r['id'] for r in references['records']]
    assert sha(ROOT/'workplace/orig/BIGFIG.XBB') == references['source_sha256']
    assert sha(ROOT/'tools/export_selection_portraits.py') == references['exporter_sha256']
    catalog_path = ROOT/'assets/hd/catalog.json'
    destination = ROOT/'assets/hd/candidates'
    screenshots = ROOT/'docs/screenshots'
    source_path = destination/'selection-portraits-source.json'
    preview_path = screenshots/'selection-portrait-candidates.png'
    screenshot_source = screenshots/'source.json'
    assert not source_path.exists() and not preview_path.exists()
    assert all(p.stat().st_uid == 1000 for p in (catalog_path, destination, screenshots, screenshot_source))
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    assert len(previous) == 119 and catalog['pngs'] == 106
    for row in previous:
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    prepared = []
    for request, reference in zip(requests, references['records']):
        original = a.references/reference['reference']
        assert sha(original) == reference['reference_sha256']
        generated = a.generated_root/Path(request['generated']).name
        assert generated.is_file() and not generated.is_symlink()
        target = destination/('selection-'+request['id']+'-v1.png')
        assert not target.exists()
        with Image.open(generated) as image:
            image.verify()
        with Image.open(generated) as image:
            assert 896 <= image.width <= 2048 and image.width == image.height
            assert image.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            size = list(image.size)
        prepared.append((request, reference, generated, target, size))
    a.output.mkdir()
    public = Image.new('RGB', (1200, 1040), '#151c28')
    comparison = Image.new('RGB', (1602, 1196), '#151c28')
    font = ImageFont.truetype(str(ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'), 19)
    heading = '十一人選角肖像 HD 候選，尚未接入正式程式'
    draw = ImageDraw.Draw(public)
    assert draw.textbbox((0, 0), heading, font=font)[2] <= 1176
    draw.text((12, 7), heading, font=font, fill='white')
    private_draw = ImageDraw.Draw(comparison)
    records = []
    for index, (request, reference, generated, target, size) in enumerate(prepared):
        shutil.copyfile(generated, target)
        assert sha(target) == sha(generated) and target.stat().st_uid == 1000
        image = Image.open(target).convert('RGB')
        x, y = index%4*300, 44+index//4*332
        label = reference['name']+' / '+request['id']
        assert draw.textbbox((0, 0), label, font=font)[2] <= 288
        draw.text((x+6, y+1), label, font=font, fill='white')
        public.paste(image.resize((300, 300), Image.Resampling.LANCZOS), (x, y+32))
        x, y = index%3*534, index//3*299
        private_draw.text((x+6, y+2), request['id']+' ORIGINAL / HD CANDIDATE', fill='white')
        comparison.paste(Image.open(a.references/reference['reference']).convert('RGB').resize((267, 267), Image.Resampling.NEAREST), (x, y+32))
        comparison.paste(image.resize((267, 267), Image.Resampling.LANCZOS), (x+267, y+32))
        records.append({'file': target.name, 'id': request['id'], 'name': reference['name'], 'index': reference['index'],
                        'sha256': sha(target), 'bytes': target.stat().st_size, 'size': size,
                        'source_file': 'BIGFIG.XBB', 'source_sha256': references['source_sha256'],
                        'record_file_offset': reference['record_file_offset'], 'pixels_file_offset': reference['pixels_file_offset'],
                        'original_size': reference['size'], 'original_pixels_sha256': reference['pixels_sha256'],
                        'original_palette_sha256': reference['palette_sha256'],
                        'tool': 'built-in image_gen', 'model_version': 'not exposed by tool',
                        'generated_source': generated.name, 'prompt': request['prompt'], 'transparent_background': False,
                        'style_reference': None if index == 0 else 'selection-jaan-v1.png',
                        'status': 'candidate portrait; not approved or integrated',
                        'visual_review': '角色辨識特徵已初步目視；五官、裁切、細節及等尺寸 UI 仍待定版，不稱精確原版肖像。'})
        catalog['files'].append({'file': str(target.relative_to(ROOT/'assets/hd')), 'sha256': sha(target), 'bytes': target.stat().st_size,
                                 'size': size, 'status': 'candidate-selection-portrait-not-integrated', 'tool': 'built-in imagegen',
                                 'source_file': 'BIGFIG.XBB', 'character': request['id'], 'generated_source': generated.name})
    public.save(preview_path)
    comparison.save(a.output/'original-vs-candidate.png')
    source = {'kind': 'eleven candidate HD selection portraits; original references stay local',
              'authorization': 'existing style B and HD generated-asset upload scope; repo visibility unchanged',
              'source_file': 'BIGFIG.XBB', 'source_sha256': references['source_sha256'],
              'references_receipt_sha256': sha(a.references/'references.json'), 'requests_sha256': sha(a.requests),
              'importer_sha256': sha(Path(__file__)), 'records': records,
              'preview': {'file': 'docs/screenshots/'+preview_path.name, 'sha256': sha(preview_path)},
              'limits': 'new painted approximations; not approval, runtime asset schema, native selection integration, full HD, or animation artwork'}
    source_path.write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n')
    catalog['files'].append({'file': str(source_path.relative_to(ROOT/'assets/hd')), 'sha256': sha(source_path),
                             'bytes': source_path.stat().st_size, 'status': 'candidate-selection-portrait-provenance'})
    catalog['pngs'] = 117
    assert catalog['files'][:119] == previous and len(catalog['files']) == 131
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
    screenshots_meta = json.loads(screenshot_source.read_text())
    screenshots_meta['prototype_captures'].append({'kind': 'HD art contact sheet, not native capture or original-mode art',
        'file': preview_path.name, 'sha256': sha(preview_path), 'source': 'assets/hd/candidates/selection-portraits-source.json',
        'source_sha256': sha(source_path), 'renderer': 'tools/import_selection_portraits.py', 'renderer_sha256': sha(Path(__file__)),
        'platform': 'Pillow 11.3.0 in Docker; not runtime or platform acceptance',
        'authorization': 'user requested HD upload and GitHub-visible pictures',
        'limits': 'candidate art only, no original images or palette; not formal selection UI or integration'})
    screenshot_source.write_text(json.dumps(screenshots_meta, ensure_ascii=False, indent=2)+'\n')
    result = {'requests_sha256': sha(a.requests), 'references_sha256': sha(a.references/'references.json'),
              'importer_sha256': sha(Path(__file__)), 'previous_catalog_entries': previous,
              'source_sha256': sha(source_path), 'catalog_sha256': sha(catalog_path),
              'preview_sha256': sha(preview_path), 'private_comparison_sha256': sha(a.output/'original-vs-candidate.png'),
              'records': records, 'PNG_count': 117, 'catalog_entries': 131,
              'asset_payload_bytes': sum(x['bytes'] for x in catalog['files'])}
    (a.output/'receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('records', 'previous_catalog_entries')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
