"""輸出本機蜘蛛女模型交接包；包含原版參考圖，不可提交 Git 或公開發行。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=Path('/project'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();p=args.project;out=args.output
    assert not out.exists() and out.parent.is_dir() and out.parent.stat().st_uid==1000
    normal=p/'workplace/spider-source-v1';art=p/'workplace/spider-art-v1'
    wins=p/'workplace/remaining-victory-source-v1'
    data=json.loads((normal/'manifest.json').read_text())
    win=next(r for r in json.loads((wins/'manifest.json').read_text())['records'] if r['character']==8)
    assert data['unique_sources']==45 and len(win['cells'])==5
    out.mkdir();(out/'normal').mkdir();(out/'victory').mkdir();(out/'style').mkdir();(out/'prompts').mkdir()
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    def copy(src,dst,want=None):
        assert src.is_file() and not src.is_symlink()
        if want:assert sha(src)==want,src
        shutil.copyfile(src,dst)
        assert sha(src)==sha(dst)
    references=['poses-00.png','poses-01.png','poses-02.png','poses-03-nine.png']
    for file in references:copy(normal/file,out/'normal'/file)
    for cell in data['cells']:copy(normal/cell['file'],out/'normal'/cell['file'],cell['png_sha256'])
    copy(normal/'manifest.json',out/'normal/manifest.json')
    copy(wins/win['reference'],out/'victory'/win['reference'],win['reference_sha256'])
    for i in range(5):copy(wins/f'spider-win-{i:02d}.png',out/'victory'/f'spider-win-{i:02d}.png')
    (out/'victory/manifest.json').write_text(json.dumps(win,ensure_ascii=False,indent=2)+'\n')
    copy(art/'coverage-prototype.png',out/'style/covered-costume.png','4cbd89d69901d875587d2fdd471cf487917e357d52c5773b0564ecc2a75b8b74')
    copy(p/'assets/hd/characters/sarkov-poses-00.png',out/'style/arcade-style.png')
    common='''Purpose: archival preservation and HD restoration of WIDOW (Spider Woman), a fictional adult boss from the 1990s DOS fighting game Super Fighter. Preserve her recognizable original character design and the exact supplied animation cels. Use crisp hand-painted 2D arcade illustration, clean contours and controlled layered shading. Preserve facing, pose, long-limbed silhouette, hair, hands, feet and limb angles. Do not turn the low spiderlike guard into a generic standing fighter. Do not add sexualized framing, exposure, anatomy exaggeration, new costume details or poses. Fully visible figures, generous transparent margins and uninterrupted empty gutters. Genuine RGBA transparency, solid painted figure interiors, antialiased edges only. No background, floor, cast shadows, glow, labels, numbers, grid, checkerboard or watermarks. Do not crop fingers, boots or hair, and do not merge adjacent cels.\n'''
    original='Costume: preserve the costume and coverage shown in the original reference: long blonde hair, purple eye mask, purple one-piece fighting leotard, long purple gloves and tall purple boots. This is a conservative game-art restoration. Do not redesign the outfit or invent anatomical details.\n'
    covered='Costume variant: use style/covered-costume.png as the approved identity and FULLY OPAQUE PURPLE FULL-BODY SUIT reference. The original sprite sheet supplies pose and facing only. Cover shoulders, chest, torso, hips and legs continuously from neck to wrists and ankles; purple gloves and boots. No cutouts or transparent fabric.\n'
    for i,ref in enumerate(references):
        count=12 if i<3 else 9;cols=4 if i<3 else 3;rows=3
        tail=f'Input: normal/{ref}. Create exactly {count} distinct sprites arranged {cols} columns by {rows} rows, in the same row-major order. Remove source labels. Suggested output: spider-poses-{i:02d}.png. Keep style and identity identical across all four atlases.\n'
        for variant,text in [('original',original),('covered',covered)]:
            (out/'prompts'/f'{variant}-poses-{i:02d}.txt').write_text(common+text+tail)
    for variant,text in [('original',original),('covered',covered)]:
        (out/'prompts'/f'{variant}-victory.txt').write_text(common+text+'Input: victory/spider-win-source.png. Create exactly FIVE distinct complete victory sprites in ONE row of FIVE columns, in the original left-to-right order. Suggested output: spider-win.png. Match every original cel, including the subtle differences between similar cels.\n')
    for name in ['request-00.json','covered-request-00.json','accepted-design.json']:
        copy(art/name,out/'prompts'/('historical-'+name))
    copy(p/'workplace/spider-restoration-request-v1.json',out/'prompts/historical-single-cel-restoration.json')
    readme='''# 蜘蛛女：其他模型用素材包

這份包供本機遊戲文化保存與 HD 製作用。角色是成年虛構格鬥角色。原版參考圖仍屬原作素材，本包不加入 Git，也不授權公開散布。

## 開始方式

1. 想沿原圖加強，使用 prompts/original-poses-00.txt，附 normal/poses-00.png。
2. 其餘三批分別用同名 poses-01、poses-02、poses-03 提示詞及參考圖；最後一批實際參考檔名為 poses-03-nine.png。
3. 先前確認的全覆蓋連身衣方案另有 covered 提示詞，搭配 style/covered-costume.png。兩種方案分開生成，不要混成一套。
4. style/arcade-style.png 只供筆觸、輪廓及明暗參考，不照抄其男性角色、服裝或姿勢。
5. 勝利圖使用 original-victory.txt 或 covered-victory.txt，附 victory/spider-win-source.png。

## 應回傳的檔案

- spider-poses-00.png：4×3，共 12 格，原始來源 ordinal 0–11。
- spider-poses-01.png：4×3，共 12 格，ordinal 12–23。
- spider-poses-02.png：4×3，共 12 格，ordinal 24–35。
- spider-poses-03.png：3×3，共 9 格，ordinal 36–44。
- spider-win.png：5×1，共 5 格。

請交回未經壓縮重畫的原始 PNG。透明背景必須是真的 alpha；人物內部保持不透明，格子之間留連續空白，人物不要跨格或貼邊。不需在圖片上加入編號。

normal/slot-00.png 至 slot-44.png 是各自原尺寸 PNG，可供逐格比對。45 組一般來源覆蓋 72 個指標槽，slot-00 同時有多個別名；對照表在 normal/manifest.json。victory/ 另有五張原尺寸 PNG 及 72 槽對照。

## 提示詞與生成紀錄

original-* 是這次依使用者要求整理的原版造型加強方向；covered-* 是先前選定連身衣方向。提示詞只如實交代文化保存用途，不保證任何模型接受。historical-*.json 保留精確舊請求及造型選擇，其中舊絕對路徑只作歷史，不是本包的操作入口。內建工具的原服裝、連身衣圖集及單格修復均曾拒絕，專案目前仍使用原貌，等待新的候選圖通過檢視才接入。

## 來源身分

一般來源：SFMAN09.DAT，SHA-256 76f1a2484fd551c574279138e16f2f70971c4a7259858406e90c0211a2f3f53e。
勝利來源：JJWIN.FIG，SHA-256 7995ef671f44c58647f66a3b1a7ba1abdbdb939774bb9f54ac93d724a8fbc4ec。
本包只附解碼圖片、提示詞與清單，未附原始 DAT、FIG、EXE 或其他遊戲程式。逐檔 SHA-256 在 files.json。
'''
    (out/'README.md').write_text(readme)
    files={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file()}
    (out/'files.json').write_text(json.dumps({'kind':'local-only original-art reference handoff','files':files},ensure_ascii=False,indent=2)+'\n')
    archive=out.with_suffix('.zip');assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(out.rglob('*')):
            if f.is_file():
                info=zipfile.ZipInfo(str(f.relative_to(out)),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,f.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)+1
        for name,want in files.items():assert hashlib.sha256(z.read(name)).hexdigest()==want
    print(json.dumps({'zip':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'normal_cels':45,'victory_cels':5,'pngs':len(list(out.rglob('*.png'))),'entries':len(files)+1}))


if __name__=='__main__':main()
