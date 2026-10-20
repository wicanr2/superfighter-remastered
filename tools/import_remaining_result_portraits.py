"""保存其餘十張敗者原 PNG，核對原十一張 LOSEFIG，製作純 HD 候選總覽。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/project')
IDS = ['jaan', 'sarkov', 'bullet', 'phoenix', 'frank', 'onimaru', 'lan', 'kim', 'spider', 'clown', 'joe']
REVIEWS = [
    '平頭及白服保持；閉眼、嘴形與擦傷程度為近似。',
    '光頭、長鬍與紅巾保持；兩眼閉合與原版單眼狀態不同。',
    '藍黃兜帽與抬拳保持；雙眼開度及臉頰圓印為重繪近似。',
    '保留雙眼落淚與回首；髮量、嘴形及淚痕不是原像素。',
    '沿首張白髮、青藍衣緣與腫眼候選；傷勢與原版不同，未修改舊 PNG。',
    '灰綠臉、金屬板及紫罩保持；嘴巴張幅較原版小。',
    '短棕髮與紅領保持；原版浮腫臉頰被弱化，嘴角及神情仍待定版。',
    '禿額、後掠髮及金環保持；金環與側面比例及傷勢為近似。',
    '只含頭髮、臉與頸，保留紫色彩繪及淚痕；不對應身體服裝或戰鬥動畫。',
    '光頭、厚下顎、頸前辮子與圓形臉頰痕保持；表情與細節為近似。',
    '紅白彩繪、頭帶羽飾與長鼻保持；腫眼、擦傷及張嘴程度為近似。',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--requests', type=Path, required=True)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--generated-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.stat().st_uid == 1000
    requests = json.loads(a.requests.read_text())
    assert [r['id'] for r in requests] == [name for name in IDS if name != 'frank']
    selection_source = ROOT/'assets/hd/candidates/selection-portraits-source.json'
    normal = json.loads(selection_source.read_text())['records']
    assert [r['id'] for r in normal] == IDS
    old_result_source = ROOT/'assets/hd/candidates/result-source.json'
    old = json.loads(old_result_source.read_text())
    frank = next(r for r in old['records'] if r['id'] == 'loser-frank')
    destination = ROOT/'assets/hd/candidates'
    assert sha(destination/frank['file']) == frank['sha256']
    catalog_path = ROOT/'assets/hd/catalog.json'
    catalog = json.loads(catalog_path.read_text())
    previous = list(catalog['files'])
    for row in previous:
        path = ROOT/'assets/hd'/row['file']
        assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    original_path = ROOT/'workplace/orig/LOSEFIG.XBB'
    assert sha(original_path) == 'b1b1781bc799dca14f3ce0f3b74e451e654bafe88341249a977a34ab909b159c'
    original = original_path.read_bytes()
    assert len(original) == 11*8689
    source_path = destination/'result-portraits-source.json'
    preview = ROOT/'docs/screenshots/result-portrait-candidates.png'
    assert not source_path.exists() and not preview.exists()
    assert all(p.stat().st_uid == 1000 for p in (destination, catalog_path, preview.parent))
    prepared, records = [], []
    for index, character in enumerate(IDS):
        row = normal[index]
        data = original[index*8689:(index+1)*8689]
        palette, indices = data[:96], data[768:768+89*89]
        assert max(palette) <= 63 and max(indices) < 32
        rgb = bytes(v*4+v//16 for value in indices for v in palette[value*3:value*3+3])
        ref = a.references/f'loser-{index:02d}.png'
        assert Image.open(ref).convert('RGB').size == (89, 89)
        assert Image.open(ref).convert('RGB').tobytes() == rgb
        target = destination/f'result-loser-{character}-v1.png'
        if character == 'frank':
            record = dict(frank, id='frank', reused_from='assets/hd/candidates/result-source.json')
        else:
            request = next(r for r in requests if r['id'] == character)
            assert request['index'] == index and not target.exists()
            generated = a.generated_root/Path(request['generated']).name
            assert generated.is_file() and not generated.is_symlink()
            with Image.open(generated) as im:
                im.verify()
            with Image.open(generated) as im:
                assert im.width == im.height and 1200 <= im.width <= 2048
                assert im.convert('RGBA').getchannel('A').getextrema() == (255, 255)
                size = list(im.size)
            style = destination/row['file']
            assert sha(style) == row['sha256']
            panel = a.requests.parent/(character+'-reference.png')
            assert panel.is_file()
            record = {'id': character, 'file': target.name, 'size': size, 'sha256': sha(generated),
                'bytes': generated.stat().st_size, 'prompt': request['prompt'], 'tool': 'built-in image_gen',
                'model_version': 'not exposed by tool', 'generated_source': generated.name,
                'transparent_background': False, 'reference_panel_sha256': sha(panel),
                'style_reference': {'file': row['file'], 'sha256': row['sha256']}}
            prepared.append((generated, target, record))
        record.update(index=index, name=row['name'], source_file='LOSEFIG.XBB', source_sha256=sha(original_path),
            record_file_offset=index*8689, pixels_file_offset=index*8689+768,
            original_reference_sha256=sha(ref), original_RGB_sha256=hashlib.sha256(rgb).hexdigest(),
            original_size=[89, 89], status='candidate-not-approved-or-integrated', review=REVIEWS[index])
        records.append(record)
    assert len(prepared) == 10 and len(records) == 11
    a.output.mkdir()
    for generated, target, record in prepared:
        shutil.copyfile(generated, target)
        assert sha(generated) == sha(target) == record['sha256'] and target.stat().st_uid == 1000
        catalog['files'].append({'file': str(target.relative_to(ROOT/'assets/hd')), 'sha256': sha(target),
            'bytes': target.stat().st_size, 'size': record['size'], 'character': record['id'],
            'tool': 'built-in imagegen', 'status': 'candidate-result-loser-portrait-not-integrated',
            'generated_source': generated.name})
    public = Image.new('RGB', (1200, 1040), '#151c28')
    private = Image.new('RGB', (1200, 1040), '#151c28')
    font = ImageFont.truetype(str(ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'), 19)
    d = ImageDraw.Draw(public)
    d.text((12, 7), '十一人敗者肖像 HD 候選，未接正式結果畫面', font=font, fill='white')
    for row in records:
        x, y = row['index']%4*300, 44+row['index']//4*332
        label = row['name']+' / '+row['id']
        assert d.textbbox((0, 0), label, font=font)[2] <= 288
        d.text((x+6, y+1), label, font=font, fill='white')
        art = Image.open(destination/row['file']).convert('RGB')
        public.paste(art.resize((300, 300), Image.Resampling.LANCZOS), (x, y+32))
        ImageDraw.Draw(private).text((x+6, y+1), label, font=font, fill='white')
        private.paste(Image.open(a.references/f"loser-{row['index']:02d}.png").convert('RGB').resize((150, 150), Image.Resampling.NEAREST), (x, y+32))
        private.paste(art.resize((150, 150), Image.Resampling.LANCZOS), (x+150, y+32))
    public.save(preview)
    private.save(a.output/'original-vs-candidate.png')
    provenance = {'kind': 'eleven defeated result portrait candidates; ten new, Frank reused unchanged',
        'authorization': 'existing B style and generated-HD upload scope; visibility unchanged',
        'source_file': 'LOSEFIG.XBB', 'source_sha256': sha(original_path), 'records': records,
        'requests_sha256': sha(a.requests), 'importer_sha256': sha(Path(__file__)),
        'selection_portraits_source_sha256': sha(selection_source), 'first_result_source_sha256': sha(old_result_source),
        'preview': {'file': str(preview.relative_to(ROOT)), 'sha256': sha(preview)},
        'limits': 'new painted approximations; not visual approval, source-exact expressions or injuries, runtime schema, normal result verification, or full HD'}
    write_json(source_path, provenance)
    catalog['files'].append({'file': str(source_path.relative_to(ROOT/'assets/hd')), 'sha256': sha(source_path),
        'bytes': source_path.stat().st_size, 'status': 'candidate-result-portrait-provenance'})
    catalog['pngs'] += 10
    assert catalog['files'][:-11] == previous
    write_json(catalog_path, catalog)
    screen_source = ROOT/'docs/screenshots/source.json'
    screens = json.loads(screen_source.read_text())
    screens['prototype_captures'].append({'kind': 'HD defeated portrait contact sheet; not native capture',
        'file': preview.name, 'sha256': sha(preview), 'source': 'assets/hd/candidates/result-portraits-source.json',
        'source_sha256': sha(source_path), 'renderer': 'tools/import_remaining_result_portraits.py',
        'renderer_sha256': sha(Path(__file__)), 'platform': 'Pillow 11.3.0 in Docker; not runtime acceptance',
        'authorization': 'existing user HD upload request', 'limits': 'generated art only; original images and comparison stay local'})
    write_json(screen_source, screens)
    receipt = {'passed': True, 'source_sha256': sha(source_path), 'importer_sha256': sha(Path(__file__)),
        'previous_catalog_entries': previous, 'original_RGB_reconstructions': 11, 'new_generated_PNGs': 10,
        'preview_sha256': sha(preview), 'private_comparison_sha256': sha(a.output/'original-vs-candidate.png'),
        'PNG_count': catalog['pngs'], 'catalog_entries': len(catalog['files']),
        'asset_payload_bytes': sum(r['bytes'] for r in catalog['files'])}
    write_json(a.output/'receipt.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'previous_catalog_entries'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
