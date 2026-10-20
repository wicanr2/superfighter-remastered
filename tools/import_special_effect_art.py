"""保留內建生成 PNG 原 bytes，檢查透明分隔；只匯入私有候選，不接正式圖集。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from prepare_hd_characters import atlas_regions


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generated-root', type=Path, required=True)
    p.add_argument('--recheck', action='store_true', help='核對既有候選原 bytes，另存新報告')
    p.add_argument('images', nargs='+', help='group=generated-filename.png')
    a = p.parse_args()
    out = Path('/project/workplace/remaining-special-audit-v1/art-v1')
    assert out.is_dir() and out.stat().st_uid == 1000 and a.generated_root.is_dir()
    for image in a.images:
        group, filename = image.split('=', 1)
        assert Path(group).name == group and Path(filename).name == filename
        source = a.generated_root / filename
        target = out / (group+'.png')
        request = out / (group+'-request.json')
        r = json.loads(request.read_text())
        assert r['group'] == group and source.is_file()
        assert a.recheck == target.exists()
        reference = Path(r['referenced_image_paths'][0])
        if not reference.is_file():
            reference = out / reference.name
        assert sha(reference) == r['reference_sha256']
        if not a.recheck:
            shutil.copyfile(source, target)
        assert sha(source) == sha(target)
        with Image.open(target) as im:
            alpha = im.getchannel('A').getextrema() if im.mode == 'RGBA' else None
            regions, rejection = None, None
            try:
                # 正式載入器要求透明區與 alpha >= 128 的實體，不要求最大值恰為 255。
                assert alpha is not None and alpha[0] == 0 and alpha[1] >= 128, '缺少透明區或可辨識的實體圖像'
                regions = atlas_regions(im, *r['grid'])
            except AssertionError as exc:
                rejection = str(exc)
            result = {'kind': 'private generated art candidate, not production acceptance',
                      'group': group, 'source_path': str(source), 'sha256': sha(target), 'bytes': target.stat().st_size,
                      'size': list(im.size), 'mode': im.mode, 'alpha_range': alpha, 'regions': regions,
                      'registration_rejection': rejection, 'request_sha256': sha(request),
                      'importer_sha256': sha(Path(__file__)), 'generator': 'built-in imagegen',
                      'transparent_background_requested': True, 'visual_review': 'pending'}
        suffix = '-recheck.json' if a.recheck else '-import.json'
        (out / (group+suffix)).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
