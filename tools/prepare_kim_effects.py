"""依 READY 審查加入金太極十份第二色盤原圖，保留所有舊姿態與 PNG。"""
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
SLOTS = (6, 37, 49, 50, 51, 52, 53, 54, 55, 56)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=ROOT / 'assets/hd/characters')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and args.output.parent.is_dir() and args.output.parent.stat().st_uid == 1000
    art = ROOT / 'workplace/kim-effects-art-v1'
    review = json.loads((art / 'evidence-review.json').read_text())
    assert review['status'] == 'READY' and sha(args.base / 'manifest.json') == review['base_manifest_sha256']
    for name, wanted in review['inputs'].items():
        assert sha(ROOT / name) == wanted, name
    base = json.loads((args.base / 'manifest.json').read_text())
    assert base['version'] == 3 and len(base['poses']) == 1485 and len(base['atlases']) == 67
    manifest = copy.deepcopy(base)
    data = (ROOT / 'workplace/orig/SFMAN08.DAT').read_bytes()
    assert hashlib.sha256(data).hexdigest() == '5579dee3e846d65905db84d769fae4378051e1a5cec74bed509885754cef165c'
    png = art / 'kim-effects.png'
    image = Image.open(png)
    assert image.mode == 'RGBA' and image.getchannel('A').getextrema() == (0, 255)
    regions = atlas_regions(image, 5, 2)
    assert regions == json.loads((art / 'regions.json').read_text())
    manifest['atlases'].append({'file': 'kim-effects.png', 'sha256': sha(png), 'width': image.width, 'height': image.height})
    for slot, region in zip(SLOTS, regions):
        assert not any(x['character'] == 7 and x.get('palette_bank', 0) == 1 and x['slot'] == slot for x in manifest['poses'])
        segment, offset = struct.unpack_from('<HH', data, 0xb28 + slot * 4)
        at = 0xc48 + segment * 16 + offset
        width, height = data[at:at + 2]
        end = at + 2 + (width + 1) // 2 * height
        manifest['poses'].append({'character': 7, 'palette_bank': 1, 'slot': slot, 'width': width, 'height': height,
                                  'source_offset': at, 'source_sha256': hashlib.sha256(data[at:end]).hexdigest(),
                                  'atlas': 'kim-effects.png', 'rect': region['rect']})
    manifest['evidence'].append('docs/spec/042-kim-effects.md')
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    pixels = sum(x['width'] * x['height'] for x in manifest['atlases'])
    assert pixels == 105769615 and pixels <= 101 * 1024 * 1024 and len(encoded) <= 512 * 1024
    assert manifest['poses'][:1485] == base['poses'] and len(manifest['poses']) == 1495
    args.output.mkdir()
    for p in args.base.iterdir():
        assert p.is_file() and not p.is_symlink()
        if p.name != 'manifest.json':
            shutil.copyfile(p, args.output / p.name)
            assert sha(p) == sha(args.output / p.name)
    shutil.copyfile(png, args.output / 'kim-effects.png')
    (args.output / 'manifest.json').write_bytes(encoded)
    provenance = {'kind': 'Kim normal-input second-palette effects, generated PNG bytes preserved',
                  'tool_sha256': sha(Path(__file__)), 'base_manifest_sha256': sha(args.base / 'manifest.json'),
                  'source_file': 'SFMAN08.DAT', 'source_sha256': hashlib.sha256(data).hexdigest(),
                  'request': json.loads((art / 'request.json').read_text()), 'image_sha256': sha(png),
                  'evidence_review_sha256': sha(art / 'evidence-review.json'), 'regions': regions,
                  'registered_effect_slots': list(SLOTS), 'limits': 'ten sources in declared normal keyboard sequences; not complete animation or quick-move enablement',
                  'rights': 'user authorized HD generation and repository upload; original references/palettes/CPU sidecars stay local'}
    (args.output / 'kim-effects-source.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'poses': 1495, 'atlases': 68, 'manifest_bytes': len(encoded), 'atlas_pixels': pixels,
                      'manifest_sha256': sha(args.output / 'manifest.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
