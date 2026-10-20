"""在 Docker 內收錄已去背的蜘蛛女候選，不修改正式角色對照表。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--incoming-root', type=Path, required=True)
    parser.add_argument('--project', type=Path, default=Path('/project'))
    args = parser.parse_args()
    p, incoming = args.project, args.incoming_root
    destination = p / 'assets/hd/candidates/spider'
    assert not destination.exists() and destination.parent.is_dir()
    assert destination.parent.stat().st_uid == 1000
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    catalog_path = p / 'assets/hd/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    baseline = {entry['file']: entry['sha256'] for entry in catalog['files']}
    for file, digest in baseline.items():
        assert sha(p / 'assets/hd' / file) == digest
    runtime_hash = sha(p / 'assets/hd/characters/manifest.json')
    batches = [
        ('atlases-v1', 'transparent-v1', 'spider-hd-png', 5),
        ('cels-v2', 'spider-normal-hd-png-v2-transparent-v1', 'spider-normal-hd-png-v2', 10),
    ]
    observed = {
        0: ('低位跪伏，正面視角', 'needs-pose-review'),
        1: ('雙手觸地低伏', 'needs-pose-review'),
        21: ('俯臥，一腿抬起', 'needs-pose-review'),
        24: ('彩色水平細條', 'filename-pose-mismatch'),
        29: ('空中蜷身', 'filename-pose-mismatch'),
        33: ('跪蹲', 'filename-pose-mismatch'),
        34: ('橫向俯臥', 'filename-pose-mismatch'),
        41: ('仰身空中姿勢', 'filename-pose-mismatch'),
        43: ('紫黃色尖形特效', 'filename-pose-mismatch'),
        44: ('空中人物姿勢', 'filename-pose-mismatch'),
    }
    references = json.loads((p / 'workplace/spider-source-v1/manifest.json').read_text())
    source_cells = {cell['slot']: cell for cell in references['cells']}
    records = []
    destination.mkdir()
    for batch, processed_name, original_name, count in batches:
        manifest_path = incoming / processed_name / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        assert manifest['original_files_unchanged'] and len(manifest['files']) == count
        (destination / batch).mkdir()
        for record in manifest['files']:
            name = record['file']
            assert Path(name).name == name and name.endswith('.png')
            src = incoming / processed_name / name
            original = incoming / original_name / name
            assert sha(src) == record['output_sha256']
            assert sha(original) == record['input_sha256']
            with Image.open(original) as raw, Image.open(src) as clean:
                assert raw.mode == clean.mode == 'RGBA'
                assert list(raw.size) == list(clean.size) == record['size']
                before, after = raw.tobytes(), clean.tobytes()
                assert all(before[channel::4] == after[channel::4] for channel in range(3))
                assert all(b == a or b == 0 for a, b in zip(before[3::4], after[3::4]))
                assert clean.getchannel('A').getextrema() == (0, 255)
                size = list(clean.size)
            dest = destination / batch / name
            shutil.copyfile(src, dest)
            assert sha(dest) == record['output_sha256'] and dest.stat().st_uid == 1000
            relative = str(dest.relative_to(p / 'assets/hd'))
            item = {
                'file': f'{batch}/{name}', 'batch': batch,
                'size': size, 'bytes': dest.stat().st_size, 'sha256': sha(dest),
                'generator': 'external model supplied by user; model/version not supplied',
                'raw_input_sha256': record['input_sha256'],
                'local_input': f'../spider-woman-hd/{original_name}/{name}',
                'local_processed_input': f'../spider-woman-hd/{processed_name}/{name}',
                'processing_script_sha256': manifest['script_sha256'],
                'processing_manifest_sha256': sha(manifest_path),
                'newly_transparent_pixels': record['newly_transparent_pixels'],
                'rgb_and_dimensions_unchanged': True,
                'runtime_registered': False,
            }
            if batch == 'cels-v2':
                slot = int(Path(name).stem.rsplit('-', 1)[1])
                cell = source_cells[slot]
                item.update(filename_claimed_normal_slot=slot,
                            observed_content=observed[slot][0], review_status=observed[slot][1],
                            original_source_size=[cell['width'], cell['height']],
                            original_packed_sha256=cell['source_sha256'])
            else:
                item['review_status'] = 'sheet-order-and-pose-review-required'
            records.append(item)
            catalog['files'].append({
                'file': relative, 'sha256': sha(dest), 'bytes': dest.stat().st_size,
                'size': size, 'status': 'candidate-character-not-registered',
                'tool': 'local Python/Pillow alpha-only processing of user-provided external-model art',
                'source_index': 'candidates/spider/source.json',
            })
    provenance = {
        'version': 1, 'kind': 'candidate art inventory; not runtime character pack',
        'authorization': 'user requested that HD art be stored in existing GitHub repository',
        'processing': 'only connected light-gray background alpha removed; RGB unchanged',
        'import_script_sha256': sha(Path(__file__)),
        'files': records, 'runtime_registered_keys': 0,
        'original_reference_pngs_included': False,
        'raw_external_inputs_included': False,
        'limits': 'filenames are input labels, not accepted source-to-animation mappings',
    }
    source = destination / 'source.json'
    source.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    catalog['files'].append({'file': 'candidates/spider/source.json', 'sha256': sha(source),
                             'bytes': source.stat().st_size, 'status': 'candidate-source-metadata',
                             'tool': 'tools/import_spider_candidates.py'})
    catalog['pngs'] = sum(entry['file'].endswith('.png') for entry in catalog['files'])
    assert catalog['pngs'] == 82 and len(catalog['files']) == 86
    assert len({entry['file'] for entry in catalog['files']}) == len(catalog['files'])
    assert sha(p / 'assets/hd/characters/manifest.json') == runtime_hash
    for file, digest in baseline.items():
        assert sha(p / 'assets/hd' / file) == digest
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    receipt = {'imported_pngs': len(records), 'catalog_pngs': catalog['pngs'],
               'catalog_entries': len(catalog['files']),
               'payload_bytes': sum(entry['bytes'] for entry in catalog['files']),
               'runtime_manifest_sha256': runtime_hash, 'runtime_pack_unchanged': True,
               'source_index_sha256': sha(source)}
    (p / 'workplace/spider-art-v1/repo-import-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
