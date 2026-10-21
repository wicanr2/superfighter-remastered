"""核對首版收據，只上傳 patch 的四個引擎包與公開 manifest，再發布草稿。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path('/project')
REPO='wicanr2/superfighter-remastered'

def gh(*words,json_output=False):
    result=subprocess.check_output(['gh',*map(str,words)],text=True,timeout=900)
    return json.loads(result) if json_output else result.strip()

def read_release(version):
    # 草稿尚未建立正式 tag；以有權限的清單取得草稿本身，再按 id／資產核對。
    releases=gh('api',f'repos/{REPO}/releases?per_page=100',json_output=True)
    matches=[x for x in releases if x['tag_name']==version]
    assert len(matches)==1,'找不到唯一的發行版本'
    return matches[0]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['draft','publish','verify'])
    parser.add_argument('--target',required=True)
    parser.add_argument('--notes-file',type=Path,help='已審閱的該版發行說明；v1 必填，不能沿用首版完成聲明')
    a=parser.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.target)
    version=(ROOT/'VERSION').read_text().strip();assert re.fullmatch(r'v\.\d+\.\d+\.\d+-\d{8}',version)
    out=ROOT/'dist-all'/version;smoke=out/'smoke';patch=out/'patch'
    manifest=json.loads((patch/'release-manifest.json').read_text())
    assert manifest['version']==version and manifest['original_game_included'] is False and manifest['video_published'] is False
    audit=json.loads((smoke/'package-audit.json').read_text())
    assert audit['public_original_data_excluded'] and len(audit['packages'])==8
    for platform in ('linux','windows'):
        check=json.loads((smoke/(platform+'-startup')/'receipt.json').read_text());assert len(check['checks'])==2 and all(x['startup'] for x in check['checks'])
    for platform in ('native','wine'):
        check=json.loads((ROOT/f'workplace/keyboard-{platform}-v1/receipt.json').read_text());assert len(check['checks'])==6
    if version.startswith('v.1.'):
        for character in (8,9,10):
            receipt=json.loads((out/f'promo/boss-{character}/receipt.json').read_text())
            assert receipt['version']==version and receipt['character']==character and len(receipt['clips'])==2
            assert not receipt['clips'][1]['end_state']['core']['training']['modified']
            assert receipt['clips'][1]['end_state']['core']['fighters'][0]==character
        assert a.notes_file and a.notes_file.is_file(), 'v1 requires reviewed current release notes'
    else:
        assert len(json.loads((smoke/'linux-play-record/receipt.json').read_text())['checks'])==4
    promo=json.loads((out/'promo/promo-checks.json').read_text())
    assert promo['full_decode'] and promo['visual_contact_sheet_review']=='passed' and -40<promo['peak_db']<0
    assets={}
    for record in manifest['files']:
        p=out/record['file'];assert p.parent==patch and record['kind']=='patch' and p.name.endswith('-engine.zip')
        assert p.stat().st_size==record['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']
        assets[p.name]={'path':p,'sha256':record['sha256'],'bytes':record['bytes']}
    assert len(assets)==4
    p=patch/'release-manifest.json';assets[p.name]={'path':p,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    if a.stage=='draft':
        existing=gh('release','list','--repo',REPO,'--limit','100','--json','tagName,isDraft',json_output=True)
        assert not any(x['tagName']==version for x in existing),'版號已存在，拒絕覆寫'
        notes=a.notes_file or smoke/'public-release-notes.md'
        if not a.notes_file:
            notes.write_text(f'''快打至尊 Remastered {version} 首版，保留原版核心，接入原生桌面操作與部分街機手繪 HD。

- Windows x86-64、Linux x86-64、macOS Intel／Apple Silicon，各一份引擎 ZIP。
- 公開包不含原版遊戲。玩家自備合法資料，以 `-import-data 原版目錄或jsdos檔 -data game-data` 匯入。既有目錄不覆寫。
- 兩人鍵盤可重綁八方向、拳腳與四個快捷；手把保留兩人獨立指派及 R1／R2／L1／L2 四格。
- 斬的四招已有原版路徑證據。其他角色目前可保存四格配置，實際快捷仍拒絕，等待逐招驗證。
- 蜘蛛女、小丑、印第安喬可在單打及雙打選用。完整魔王過關及結局尚未驗證。
- 練習模式提供雙方滿血鎖定、停時與電腦中立。HD 覆蓋屋頂、部分角色／勝利姿態、特效與介面；缺件回退原貌。

Linux 與 Windows Wine 已驗解壓後啟動、資料匯入及自動準備 HD 參考；鍵盤重綁／保存／雙人輸入／斬快捷分別通過。macOS 已核對 Mach-O、架構與內容，尚無真機與簽章驗收。實體手把、遊戲音訊串流、正式速度及完整 HD 仍待完成。

本機完整版與含原版 MIDI 配樂的推廣片不公開。此 Release 僅含四個引擎包及 SHA-256 manifest。自有程式採 RRSAL-1.0；第三方授權隨包提供。
''')
        gh('release','create',version,'--repo',REPO,'--draft','--target',a.target,'--title','快打至尊 Remastered '+version,'--notes-file',notes)
        for item in assets.values():gh('release','upload',version,'--repo',REPO,item['path'])
    release=read_release(version)
    assert release['tag_name']==version and release['target_commitish']==a.target
    remote={x['name']:x for x in release['assets']};assert set(remote)==set(assets)
    for name,item in assets.items():
        assert remote[name]['size']==item['bytes']
        digest=remote[name].get('digest')
        if digest:assert digest=='sha256:'+item['sha256']
        else:
            target=smoke/'github-download';target.mkdir(exist_ok=True)
            gh('release','download',version,'--repo',REPO,'--pattern',name,'--dir',target)
            assert hashlib.sha256((target/name).read_bytes()).hexdigest()==item['sha256']
    if a.stage=='publish':
        assert release['draft'],'已發布版不可變更'
        gh('release','edit',version,'--repo',REPO,'--draft=false')
        release=read_release(version)
        assert not release['draft'] and release['published_at']
    report={'version':version,'target':a.target,'url':release['html_url'],'draft':release['draft'],'published_at':release['published_at'],
            'assets':[{k:v for k,v in x.items() if k in ('name','size','digest','browser_download_url')} for x in release['assets']],
            'public_original_data_excluded':True,'local_video_uploaded':False}
    (smoke/('github-'+a.stage+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
