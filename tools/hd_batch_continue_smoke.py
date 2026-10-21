"""049 正式單打接關：原 AI 擊倒、HD 切換與兩個返回分支。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--choice',type=int,choices=(0,1),required=True)
    parser.add_argument('--fallback',action='store_true')
    parser.add_argument('--quit-after-seconds',type=int,default=1200)
    args=parser.parse_args()
    script=Path(__file__).read_bytes()
    script_sha=hashlib.sha256(script).hexdigest()
    assert args.quit_after_seconds>0
    args.output.mkdir(exist_ok=False)
    (args.output/Path(__file__).name).write_bytes(script)
    for name in ('home','runtime'): (args.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(args.output/'home'),XDG_RUNTIME_DIR=str(args.output/'runtime'),
        LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    observe,capture=args.output/'observe.json',args.output/'capture.png'
    command=[str(args.binary),'-data','/orig','-user-data',str(args.output/'user-data'),'-observe',str(observe),
        '-capture',str(capture),'-quit-after',str(args.quit_after_seconds)+'s',
        '-hd-screens','/nonexistent' if args.fallback else str(args.binary.parent/'assets/hd')]
    processes,logs,events=[],[],[]
    game,window=None,None
    started=time.monotonic()
    def spawn(cmd,label):
        log=(args.output/(label+'.log')).open('wb');logs.append(log)
        process=subprocess.Popen(cmd,env=env,stdout=log,stderr=log);processes.append(process);return process
    def state():
        try:return json.loads(observe.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=90,progress=False):
        end=time.monotonic()+seconds;hard=started+args.quit_after_seconds;last_steps=None;last=None
        while time.monotonic()<min(end,hard):
            if game is not None and game.poll() is not None:raise RuntimeError('native exited '+str(game.returncode))
            last=state()
            if last:
                assert not last['core'].get('error'),last
                assert not last['core']['training']['modified']
                if predicate(last):return last
                steps=last['core']['steps']
                if progress and last_steps is not None and steps>last_steps:end=min(time.monotonic()+seconds,hard)
                last_steps=steps
            time.sleep(.03)
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
        for path in capture.parent.glob(capture.name+'.*'):path.unlink()
        key('F12');end=time.monotonic()+15
        while not capture.exists() and time.monotonic()<end:time.sleep(.02)
        assert capture.exists()
        # Capture metadata is committed after PNG, wait for the complete capture set.
        wait(lambda s:s['core']['paused'],10)
        meta=Path(str(capture)+'.capture.json')
        end=time.monotonic()+10
        while not meta.exists() and time.monotonic()<end:time.sleep(.02)
        assert meta.exists()
        shutil.copyfile(capture,args.output/(name+'.png'))
        for path in capture.parent.glob(capture.name+'.*'):
            shutil.copyfile(path,args.output/(name+'.png'+path.name[len(capture.name):]))
        current=state();events.append({'name':name,'state':current})
        print(name,'steps',current['core']['steps'],'continue',current.get('result_hd'),'HD',current['result_hd_active'],flush=True)
    def freeze():
        click(265,32);return wait(lambda s:s['core']['paused'])
    def resume():
        click(110,32);wait(lambda s:not s['core']['paused'])
    def view(s):return (s.get('result_hd') or {}).get('continue')
    def choose(side):
        key('Right' if side else 'Left')
        wait(lambda s:view(s) is not None and view(s)['selected']==side,progress=True)
        freeze()
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        end=time.monotonic()+30
        while window is None and time.monotonic()<end:
            try:window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1]
            except (subprocess.CalledProcessError,IndexError):time.sleep(.05)
        assert window is not None;xdo('windowfocus','--sync',window)
        if not state()['hd_enabled']:
            click(830,32);wait(lambda s:s['hd_enabled'])
        resume();wait(lambda s:s['core']['steps']>=40_000_000,progress=True)
        xdo('mousemove','--window',window,242,607);xdo('mousedown',1)
        before=state()['core']['steps']
        wait(lambda s:s['core']['steps']>=before+1_250_000,progress=True)
        xdo('mouseup',1)
        wait(lambda s:s['core'].get('selection',{}).get('player')==0,progress=True)
        before=state()['core']['steps'];wait(lambda s:s['core']['steps']>=before+8_000_000,progress=True)
        key('Return')
        wait(lambda s:s['core']['battle'] and s['core']['mode']==0 and s['core']['fighters'][0]==0 and s['core']['frames']>0,progress=True)
        opening=freeze();opponent=opening['core']['fighters'][1]
        assert 0<=opponent<11
        shot('single-battle');resume()
        losses=set()
        def lost_and_prompt(s):
            h=s['presentation'].get('hud',{}).get('state',{})
            if h and h['display_health'][0]==0 and h['display_health'][1]>0:losses.add(h['round_index'])
            return view(s) is not None
        wait(lost_and_prompt,180,progress=True)
        assert losses=={0,1},losses
        frozen=freeze();assert view(frozen)['selected']==0
        assert frozen['result_hd']['characters']==[0,opponent]
        assert frozen['result_hd_active']==(not args.fallback)
        shot('continue-left-hd')
        click(830,32);original=wait(lambda s:not s['hd_enabled'] and not s['hd_active']);shot('continue-left-original')
        click(830,32);restored=wait(lambda s:s['hd_enabled'] and s['result_hd_active']==(not args.fallback));shot('continue-left-restored')
        for field in ('core','presentation','settings','assigned','result_hd'):
            assert frozen[field]==original[field]==restored[field],field
        resume();choose(1);shot('continue-right-hd')
        resume();choose(0);shot('continue-left-after-toggle')
        if args.choice==1:resume();choose(1)
        shot('continue-chosen')
        resume();key('Return')
        wait(lambda s:not s.get('result_hd') and not s['result_hd_active'],progress=True)
        before=state()['core']['steps'];wait(lambda s:s['core']['steps']>=before+75_000_000,progress=True)
        freeze();shot('after-continue-choice')
        destination=state()['core']
        assert not destination['battle'] and (destination.get('selection') is not None)==(args.choice==0)
        receipt={'kind':'049 formal Linux single-player AI loss and continue sample',
            'choice':args.choice,'opponent':opponent,'fallback':args.fallback,'knockout_rounds':sorted(losses),'events':events,'command':command,
            'binary_sha256':sha(args.binary),'script_sha256':script_sha,
            'elapsed_seconds':time.monotonic()-started,'inputs':'normal X11 title/selection/continue keyboard and mouse; no battle input, training, health, winner, position or RNG writes'}
        (args.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        (args.output/'failure.json').write_text(json.dumps({'error':repr(exc),'state':state(),'events':events,
            'command':command,'elapsed_seconds':time.monotonic()-started,'script_sha256':script_sha},ensure_ascii=False,indent=2)+'\n')
        raise
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        for log in logs:log.close()


if __name__=='__main__':main()
