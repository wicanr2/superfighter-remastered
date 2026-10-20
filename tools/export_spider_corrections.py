"""輸出蜘蛛女首批補稿的逐格提示詞、原始參考與可驗 ZIP，僅供本機使用。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path('/project'))
    parser.add_argument('--style', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    assert not out.exists() and out.parent.is_dir() and out.parent.stat().st_uid == 1000
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = args.project / 'workplace/spider-model-handoff-v1'
    normal = json.loads((source / 'normal/manifest.json').read_text())
    victory = json.loads((source / 'victory/manifest.json').read_text())
    cells = {cell['slot']: cell for cell in normal['cells']}
    descriptions = {
        0: ('低伏待機第一格', 'Retain the very low, forward-bent spiderlike guard, both hands near the ground and the original asymmetric leg placement. Do not stand upright or substitute an ordinary squat.'),
        1: ('低伏待機第二格', 'Match this second low-guard cel separately. Retain its specific back angle, raised hips, arm length and leg placement. Do not duplicate cel 00 or stand upright.'),
        21: ('倒地第一格', 'Keep the entire figure lying low and almost horizontal, in the same compact ground-level pose as the reference. Preserve the head, arms and legs on their original sides. Do not kneel, squat, stand or present a victory pose.'),
        24: ('蜷身翻轉', 'Keep the tucked, inverted rolling silhouette exactly as shown. Preserve the head below the bent legs and the compact overlapping limb arrangement. Do not untwist the pose, place the feet on the ground, or replace it with a crouch.'),
        29: ('倒地第二格', 'Keep the extended horizontal lying pose exactly as shown. Preserve the reference orientation of the head, legs and bent arms; the figure must remain very wide and low, not seated or standing.'),
        33: ('斜向仰身姿勢', 'Preserve the unusual diagonal airborne, backward-leaning body and its exact limb arrangement from the reference. Do not rotate it upright, lower the limbs into a guard, or invent a floor.'),
        34: ('倒轉斜身姿勢', 'Preserve the upside-down diagonal pose with raised feet and low head exactly as shown. Keep the same rotation and side-view silhouette. Do not automatically rotate or straighten the figure into a standing pose.'),
        41: ('低伏姿勢，亦用於勝利前段', 'Match this low, bent-over guard exactly, including its different hand and foot placement. Do not turn it into a standing celebration or reuse the pose from cel 00 or 01.'),
        43: ('一列高的細長圖像來源', 'This reference is a very thin horizontal strip, 94 by 1 source pixels. Reproduce only the strip and its original colored/transparent segments. No person, face, hands, feet, text, weapon, beam cone or additional glow. Its gameplay purpose is not established, so do not invent a new effect.'),
        44: ('黃色輪廓特效姿態', 'Preserve the supplied diagonal game-effect silhouette, existing yellow rim and internal source shapes. This is a flat stylized game-effect cel, not a realistic anatomy study. Do not add realistic anatomical detail, a skeleton, new lightning bolts, a new pose or a standing character.'),
    }
    out.mkdir()
    for directory in ['references', 'prompts', 'style']:
        (out / directory).mkdir()
    assert args.style.is_file() and not args.style.is_symlink()
    shutil.copyfile(args.style, out / 'style/external-style.png')
    assert sha(args.style) == sha(out / 'style/external-style.png')
    records = []
    combined = []
    for slot, (title, instruction) in descriptions.items():
        cell = cells[slot]
        original = source / 'normal' / cell['file']
        assert sha(original) == cell['png_sha256']
        reference = f'references/normal-{slot:02d}.png'
        shutil.copyfile(original, out / reference)
        assert sha(out / reference) == cell['png_sha256']
        common = (
            'Task: produce ONE pose-accurate HD cel for archival restoration of the 1990s DOS fighting game Super Fighter. '
            'The fighter is a fictional adult character. This is functional game animation artwork.\n'
            f'Image 1: {reference}. This is the sole authority for pose, facing, rotation, silhouette, '
            f'limb angles and the painted bounding-box aspect ratio ({cell["width"]}:{cell["height"]}). '
            'Trace the composition of this single cel faithfully; do not invent a better-looking pose.\n'
        )
        if slot != 43:
            common += (
                'Image 2: style/external-style.png. Use only its established character identity, blonde hair, '
                'purple eye mask, outfit coverage, purple gloves and boots, clean hand-painted arcade contours and shading. '
                'Do not copy its sprite poses, sheet layout or camera direction. Do not add exposure or change the costume.\n'
            )
        common += instruction + '\n'
        common += (
            'Output exactly ONE isolated cel in a 1024 by 1024 PNG, with genuine transparent alpha. '
            'Keep the full painted subject within generous empty margins. Preserve the reference subject aspect ratio; '
            'do not stretch it to fill the square canvas. Keep figure interiors opaque and antialias only the edges. '
            'No checkerboard, backdrop, ground, cast shadow, labels, numbering, grid, multiple poses or watermark. '
            f'Save as spider-normal-{slot:02d}.png.\n'
        )
        prompt = f'prompts/normal-{slot:02d}.txt'
        (out / prompt).write_text(common)
        aliases = [x['slot'] for x in victory['cells'] if x['source_sha256'] == cell['source_sha256']]
        records.append({'normal_slot': slot, 'title': title, 'reference': reference, 'prompt': prompt,
                        'output': f'spider-normal-{slot:02d}.png', 'original_size': [cell['width'], cell['height']],
                        'source_sha256': cell['source_sha256'], 'original_png_sha256': cell['png_sha256'],
                        'byte_identical_victory_slots': aliases})
        combined.append(f'{slot:02d}：{title}\n\n{common}')
    assert [(r['normal_slot'], r['byte_identical_victory_slots']) for r in records if r['byte_identical_victory_slots']] == [(0,[0]),(1,[1]),(41,[2])]
    (out / '全部提示詞.txt').write_text('\n\n'.join(combined), encoding='utf-8-sig', newline='\r\n')
    readme = '''蜘蛛女：首批逐格補稿

這份包先補七張缺少的倒地、翻轉及特效來源，再修正三張低伏姿勢，共十張。
這十張不是全角色驗收清單，其餘三十五張仍待姿勢對應審查。

使用方式：
1. 每次只選一個 prompts/normal-NN.txt。
2. 附同編號的 references/normal-NN.png，作為姿勢與方向唯一依據。
3. 除 43 外，再附 style/external-style.png，只用於造型與筆觸。
4. 不要把十張合成圖集，不要把前一張生成圖當成下一張的姿勢參考。
5. 回傳十張原始 PNG，檔名照提示詞，保留真正透明背景。若模型只能給純色底，另註明即可，後續再處理去背。

優先：21、24、29、33、34、43、44。修正：00、01、41。
00／01／41 的原始 packed bytes 分別與 WIN 槽 0／1／2 完全相同，通過後可共用這三張，不必重畫另一套勝利前段。
43 的實際來源只有 94×1。保留細長形狀，不要因看不到角色而自行補出人形；目前用途未證實。
44 是黃色輪廓的效果圖，保留原圖輪廓，不增加寫實身體細節或自行發明雷電。

原版 PNG 只供本機參考，未附原始 DAT／FIG／EXE，不加入公開儲存庫。
SFMAN09.DAT：76f1a2484fd551c574279138e16f2f70971c4a7259858406e90c0211a2f3f53e
JJWIN.FIG：7995ef671f44c58647f66a3b1a7ba1abdbdb939774bb9f54ac93d724a8fbc4ec
清單與逐檔雜湊見 manifest.json、files.json。
'''
    (out / '使用說明.txt').write_text(readme, encoding='utf-8-sig', newline='\r\n')
    (out / 'manifest.json').write_text(json.dumps({'scope':'ten initial missing/correction cels; other cels not yet accepted',
        'script_sha256':sha(Path(__file__)), 'style_sha256':sha(args.style), 'records':records},ensure_ascii=False,indent=2)+'\n')
    files = {str(f.relative_to(out)): sha(f) for f in out.rglob('*') if f.is_file()}
    (out / 'files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
    archive = out.with_suffix('.zip')
    assert not archive.exists()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                info=zipfile.ZipInfo(str(path.relative_to(out)),date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,path.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)+1
        for name,want in files.items():assert hashlib.sha256(z.read(name)).hexdigest()==want
        for info in z.infolist():
            if not info.filename.isascii():assert info.flag_bits & 0x800
        for name in ['使用說明.txt','全部提示詞.txt']:
            text=z.read(name);assert text.startswith(b'\xef\xbb\xbf') and b'\r\n' in text
            assert b'\n' not in text.replace(b'\r\n',b'')
    assert all(f.stat().st_uid == 1000 for f in out.rglob('*')) and archive.stat().st_uid == 1000
    print(json.dumps({'zip':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'single_cel_prompts':len(records)},ensure_ascii=False))


if __name__ == '__main__':
    main()
