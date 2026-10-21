"""建立隔離原生驗證目錄；原版另掛，選填的原音 OGG 只留本機。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import build_desktop

ROOT=Path('/project')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--audio-root',type=Path)
    a=p.parse_args()
    build=json.loads(a.binary.with_name(a.binary.name+'.build.json').read_text())
    assert build['binary_sha256']==sha(a.binary)
    assert build['compiled_inputs']==build_desktop.compiled_inputs(ROOT)
    a.output.mkdir(exist_ok=False)
    binary=a.output/a.binary.name
    shutil.copyfile(a.binary,binary);binary.chmod(0o755)
    art=ROOT/'assets/hd';dest=a.output/'assets/hd'
    dest.mkdir(parents=True)
    characters=json.loads((art/'characters/manifest.json').read_text())
    (dest/'characters').mkdir()
    shutil.copyfile(art/'characters/manifest.json',dest/'characters/manifest.json')
    for row in characters['atlases']:
        source=art/'characters'/row['file']
        assert sha(source)==row['sha256']
        shutil.copyfile(source,dest/'characters'/row['file'])
    screens=json.loads((art/'screens.json').read_text())
    scenes=json.loads((ROOT/'internal/hd/background-sources.json').read_text())
    files={x['file']:x['sha256'] for x in screens['images']}
    files.update({x['image_file']:x['image_sha256'] for x in scenes})
    for relative,want in files.items():
        assert sha(art/relative)==want
        output=dest/relative;output.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(art/relative,output)
    shutil.copyfile(art/'screens.json',dest/'screens.json')
    if a.audio_root:
        audio=json.loads((a.audio_root/'manifest.json').read_text())
        assert audio['kind']=='original-audio-ogg' and len(audio['clips'])==55
        assert audio['registry_sha256']==sha(ROOT/'internal/originalaudio/sources.json')
        for row in audio['clips']:
            assert sha(a.audio_root/row['file'])==row['sha256']
        shutil.copytree(a.audio_root,a.output/'assets/audio/original')
    inventory={str(f.relative_to(a.output)):sha(f) for f in sorted(a.output.rglob('*')) if f.is_file()}
    (a.output/'stage.json').write_text(json.dumps(dict(version=build['version'],binary_sha256=sha(binary),files=inventory,original_game_included=False,original_audio_included=bool(a.audio_root),rights='local verification only' if a.audio_root else 'engine and HD art'),indent=2)+'\n')
    print(json.dumps(dict(binary=str(binary),files=len(inventory),original_game_included=False)))


if __name__=='__main__':main()
