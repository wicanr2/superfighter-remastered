"""Docker 內建立公開引擎包與 full-local；嚴格分離原版資料。"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile


ROOT=Path('/project')
TARGETS=[('linux-amd64','superfighter-linux-amd64'),('windows-amd64','superfighter-windows-amd64.exe'),
         ('macos-amd64','superfighter-macos-amd64'),('macos-arm64','superfighter-macos-arm64')]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def licenses(output):
    assert not output.exists()
    output.mkdir(parents=True)
    raw=subprocess.check_output(['go','list','-deps','-f','{{with .Module}}{{.Path}}|{{.Dir}}{{end}}','./cmd/superfighter'],cwd=ROOT,text=True)
    result=[]
    for line in sorted(set(raw.splitlines())):
        if '|' not in line:continue
        name,directory=line.split('|',1)
        if name=='github.com/wicanr2/superfighter-remastered':continue
        found=[]
        for pattern in ('LICENSE*','COPYING*','NOTICE*'):
            for p in sorted(Path(directory).glob(pattern)):
                if not p.is_file():continue
                target=output/(name.replace('/','__')+'__'+p.name)
                shutil.copyfile(p,target)
                found.append({'file':target.name,'sha256':sha(target)})
        assert found,('dependency has no license',name)
        result.append({'module':name,'licenses':found})
    goroot=Path(subprocess.check_output(['go','env','GOROOT'],text=True).strip())
    shutil.copyfile(goroot/'LICENSE',output/'Go-LICENSE.txt')
    shutil.copyfile(ROOT/'internal/desktop/assets/OFL.txt',output/'NotoSansCJKtc-OFL.txt')
    (output/'sources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'licensed_modules':len(result)}))


def readme(version,local,platform):
    data='本包只供本機保存，已含固定原版資料。不得上傳或重新散布。' if local else '本包不含原版遊戲。請自備合法原版目錄或 jsdos ZIP，以 -import-data 匯入。'
    return f'''快打至尊 Remastered {version}
平台：{platform}

{data}

啟動：Windows 執行 Start.cmd；Linux 執行 Start.sh；macOS 開啟 Superfighter Remastered.app。
公開包匯入：Windows 將原版目錄或 jsdos 檔拖到 Import-game.cmd。
Linux：./superfighter-linux-amd64 -import-data /path/to/original -data game-data
macOS：執行 Import-game.command，再輸入自己的原版資料路徑。
匯入只接受本專案已驗版本，會逐檔核對，拒絕覆寫既有目錄。

操作：F10 開設定，F8 切換手把／鍵盤頁；Tab 選欄位、Enter 重綁、Delete 清空、Esc 取消。
P1：QWE／A D／ZXC 八方向，Tab 拳，左 Shift 腳；四快捷為主鍵盤 1／2／3／4。
P2：數字鍵盤 789／4 6／123，Enter 拳、右 Shift 腳；四快捷為主鍵盤 7／8／9／0。
鍵盤可自訂，兩人分開保存；四格招式與手把 R1／R2／L1／L2 共用。
Esc 暫停前端，不送原版補血；F9 切換雙方鎖滿血、停時與 AI 中立的練習模式。
魔王：單打與雙打都可選蜘蛛女、小丑、印第安喬；正常選角後確認。
HD：按工具列的原貌／HD 角色切換。未知動作、場景或缺件整格保留原貌。
設定保存在作業系統使用者設定目錄 SuperfighterRemastered，原版來源不回寫。

目前限制：實際快速出招只開已驗的斬四招；其他角色四格可以設定，實際出招明示拒絕。
蜘蛛女只有低伏靜態近似稿；完整動畫與其餘場景尚未完成，遊戲音樂／語音串流尚未接入。
標題、選角與結果畫面的 HD 原型未納入。本機完整版指包含原版資料，不代表完整 HD。
目前暫停 HD 開發，實體手把、真機速度、魔王單打過關及結局留待人工驗證。
Linux 與 Windows Wine 有原生驗證；Wine 不等於 Windows 真機。macOS 未作真機驗收或簽章。
Linux 需要 X11／OpenGL 桌面及相容的系統函式庫。

授權：自有程式與文件為 RRSAL-1.0，完整條款見 LICENSE。
第三方元件見 licenses/。本條款不涵蓋原版資料與角色／場景等原作權利。
儲存庫：https://github.com/wicanr2/superfighter-remastered
'''


def archive_tree(source,target,version):
    date=datetime.datetime.strptime(version[-8:],'%Y%m%d')
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(source.rglob('*')):
            if not p.is_file():continue
            info=zipfile.ZipInfo(source.name+'/'+p.relative_to(source).as_posix(),(date.year,date.month,date.day,0,0,0))
            info.create_system=3
            info.external_attr=(stat.S_IFREG|stat.S_IMODE(p.stat().st_mode))<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['licenses','packages','audit'])
    p.add_argument('--build-dir',type=Path,default=ROOT/'workplace/bin')
    p.add_argument('--license-dir',type=Path,default=ROOT/'workplace/release-licenses-v1')
    p.add_argument('--original-root',type=Path,default=Path('/orig'))
    a=p.parse_args()
    if a.stage=='licenses':licenses(a.license_dir);return
    version=(ROOT/'VERSION').read_text().strip()
    assert re.fullmatch(r'v\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]{8}',version)
    output=ROOT/'dist-all'/version
    originals=json.loads((ROOT/'internal/gamefiles/source-manifest.json').read_text())
    protected={x['sha256'] for x in originals}
    if a.stage=='packages':
        assert not output.exists() and a.license_dir.is_dir()
        assert ROOT.stat().st_uid==1000
        for kind in ('patch','full-local','promo','smoke'):(output/kind).mkdir(parents=True)
        records=[]
        for platform,binary_name in TARGETS:
            binary=a.build_dir/binary_name
            build=json.loads(binary.with_name(binary.name+'.build.json').read_text())
            assert build['binary_sha256']==sha(binary) and build['version']==version
            for filename,digest in build['compiled_inputs'].items():assert sha(ROOT/filename)==digest,filename
            for local in (False,True):
                kind='full-local' if local else 'patch'
                top=f'Superfighter-Remastered-{version}-{platform}'
                with tempfile.TemporaryDirectory(prefix='release-stage-',dir=ROOT/'workplace') as temporary:
                    base=Path(temporary)/top;base.mkdir()
                    if platform.startswith('macos'):
                        contents=base/'Superfighter Remastered.app/Contents'
                        payload=contents/'Resources';exe=contents/'MacOS/superfighter'
                        exe.parent.mkdir(parents=True);payload.mkdir(parents=True)
                        plist={'CFBundleName':'Superfighter Remastered','CFBundleDisplayName':'快打至尊 Remastered',
                               'CFBundleIdentifier':'io.github.wicanr2.superfighter-remastered','CFBundleExecutable':'superfighter',
                               'CFBundlePackageType':'APPL','CFBundleShortVersionString':version[2:].split('-')[0],
                               'CFBundleVersion':version[2:].split('-')[0],'CFBundleGetInfoString':version,'SuperfighterReleaseVersion':version,
                               'LSMinimumSystemVersion':'11.0','NSHighResolutionCapable':True}
                        (contents/'Info.plist').write_bytes(plistlib.dumps(plist))
                        importer='#!/bin/bash\nbase="$(cd "$(dirname "$0")" && pwd)"\nsource="$1"\nif [ -z "$source" ]; then read -r -p "Original data directory or jsdos ZIP: " source; fi\n"$base/Superfighter Remastered.app/Contents/MacOS/superfighter" -import-data "$source" -data "$base/Superfighter Remastered.app/Contents/Resources/game-data"\n'
                        (base/'Import-game.command').write_text(importer);(base/'Import-game.command').chmod(0o755)
                    else:
                        payload=base;exe=base/binary_name
                        if platform.startswith('windows'):
                            (base/'Start.cmd').write_bytes(('@echo off\r\ncd /d "%~dp0"\r\n'+binary_name+' %*\r\nif errorlevel 1 pause\r\n').encode())
                            (base/'Import-game.cmd').write_bytes(('@echo off\r\ncd /d "%~dp0"\r\nif "%~1"=="" (echo Drag your original directory or jsdos ZIP onto this file. & pause & exit /b 1)\r\n'+binary_name+' -import-data "%~1" -data game-data\r\npause\r\n').encode())
                        else:
                            (base/'Start.sh').write_text('#!/bin/sh\ncd "$(dirname "$0")" || exit 1\nexec ./'+binary_name+' "$@"\n');(base/'Start.sh').chmod(0o755)
                    shutil.copyfile(binary,exe);exe.chmod(0o755)
                    shutil.copytree(ROOT/'assets/hd/characters',payload/'assets/hd/characters')
                    background=payload/'assets/hd/backgrounds';background.mkdir(parents=True)
                    shutil.copyfile(ROOT/'assets/hd/backgrounds/rooftop.png',background/'rooftop.png')
                    if local:
                        dest=payload/'game-data';dest.mkdir()
                        for record in originals:
                            source=a.original_root/record['name']
                            assert sha(source)==record['sha256'] and source.stat().st_size==record['bytes']
                            shutil.copyfile(source,dest/record['name'])
                    shutil.copyfile(ROOT/'LICENSE',base/'LICENSE')
                    shutil.copytree(a.license_dir,base/'licenses')
                    (base/'README-zh-TW.txt').write_text(readme(version,local,platform),encoding='utf-8-sig')
                    (base/'VERSION').write_text(version+'\n')
                    inventory={str(f.relative_to(base)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(base.rglob('*')) if f.is_file()}
                    manifest={'version':version,'platform':platform,'kind':kind,'original_game_included':local,
                              'binary':str(exe.relative_to(base)),'compiled_receipt_sha256':sha(binary.with_name(binary.name+'.build.json')),
                              'files':inventory,'rights':'local only with original game' if local else 'engine and generated HD; user supplies original data'}
                    (base/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
                    archive=output/kind/f'{top}-{kind if local else "engine"}.zip'
                    archive_tree(base,archive,version)
                records.append({'file':str(archive.relative_to(output)),'sha256':sha(archive),'bytes':archive.stat().st_size,'kind':kind,'platform':platform})
        all_records={'version':version,'files':records}
        (output/'SHA256SUMS.json').write_text(json.dumps(all_records,indent=2)+'\n')
        public={'version':version,'original_game_included':False,'files':[x for x in records if x['kind']=='patch'],
                'video_published':False,'limits':'initial partial HD; Jaan specials only; Wine and macOS hardware limitations in README'}
        (output/'patch/release-manifest.json').write_text(json.dumps(public,indent=2)+'\n')
        print(json.dumps({'version':version,'packages':len(records),'output':str(output)}))
    result=[]
    for record in json.loads((output/'SHA256SUMS.json').read_text())['files']:
        archive=output/record['file'];assert sha(archive)==record['sha256']
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            names=z.namelist();assert len(names)==len(set(names))
            assert all(not name.startswith('/') and '..' not in Path(name).parts for name in names)
            manifest_name=next(n for n in names if n.count('/')==1 and n.endswith('/manifest.json'))
            prefix=manifest_name.removesuffix('manifest.json');m=json.loads(z.read(manifest_name))
            assert m['version']==version and m['platform']==record['platform'] and m['kind']==record['kind']
            assert set(names)=={prefix+name for name in m['files']}|{manifest_name}
            for name,item in m['files'].items():
                data=z.read(prefix+name);assert hashlib.sha256(data).hexdigest()==item['sha256'] and len(data)==item['bytes']
                if record['kind']=='patch':
                    assert hashlib.sha256(data).hexdigest() not in protected,(record['file'],name)
                    assert 'game-data' not in Path(name).parts
                    assert Path(name).suffix.upper() not in {'.DAT','.FIG','.XBB','.XGB','.MUS','.PPM','.PAH','.COM','.IDX','.RGB'}
            assert z.read(prefix+'VERSION').decode().strip()==version
            assert z.read(prefix+'README-zh-TW.txt').startswith(b'\xef\xbb\xbf')
            assert 'LICENSE' in m['files'] and any(n.startswith('licenses/') for n in m['files'])
            if record['kind']=='full-local':assert sum('/game-data/' in n for n in names)==len(originals)
            result.append({'file':record['file'],'files':len(names),'verified':True})
    audit={'version':version,'packages':result,'public_original_data_excluded':True,'local_original_files_per_package':len(originals)}
    (output/'smoke/package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))


if __name__=='__main__':main()
