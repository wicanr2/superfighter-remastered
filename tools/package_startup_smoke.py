"""啟動解壓後的公開／本機封包，驗版本、缺資料提示、ZIP 匯入與 HD 自動準備。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--platform',choices=['linux-amd64','windows-amd64'],required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--extracted-index',type=Path,default=Path('/project/workplace/release-unpacked-v1/extracted.json'))
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    root=Path('/project');version=(root/'VERSION').read_text().strip()
    inputs=json.loads(a.extracted_index.read_text())
    env=dict(os.environ,DISPLAY=':88',HOME=str(a.output/'home'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    (a.output/'home').mkdir();runtime=a.output/'runtime';runtime.mkdir(mode=0o700);env['XDG_RUNTIME_DIR']=str(runtime)
    wine=a.platform.startswith('windows')
    if wine:env.update(WINEPREFIX=str(a.output/'wine-prefix'),WINEARCH='win64',WINEDEBUG='-all',WINEDLLOVERRIDES='winemenubuilder.exe=d',EBITENGINE_GRAPHICS_LIBRARY='opengl')
    xvfb=subprocess.Popen(['Xvfb',':88','-screen','0','1280x1024x24','-nolisten','tcp'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    game=None
    checks=[]
    def cmd(binary,words):
        parts=[str(binary),*map(str,words)]
        return ['wine',parts[0],*['Z:'+w.replace('/','\\') if w.startswith('/') else w for w in parts[1:]]] if wine else parts
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def state():
        try:return json.loads(observe.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=90):
        deadline=time.monotonic()+seconds;last=None
        while time.monotonic()<deadline:
            if game is not None and game.poll() is not None:raise RuntimeError('packaged process exited')
            last=state()
            if last and predicate(last):return last
            time.sleep(.03)
        raise TimeoutError(last)
    def key(name):
        before=state()['frontend_updates'];xdo('keydown',name)
        pressed=wait(lambda s:s['frontend_updates']>=before+2,10)
        xdo('keyup',name);wait(lambda s:s['frontend_updates']>=pressed['frontend_updates']+2,10)
    def stop(proc):
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
    try:
        time.sleep(.3)
        for kind in ('patch','full-local'):
            item=next(x for x in inputs if x['platform']==a.platform and x['kind']==kind)
            package=Path(item['root']);binary=Path(item['binary'])
            result=subprocess.run(cmd(binary,['-version']),cwd=package,env=env,capture_output=True,text=True,timeout=90)
            assert result.returncode==0 and version in result.stdout,(result.returncode,result.stdout,result.stderr)
            data=package/'game-data'
            if kind=='patch':
                assert not data.exists()
                missing=subprocess.run(cmd(binary,['-data',data]),cwd=package,env=env,capture_output=True,text=True,timeout=90)
                assert missing.returncode!=0 and '-import-data' in missing.stderr
                imported=subprocess.run(cmd(binary,['-import-data',root/'快打至尊.jsdos','-data',data]),cwd=package,env=env,capture_output=True,text=True,timeout=90)
                assert imported.returncode==0,(imported.stdout,imported.stderr)
                again=subprocess.run(cmd(binary,['-import-data',root/'快打至尊.jsdos','-data',data]),cwd=package,env=env,capture_output=True,text=True,timeout=90)
                assert again.returncode!=0
            expected=json.loads((root/'internal/gamefiles/source-manifest.json').read_text())
            for entry in expected:assert hashlib.sha256((data/entry['name']).read_bytes()).hexdigest()==entry['sha256']
            current=a.output/kind;current.mkdir();observe=current/'observe.json';capture=current/'settings.png'
            log=(current/'native.log').open('wb')
            game=subprocess.Popen(cmd(binary,['-user-data',current/'user-data','-observe',observe,'-capture',capture,'-quit-after','150s']),cwd=package,env=env,stdout=log,stderr=log)
            loaded=wait(lambda s:s['core']['paused'])
            assert loaded['version']==version and len(loaded['settings']['keyboard'])==2
            assert loaded['audio']['loaded']==(kind=='full-local')
            bg=current/'user-data/hd-backgrounds-v2'
            collection=json.loads((bg/'manifest.json').read_text())
            assert collection['version']==2 and collection['kind']=='background-collection' and len(collection['backgrounds'])==11
            for source in json.loads((root/'internal/hd/background-sources.json').read_text()):
                child=bg/f"scene-{source['scene']:02d}"
                assert hashlib.sha256((child/'reference.idx').read_bytes()).hexdigest()==source['reference_sha256']
                assert hashlib.sha256((child/'palette.rgb').read_bytes()).hexdigest()==source['palette_sha256']
            deadline=time.monotonic()+30
            window=None
            while time.monotonic()<deadline:
                try:
                    window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1]
                    break
                except (subprocess.CalledProcessError,IndexError):
                    time.sleep(.1)
            if window is None:raise TimeoutError('packaged window did not become visible')
            xdo('windowfocus','--sync',window);key('F10');wait(lambda s:s['panel']);key('F12')
            deadline=time.monotonic()+10
            while not capture.exists() and time.monotonic()<deadline:time.sleep(.03)
            assert capture.is_file() and state()['core']['steps']==0
            key('Escape')
            xdo('mousemove','--window',window,110,32);xdo('mousedown',1)
            wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
            started=wait(lambda s:not s['core']['paused'] and s['core']['steps']>=1_000_000)
            stop(game);game=None;log.close()
            checks.append({'kind':kind,'version':version,'startup':True,'original_files':len(expected),'HD_reference_generated_from_user_data':True,
                           'missing_source_and_safe_import_verified':kind=='patch','binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
                           'settings_capture':str(capture.relative_to(a.output)),'steps':started['core']['steps']})
        result={'version':version,'platform':a.platform,'wine':wine,'checks':checks,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'limits':'actual extracted package startup and CLI; Windows under Wine, no native Windows/macOS hardware'}
        (a.output/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
    finally:
        stop(game)
        if wine:subprocess.run(['wineserver','-k'],env=env,timeout=10,check=False)
        stop(xvfb)


if __name__=='__main__':main()
