"""依已驗 025 的 BIGFIG.XBB 契約匯出十一張私有原肖像，供 HD 候選參考。"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw

ROOT = Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    source = ROOT/'workplace/orig/BIGFIG.XBB'
    manifest = json.loads((ROOT/'workplace/source-manifest.json').read_text())
    expected = next(x['sha256'] for x in manifest['files'] if x['name'] == source.name)
    assert sha(source) == expected
    identities = re.findall(r'\{"([a-z]+)", "([^"]+)", \[\]string', (ROOT/'internal/controls/settings.go').read_text())
    assert len(identities) == 11 and len(set(x[0] for x in identities)) == 11
    data = source.read_bytes()
    assert len(data) == 11*0x21f1
    a.output.mkdir()
    contact = Image.new('RGB', (4*267, 3*291), '#151c28')
    labels = ImageDraw.Draw(contact)
    records = []
    for index, (identity, name) in enumerate(identities):
        start = index*0x21f1
        palette = data[start:start+0x60]
        pixels = data[start+0x300:start+0x21f1]
        assert len(pixels) == 89*89 and max(pixels) < 32 and max(palette) <= 63
        rgb = bytes(v*4+v//16 for v in palette)
        image = Image.frombytes('P', (89, 89), pixels)
        image.putpalette(rgb+bytes(768-len(rgb)))
        image = image.convert('RGB')
        target = a.output/(identity+'-original.png')
        image.save(target)
        x, y = index%4*267, index//4*291
        labels.text((x+6, y+5), f'{index}: {identity}', fill='white')
        contact.paste(image.resize((267, 267), Image.Resampling.NEAREST), (x, y+24))
        records.append({'index': index, 'id': identity, 'name': name, 'source': source.name,
                        'source_sha256': expected, 'record_file_offset': start,
                        'pixels_file_offset': start+0x300, 'size': [89, 89],
                        'pixels_sha256': hashlib.sha256(pixels).hexdigest(),
                        'palette_sha256': hashlib.sha256(palette).hexdigest(),
                        'reference': target.name, 'reference_sha256': sha(target)})
    contact.save(a.output/'original-contact.png')
    result = {'kind': 'private original selection portraits; not HD artwork or runtime evidence',
              'source_sha256': expected, 'exporter_sha256': sha(Path(__file__)), 'records': records,
              'consumer_evidence': 'docs/spec/025-boss-selection.md: sub_10E86; original file offsets distinct from IDA MZ linear',
              'limits': 'raw originals stay local; no format approval, generation, integration or complete normal-player-path claim'}
    (a.output/'references.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'portraits': len(records), 'source_sha256': expected, 'output': str(a.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
