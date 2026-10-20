"""四人正常原生特殊光效、同狀態切換及舊包整格回退。"""
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
    p.add_argument('--character',type=int,choices=(3,6,9,10),required=True)
    p.add_argument('--family',default='',help='isolate one ordinary-input family from a fresh match')
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--hd-characters',type=Path,required=True)
    p.add_argument('--expect-original',action='store_true')
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    source=Path(__file__).read_bytes();(a.output/'remaining_effects_smoke.py').write_bytes(source)
    for name in ('home','runtime'):(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','900s','-hd-assets','/project/workplace/hd-rooftop-study','-hd-characters',str(a.hd_characters)]
    processes=[];logs=[];events=[];game=None;started=time.monotonic()
    def spawn(cmd,name):
        f=(a.output/(name+'.log')).open('wb');logs.append(f)
        proc=subprocess.Popen(cmd,env=env,stdout=f,stderr=f);processes.append(proc);return proc
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
            time.sleep(.005)
        raise TimeoutError(last)
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
        down=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
        wait(lambda s:not s['mouse_left'] and s['frontend_updates']>down['frontend_updates'],10)
    def key(name):
        before=state()['frontend_updates'];xdo('keydown',name)
        down=wait(lambda s:s['frontend_updates']>=before+2,10);xdo('keyup',name)
        wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
    def shot(name):
        capture.unlink(missing_ok=True)
        for item in capture.parent.glob('capture.png.*'):item.unlink()
        key('F12');end=time.monotonic()+15
        while not capture.exists() and time.monotonic()<end:time.sleep(.005)
        assert capture.exists()
        shutil.copyfile(capture,a.output/(name+'.png'))
        for item in capture.parent.glob('capture.png.*'):
            shutil.copyfile(item,a.output/(name+'.png'+item.name[len('capture.png'):]))
        snapshot=state();events.append({'name':name,'state':snapshot})
        print(name,snapshot['core']['steps'],snapshot['hd_active'],flush=True)
    def effect(s,slot):
        return any(l.get('sprite',{}).get('effect') and l['sprite']['character']==a.character and l['sprite']['slot'] in slot for l in s['presentation'].get('layers',[]))
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1];xdo('windowfocus','--sync',window)
        click(110,32);wait(lambda s:s['core']['steps']>=40_000_000)
        xdo('mousemove','--window',window,455,607);xdo('mousedown',1)
        before=state()['core']['steps'];wait(lambda s:s['core']['steps']>=before+1_250_000);xdo('mouseup',1)
        wait(lambda s:s['core']['steps']>=65_000_000)
        for _ in range(a.character):
            before=state()['core']['steps'];key('Right');wait(lambda s:s['core']['steps']>=before+1_000_000)
        key('Return');wait(lambda s:s['core']['steps']>=85_000_000)
        for _ in range(abs(a.character-4)):key('Left' if a.character>4 else 'Right')
        key('Return');wait(lambda s:s['core']['battle'] and s['core']['frames']>8)
        assert state()['core']['fighters']==[a.character,4]
        click(265,32);wait(lambda s:s['core']['paused']);click(830,32);wait(lambda s:s['hd_active']);shot('normal-hd')
        click(110,32);wait(lambda s:not s['core']['paused'])
        phase_events=[];groups=[];held=[]
        def hold(keys,frames):
            before=state()['core']['frames']
            masks={'x':4,'c':5,'d':1,'Tab':16,'a':2,'z':6,'Shift_L':32}
            mask=0
            for name in keys:mask|=masks[name]
            transition=[]
            if held:transition+=['keyup','--delay','0',*held]
            transition+=['keydown','--delay','0',*keys]
            xdo(*transition);held[:]=keys
            pressed=wait(lambda s:s['core']['frames']>before and s['core']['key_values'][0]==mask,60)
            observed=wait(lambda s:s['core']['frames']>=pressed['core']['frames']+frames-1 and s['core']['key_values'][0]==mask,60)
            phase_events.append({'keys':keys,'mask':mask,'minimum_frames':frames,'before':before,'pressed':pressed['core']['frames'],'after':observed['core']['frames'],'key_values':observed['core']['key_values'],'paths':observed['core']['paths']})
        actions={
            3:[('cyan-charge',((['a'],24),(['d','Tab','Shift_L'],2)),{15,39}),('gold-arc',((['a'],1),(['z'],1),(['x','Shift_L'],2)),{56})],
            6:[('gold-wave',((['a'],24),(['d','Tab'],2)),{9,11,12,20,26,57,58})],
            9:[('cyan-projectile',((['x'],1),(['c'],1),(['d','Tab'],2)),{14,19,49,60,61}),('cyan-rings',((['x'],1),(['c'],1),(['d','Tab','Shift_L'],2)),{57,58,59})],
            10:[('orange-wave',((['a'],24),(['d','Tab'],2)),{41,42,43})],
        }[a.character]
        if a.family:
            actions=[x for x in actions if x[0]==a.family]
            assert len(actions)==1,'unknown family'
        for label,phases,slots in actions:
            wait(lambda s:s['core']['paths'][0]==0 and s['core']['key_values'][0]==0)
            for keys,frames in phases:hold(keys,frames)
            xdo('keyup','--delay','0',*held);held.clear()
            observed=wait(lambda s:effect(s,slots),45)
            xdo('keydown','Escape');wait(lambda s:s['core']['paused']);xdo('keyup','Escape')
            frozen=state();assert effect(frozen,slots),(label,frozen)
            assert frozen['hd_active']!=a.expect_original,frozen['hd_reason']
            actual=[l['sprite']['slot']for l in frozen['presentation']['layers']if l.get('sprite',{}).get('effect') and l['sprite']['character']==a.character]
            groups.append({'label':label,'effect_slots':actual,'minimum_observed_serial':observed['presentation']['serial']})
            shot(label+'-hd')
            click(830,32);original=wait(lambda s:not s['hd_enabled']);shot(label+'-original')
            click(830,32);restored=wait(lambda s:s['hd_enabled']);shot(label+'-restored')
            for field in ('core','presentation','settings','assigned'):assert frozen[field]==original[field]==restored[field],field
            click(110,32);wait(lambda s:not s['core']['paused'])
            wait(lambda s:s['core']['paths'][0]==0 and s['core']['key_values'][0]==0 and s['hd_active'] and not any(l.get('sprite',{}).get('effect') for l in s['presentation'].get('layers',[])),120)
        click(265,32);wait(lambda s:s['core']['paused']);shot('after-effects')
        receipt={'kind':'normal native four-character special-effect families; not full animation or hardware acceptance','character':a.character,'family_filter':a.family,'events':events,'groups':groups,'phases':phase_events,'command':command,'expected_original':a.expect_original,'script_sha256':hashlib.sha256(source).hexdigest(),'binary_sha256':hashlib.sha256(a.binary.read_bytes()).hexdigest(),'character_manifest_sha256':hashlib.sha256((a.hd_characters/'manifest.json').read_bytes()).hexdigest(),'inputs':'X11 keyboard/mouse only; no training or game-state writes','elapsed_seconds':time.monotonic()-started}
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        (a.output/'failure.json').write_text(json.dumps({'error':repr(exc),'events':events,'phases':locals().get('phase_events',[]),'groups':locals().get('groups',[]),'state':state(),'script_sha256':hashlib.sha256(source).hexdigest()},ensure_ascii=False,indent=2)+'\n');raise
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for f in logs:f.close()

if __name__=='__main__':main()
