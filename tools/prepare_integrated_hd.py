"""Docker 內建立 049 的公開素材索引；原版只讀取雜湊，不輸出原始像素。"""
import hashlib
import json
from pathlib import Path

from PIL import Image
from hd_source_probe import decode_candidate

ROOT = Path('/project')
ART = ROOT / 'assets/hd'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    assert ROOT.stat().st_uid == 1000
    files = ['I5.XGB', 'I12.XGB', 'I4.XGB', 'I7.XGB', 'I2.XGB', 'I3.XGB', 'I10.XGB', 'I9.XGB', 'I8.XGB', 'I1.XGB', 'I13.XGB']
    candidates = json.loads((ART / 'candidates/backgrounds-source.json').read_text())['records']
    images = {r['source_file']: 'candidates/' + r['file'] for r in candidates}
    images.update({'I2.XGB': 'backgrounds/rooftop.png'})
    dojo = [p for p in ART.rglob('*.png') if 'dojo' in p.name]
    assert len(dojo) == 1
    images['I5.XGB'] = str(dojo[0].relative_to(ART))
    images.update({'I4.XGB': 'candidates/street-i4-v2.png', 'I10.XGB': 'candidates/grotto-i10-v2.png', 'I8.XGB': 'candidates/auditorium-i8-v2.png'})
    definitions = []
    for scene, source in enumerate(files):
        original = ROOT / 'workplace/orig' / source
        width, height, palette, indices = decode_candidate(original.read_bytes())
        assert (width, height) == (480, 204)
        rgb = bytes(v * 4 + v // 16 for v in palette[:384])
        image = ART / images[source]
        with Image.open(image) as art:
            iw, ih = art.size
        definitions.append(dict(scene=scene, source=source, source_sha256=sha(original),
                                reference_sha256=hashlib.sha256(indices).hexdigest(), palette_sha256=hashlib.sha256(rgb).hexdigest(),
                                image_file=images[source], image_sha256=sha(image), image_width=iw, image_height=ih))
    write(ROOT / 'internal/hd/background-sources.json', definitions)
    screens = []

    def add(key, name):
        file = ART / name
        with Image.open(file) as image:
            width, height = image.size
        screens.append(dict(key=key, file=name, sha256=sha(file), width=width, height=height))

    add('title-person', 'candidates/title-person-v1.png')
    add('title-logo', 'candidates/title-logo-v1.png')
    add('selection-vs', 'candidates/selection-vs-v1.png')
    for prefix, manifest in [('left', 'selection-portraits-source.json'), ('right', 'result-portraits-source.json')]:
        for i, row in enumerate(json.loads((ART / 'candidates' / manifest).read_text())['records']):
            assert sha(ART / 'candidates' / row['file']) == row['sha256']
            add(f'{prefix}-{i}', 'candidates/' + row['file'])
    add('paper', 'candidates/result-newspaper-v1.png')
    for i in range(7):
        add(f'flag-{i}', f'candidates/result-flag-{i:02d}-v1.png')
    assert len(screens) == 33
    write(ART / 'screens.json', dict(version=1, kind='hd-screen-art', images=screens))
    print(json.dumps(dict(backgrounds=len(definitions), screen_images=len(screens))))


if __name__ == '__main__':
    main()
