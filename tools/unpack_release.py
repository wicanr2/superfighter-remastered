"""在 Docker 內將已驗封包解至全新測試目錄，保留執行權限並建立啟動索引。"""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path('/project')
    version = (root / 'VERSION').read_text().strip()
    delivery = root / 'dist-all' / version
    records = json.loads((delivery / 'SHA256SUMS.json').read_text())
    assert records['version'] == version
    args.output.mkdir(parents=True, exist_ok=False)
    extracted = []
    for item in records['files']:
        source = delivery / item['file']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256']
        dest = args.output / (item['platform'] + '-' + item['kind'])
        dest.mkdir()
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                path = Path(info.filename)
                assert not path.is_absolute() and '..' not in path.parts
                assert (info.external_attr >> 16) & 0o170000 == 0o100000
                target = dest / path
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as incoming, target.open('xb') as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                target.chmod((info.external_attr >> 16) & 0o777)
        manifests = list(dest.glob('*/manifest.json'))
        assert len(manifests) == 1
        manifest = json.loads(manifests[0].read_text())
        package = manifests[0].parent
        assert (manifest['version'], manifest['platform'], manifest['kind']) == (version, item['platform'], item['kind'])
        for name, record in manifest['files'].items():
            assert hashlib.sha256((package / name).read_bytes()).hexdigest() == record['sha256']
        if item['platform'].startswith('macos'):
            info = plistlib.loads((package / 'Superfighter Remastered.app/Contents/Info.plist').read_bytes())
            assert info['SuperfighterReleaseVersion'] == version
            assert info['CFBundleShortVersionString'] == version[2:].split('-')[0]
        extracted.append(dict(platform=item['platform'], kind=item['kind'], root=str(package), binary=str(package / manifest['binary'])))
    (args.output / 'extracted.json').write_text(json.dumps(extracted, indent=2) + '\n')
    print(json.dumps(dict(version=version, packages=len(extracted), index=str(args.output / 'extracted.json'))))


if __name__ == '__main__':
    main()
