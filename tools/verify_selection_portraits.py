"""獨立核對十一張私有原肖像解碼、生成原 bytes、候選清單及純 HD 預覽來源。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path('/project')
IDS = ['jaan', 'sarkov', 'bullet', 'phoenix', 'frank', 'onimaru', 'lan', 'kim', 'spider', 'clown', 'joe']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--imported', type=Path, required=True)
    a = p.parse_args()
    source_path = ROOT/'assets/hd/candidates/selection-portraits-source.json'
    source = json.loads(source_path.read_text())
    references = json.loads((a.references/'references.json').read_text())
    imported = json.loads((a.imported/'receipt.json').read_text())
    catalog = json.loads((ROOT/'assets/hd/catalog.json').read_text())
    assert len(source['records']) == len(references['records']) == 11
    assert [r['id'] for r in source['records']] == [r['id'] for r in references['records']] == IDS
    assert len(catalog['files']) == 131 and catalog['pngs'] == 117
    assert catalog['files'][:119] == imported['previous_catalog_entries']
    assert sha(source_path) == imported['source_sha256']
    assert sha(ROOT/'assets/hd/catalog.json') == imported['catalog_sha256']
    assert sha(ROOT/'tools/export_selection_portraits.py') == references['exporter_sha256']
    assert sha(ROOT/'tools/import_selection_portraits.py') == imported['importer_sha256'] == source['importer_sha256']
    assert sha(a.references/'references.json') == imported['references_sha256'] == source['references_receipt_sha256']
    original = ROOT/'workplace/orig/BIGFIG.XBB'
    assert sha(original) == source['source_sha256'] == '4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477'
    data = original.read_bytes()
    assert len(data) == 11*8689
    proofs = []
    for index, (row, ref) in enumerate(zip(source['records'], references['records'])):
        start = index*8689
        palette = data[start:start+96]
        pixels = data[start+768:start+8689]
        rgb = bytes(v*4+v//16 for value in pixels for v in palette[value*3:value*3+3])
        assert len(rgb) == 89*89*3
        reference = a.references/ref['reference']
        assert Image.open(reference).convert('RGB').tobytes() == rgb
        assert sha(reference) == ref['reference_sha256']
        assert row['index'] == ref['index'] == index and row['source_file'] == 'BIGFIG.XBB'
        assert row['record_file_offset'] == ref['record_file_offset'] == start
        assert row['pixels_file_offset'] == ref['pixels_file_offset'] == start+768
        assert hashlib.sha256(pixels).hexdigest() == ref['pixels_sha256'] == row['original_pixels_sha256']
        assert hashlib.sha256(palette).hexdigest() == ref['palette_sha256'] == row['original_palette_sha256']
        target = ROOT/'assets/hd/candidates'/row['file']
        assert sha(target) == row['sha256'] and target.stat().st_size == row['bytes']
        assert row['status'] == 'candidate portrait; not approved or integrated' and row['tool'] == 'built-in image_gen'
        assert row['prompt'] and row['transparent_background'] is False
        assert row['style_reference'] == (None if index == 0 else 'selection-jaan-v1.png')
        registered = next(x for x in catalog['files'] if x['file'] == str(target.relative_to(ROOT/'assets/hd')))
        assert registered['character'] == IDS[index] and registered['sha256'] == sha(target)
        with Image.open(target) as image:
            image.verify()
        with Image.open(target) as image:
            assert list(image.size) == row['size'] == [1254, 1254]
            assert image.convert('RGBA').getchannel('A').getextrema() == (255, 255)
            assert image.convert('RGB').tobytes() != Image.frombytes('RGB', (89, 89), rgb).resize(image.size, Image.Resampling.NEAREST).tobytes()
        proofs.append({'id': IDS[index], 'original_rgb_matches': True, 'candidate_sha256': sha(target), 'size': row['size']})
    assert len({x['candidate_sha256'] for x in proofs}) == 11
    preview = ROOT/source['preview']['file']
    assert sha(preview) == source['preview']['sha256'] == imported['preview_sha256']
    assert Image.open(preview).size == (1200, 1040)
    screenshots = json.loads((ROOT/'docs/screenshots/source.json').read_text())
    screenshot = next(x for x in screenshots['prototype_captures'] if x['file'] == preview.name)
    assert screenshot['source_sha256'] == sha(source_path) and screenshot['sha256'] == sha(preview)
    assert screenshot['kind'] == 'HD art contact sheet, not native capture or original-mode art'
    assert sha(a.imported/'original-vs-candidate.png') == imported['private_comparison_sha256']
    result = {'kind': 'independent portrait source and generated-asset identity review', 'status': 'passed',
              'portraits': 11, 'original_RGB_reconstructions': 11, 'proofs': proofs,
              'source_sha256': sha(source_path), 'import_receipt_sha256': sha(a.imported/'receipt.json'),
              'verifier_sha256': sha(Path(__file__)), 'preview_sha256': sha(preview),
              'previous_catalog_entries_unchanged': 119,
              'limits': 'source bytes, mapping and PNG identity only; visual likeness is approximate and pending approval; no native integration or complete HD claim'}
    report = a.imported/'comparison.json'
    assert not report.exists()
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'proofs'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
