"""正常選角與雙打實錄；只送鍵鼠，不修改生命、勝負、座標或亂數。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time
import wave


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--character',type=int,choices=(8,9,10),required=True)
    p.add_argument('--opponent',type=int,choices=range(8),required=True)
    p.add_argument('--fps',type=int,choices=[30,60],default=30)
    p.add_argument('--renderer',choices=['software','nvidia','egl'],default='software')
    p.add_argument('--portraits',action='store_true',default=True,help='select through in-game portraits; retained for existing recording commands')
    p.add_argument('--intro',action='store_true',help='額外錄製遊戲內 HD 標題與原音')
    p.add_argument('--software-threads',type=int,choices=range(1,9),default=2,help='本機軟體繪圖執行緒數，不改遊戲計時')
    p.add_argument('--encoder',choices=['libx264','h264_vaapi'],default='libx264',help='錄影編碼器；VAAPI 需要明示 renderD128 裝置')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    script_bytes=Path(__file__).read_bytes();script_sha=hashlib.sha256(script_bytes).hexdigest()
    (a.output/Path(__file__).name).write_bytes(script_bytes)
    for name in ('home','runtime','pulse'):(a.output/name).mkdir(mode=0o700)
    socket=a.output/'pulse/native'
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),
             PULSE_RUNTIME_PATH=str(a.output/'pulse'),PULSE_SERVER='unix:'+str(socket),
             LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS=str(a.software_threads),GOMAXPROCS='2')
    if a.renderer in ('nvidia','egl'):env.pop('LIBGL_ALWAYS_SOFTWARE',None)
    (a.output/'home/.asoundrc').write_text('pcm.!default { type pulse }\nctl.!default { type pulse }\n')
    observe=a.output/'observe.json';processes=[];logs=[];events=[];clips=[];draws={};game=None;started=time.monotonic()
    def spawn(cmd,name,stdout=None):
        log=(a.output/(name+'.log')).open('wb');logs.append(log)
        proc=subprocess.Popen(cmd,env=env,stdout=stdout if stdout is not None else log,stderr=log)
        processes.append(proc);return proc
    def state():
        try:return json.loads(observe.read_text())
        except(FileNotFoundError,json.JSONDecodeError):return None
    def record_state(label=None):
        s=state()
        if not s:return None
        assert not s['core'].get('error') and not s['audio'].get('error')
        assert not s['core']['training']['modified']
        for f in s.get('performance',{}).get('recent')or[]:draws[f['draw']]=f
        events.append(dict(performance=s.get('performance'),label=label,seconds=time.monotonic()-started,core=s['core'],audio=s['audio'],
                           hd_active=s['hd_active'],title_hd_active=s['title_hd_active'],selection_hd_active=s['selection_hd_active'],
                           selection_hd=s.get('selection_hd'),selection_waiting=s.get('selection_waiting',False),
                           scene=s['presentation']['scene'],actors=s['presentation'].get('actors')))
        return s
    def wait(predicate,seconds=150):
        end=min(started+870,time.monotonic()+seconds)
        while time.monotonic()<end:
            if game is not None and game.poll()is not None:raise RuntimeError(('game exit',game.returncode))
            s=record_state()
            if s and predicate(s):return s
            time.sleep(.04)
        raise TimeoutError(state())
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
        s=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
        wait(lambda n:not n['mouse_left']and n['frontend_updates']>s['frontend_updates'],10)
    def key(name):
        start=state()['frontend_updates'];xdo('keydown',name)
        down=wait(lambda s:s['frontend_updates']>=start+2,10);xdo('keyup',name)
        wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
    def hold(name,seconds):
        xdo('keydown',name);end=time.monotonic()+seconds
        while time.monotonic()<end:record_state();time.sleep(.05)
        xdo('keyup',name)
    def begin_clip(name):
        pcm=a.output/(name+'.pcm');raw=pcm.open('wb');logs.append(raw)
        recorder=spawn(['parec','--device=kdzz.monitor','--raw','--format=s16le','--rate=48000',
                        '--channels=2','--latency-msec=10'],name+'-audio',raw)
        video=a.output/(name+'.mp4');progress=a.output/(name+'-progress.txt')
        device=['-vaapi_device','/dev/dri/renderD128']if a.encoder=='h264_vaapi'else[]
        encode=['-vf','format=nv12,hwupload','-c:v','h264_vaapi','-qp','20','-bf','0']if device else['-c:v','libx264','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p']
        rec=spawn(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',*device,'-f','x11grab',
                   '-draw_mouse','1','-framerate',str(a.fps),'-video_size','1120x820','-i',':89.0',
                   '-an',*encode,'-threads','1','-progress',str(progress),'-stats_period','0.1',str(video)],name+'-video')
        end=time.monotonic()+15;us=0
        while time.monotonic()<end:
            if progress.exists():
                rows=progress.read_text().splitlines()
                values=[int(r.split('=',1)[1])for r in rows if r.startswith('out_time_us=')and r.split('=',1)[1].isdigit()]
                if values and values[-1]>0:us=values[-1];break
            if rec.poll()is not None:raise RuntimeError('video recorder exited')
            time.sleep(.03)
        assert us>0 and pcm.stat().st_size>0
        # Capture clocks are sampled together, independent of FFmpeg Pulse timestamp rebasing.
        offset=pcm.stat().st_size/192000-us/1_000_000
        mark=record_state(name+'-start');print(name,'recording',flush=True)
        return dict(name=name,video=video,pcm=pcm,raw=raw,rec=rec,recorder=recorder,
                    audio_offset_seconds=offset,started=time.monotonic(),start_state=mark)
    def end_clip(c):
        c['end_state']=record_state(c['name']+'-end')
        for proc in (c['rec'],c['recorder']):
            proc.send_signal(signal.SIGINT);proc.wait(timeout=20)
        c['raw'].close();pcm=c['pcm'];wav=pcm.with_suffix('.wav')
        with wave.open(str(wav),'wb')as w:
            w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(pcm.read_bytes())
        pcm.unlink()
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(c['video'])],text=True,timeout=15))
        seconds=float(info['format']['duration']);assert seconds>5
        with wave.open(str(wav))as w:audio_seconds=w.getnframes()/w.getframerate()
        assert abs(audio_seconds-c['audio_offset_seconds']-seconds)<.7
        row=dict(name=c['name'],video=c['video'].name,video_sha256=sha(c['video']),audio=wav.name,audio_sha256=sha(wav),
                 duration=seconds,audio_offset_seconds=c['audio_offset_seconds'],
                 start_state=c['start_state'],end_state=c['end_state'],audio_alignment='raw sample clock minus initial video progress; capture approximation within 0.7s')
        if c['start_state'].get('performance')and c['end_state'].get('performance'):
            b,e=c['start_state'],c['end_state']
            # End state is taken before stopping encoders; use its recorded wall time.
            dt=next(x['seconds']for x in reversed(events)if x['label']==c['name']+'-end')-next(x['seconds']for x in reversed(events)if x['label']==c['name']+'-start')
            row['performance']=dict(wall_seconds=dt,draws_per_second=(e['performance']['draws']-b['performance']['draws'])/dt,
                                    updates_per_second=(e['frontend_updates']-b['frontend_updates'])/dt,
                                    original_frames_per_second=max(0,e['core']['frames']-b['core']['frames'])/dt)
        clips.append(row);return row
    wrapper=['/opt/VirtualGL/bin/vglrun','-d','egl0','-c','proxy']if a.renderer in ('nvidia','egl')else[]
    command=wrapper+[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-quit-after','880s']
    if a.fps==60:command+=['-capture-fps','60','-capture',str(a.output/'selection.png')]
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb');time.sleep(.3)
        spawn(['pulseaudio','--daemonize=no','--exit-idle-time=-1','--use-pid-file=no','-n',
               '--load=module-native-protocol-unix socket='+str(socket)+' auth-anonymous=1',
               '--load=module-null-sink sink_name=kdzz rate=48000 channels=2','--log-level=warning'],'pulse')
        end=time.monotonic()+15
        while not socket.exists()and time.monotonic()<end:time.sleep(.05)
        subprocess.run(['pactl','set-default-sink','kdzz'],env=env,check=True,timeout=5)
        if a.renderer in ('nvidia','egl'):
            renderer=subprocess.check_output(wrapper+['glxinfo','-B'],env=env,text=True,timeout=15)
            assert'llvmpipe'not in renderer and'softpipe'not in renderer
            if a.renderer=='nvidia':assert'NVIDIA'in renderer
            (a.output/'renderer.txt').write_text(renderer)
        else:
            renderer='LIBGL_ALWAYS_SOFTWARE=1; software threads='+str(a.software_threads)
            if shutil.which('glxinfo'):
                renderer+='\n'+subprocess.check_output(['glxinfo','-B'],env=env,text=True,timeout=15)
            (a.output/'renderer.txt').write_text(renderer)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        window=None;end=time.monotonic()+30
        while time.monotonic()<end:
            try:
                result=xdo('search','--onlyvisible','--name','Remastered').splitlines()
                if result:window=result[-1];break
            except subprocess.CalledProcessError:pass
            time.sleep(.05)
        assert window is not None;xdo('windowfocus','--sync',window)
        xdo('windowmove',window,0,0)
        # Xvfb has no window manager; measure the real client location before X11 capture.
        geometry=xdo('getwindowgeometry','--shell',window)
        assert 'X=0\n'in geometry and 'Y=0\n'in geometry,geometry
        click(110,32);wait(lambda s:s['core'].get('title_hd'))
        if not state()['hd_enabled']:click(830,32)
        wait(lambda s:s['title_hd_active'])
        if a.intro:
            c=begin_clip('intro')
            while time.monotonic()-c['started']<8:
                assert record_state()['title_hd_active'];time.sleep(.05)
            end_clip(c)
            if a.fps==60:
                key('F12');wait(lambda s:(a.output/'selection.png').is_file(),15)
                shutil.copy2(a.output/'selection.png',a.output/'title-hd.png')
        key('Right');wait(lambda s:s['core'].get('title_hd',{}).get('selected')==1);key('Return')
        wait(lambda s:s['selection_hd_active']and s['core'].get('selection',{}).get('player')==0)
        c=begin_clip('selection');time.sleep(.7)
        click(80+(110+33*(a.character-8)+16)*3,64+(164+16)*3)
        wait(lambda s:s['core'].get('selection',{}).get('cursor')==a.character and s['core']['selection'].get('target',-1)<0 and s.get('selection_hd',{}).get('portraits',[-1,-1])[0]==a.character)
        record_state('boss-selected');time.sleep(1.4);key('Return')
        wait(lambda s:s['selection_hd_active']and s['core'].get('selection',{}).get('player')==1 and s.get('selection_hd',{}).get('player')==1)
        time.sleep(.3)
        click(80+(28+33*a.opponent+16)*3,64+(127+16)*3)
        wait(lambda s:s['core'].get('selection',{}).get('cursor')==a.opponent and s['core']['selection'].get('target',-1)<0 and s.get('selection_hd',{}).get('portraits',[-1,-1])[1]==a.opponent)
        record_state('second-player-selected')
        stop_at=max(c['started']+8,time.monotonic()+2.5)
        while time.monotonic()<stop_at:record_state();time.sleep(.05)
        end_clip(c)
        origin=next(e['seconds']for e in events if e['label']=='selection-start')
        boss_at=next(e['seconds']for e in events if e['label']=='boss-selected')-origin
        second_at=next(e['seconds']for e in events if e['label']=='second-player-selected')-origin
        clips[-1]['edit_windows']=[dict(start=max(0,boss_at-.2),seconds=2),dict(start=max(0,second_at-2),seconds=4)]
        assert all(w['start']+w['seconds']<=clips[-1]['duration']for w in clips[-1]['edit_windows'])
        if a.fps==60:
            previous=(a.output/'selection.png').stat().st_mtime_ns if (a.output/'selection.png').exists()else 0
            key('F12');wait(lambda s:(a.output/'selection.png').is_file()and(a.output/'selection.png').stat().st_mtime_ns>previous,15)
        key('Return')
        wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active'])
        assert state()['core']['fighters']==[a.character,a.opponent]
        initial=state()['core']
        xdo('keydown','d')
        # Character origins differ by sprite width; collision can stop at a gap of 58.
        # Use the already verified normal-match walk budget, then release and attack.
        wait(lambda s:s['core']['frames']>=initial['frames']+90 or s['core']['steps']>=initial['steps']+150_000_000,90)
        xdo('keyup','d')
        c=begin_clip('gameplay');before=state()['core']['frames']
        for name,seconds in [('Tab',1.5),('Shift_L',1.5),('Return',1.2),('w',1),('x',1),
                             ('Tab',1.5),('Shift_L',1.5),('Return',1.2),('a',.8),('d',.8),('Tab',1.5),('Shift_L',1.5)]:
            hold(name,seconds)
        while time.monotonic()-c['started']<16:record_state();time.sleep(.05)
        row=end_clip(c)
        assert row['end_state']['core']['frames']>before+15
        assert any(e['core']['health']!=[124,124]for e in events if e['seconds']>=next(x['seconds']for x in events if x['label']=='gameplay-start')), 'no attack damage observed'
        assert all(x['audio']['rejected']==0 for x in events)
        selected=[d for d in draws.values()if d.get('selection')and d.get('hd_enabled')]
        raw=[d for d in selected if not d['hd_active']]
        assert selected and not raw,raw
        (a.output/'draws.json').write_text(json.dumps(list(draws.values()),indent=2)+'\n')
        receipt=dict(version=state()['version'],character=a.character,opponent=a.opponent,binary_sha256=sha(a.binary),
                     command=command,clips=clips,events=events,script_sha256=script_sha,encoder=a.encoder,
                     character_manifest_sha256=sha(a.binary.parent/'assets/hd/characters/manifest.json'),
                     renderer=a.renderer,renderer_identity=renderer,software_threads=a.software_threads,capture_fps=a.fps,portrait_selection=a.portraits,hd_intro=a.intro,
                     selection_presentation=dict(draws=len(selected),original_frames=len(raw)),
                     rights='local-only game recordings and original audio; never Git or public Release',
                     limits='normal Linux native app under Xvfb with ordinary keyboard/mouse; no physical controller, full game, original speed or hardware audio parity claim')
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print('recorded boss',a.character,flush=True)
    except Exception as exc:
        (a.output/'failure.json').write_text(json.dumps(dict(error=repr(exc),clips=clips,events=events,state=state()),ensure_ascii=False,indent=2)+'\n');raise
    finally:
        for proc in reversed(processes):
            if proc.poll()is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for log in logs:log.close()


if __name__=='__main__':main()
