"""049 正式場景抽樣：正常雙打選角、捲動及同狀態原貌切換。"""
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
    p.add_argument('--player0',type=int,choices=range(11),default=0)
    p.add_argument('--player1',type=int,choices=range(11),required=True)
    p.add_argument('--exercise',action='store_true')
    p.add_argument('--wine',action='store_true')
    p.add_argument('--cursor-only',action='store_true',help='另驗可見原游標、原右下限界與滑鼠雙打入口')
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    assert not(a.cursor_only and a.fallback)
    script=Path(__file__).read_bytes();(a.output/Path(__file__).name).write_bytes(script)
    for name in('home','runtime'):(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    env.pop('KDZZ_TITLE_PROTOTYPE_ART',None)

    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','900s','-hd-screens','/nonexistent' if a.fallback else str(a.binary.parent/'assets/hd')]
    if a.wine:
        env.update(WINEPREFIX=str(a.output/'wine-prefix'),WINEARCH='win64',WINEDEBUG='-all',WINEDLLOVERRIDES='winemenubuilder.exe=d',EBITENGINE_GRAPHICS_LIBRARY='opengl')
        command=['wine',command[0],*['Z:'+word.replace('/','\\') if word.startswith('/') else word for word in command[1:]]]
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
                title=last['core'].get('title_hd')
                if title and last['title_hd_active']:seen.add(title['phase'])
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
    def title(s):return s['core'].get('title_hd')
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
        print(name,snapshot['core']['steps'],snapshot['core']['title_stage'],snapshot['title_hd_active'],flush=True)
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        deadline=time.monotonic()+30;window=None
        while time.monotonic()<deadline:
            try:
                found=xdo('search','--onlyvisible','--name','Remastered').splitlines()
                if found:window=found[-1];break
            except subprocess.CalledProcessError:pass
            time.sleep(.05)
        assert window is not None,'native window not visible'
        xdo('windowfocus','--sync',window)
        resume();selected(0)
        click(830,32);wait(lambda s:s['hd_enabled'])
        key('Right');selected(1);key('Return')
        wait(lambda s:s['core'].get('selection')is not None)
        for player,character in enumerate((a.player0,a.player1)):
            wait(lambda s:s['core'].get('selection',{}).get('player')==player and s['selection_hd_active'])
            click(24+(character%6)*180+86,700+(character//6)*40+18)
            wait(lambda s:s['core'].get('selection',{}).get('cursor')==character and s['core']['selection'].get('target',-1)<0)
            pause();shot('selection-player-'+str(player));resume()
            click(1010,758)
        wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active'])
        pause();frozen=state();shot('battle-hd')
        assert frozen['core']['fighters']==[a.player0,a.player1]
        assert frozen['presentation']['scene']==a.player1
        click(830,32);original=wait(lambda s:not s['hd_enabled']);shot('battle-original')
        click(830,32);restored=wait(lambda s:s['hd_enabled']and s['hd_active']);shot('battle-restored')
        for field in('core','presentation','settings','assigned'):
            assert frozen[field]==original[field]==restored[field],field
        if a.exercise:
            resume()
            for label,name,count in [('walk','d',30),('crouch','x',10),('jump','w',10),('punch','Tab',15),('kick','Shift_L',15)]:
                initial=state()['core']['frames'];xdo('keydown',name)
                wait(lambda s:s['core']['frames']>=initial+count)
                xdo('keyup',name);pause();shot(label)
                assert state()['core']['battle']and not state()['core']['training']['modified']
                resume()
            initial=state()['core']['frames'];wait(lambda s:s['core']['frames']>=initial+20)
            pause();shot('after-release')
        receipt={'kind':'049 formal normal double-player scene sample','command':command,'wine':a.wine,'player0':a.player0,'player1':a.player1,
                 'scene':a.player1,'events':events,'script_sha256':sha(Path(__file__)), 'binary_sha256':sha(a.binary),
                 'character_manifest_sha256':sha(a.binary.parent/'assets/hd/characters/manifest.json'),
                 'input':'X11 keyboard/mouse only, no injected game state, RNG or training',
                 'elapsed_seconds':time.monotonic()-started,'limits':'selected ordinary actions only; no complete animation or physical controller claim'}
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as error:
        (a.output/'failure.json').write_text(json.dumps({'error':repr(error),'state':state(),'events':events,'seen':sorted(seen),'script_sha256':hashlib.sha256(script).hexdigest()},ensure_ascii=False,indent=2)+'\n');raise
    finally:
        if a.wine:
            subprocess.run(['wineserver','-k'],env=env,timeout=10,check=False)
        for process in reversed(processes):
            if process.poll()is None:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        for log in logs:log.close()


if __name__=='__main__':main()
