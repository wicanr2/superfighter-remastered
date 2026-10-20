"""審查或依 READY 加入二十一個第二色盤鍵，保留舊素材與生成 PNG bytes。"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
from PIL import Image
from prepare_hd_characters import atlas_regions

ROOT = Path('/project')
ART = ROOT / 'workplace/remaining-special-audit-v1/art-v1'
GROUPS = [
    ('phoenix-special-effects', 3, [15, 39, 56], [0, 1, 2], '-import.json'),
    ('lan-effects-a', 6, [9, 11, 12], [0, 1, 2], '-import.json'),
    ('lan-effects-b', 6, [20, 26, 57, 58], [0, 1, 2, 3], '-recheck.json'),
    ('clown-effects', 9, [14, 19, 49, 60, 61], [0, 1, 2, 6, 7], '-import.json'),
    ('clown-rings-v3', 9, [57, 58, 59], [2, 0, 1], '-import.json'),
    ('joe-effects', 10, [41, 42, 43], [0, 1, 2], '-import.json'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, default=ROOT / 'assets/hd/characters')
    p.add_argument('--output', type=Path)
    p.add_argument('--review-only', action='store_true')
    a = p.parse_args()
    base = json.loads((a.base / 'manifest.json').read_text())
    assert base['version'] == 3 and len(base['poses']) == 1495 and len(base['atlases']) == 68
    m = copy.deepcopy(base)
    selected = []
    for name, character, slots, order, suffix in GROUPS:
        request_path = ART / (name+'-request.json')
        request = json.loads(request_path.read_text())
        imported = json.loads((ART / (name+suffix)).read_text())
        png = ART / (name+'.png')
        assert sha(png) == imported['sha256'] and sha(request_path) == imported['request_sha256']
        with Image.open(png) as image:
            assert image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0
            regions = atlas_regions(image, *request['grid'])
            assert regions == imported['regions']
            atlas = {'file': name+'.png', 'sha256': sha(png), 'width': image.width, 'height': image.height}
        m['atlases'].append(atlas)
        source = ROOT / 'workplace/orig' / request['source_file']
        assert sha(source) == request['source_file_sha256']
        assert any(x['character'] == character and x.get('source_bank', '') == '' and x['sha256'] == sha(source) for x in base['sources'])
        raw = source.read_bytes()
        poses = []
        for slot, ordinal in zip(slots, order):
            assert not any(x['character'] == character and x['slot'] == slot and x.get('palette_bank', 0) == 1 for x in m['poses'])
            segment, offset = struct.unpack_from('<HH', raw, 0xb28+slot*4)
            at = 0xc48+segment*16+offset
            width, height = raw[at:at+2]
            end = at+2+(width+1)//2*height
            proof = next(x for x in request['records'] if x['slot'] == slot)
            digest = hashlib.sha256(raw[at:end]).hexdigest()
            assert at == proof['source_offset'] and digest == proof['source_sha256']
            pose = {'character': character, 'palette_bank': 1, 'slot': slot, 'width': width, 'height': height,
                    'source_offset': at, 'source_sha256': digest, 'atlas': name+'.png', 'rect': regions[ordinal]['rect']}
            m['poses'].append(pose)
            poses.append({'slot': slot, 'region_ordinal': ordinal, 'source_offset': at, 'source_sha256': digest,
                          'width': width, 'height': height, 'rect': regions[ordinal]['rect']})
        selected.append({'file': name+'.png', 'sha256': sha(png), 'size': [atlas['width'], atlas['height']],
                         'character': character, 'source_file': source.name, 'source_file_sha256': sha(source),
                         'request_sha256': sha(request_path), 'prompt': request['prompt'], 'grid': request['grid'],
                         'poses': poses, 'unused_regions': sorted(set(range(len(regions)))-set(order))})
    m['evidence'].append('docs/spec/044-remaining-special-effects.md')
    encoded = (json.dumps(m, ensure_ascii=False, indent=2)+'\n').encode()
    pixels = sum(x['width']*x['height'] for x in m['atlases'])
    plan = {'kind': 'prospective read-only asset capacity and source review', 'poses': len(m['poses']),
            'atlases': len(m['atlases']), 'new_keys': 21, 'manifest_bytes': len(encoded), 'atlas_pixels': pixels,
            'minimum_Mi_pixels': (pixels+1048575)//1048576, 'minimum_8KiB_manifest_units': (len(encoded)+8191)//8192,
            'base_manifest_sha256': sha(a.base/'manifest.json'), 'selected': selected, 'preparer_sha256': sha(Path(__file__))}
    if a.review_only:
        (ART/'capacity-review.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({k: v for k, v in plan.items() if k != 'selected'}, ensure_ascii=False))
        return
    review = json.loads((ART/'evidence-review.json').read_text())
    assert review['status'] == 'READY' and review['base_manifest_sha256'] == plan['base_manifest_sha256']
    assert sha(ART/'capacity-review.json') == review['capacity_review_sha256']
    for name, digest in review['inputs'].items():
        assert sha(ROOT/name) == digest, name
    assert a.output and not a.output.exists() and a.output.parent.stat().st_uid == 1000
    assert len(encoded) <= review['manifest_limit_bytes'] and pixels <= review['atlas_limit_Mi_pixels']*1048576
    assert len(m['poses']) == 1516 and len(m['atlases']) == 74 and m['poses'][:1495] == base['poses']
    a.output.mkdir()
    for source in a.base.iterdir():
        assert source.is_file() and not source.is_symlink()
        if source.name != 'manifest.json':
            shutil.copyfile(source, a.output/source.name)
            assert sha(source) == sha(a.output/source.name)
    for item in selected:
        assert not (a.output/item['file']).exists()
        shutil.copyfile(ART/item['file'], a.output/item['file'])
        assert sha(a.output/item['file']) == item['sha256']
    (a.output/'manifest.json').write_bytes(encoded)
    provenance = {'kind': 'ordinary-input second-palette generated effects, not shortcut enablement',
                  'tool': 'built-in imagegen', 'base_manifest_sha256': plan['base_manifest_sha256'],
                  'evidence_review_sha256': sha(ART/'evidence-review.json'), 'preparer_sha256': sha(Path(__file__)),
                  'records': selected, 'rights': 'user authorized HD generation and repo upload; originals, palettes and CPU receipts local only',
                  'limits': '21 declared source keys, unregistered discarded cells never drawn; full animation and remaining palette transitions separate'}
    (a.output/'remaining-special-effects-source.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in plan.items() if k != 'selected'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
