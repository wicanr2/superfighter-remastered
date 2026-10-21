"""049／050 最後抽樣：蜘蛛女 B、原音切歌／語音、暫停／靜音及虛擬裝置實錄。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import wave


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    script=Path(__file__).read_bytes();(a.output/Path(__file__).name).write_bytes(script)
    for name in ('home','runtime','pulse'):(a.output/name).mkdir(mode=0o700)
    socket=a.output/'pulse/native'
    env=dict(os.environ,DISPLAY=':89',HOME=str(a.output/'home'),XDG_RUNTIME_DIR=str(a.output/'runtime'),
             PULSE_RUNTIME_PATH=str(a.output/'pulse'),PULSE_SERVER='unix:'+str(socket),
             LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',GOMAXPROCS='2')
    (a.output/'home/.asoundrc').write_text('pcm.!default { type pulse }\nctl.!default { type pulse }\n')
    observe=a.output/'observe.json';capture=a.output/'capture.png'
    command=[str(a.binary),'-data','/orig','-user-data',str(a.output/'user-data'),'-observe',str(observe),'-capture',str(capture),'-quit-after','900s']
    processes=[];logs=[];events=[];marks=[];game=None;recording=None;started=time.monotonic();capture_started=None
    def spawn(cmd,name):
        log=(a.output/(name+'.log')).open('wb');logs.append(log)
        proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=log);processes.append(proc);return proc
    def state():
        try:return json.loads(observe.read_text())
        except(FileNotFoundError,json.JSONDecodeError):return None
    def wait(predicate,seconds=120):
        deadline=min(started+890,time.monotonic()+seconds);last=None
        while time.monotonic()<deadline:
            if game is not None and game.poll()is not None:raise RuntimeError(('game exited',game.returncode))
            last=state()
            if last:
                assert not last['core'].get('error') and not last['audio'].get('error'),last
                assert not last['core']['training']['modified']
                if predicate(last):return last
            time.sleep(.01)
        raise TimeoutError(last)
    def xdo(*words):return subprocess.check_output(['xdotool',*map(str,words)],env=env,text=True,timeout=5).strip()
    def click(x,y):
        xdo('mousemove','--window',window,x,y);xdo('mousedown',1)
        down=wait(lambda s:s['mouse_left'],10);xdo('mouseup',1)
        wait(lambda s:not s['mouse_left']and s['frontend_updates']>down['frontend_updates'],10)
    def key(name):
        before=state()['frontend_updates'];xdo('keydown',name)
        down=wait(lambda s:s['frontend_updates']>=before+2,10);xdo('keyup',name)
        wait(lambda s:s['frontend_updates']>=down['frontend_updates']+2,10)
    def pause():
        key('Escape');return wait(lambda s:s['core']['paused']and s['audio']['paused'])
    def resume():click(110,32);return wait(lambda s:not s['core']['paused']and not s['audio']['paused'])
    def mark(name):
        marks.append(dict(name=name,seconds=time.monotonic()-capture_started,
                          recorded_frames=(a.output/'device-output.pcm').stat().st_size//4,
                          audio=state()['audio'],steps=state()['core']['steps']))
    def shot(name):
        capture.unlink(missing_ok=True)
        for f in capture.parent.glob('capture.png.*'):f.unlink()
        key('F12');deadline=time.monotonic()+20
        while not Path(str(capture)+'.capture.json').exists()and time.monotonic()<deadline:time.sleep(.01)
        assert Path(str(capture)+'.capture.json').exists()
        shutil.copyfile(capture,a.output/(name+'.png'))
        for f in capture.parent.glob('capture.png.*'):shutil.copyfile(f,a.output/(name+'.png'+f.name[len('capture.png'):]))
        snapshot=state();events.append(dict(name=name,state=snapshot))
        print(name,snapshot['core']['steps'],snapshot['audio'],flush=True)
    try:
        spawn(['Xvfb',':89','-screen','0','1280x1024x24','-nolisten','tcp'],'xvfb')
        spawn(['pulseaudio','--daemonize=no','--exit-idle-time=-1','--use-pid-file=no','-n',
               '--load=module-native-protocol-unix socket='+str(socket)+' auth-anonymous=1',
               '--load=module-null-sink sink_name=kdzz rate=48000 channels=2','--log-level=warning'],'pulse')
        deadline=time.monotonic()+15
        while not socket.exists()and time.monotonic()<deadline:time.sleep(.05)
        assert socket.exists()
        subprocess.run(['pactl','set-default-sink','kdzz'],env=env,check=True,timeout=5)
        sources=subprocess.check_output(['pactl','list','short','sources'],env=env,text=True,timeout=5)
        assert 'kdzz.monitor'in sources
        capture_started=time.monotonic()
        raw=(a.output/'device-output.pcm').open('wb');logs.append(raw)
        capture_log=(a.output/'capture-audio.log').open('wb');logs.append(capture_log)
        recording=subprocess.Popen(['parec','--device=kdzz.monitor','--raw','--format=s16le','--rate=48000',
                                    '--channels=2','--latency-msec=10'],env=env,stdout=raw,stderr=capture_log)
        processes.append(recording)
        game=spawn(command,'native');wait(lambda s:s['core']['paused'])
        deadline=time.monotonic()+30;window=None
        while time.monotonic()<deadline:
            try:
                windows=xdo('search','--onlyvisible','--name','Remastered').splitlines()
                if windows:window=windows[-1];break
            except subprocess.CalledProcessError:pass
            time.sleep(.05)
        assert window is not None;xdo('windowfocus','--sync',window)
        resume()
        wait(lambda s:s['core'].get('title_hd')and s['audio']['device_ready']and s['audio']['music_id']=='music-01'and s['audio']['music_position_ms']>2000)
        mark('title-audible');time.sleep(1)
        frozen=pause();mark('pause-start');position=state()['audio']['music_position_ms'];time.sleep(2)
        assert abs(state()['audio']['music_position_ms']-position)<50
        assert state()['core']['steps']==frozen['core']['steps'];mark('pause-end')
        click(830,32);wait(lambda s:s['title_hd_active']);shot('title-hd')
        click(830,32);wait(lambda s:not s['hd_enabled']);shot('title-original')
        click(830,32);wait(lambda s:s['title_hd_active']);shot('title-restored')
        resume();before=state()['audio']['music_position_ms'];wait(lambda s:s['audio']['music_position_ms']>before+700)
        click(1024,796);wait(lambda s:not s['audio']['enabled']);mark('mute-start')
        before=state()['audio']['music_position_ms'];time.sleep(2)
        assert state()['audio']['music_position_ms']>before+1000;mark('mute-end')
        click(1024,796);wait(lambda s:s['audio']['enabled']);mark('unmute');time.sleep(1)
        key('Right');wait(lambda s:s['core'].get('title_hd',{}).get('selected')==1);key('Return')
        wait(lambda s:s['selection_hd_active']and s['audio']['music_id']=='music-02');mark('selection-audible')
        for player,character in enumerate((8,4)):
            wait(lambda s:s['core'].get('selection',{}).get('player')==player)
            click(24+(character%6)*180+86,700+(character//6)*40+18)
            wait(lambda s:s['core'].get('selection',{}).get('cursor')==character and s['core']['selection'].get('target',-1)<0)
            pause();shot('selection-player-'+str(player));resume();click(1010,758)
        wait(lambda s:s['core']['battle']and s['core']['frames']>8 and s['hd_active']and s['audio']['music_events']>=3)
        assert state()['audio']['music_id']not in ('music-01','music-02')
        mark('battle-audible');time.sleep(1)
        pause();shot('battle-hd');click(830,32);wait(lambda s:not s['hd_enabled']);shot('battle-original')
        click(830,32);wait(lambda s:s['hd_active']);shot('battle-restored');resume()
        before_voice=state()['audio']['voice_events']
        for label,name,count in [('walk','d',30),('crouch','x',10),('jump','w',10),('punch','Tab',15),('kick','Shift_L',15)]:
            initial=state()['core']['frames'];xdo('keydown',name);wait(lambda s:s['core']['frames']>=initial+count)
            xdo('keyup',name);pause();shot(label)
            assert state()['hd_active']and state()['hd_characters_active'],(label,state()['hd_reason'])
            resume()
        assert state()['audio']['voice_events']>before_voice and state()['audio']['rejected']==0
        mark('after-attacks')
        music_id=state()['audio']['music_id']
        bank=json.loads((a.binary.parent/'assets/audio/original/manifest.json').read_text())
        duration=next(x['duration_seconds']for x in bank['clips']if x['id']==music_id)
        wait(lambda s:s['audio']['music_id']==music_id and s['audio']['music_position_ms']>(duration+.7)*1000,90)
        mark('music-loop-audible');time.sleep(1);pause();shot('after-release')
        recording.send_signal(signal.SIGINT);recording.wait(timeout=15)
        raw.close()
        pcm=a.output/'device-output.pcm'
        with wave.open(str(a.output/'device-output.wav'),'wb')as destination:
            destination.setparams((2,2,48000,0,'NONE','not compressed'))
            destination.writeframes(pcm.read_bytes())
        pcm.unlink()
        assert (a.output/'device-output.wav').stat().st_size>48000*4*5
        receipt=dict(kind='049/050 formal Linux original-audio and Spider sample',command=command,events=events,audio_marks=marks,
                     sample_rate=48000,channels=2,device='Oto ALSA pulse plugin -> private PulseAudio null sink -> monitor capture',
                     audio_file='device-output.wav',audio_sha256=sha(a.output/'device-output.wav'),
                     audio_clock='parec raw frame count at each event; 10ms requested capture latency; no FFmpeg timestamp rebasing',script_sha256=sha(Path(__file__)),
                     binary_sha256=sha(a.binary),character_manifest_sha256=sha(a.binary.parent/'assets/hd/characters/manifest.json'),
                     input='normal X11 keyboard/mouse only, no health, winner, position or RNG writes',elapsed_seconds=time.monotonic()-started,
                     limits='normal sampled actions, software MIDI timbre and nominal PCM; virtual audio device output, not physical speakers, human listening or full animation')
        (a.output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    except Exception as exc:
        (a.output/'failure.json').write_text(json.dumps(dict(error=repr(exc),state=state(),events=events,marks=marks,script_sha256=sha(Path(__file__))),ensure_ascii=False,indent=2)+'\n');raise
    finally:
        if recording is not None and recording.poll()is None:
            recording.send_signal(signal.SIGINT)
            try:recording.wait(timeout=10)
            except subprocess.TimeoutExpired:recording.kill();recording.wait(timeout=5)
        for proc in reversed(processes):
            if proc.poll()is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
        for log in logs:log.close()


if __name__=='__main__':main()
