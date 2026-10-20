"""正常法蘭克同角雙打，核對雙色、行走、切換及舊程式回退。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--hd-characters',type=Path,required=True)
    p.add_argument('--expect-original',action='store_true');a=p.parse_args();a.output.mkdir(exist_ok=False)
    source=Path(__file__).read_bytes();(a.output/'duplicate_palette_smoke.py').write_bytes(source)
    for name in ('home','runtime'):(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','900s','-hd-assets','/project/workplace/hd-rooftop-study','-hd-characters',str(a.hd_characters)]
    processes=[];logs=[];events=[];game=None;started=time.monotonic()
    def spawn(cmd,name):
        f=(a.output/(name+'.log')).open('wb');logs.append(f);proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=f);processes.append(proc);return proc
    def state():
        try:return json.loads(observe.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=90):
        end=min(started+890,time.monotonic()+seconds);last=None
        while time.monotonic()<end:
            if game and game.poll() is not None:raise RuntimeError(f'game exited {game.returncode}')
            last=state()
            if last:
                assert not last['core'].get('error'),last['core']
                if predicate(last):return last
            time.sleep(.02)
        raise TimeoutError(last)
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1);down=wait(lambda s:s['mouse_left'],10)
        xdo('mouseup',1);wait(lambda s:not s['mouse_left'] and s['frontend_updates']>down['frontend_updates'],10)
    def key(name):
        before=state()['frontend_updates'];xdo('keydown',name);down=wait(lambda s:s['frontend_updates']>=before+2,10)
        xdo('keyup',name);wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
    def shot(name):
        capture.unlink(missing_ok=True)
        for item in capture.parent.glob('capture.png.*'):item.unlink()
        key('F12');end=time.monotonic()+15
        while not capture.exists() and time.monotonic()<end:time.sleep(.02)
        assert capture.exists();shutil.copyfile(capture,a.output/(name+'.png'))
        for item in capture.parent.glob('capture.png.*'):shutil.copyfile(item,a.output/(name+'.png'+item.name[len('capture.png'):]))
        snapshot=state();events.append({'name':name,'state':snapshot});print(name,snapshot['core']['steps'],snapshot['hd_active'],flush=True)
    def compare(prefix):
        frozen=state();assert frozen['core']['paused'] and frozen['hd_active']!=a.expect_original
        if a.expect_original:assert '角色色盤轉場' in frozen['hd_reason']
        shot(prefix+'-hd');click(830,32);original=wait(lambda s:not s['hd_enabled']);shot(prefix+'-original')
        click(830,32);restored=wait(lambda s:s['hd_enabled']);shot(prefix+'-restored')
        for field in ('core','presentation','settings','assigned'):assert frozen[field]==original[field]==restored[field],field
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1];xdo('windowfocus','--sync',window)
        click(110,32);wait(lambda s:s['core']['steps']>=40_000_000)
        xdo('mousemove','--window',window,455,607);xdo('mousedown',1);before=state()['core']['steps']
        wait(lambda s:s['core']['steps']>=before+1_250_000);xdo('mouseup',1);wait(lambda s:s['core']['steps']>=65_000_000)
        for _ in range(4):
            before=state()['core']['steps'];key('Right');wait(lambda s:s['core']['steps']>=before+1_000_000)
        key('Return');wait(lambda s:s['core']['steps']>=85_000_000);key('Return')
        wait(lambda s:s['core']['battle'] and s['core']['frames']>8 and s['presentation'].get('layers_complete') and not s['presentation'].get('round_message'))
        assert state()['core']['fighters']==[4,4]
        click(265,32);wait(lambda s:s['core']['paused']);click(830,32);wait(lambda s:s['hd_enabled'])
        compare('idle')
        click(110,32);wait(lambda s:not s['core']['paused']);before=state()['core']['frames']
        # 已驗右側法蘭克按 KP_Left 前進時，原版 key_values 觀測值為 2。
        xdo('keydown','KP_Left');wait(lambda s:s['core']['key_values'][1]==2)
        wait(lambda s:s['core']['frames']>=before+8);click(265,32);wait(lambda s:s['core']['paused'])
        xdo('keyup','KP_Left');compare('walk')
        click(110,32);wait(lambda s:not s['core']['paused'])
        wait(lambda s:s['core']['paths']==[0,0] and s['core']['key_values']==[0,0] and s['hd_active']!=a.expect_original)
        click(265,32);wait(lambda s:s['core']['paused']);shot('after-release')
        receipt={'kind':'normal native duplicate Frank colours, movement and paused switching','events':events,'command':command,'expected_original':a.expect_original,'binary_sha256':hashlib.sha256(a.binary.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(source).hexdigest(),'character_manifest_sha256':hashlib.sha256((a.hd_characters/'manifest.json').read_bytes()).hexdigest(),'inputs':'X11 keyboard/mouse only; no training or game-state writes','elapsed_seconds':time.monotonic()-started}
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        (a.output/'failure.json').write_text(json.dumps({'error':repr(exc),'events':events,'state':state(),'script_sha256':hashlib.sha256(source).hexdigest()},ensure_ascii=False,indent=2)+'\n');raise
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for f in logs:f.close()

if __name__=='__main__':main()
