"""固定 Docker 工具鏈：唯讀原版 MIDI／四位元 PCM，轉成本機專用 OGG。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import wave

ROOT=Path('/project')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def midi_seconds(data):
    assert data[:4]==b'MThd' and struct.unpack_from('>IHHH',data,4)==(6,0,1,240)
    assert data[14:18]==b'MTrk'
    length=struct.unpack_from('>I',data,18)[0]
    assert len(data)==22+length
    at=22;tempo=500000;seconds=0.;running=None
    def vlq():
        nonlocal at
        value=0
        for _ in range(4):
            assert at<len(data)
            byte=data[at];at+=1;value=(value<<7)|(byte&127)
            if byte<128:return value
        raise ValueError('invalid MIDI variable-length quantity')
    while at<len(data):
        delta=vlq();seconds+=delta*tempo/240000000
        status=data[at]
        if status>=128:at+=1
        else:
            assert running is not None
            status=running
        if status==255:
            kind=data[at];at+=1;n=vlq();payload=data[at:at+n];at+=n
            assert len(payload)==n
            if kind==81:
                assert n==3;tempo=int.from_bytes(payload,'big')
            if kind==47:
                assert n==0 and at==len(data) and seconds>0
                return seconds
        elif status in (240,247):
            n=vlq();at+=n;running=None
        else:
            assert 128<=status<=239
            running=status;at+=1 if status&240 in (192,208)else 2
        assert at<=len(data)
    raise ValueError('MIDI end-of-track missing')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir() and a.output.parent.stat().st_uid==1000
    registry_path=ROOT/'internal/originalaudio/sources.json'
    registry=json.loads(registry_path.read_text())
    sources={}
    for row in registry['sources']:
        data=(a.original_root/row['file']).read_bytes()
        assert sha(data)==row['sha256']
        sources[row['file']]=data
    font=Path('/usr/share/sounds/sf2/FluidR3_GM.sf2')
    assert sha(font.read_bytes())=='74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0'
    a.output.mkdir()
    result=[]
    for row in registry['clips']:
        raw=sources[row['file']][row['offset']:row['offset']+row['bytes']]
        assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
        destination=a.output/(row['id']+'.ogg')
        commands=[]
        with tempfile.TemporaryDirectory(prefix='audio-convert-',dir=a.output)as temporary:
            temp=Path(temporary);wav=temp/'source.wav'
            if row['kind']=='music':
                duration=midi_seconds(raw)
                mid=temp/'source.mid';mid.write_bytes(raw)
                command=['timidity','-Ow','-s','48000','-A','30','-o',str(wav),str(mid)]
                commands.append(command)
                run=subprocess.run(command,capture_output=True,text=True,timeout=120)
                assert run.returncode==0,run.stderr
                filters=f'volume=0.75,afade=t=in:d=0.005,afade=t=out:st={max(0,duration-.005):.9f}:d=0.005'
            else:
                assert raw[:17]==b'Compact PCM File\x1a' and len(raw)>=33
                count=struct.unpack_from('<H',raw,27)[0]
                assert len(raw)==32+count and count>0
                pcm=bytes(v<<4 for byte in raw[32:]for v in (byte>>4,byte&15))
                duration=len(pcm)/8000
                with wave.open(str(wav),'wb')as out:
                    out.setparams((1,1,8000,len(pcm),'NONE','not compressed'));out.writeframes(pcm)
                filters='volume=0.75'
            command=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-i',str(wav),'-t',f'{duration:.9f}',
                     '-af',filters,'-ar','48000','-ac','2','-c:a','libvorbis','-q:a','5',str(destination)]
            commands.append(command);subprocess.run(command,check=True,timeout=120)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(destination)],text=True,timeout=20))['streams'][0]
        assert info['codec_name']=='vorbis' and int(info['sample_rate'])==48000 and info['channels']==2
        decoded=subprocess.check_output(['ffmpeg','-v','error','-nostdin','-i',str(destination),'-f','s16le','-ar','48000','-ac','2','-'],timeout=60)
        values=struct.unpack('<'+'h'*(len(decoded)//2),decoded)
        peak=max(abs(v)for v in values)
        assert peak>16 and sum(v!=0 for v in values)>100
        clipping=sum(abs(v)>=32760 for v in values)/len(values)
        assert clipping<.001,(row['id'],clipping)
        assert abs(len(values)/96000-duration)<.04,(row['id'],duration,len(values)/96000)
        result.append(dict(id=row['id'],kind=row['kind'],source_sha256=row['sha256'],file=destination.name,
                           sha256=sha(destination.read_bytes()),duration_seconds=duration,frames=int(round(duration*48000)),
                           decoded_frames=len(values)//2,peak=peak,clipping_ratio=clipping,loop=row['kind']=='music',
                           conversion_commands=commands))
        print(row['id'],round(duration,3),'seconds peak',peak,flush=True)
    manifest=dict(version=1,kind='original-audio-ogg',sample_rate=48000,channels=2,registry_sha256=sha(registry_path.read_bytes()),clips=result,
                  rights='original audio derivatives; local only, not Git or public engine Release',
                  renderer=dict(midi='TiMidity++ 2.14.0 -A30, original MIDI unchanged; 0.75 encoder headroom',soundfont='FluidR3_GM.sf2',soundfont_sha256=sha(font.read_bytes()),
                                encoder='FFmpeg 5.1.9 libvorbis q5, 48kHz stereo',PCM='unsigned 4-bit linear nibbles high then low, nominal original request 8000Hz'),
                  limits='software MIDI timbre, 5ms music seam taper, nominal PCM duration approximation; no new HD score, voice remaster, hardware waveform or listening acceptance')
    (a.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(clips=len(result),output=str(a.output))))


if __name__=='__main__':main()
