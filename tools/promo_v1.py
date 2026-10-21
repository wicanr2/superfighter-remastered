"""v1 本機實錄推廣片：三魔王選角／遊玩、原音、逐段動態與權利檢查。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path('/project');VERSION=(ROOT/'VERSION').read_text().strip()
OUT=ROOT/'dist-all'/VERSION/'promo'
BANK=ROOT/'workplace/hd-batch-integration-v1/original-audio-ogg-v2'
NAMES={8:'蜘蛛女',9:'小丑',10:'印第安喬'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(cmd,timeout=180):return subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=timeout)
def probe(path):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]).stdout)


def prepare():
    from PIL import Image,ImageDraw,ImageFont
    assert VERSION=='v.1.0.0-20261021'
    font=ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf';bounds=[]
    def text(im,words,y,size=30,fill='#e8edff'):
        d=ImageDraw.Draw(im);f=ImageFont.truetype(str(font),size);b=d.textbbox((0,0),words,font=f)
        w,h=b[2]-b[0],b[3]-b[1];x=(1280-w)//2
        assert x>=40 and y>=0 and y+h<=700,(words,w,h)
        d.text((x,y-b[1]),words,font=f,fill=fill);bounds.append(dict(text=words,box=[x,y,x+w,y+h]))
    def card():
        im=Image.new('RGB',(1280,720),'#071427');d=ImageDraw.Draw(im)
        for y in range(720):d.line((0,y,1280,y),fill=(7,20+int(y/30),39+int(y/14)))
        d.rectangle((64,65,1216,80),fill='#f8d04e');d.rectangle((64,640,1216,646),fill='#42dcff')
        return im
    im=card();text(im,'快打至尊',155,82,'#f8d04e');text(im,'Remastered',270,54)
    text(im,'正式版 v1.0.0',380,36,'#42dcff');text(im,'三名魔王，直接上場',465,35)
    text(im,VERSION,565,24);im.save(OUT/'title.png')
    im=card();text(im,'Windows・macOS・Linux',160,46,'#f8d04e')
    text(im,'雙人對戰・手把與鍵盤可設定',280,34);text(im,'原版核心 × 街機手繪 HD',365,36,'#42dcff')
    text(im,'玩家自備原版資料；完整版與影片只留本機',465,25)
    text(im,VERSION,560,25);im.save(OUT/'end.png')
    plan=[dict(name='title',kind='card',seconds=4,audio='music-01.ogg')]
    sources={str(font.relative_to(ROOT)):sha(font)}
    for character,label in NAMES.items():
        folder=OUT/f'boss-{character}';r=json.loads((folder/'receipt.json').read_text())
        assert r['version']==VERSION and r['character']==character
        assert any(e['label']=='boss-selected'and e['core']['selection']['cursor']==character for e in r['events'])
        assert r['clips'][1]['end_state']['core']['fighters'][0]==character
        assert r['clips'][1]['end_state']['core']['health']!=[124,124]
        sources[str((folder/'receipt.json').relative_to(ROOT))]=sha(folder/'receipt.json')
        for clip in r['clips']:
            seconds=8 if clip['name']=='selection'else 14
            assert clip['duration']>=seconds
            for kind in ('video','audio'):
                f=folder/clip[kind];assert sha(f)==clip[kind+'_sha256'];sources[str(f.relative_to(ROOT))]=sha(f)
            title=f'直接選擇魔王：{label}'if clip['name']=='selection'else f'{label}，實際對戰'
            subtitle='下方姓名按鈕選角，確認即可上場'if clip['name']=='selection'else'Linux 原生程式實錄・原版核心執行'
            overlay=Image.new('RGBA',(1280,720),(0,0,0,0));d=ImageDraw.Draw(overlay)
            d.rectangle((0,624,1280,720),fill=(7,20,39,255));d.line((65,624,1215,624),fill='#f8d04e',width=2)
            text(overlay,title,638,29,'#f8d04e');text(overlay,subtitle,674,21)
            name=f'{character}-{clip["name"]}';overlay.save(OUT/(name+'-overlay.png'))
            plan.append(dict(name=name,kind='native selection'if clip['name']=='selection'else'native gameplay',
                             seconds=seconds,folder=folder.name,clip=clip,character=character))
    plan.append(dict(name='end',kind='card',seconds=5,audio='music-08.ogg'))
    audio_manifest=json.loads((BANK/'manifest.json').read_text())
    for name in ('music-01.ogg','music-08.ogg'):
        row=next(r for r in audio_manifest['clips']if r['file']==name);assert sha(BANK/name)==row['sha256']
        sources[str((BANK/name).relative_to(ROOT))]=sha(BANK/name)
    source=dict(version=VERSION,visibility='local-only; no movie, raw footage or audio in Git/GitHub Release',
                segments=plan,sources=sources,font_sha256=sha(font),text_bounds=bounds,duration=sum(p['seconds']for p in plan),
                music='actual original MIDI/PCM from the native app; card music uses the same verified OGG bank; TiMidity/FluidR3 software timbre, not original OPL hardware',
                capture='normal keyboard/mouse via native Linux game in Xvfb; no teleport, state injection, forced wins, training or time acceleration',
                differences_from_previous_promo=['66 seconds native recording instead of 18 seconds','all three bosses selected and played on camera','HUD gold/cyan motif and live montage instead of repeated integration stills'],
                limits='physical gamepad, native Windows/macOS, full animations/endings and human listening remain unverified')
    (OUT/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
    print('prepared',source['duration'],'seconds; 66 seconds live selection/gameplay')


def render():
    source=json.loads((OUT/'source.json').read_text());commands=[];files=[]
    common=['-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',
            '-r','30','-c:a','aac','-b:a','192k','-ar','48000','-ac','2']
    for i,s in enumerate(source['segments']):
        dest=OUT/f'segment-{i:02d}.mp4';seconds=s['seconds']
        if s['kind']=='card':
            cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','30','-i',str(OUT/(s['name']+'.png')),
                 '-stream_loop','-1','-i',str(BANK/s['audio']),'-t',str(seconds),'-af',
                 f'volume=0.3,afade=t=in:d=0.15,afade=t=out:st={seconds-.6}:d=0.6',*common,str(dest)]
        else:
            folder=OUT/s['folder'];clip=s['clip'];offset=clip['audio_offset_seconds']
            audio=f'atrim=start={max(0,offset)}:duration={seconds},asetpts=PTS-STARTPTS'
            if offset<0:audio+=f',adelay={int(-offset*1000)}:all=1'
            audio+=f',apad=whole_dur={seconds},atrim=duration={seconds},volume=0.85,afade=t=in:d=0.02,afade=t=out:st={seconds-.02}:d=0.02'
            video=('scale=824:604,pad=1280:720:228:8:color=0x071427'if s['kind']=='native selection'else
                   'crop=960:576:80:76,scale=1024:614,pad=1280:720:128:8:color=0x071427')
            cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(folder/clip['video']),'-i',str(folder/clip['audio']),
                 '-loop','1','-i',str(OUT/(s['name']+'-overlay.png')),'-filter_complex_threads','1','-filter_complex',
                 f'[0:v]{video}[v];[v][2:v]overlay=0:0[vout];[1:a]{audio}[aout]',
                 '-map','[vout]','-map','[aout]','-t',str(seconds),*common,str(dest)]
        run(cmd);commands.append(cmd);files.append(dest)
    commands.append(assemble())
    (OUT/'render-commands.json').write_text(json.dumps(commands,indent=2)+'\n')


def assemble():
    source=json.loads((OUT/'source.json').read_text())
    files=[OUT/f'segment-{i:02d}.mp4'for i in range(len(source['segments']))]
    listing=OUT/'segments.txt';listing.write_text(''.join("file '"+str(f)+"'\n"for f in files))
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),
         '-vf','fps=30','-af','aresample=async=1:first_pts=0','-t',str(source['duration']),
         '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(OUT/(VERSION+'-local-promo.mp4'))]
    run(cmd);(OUT/'assembly-command.json').write_text(json.dumps(cmd,indent=2)+'\n');return cmd


def check():
    source=json.loads((OUT/'source.json').read_text());movie=OUT/(VERSION+'-local-promo.mp4');info=probe(movie)
    video=next(s for s in info['streams']if s['codec_type']=='video');audio=next(s for s in info['streams']if s['codec_type']=='audio')
    assert(video['width'],video['height'],video['avg_frame_rate'])==(1280,720,'30/1')
    assert abs(float(info['format']['duration'])-75)<.12 and audio['sample_rate']=='48000'and audio['channels']==2
    scan=run(['ffmpeg','-hide_banner','-i',str(movie),'-vf','blackdetect=d=0.3:pix_th=0.10',
              '-af','volumedetect,astats=metadata=0:reset=0','-f','null','-'],180)
    (OUT/'decode-audio-black.log').write_text(scan.stderr);assert'black_start:'not in scan.stderr
    peak=float(re.search(r'max_volume: ([-\d.]+) dB',scan.stderr)[1]);assert -35<peak<-.1
    checks=[];cursor=0
    for i,s in enumerate(source['segments']):
        f=OUT/f'segment-{i:02d}.mp4';segment=probe(f)
        assert abs(float(segment['format']['duration'])-s['seconds'])<.1
        row=dict(name=s['name'],start=cursor,end=cursor+s['seconds'],kind=s['kind'])
        if s['kind']=='native gameplay':
            r=run(['ffmpeg','-hide_banner','-i',str(f),'-vf','crop=1024:614:128:8,freezedetect=n=-50dB:d=2',
                   '-an','-f','null','-'],90)
            (OUT/(s['name']+'-freeze.log')).write_text(r.stderr)
            row['freeze_events']=re.findall(r'freeze_(?:start|duration|end): [\d.]+',r.stderr)
            assert not row['freeze_events'],(s['name'],row['freeze_events'])
        if s['kind']!='card':
            r=run(['ffmpeg','-hide_banner','-i',str(f),'-vn','-af','volumedetect','-f','null','-'],90)
            row['peak_db']=float(re.search(r'max_volume: ([-\d.]+) dB',r.stderr)[1]);assert -35<row['peak_db']<-.1
        checks.append(row);cursor+=s['seconds']
    # Also expose each selection/gameplay segment independently for visual review.
    for i,s in enumerate(source['segments']):
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(checks[i]['start']+min(3,s['seconds']/2)),
             '-i',str(movie),'-frames:v','1',str(OUT/(s['name']+'-review.png'))])
    inputs=[]
    for s in source['segments']:inputs+=['-i',str(OUT/(s['name']+'-review.png'))]
    filters=';'.join(f'[{i}:v]scale=320:180[s{i}]'for i in range(8))
    filters+=';'+''.join(f'[s{i}]'for i in range(8))+'xstack=inputs=8:layout=0_0|320_0|640_0|960_0|0_180|320_180|640_180|960_180[out]'
    run(['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex_threads','1',
         '-filter_complex',filters,'-map','[out]','-frames:v','1',str(OUT/'contact-sheet.png')])
    report=dict(version=VERSION,file=movie.name,visibility='local-only',sha256=sha(movie),bytes=movie.stat().st_size,
                duration=info['format']['duration'],video=[1280,720,'30/1'],audio=['AAC',48000,2],full_decode=True,
                peak_db=peak,black_intervals=[],segments=checks,native_footage_seconds=66,
                three_bosses_selected_and_played=[8,9,10],text_bounds_checked=True,visual_contact_sheet_review='pending',
                source_sha256=sha(OUT/'source.json'),script_sha256=sha(Path(__file__)),
                limits='capture A/V alignment approximation; software original MIDI timbre; no human listening or physical hardware claim')
    (OUT/'ffprobe.json').write_text(json.dumps(info,indent=2)+'\n')
    (OUT/'promo-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('prepare','render','assemble','check'));a=p.parse_args()
    globals()[a.stage]()
