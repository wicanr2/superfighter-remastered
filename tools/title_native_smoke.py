"""隔離原生標題 HD 原型：原鍵鼠、同狀態切換、設定往返與進入雙打。"""
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
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--fallback',action='store_true')
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    script=Path(__file__).read_bytes();(a.output/'title_native_smoke.py').write_bytes(script)
    for name in('home','runtime'):(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    env.pop('KDZZ_TITLE_PROTOTYPE_ART',None)
    if not a.fallback:env['KDZZ_TITLE_PROTOTYPE_ART']='/project/workplace/title-animation-v3'
    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','900s','-hd-assets','/project/workplace/hd-rooftop-study','-hd-characters','/project/assets/hd/characters']
    processes=[];logs=[];events=[];game=None;started=time.monotonic();seen=set()
    def spawn(cmd,name):
        log=(a.output/(name+'.log')).open('wb');logs.append(log)
        process=subprocess.Popen(cmd,env=env,stdout=log,stderr=log);processes.append(process);return process
    def state():
        try:return json.loads(observe.read_text())
        except(FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=120):
        end=min(started+890,time.monotonic()+seconds);last=None
        while time.monotonic()<end:
            if game and game.poll()is not None:raise RuntimeError(('game exited',game.returncode))
            last=state()
            if last:
                assert not last['core'].get('error'),last['core']
                title=last['core'].get('title_prototype')
                if title and last['title_hd_prototype']:seen.add(title['phase'])
                if predicate(last):return last
            time.sleep(.005)
        raise TimeoutError(last)
    def xdo(*args):return subprocess.check_output(['xdotool',*map(str,args)],env=env,text=True,timeout=5).strip()
    def key(name):
        before=state()['frontend_updates'];xdo('keydown',name)
        down=wait(lambda s:s['frontend_updates']>=before+2,10);xdo('keyup',name)
        wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
        down=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
        wait(lambda s:not s['mouse_left']and s['frontend_updates']>down['frontend_updates'],10)
    def pause():
        key('Escape');return wait(lambda s:s['core']['paused'])
    def resume():
        click(110,32);wait(lambda s:not s['core']['paused'])
    def title(s):return s['core'].get('title_prototype')
    def selected(value):return wait(lambda s:title(s)and title(s)['selected']==value)
    def shot(name):
        capture.unlink(missing_ok=True)
        for item in capture.parent.glob('capture.png.*'):item.unlink()
        key('F12');end=time.monotonic()+20
        while not capture.exists()and time.monotonic()<end:time.sleep(.005)
        assert capture.exists()
        shutil.copyfile(capture,a.output/(name+'.png'))
        for item in capture.parent.glob('capture.png.*'):shutil.copyfile(item,a.output/(name+'.png'+item.name[len('capture.png'):]))
        snapshot=state();events.append({'name':name,'state':snapshot})
        print(name,snapshot['core']['steps'],snapshot['core']['title_prototype_stage'],snapshot['title_hd_prototype'],flush=True)
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=xdo('search','--onlyvisible','--name','Remastered').splitlines()[-1];xdo('windowfocus','--sync',window)
        resume();selected(0);pause();assert title(state())
        click(830,32);wait(lambda s:s['hd_enabled']and s['title_hd_prototype']!=a.fallback)
        frozen=state();shot('title-hd')
        click(830,32);original=wait(lambda s:not s['hd_enabled']);shot('title-original')
        click(830,32);restored=wait(lambda s:s['hd_enabled']);shot('title-restored')
        for field in('core','presentation','settings','assigned'):assert frozen[field]==original[field]==restored[field],field
        resume()
        if a.fallback:
            key('Right');selected(1);pause();shot('fallback-next-selection')
        else:
            wait(lambda s:len(seen)==8,180)
            key('Right');selected(1);pause();shot('versus-highlight-hd');resume()
            key('Right');selected(2);pause();shot('settings-highlight-hd');resume()
            key('Return');wait(lambda s:s['core']['title_prototype_stage']=='settings'and not title(s)and not s['title_hd_prototype']);pause();shot('settings-original');resume()
            ip=0x0b89
            wait(lambda s:s['core']['title_prototype_input']['runtime_ip']==ip and s['core']['title_prototype_input']['buttons']&1==0)
            before=state()['core']['steps'];xdo('mousemove','--window',window,860,433);xdo('mousedown',1)
            wait(lambda s:s['core']['title_prototype_input']['runtime_ip']==ip and s['core']['title_prototype_input']['steps']>before and s['core']['title_prototype_input']['buttons']&1 and not s['core']['title_prototype_input']['old_buttons']&1,90)
            xdo('mouseup',1)
            wait(lambda s:title(s)and s['title_hd_prototype']);pause();shot('returned-title-hd');resume()
            for _ in range(4):
                if title(state())and title(state())['selected']==1:break
                old=title(state())['selected'];key('Right');selected((old+1)%4)
            selected(1);key('Return')
            wait(lambda s:s['core'].get('selection')is not None and not title(s)and not s['title_hd_prototype']);pause();shot('versus-selection-original');resume()
            key('Return');wait(lambda s:s['core'].get('selection',{}).get('player')==1)
            for _ in range(4):
                current=state()['core']['selection']['cursor'];key('Right');wait(lambda s:s['core'].get('selection',{}).get('cursor')==current+1)
            key('Return');wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active']);pause();shot('battle-hd-after-title')
            assert not title(state())and not state()['title_hd_prototype']and state()['core']['fighters']==[0,4]
        receipt={'kind':'disposable native 046 prototype; not production acceptance','command':command,'fallback':a.fallback,
                 'events':events,'observed_HD_phases':sorted(seen),'script_sha256':hashlib.sha256(script).hexdigest(),
                 'binary_sha256':sha(a.binary),'character_manifest_sha256':sha(Path('/project/assets/hd/characters/manifest.json')),
                 'input':'X11 keyboard/mouse only, no injected game state or training','elapsed_seconds':time.monotonic()-started,
                 'limits':'Linux copied module only; material source-mask remains hypothesis, cursor remains original, no formal format/HD completion or hardware controller claim'}
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as error:
        (a.output/'failure.json').write_text(json.dumps({'error':repr(error),'state':state(),'events':events,'seen':sorted(seen),'script_sha256':hashlib.sha256(script).hexdigest()},ensure_ascii=False,indent=2)+'\n');raise
    finally:
        for process in reversed(processes):
            if process.poll()is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        for log in logs:log.close()


if __name__=='__main__':main()
