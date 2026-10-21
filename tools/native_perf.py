"""正常選角後比較原貌／HD 與錄影成本，保存實際 renderer 和畫格時間。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import statistics
import subprocess
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['original','hd'],required=True)
    p.add_argument('--renderer',choices=['nvidia','egl','software'],required=True)
    p.add_argument('--record',action='store_true')
    p.add_argument('--cache-check',action='store_true',help='diagnostic build only: paused fresh/cached GPU pixel comparison')
    p.add_argument('--vsync',choices=['on','off','paced'],default='on',help='diagnostic build only')
    p.add_argument('--selection-only',action='store_true',help='validate approved two-row portrait input on production build')
    p.add_argument('--selection-atomic',action='store_true',help='選角錄影與完整畫面發布檢查；使用 --selection-only')
    p.add_argument('--capture-fps',type=int,choices=[0,60],default=0,help='production -capture-fps option')
    p.add_argument('--seconds',type=int,default=20)
    a=p.parse_args();assert 10<=a.seconds<=60
    assert (a.binary.parent/'assets/hd/screens.json').is_file(), 'runtime HD assets missing'
    a.output.mkdir(exist_ok=False)
    for name in ['home','runtime','pulse']:(a.output/name).mkdir(mode=0o700)
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),
             LP_NUM_THREADS='2',GOMAXPROCS='2',PULSE_SERVER='unix:'+str(a.output/'pulse/native'))
    env['KDZZ_TEST_VSYNC']=a.vsync
    env.pop('LIBGL_ALWAYS_SOFTWARE',None)
    if a.renderer=='software':env['LIBGL_ALWAYS_SOFTWARE']='1'
    (a.output/'home/.asoundrc').write_text('pcm.!default { type pulse }\nctl.!default { type pulse }\n')
    processes=[];logs=[];game=None;video=None;events=[];started=time.monotonic()
    observe=a.output/'observe.json';draw_samples={}
    def spawn(cmd,name):
        f=(a.output/(name+'.log')).open('wb');logs.append(f)
        r=subprocess.Popen(cmd,env=env,stdout=f,stderr=f);processes.append(r);return r
    def read():
        try:
            s=json.loads(observe.read_text())
            if a.selection_atomic:
                for f in s.get('performance',{}).get('recent')or[]:draw_samples[f['draw']]=f
            return s
        except(FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=120):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if game and game.poll()is not None:raise RuntimeError(('app exit',game.returncode))
            s=read()
            if s:
                assert not s['core'].get('error') and not s['core']['training']['modified']
                if predicate(s):return s
            time.sleep(.005 if a.selection_atomic else .02)
        raise TimeoutError(read())
    def xdo(*args):return subprocess.check_output(['xdotool',*map(str,args)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
        s=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
        wait(lambda n:not n['mouse_left']and n['frontend_updates']>s['frontend_updates'],10)
    def key(name):
        start=read()['frontend_updates'];xdo('keydown',name)
        s=wait(lambda s:s['frontend_updates']>=start+2,10);xdo('keyup',name)
        wait(lambda n:n['frontend_updates']>=s['frontend_updates']+2,10)
    def capture(name):
        target=a.output/'battle.png'
        old=target.stat().st_mtime_ns if target.exists()else 0
        key('F12');wait(lambda s:target.exists()and target.stat().st_mtime_ns>old)
        shutil.copy2(target,a.output/(name+'.png'))
        shutil.copy2(a.output/'battle.png.capture.json',a.output/(name+'.png.capture.json'))
    def sample(label):
        s=read();assert s and s['core']['battle'] and not s['core']['training']['modified']
        row=dict(seconds=time.monotonic(),label=label,state=s);events.append(row);return row
    def percentile(values,n):
        v=sorted(values);return v[min(len(v)-1,int((len(v)-1)*n/100))]
    def cpu_stat():
        path=Path('/sys/fs/cgroup/cpu.stat')
        return {k:int(v)for k,v in (line.split()for line in path.read_text().splitlines())}if path.is_file()else {}
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.4)
        spawn(['pulseaudio','--daemonize=no','--exit-idle-time=-1','--use-pid-file=no','-n',
               '--load=module-native-protocol-unix socket='+str(a.output/'pulse/native')+' auth-anonymous=1',
               '--load=module-null-sink sink_name=kdzz rate=48000 channels=2','--log-level=warning'],'pulse')
        deadline=time.monotonic()+15
        while not (a.output/'pulse/native').exists() and time.monotonic()<deadline:time.sleep(.05)
        subprocess.run(['pactl','set-default-sink','kdzz'],env=env,check=True,timeout=5)
        wrapper=['/opt/VirtualGL/bin/vglrun','-d','egl0','-c','proxy'] if a.renderer in ('nvidia','egl') else []
        if a.renderer=='software' and shutil.which('glxinfo')is None:
            renderer='LIBGL_ALWAYS_SOFTWARE=1; GL identity query unavailable in this legacy capture image'
        else:
            renderer=subprocess.check_output(wrapper+['glxinfo','-B'],env=env,text=True,timeout=15)
        (a.output/'renderer.txt').write_text(renderer)
        if a.renderer=='nvidia':assert 'NVIDIA' in renderer and 'llvmpipe' not in renderer
        if a.renderer=='egl':assert 'llvmpipe'not in renderer and'softpipe'not in renderer
        command=wrapper+[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),
                         '-observe',str(observe),'-capture',str(a.output/'battle.png'),'-quit-after','240s']
        if a.capture_fps:command+=['-capture-fps',str(a.capture_fps)]
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=None;deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            try:
                rows=xdo('search','--onlyvisible','--name','Remastered').splitlines()
                if rows:window=rows[-1];break
            except subprocess.CalledProcessError:pass
            time.sleep(.05)
        assert window;xdo('windowfocus','--sync',window);xdo('windowmove',window,0,0)
        if a.selection_atomic:
            assert a.selection_only
            video=spawn(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-y','-f','x11grab','-draw_mouse','0',
                         '-framerate','60','-video_size','1120x820','-i',':89.0','-an','-c:v','libx264','-preset','ultrafast',
                         '-crf','18','-threads','1','-pix_fmt','yuv420p',str(a.output/'selection.mp4')],'selection-video')
        click(110,32);wait(lambda s:s['core'].get('title_hd'))
        if read()['hd_enabled']!=(a.mode=='hd'):click(830,32)
        wait(lambda s:s['hd_enabled']==(a.mode=='hd'),10)
        if a.selection_atomic:
            wait(lambda s:s['title_hd_active']);capture('title-hd')
        key('Right');wait(lambda s:s['core'].get('title_hd',{}).get('selected')==1);key('Return')
        wait(lambda s:s['core'].get('selection',{}).get('player')==0)
        if a.selection_only:
            checks=[]
            def portrait(character):
                x,y=(28+33*character,127)if character<8 else(110+33*(character-8),164)
                click(80+(x+16)*3,64+(y+16)*3)
                return wait(lambda s:s['selection_hd_active']and s['core']['selection']['cursor']==character and s['core']['selection']['target']<0 and s['selection_hd']['portraits'][s['core']['selection']['player']]==character,30)
            for side in range(2):
                for character in range(11):
                    s=portrait(character);checks.append(dict(player=side,character=character,selection=s['core']['selection'],portraits=s['selection_hd']['portraits']))
                if side==0:
                    portrait(8);key('Escape');wait(lambda s:s['core']['paused'])
                    click(80+(143+16)*3,64+(164+16)*3)
                    assert read()['core']['selection']['cursor']==8 and read()['core']['selection']['target']<0
                    checks.append(dict(paused_portrait_ignored=True))
                    click(110,32);wait(lambda s:not s['core']['paused'])
                    click(830,32);wait(lambda s:not s['hd_enabled']and not s['selection_hd_active'])
                    click(830,32);wait(lambda s:s['selection_hd_active']);portrait(8)
                    checks.append(dict(original_mode_and_hd_restore=True))
                    capture('selection-player0')
                else:
                    capture('selection-player1')
                # The former external name/confirm buttons must no longer accept input.
                before=read()['frontend_updates']
                click(110,718);click(1010,758)
                wait(lambda s:s['frontend_updates']>=before+4)
                selected=read()['core']['selection']
                assert selected['player']==side and selected['cursor']==(8 if side==0 else 10) and selected['target']<0
                checks.append(dict(player=side,removed_button_positions_ignored=True))
                if side==0:
                    click(830,32);wait(lambda s:not s['hd_enabled']and not s['selection_hd_active'])
                    key('Left');wait(lambda s:s['core']['selection']['cursor']==7 and s['core']['selection']['target']<0)
                    key('Right');wait(lambda s:s['core']['selection']['cursor']==8 and s['core']['selection']['target']<0)
                    if a.selection_atomic:
                        click(830,32);wait(lambda s:s['selection_hd_active'])
                    key('Return');wait(lambda s:s['core'].get('selection',{}).get('player')==1)
                    if a.selection_atomic:
                        checks.append(dict(original_navigation_and_hd_player_handoff=True))
                    else:
                        assert not read()['hd_enabled']
                        checks.append(dict(original_mode_player0_confirmed_to_player1=True))
                        click(830,32);wait(lambda s:s['selection_hd_active'])
                else:key('Return')
            s=wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active'])
            assert s['core']['fighters']==[8,10]
            if a.selection_atomic:capture('battle-hd')
            report=dict(status='passed',checks=checks,battle=s['core'],binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
                        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rights='local source evidence; only approved HD screenshots may be copied to Git')
            if a.selection_atomic:
                selected=[x for x in draw_samples.values()if x.get('selection')and x.get('hd_enabled')]
                raw=[x for x in selected if not x['hd_active']]
                report['selection_presentation']=dict(draws=len(selected),original_frames=len(raw),waiting_frames=sum(x['selection_waiting']for x in selected),raw=raw)
                (a.output/'draws.json').write_text(json.dumps(list(draw_samples.values()),indent=2)+'\n')
                assert selected and not raw,report['selection_presentation']
            (a.output/'receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False),flush=True);return
        def choose(character):
            if a.mode=='hd':
                # The original announces player 2 before its portrait has finished drawing.
                # Wait for the matching rendered selection view before sending a mouse click.
                ready=lambda s:s['selection_hd_active']and s.get('selection_hd')is not None and s['selection_hd']['player']==s['core']['selection']['player']and s['selection_hd']['portraits'][s['core']['selection']['player']]>=0
                first=wait(ready)
                wait(lambda s:ready(s)and s['performance']['draws']>=first['performance']['draws']+2)
                x,y=(28+33*character,127)if character<8 else(110+33*(character-8),164)
                click(80+(x+16)*3,64+(y+16)*3)
                wait(lambda s:s['core']['selection']['cursor']==character and s['core']['selection']['target']<0)
            else:
                for _ in range(11):
                    if read()['core']['selection']['cursor']==character:break
                    before=read()['core']['selection']['cursor'];key('Right')
                    wait(lambda s:s['core']['selection']['cursor']!=before and s['core']['selection']['target']<0)
                assert read()['core']['selection']['cursor']==character
        choose(8);key('Return');wait(lambda s:s['core'].get('selection',{}).get('player')==1)
        choose(4);key('Return');wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active']==(a.mode=='hd'))
        assert read()['core']['fighters']==[8,4]
        key('F12');wait(lambda s:(a.output/'battle.png').is_file());time.sleep(1)
        cache_equivalence=None
        if a.cache_check:
            key('Escape');wait(lambda s:s['core']['paused'])
            if not read()['performance'].get('cache_bypass'):key('F7')
            wait(lambda s:s['performance']['cache_bypass']);time.sleep(.2)
            first=read()
            def grab(name):
                dest=a.output/(name+'.png')
                subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','x11grab',
                                '-video_size','1120x820','-i',':89.0','-frames:v','1',str(dest)],env=env,check=True,timeout=15)
                return subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(dest),
                                                '-vf','crop=960:600:80:64','-f','rawvideo','-pix_fmt','rgba','-'],timeout=15)
            fresh=grab('cache-fresh')
            key('F7');wait(lambda s:not s['performance']['cache_bypass']and s['performance']['cache_hits']>first['performance']['cache_hits']+5)
            cached=grab('cache-reused');last=read()
            assert first['core']==last['core'],'paused core changed during rendering comparison'
            assert fresh==cached,'GPU cached viewport differs from fresh rendering'
            cache_equivalence=dict(pixels_equal=True,rgba_bytes=len(fresh),sha256=hashlib.sha256(fresh).hexdigest(),core_steps=first['core']['steps'])
            key('Escape');wait(lambda s:not s['core']['paused']);time.sleep(.5)
        if a.record:
            video=spawn(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-y','-f','x11grab',
                         '-draw_mouse','0','-framerate','60','-video_size','1120x820','-i',':89.0','-an',
                         '-c:v','libx264','-preset','ultrafast','-crf','18','-threads','1','-pix_fmt','yuv420p',
                         str(a.output/'capture-60fps.mp4')],'video')
            time.sleep(.5)
        before=sample('start');cpu_before=cpu_stat();beg=time.monotonic();index=-1;held=None
        assert before['state']['hd_enabled']==(a.mode=='hd') and before['state']['hd_active']==(a.mode=='hd')
        pattern=['d','Tab','Shift_L','w','x','a','d','Tab','Shift_L','Return']
        while time.monotonic()-beg<a.seconds:
            elapsed=time.monotonic()-beg;n=int(elapsed/1.0)
            if n!=index:
                if held:xdo('keyup',held)
                held=pattern[n%len(pattern)];xdo('keydown',held);index=n
            sample(None);time.sleep(.02)
        if held:xdo('keyup',held)
        after=sample('end');cpu_after=cpu_stat();dt=after['seconds']-before['seconds'];b=before['state'];e=after['state']
        rows=[v['state']['performance'] for v in events if v['state'].get('performance')]
        assert rows,'instrumented performance build required'
        metrics={}
        for name in ['step_ms','update_ms','draw_ms','interval_ms','fps','tps']:
            values=[v[name]for v in rows];metrics[name]=dict(mean=statistics.mean(values),p50=percentile(values,50),p95=percentile(values,95),p99=percentile(values,99),max=max(values))
        unique={f['draw']:f for r in rows for f in r.get('recent',[]) if b['performance']['draws']<f['draw']<=e['performance']['draws']}
        frame_times=[unique[k]['interval_ms']for k in sorted(unique)]
        if frame_times:
            metrics['distinct_frame_intervals_ms']=dict(count=len(frame_times),mean=statistics.mean(frame_times),p95=percentile(frame_times,95),p99=percentile(frame_times,99),max=max(frame_times),over_33_3_ms=sum(x>33.3 for x in frame_times))
        report=dict(mode=a.mode,renderer=a.renderer,recording=a.record,vsync=a.vsync,capture_fps=a.capture_fps,wall_seconds=dt,
                    hd_enabled=b['hd_enabled'],hd_active=b['hd_active'],
                    cached_frames=e['performance'].get('cache_hits',0)-b['performance'].get('cache_hits',0),
                    cache_equivalence=cache_equivalence,
                    cgroup_cpu_delta={k:v-cpu_before.get(k,0)for k,v in cpu_after.items()},
                    cpu_quota=Path('/sys/fs/cgroup/cpu.max').read_text().strip() if Path('/sys/fs/cgroup/cpu.max').is_file() else None,
                    frontend_updates_per_second=(e['frontend_updates']-b['frontend_updates'])/dt,
                    draws_per_second=(e['performance']['draws']-b['performance']['draws'])/dt,
                    original_frames_per_second=(e['core']['frames']-b['core']['frames'])/dt,
                    completed_presentations_per_second=(e['presentation']['serial']-b['presentation']['serial'])/dt,
                    instructions_per_second=(e['core']['steps']-b['core']['steps'])/dt,
                    health_before=b['core']['health'],health_after=e['core']['health'],
                    metrics=metrics,binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
                    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    command=command,environment={k:env[k]for k in ['DISPLAY','LP_NUM_THREADS','GOMAXPROCS']},
                    limits='Linux native app on specified GPU or software renderer; normal keyboard/mouse; virtual display/audio; no physical display refresh or controller acceptance')
        (a.output/'receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        (a.output/'events.json').write_text(json.dumps(events,ensure_ascii=False)+'\n')
        print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception as e:
        (a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),state=read()),ensure_ascii=False,indent=2)+'\n');raise
    finally:
        if video and video.poll()is None:video.send_signal(signal.SIGINT);video.wait(timeout=20)
        for proc in reversed(processes):
            if proc.poll()is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for f in logs:f.close()


if __name__=='__main__':main()
