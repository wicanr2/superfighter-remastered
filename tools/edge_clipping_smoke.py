"""正常方向／蹲跳／拳腳走至場邊投擲，核對新舊 HD 幾何與切換。"""
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
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--hd-characters',type=Path,required=True)
    p.add_argument('--player0',type=int,choices=(0,2),required=True)
    p.add_argument('--expect-original',action='store_true')
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    source=Path(__file__).read_bytes();(a.output/'edge_clipping_smoke.py').write_bytes(source)
    for name in ('home','runtime'):(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','1500s','-hd-assets','/project/workplace/hd-rooftop-study','-hd-characters',str(a.hd_characters)]
    processes=[];logs=[];events=[];skips=[];phase_states=[];game=None;started=time.monotonic()
    interacting=False;busy=False;captured=False;watching=False
    def spawn(cmd,name):
        f=(a.output/(name+'.log')).open('wb');logs.append(f)
        proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=f);processes.append(proc);return proc
    def state():
        try:return json.loads(observe.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return None
    def edge(s):
        return any((l.get('sprite',{}).get('flags',0)&192)==192 and l['sprite']['right_clip']>0 and not l['sprite'].get('effect') for l in s['presentation'].get('layers',[]))
    def wait(predicate,seconds=120):
        end=min(started+1490,time.monotonic()+seconds);last=None
        while time.monotonic()<end:
            if game and game.poll() is not None:raise RuntimeError(f'game exited {game.returncode}')
            last=state()
            if last:
                assert not last['core'].get('error'),last['core']
                if watching and not busy and not interacting and not captured and not last['core']['paused'] and edge(last):
                    capture_edge();last=state()
                if predicate(last):return last
            time.sleep(.02)
        raise TimeoutError(last)
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        nonlocal interacting
        previous=interacting;interacting=True
        try:
            xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
            down=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
            wait(lambda s:not s['mouse_left'] and s['frontend_updates']>down['frontend_updates'],10)
        finally:interacting=previous
    def key(name):
        nonlocal interacting
        previous=interacting;interacting=True
        try:
            before=state()['frontend_updates'];xdo('keydown',name)
            down=wait(lambda s:s['frontend_updates']>=before+2,10);xdo('keyup',name)
            wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
        finally:interacting=previous
    def shot(name):
        capture.unlink(missing_ok=True)
        for item in capture.parent.glob('capture.png.*'):item.unlink()
        key('F12');end=time.monotonic()+15
        while not capture.exists() and time.monotonic()<end:time.sleep(.02)
        assert capture.exists()
        shutil.copyfile(capture,a.output/(name+'.png'))
        for item in capture.parent.glob('capture.png.*'):
            shutil.copyfile(item,a.output/(name+'.png'+item.name[len('capture.png'):]))
        snapshot=state();events.append({'name':name,'state':snapshot})
        print(name,snapshot['core']['steps'],snapshot['hd_active'],flush=True)
    def capture_edge():
        nonlocal busy,captured
        busy=True
        try:
            click(265,32);frozen=wait(lambda s:s['core']['paused'])
            if edge(frozen) and frozen['hd_active']!=a.expect_original:
                shot('edge-hd')
                click(830,32);original=wait(lambda s:not s['hd_enabled']);shot('edge-original')
                click(830,32);restored=wait(lambda s:s['hd_enabled']);shot('edge-restored')
                for field in ('core','presentation','settings','assigned'):assert frozen[field]==original[field]==restored[field],field
                captured=True
            elif len(skips)<20:skips.append({'steps':frozen['core']['steps'],'edge':edge(frozen),'reason':frozen['hd_reason']})
            click(110,32);wait(lambda s:not s['core']['paused'])
        finally:busy=False
    phases=[('idle',(),12),('walk',('d',),32),('release-walk',(),8),('crouch',('x',),16),('jump',('w',),48),('release-jump',(),12),('punch',('Tab',),20),('release-punch',(),12),('kick',('Shift_L',),24),('release-kick',(),20),('forward-jump-kick',('e','Shift_L'),52),('release-air',(),24),('close-walk',('d',),36),('close-punch',('Tab',),32),('release-close-punch',(),24),('close-kick',('Shift_L',),32),('release-close-kick',(),32)]
    all_keys=('d','x','w','Tab','Shift_L','e')
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1];xdo('windowfocus','--sync',window)
        click(110,32);wait(lambda s:s['core']['steps']>=40_000_000)
        xdo('mousemove','--window',window,455,607);xdo('mousedown',1)
        before=state()['core']['steps'];wait(lambda s:s['core']['steps']>=before+1_250_000);xdo('mouseup',1)
        wait(lambda s:s['core']['steps']>=65_000_000)
        for _ in range(a.player0):
            before=state()['core']['steps'];key('Right');wait(lambda s:s['core']['steps']>=before+1_000_000)
        key('Return');wait(lambda s:s['core']['steps']>=85_000_000)
        for _ in range(4-a.player0):
            before=state()['core']['steps'];key('Right');wait(lambda s:s['core']['steps']>=before+1_000_000)
        key('Return');wait(lambda s:s['core']['battle'] and s['core']['frames']>8)
        assert state()['core']['fighters']==[a.player0,4]
        click(830,32)
        wait(lambda s:s['hd_active'] and not s['presentation'].get('round_message') and s['presentation'].get('hud',{}).get('state',{}).get('round_state')==0)
        click(265,32);wait(lambda s:s['core']['paused']);shot('normal-hd')
        click(110,32);wait(lambda s:not s['core']['paused']);watching=True
        for name,keys,count in phases:
            xdo('keyup',*all_keys)
            if keys:xdo('keydown',*keys)
            end=state()['core']['frames']+count;wait(lambda s:s['core']['frames']>=end,180)
            phase_states.append({'phase':name,'state':state()})
            print('phase',name,state()['core']['frames'],flush=True)
        xdo('keyup',*all_keys)
        wait(lambda s:s['core']['paths'][0]==0 and s['core']['key_values'][0]==0 and s['hd_active'])
        assert captured,{'skips':skips,'state':state()}
        click(265,32);wait(lambda s:s['core']['paused']);shot('after-edge')
        receipt={'kind':'normal native clipped mirrored throw and mode restoration; not complete animation','events':events,'skips':skips,'phase_states':phase_states,'command':command,'player0':a.player0,'expected_original':a.expect_original,'script_sha256':hashlib.sha256(source).hexdigest(),'binary_sha256':hashlib.sha256(a.binary.read_bytes()).hexdigest(),'character_manifest_sha256':hashlib.sha256((a.hd_characters/'manifest.json').read_bytes()).hexdigest(),'inputs':'X11 keyboard/mouse only; no training or game-state writes','elapsed_seconds':time.monotonic()-started}
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        (a.output/'failure.json').write_text(json.dumps({'error':repr(exc),'events':events,'skips':skips,'phase_states':phase_states,'state':state(),'script_sha256':hashlib.sha256(source).hexdigest()},ensure_ascii=False,indent=2)+'\n');raise
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for f in logs:f.close()

if __name__=='__main__':main()
