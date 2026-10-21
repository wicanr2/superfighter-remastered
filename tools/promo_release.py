"""以真實封包錄影、整合截圖及原版 MIDI 軟體演奏製作本機推廣片。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/project')
VERSION=(ROOT/'VERSION').read_text().strip()
OUT=ROOT/'dist-all'/VERSION/'promo'
PLAY=ROOT/'dist-all'/VERSION/'smoke/linux-play-record'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(words):subprocess.run(words,check=True,timeout=300)

def prepare():
    from PIL import Image,ImageDraw,ImageFont
    OUT.mkdir(exist_ok=True)
    font=ROOT/'internal/desktop/assets/NotoSansCJKtc-Regular.otf'
    bounds=[]
    def base():return Image.new('RGB',(1280,720),'#0b101b')
    def line(im,text,y,size=30,color='#e8edf7'):
        draw=ImageDraw.Draw(im);f=ImageFont.truetype(str(font),size)
        box=draw.textbbox((0,0),text,font=f);w=box[2]-box[0];h=box[3]-box[1]
        assert w<=1180 and y+h<=690,(text,w,y,h)
        x=(1280-w)//2;draw.text((x,y-box[1]),text,font=f,fill=color)
        bounds.append({'text':text,'box':[x,y,x+w,y+h]})
    im=base();line(im,'快打至尊',160,76,'#f2c75b');line(im,'Remastered',275,54)
    line(im,'原版核心・原生操作・街機手繪 HD',400,34)
    line(im,VERSION+'　目前整合功能展示',500,27);line(im,'本機影片，不公開散布',620,22)
    im.save(OUT/'00-title.png')
    def still(name,source,title,subtitle):
        im=base();s=Image.open(source).convert('RGB');s.thumbnail((1120,568))
        im.paste(s,((1280-s.width)//2,12+(568-s.height)//2))
        line(im,title,603,31,'#f2c75b');line(im,subtitle,657,23);im.save(OUT/name)
    still('01-battle.png',PLAY/'battle-hd.png','1993 年台灣 DOS 格鬥遊戲，再次交鋒','整合截圖：屋頂、角色與戰鬥介面 HD；完整動畫仍在製作')
    still('03-keyboard.png',ROOT/'workplace/keyboard-native-v1/keyboard-settings.png','鍵盤重綁，兩人各四格快捷','設定介面截圖：斬四招已驗；其他角色目前僅保存配置')
    still('04-spider.png',ROOT/'workplace/release-spider-hd-v1/hd-paused.png','三名魔王，單打與雙打皆可選','蜘蛛女 HD 整合截圖：已確認低伏稿；其餘動作保留原貌')
    still('05-training.png',PLAY/'training-hd.png','練習模式：雙方滿血、停時、電腦中立','練習模式整合截圖；這是可關閉的規則擴充')
    im=base();line(im,'Windows・macOS・Linux',155,47,'#f2c75b')
    line(im,'公開引擎包，玩家自備合法原版資料',280,34)
    line(im,'本機完整版與影片另外保存',355,30)
    line(im,'音樂：原版 MIDI，TiMidity++ 軟體演奏',470,25)
    line(im,'開發暫停，完整 HD 與遊戲音訊尚未完成',535,25)
    line(im,'github.com/wicanr2/superfighter-remastered',630,22)
    im.save(OUT/'06-end.png')
    overlay=Image.new('RGBA',(1280,720),(0,0,0,0));draw=ImageDraw.Draw(overlay)
    draw.rectangle((0,620,1280,720),fill=(11,16,27,255))
    line(overlay,'解壓後的 Linux 原生封包實錄',625,29,'#f2c75b')
    line(overlay,'鍵盤快捷與移動，原版核心執行',666,21)
    overlay.save(OUT/'02-overlay.png')
    sources=[PLAY/'native-gameplay.mp4',ROOT/'workplace/original-audio-v1/original-00.mid',ROOT/'workplace/original-audio-v1/original-00.wav',font,
             PLAY/'battle-hd.png',PLAY/'training-hd.png',ROOT/'workplace/keyboard-native-v1/keyboard-settings.png',ROOT/'workplace/release-spider-hd-v1/hd-paused.png',PLAY/'receipt.json']
    record={'version':VERSION,'visibility':'local-only, never upload to Git/GitHub Release',
            'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources},'text_bounds':bounds,
            'music':{'source':'original SF000.MUS record 0, exact MIDI bytes','renderer':'TiMidity++ 2.14.0',
                     'soundfont':'FluidR3_GM.sf2','soundfont_sha256':'74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0',
                     'limits':'原版 MIDI 軟體演奏；不是原機 DAC／OPL 錄音，不含已解碼語音，不代表遊戲音訊串流完成'},
            'segments':[{'start':0,'end':5,'kind':'title'},{'start':5,'end':13,'kind':'integration still'},
                        {'start':13,'end':31,'kind':'actual native gameplay'},{'start':31,'end':39,'kind':'settings still'},
                        {'start':39,'end':47,'kind':'integration still'},{'start':47,'end':55,'kind':'training still'},
                        {'start':55,'end':60,'kind':'end card'}]}
    (OUT/'source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')

def render():
    common=['-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p','-r','30']
    segments=[]
    for i,(image,seconds) in enumerate([('00-title.png',5),('01-battle.png',8),(None,18),('03-keyboard.png',8),('04-spider.png',8),('05-training.png',8),('06-end.png',5)]):
        dest=OUT/f'segment-{i:02d}.mp4';segments.append(dest)
        if image:
            inputs=['-loop','1','-framerate','30','-i',str(OUT/image),'-t',str(seconds)]
        else:
            inputs=['-i',str(PLAY/'native-gameplay.mp4'),'-loop','1','-i',str(OUT/'02-overlay.png'),'-filter_complex',
                    '[0:v]crop=960:600:80:64,pad=1280:720:160:8:color=0x0b101b[v];[v][1:v]overlay=0:0:shortest=1', '-t','18']
        run(['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,*common,str(dest)])
    listing=OUT/'segments.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in segments))
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(ROOT/'workplace/original-audio-v1/original-00.wav'),
         '-map','0:v','-map','1:a','-t','60','-c:v','copy','-af','volume=-4dB,afade=t=in:d=1,afade=t=out:st=57:d=3','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(OUT/(VERSION+'-local-promo.mp4'))])

def check():
    movie=OUT/(VERSION+'-local-promo.mp4')
    result=subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],text=True,timeout=20)
    metadata=json.loads(result);v=next(s for s in metadata['streams'] if s['codec_type']=='video');a=next(s for s in metadata['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['avg_frame_rate'])==(1280,720,'30/1')
    assert abs(float(metadata['format']['duration'])-60)<.1 and a['sample_rate']=='48000' and a['channels']==2
    command=['ffmpeg','-hide_banner','-i',str(movie),'-vf','blackdetect=d=0.3:pix_th=0.10','-af','volumedetect','-f','null','-']
    checked=subprocess.run(command,capture_output=True,text=True,timeout=120);assert checked.returncode==0
    import re
    assert 'black_start:' not in checked.stderr,checked.stderr
    peak=float(re.search(r'max_volume: ([-\d.]+) dB',checked.stderr)[1]);assert -40<peak<0
    motion=subprocess.run(['ffmpeg','-hide_banner','-ss','13','-t','18','-i',str(movie),'-vf','freezedetect=n=-50dB:d=2','-an','-f','null','-'],capture_output=True,text=True,timeout=90)
    assert motion.returncode==0
    source_motion=subprocess.run(['ffmpeg','-hide_banner','-i',str(PLAY/'native-gameplay.mp4'),'-vf','crop=960:600:80:64,freezedetect=n=-50dB:d=2','-an','-f','null','-'],capture_output=True,text=True,timeout=90)
    assert source_motion.returncode==0
    # 靜態圖與短暫等待不是遊戲流暢度證據。保留原檢測輸出供抽看。
    (OUT/'decode-audio-black.log').write_text(checked.stderr)
    (OUT/'gameplay-freeze.log').write_text(motion.stderr)
    (OUT/'native-source-freeze.log').write_text(source_motion.stderr)
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(movie),'-vf','fps=1/8,scale=320:180,tile=4x2','-frames:v','1',str(OUT/'contact-sheet.png')])
    report={'version':VERSION,'visibility':'local-only','file':movie.name,'sha256':sha(movie),'bytes':movie.stat().st_size,
            'duration':metadata['format']['duration'],'video':[1280,720,'30/1'],'audio':['AAC',48000,2],'peak_db':peak,
            'full_decode':True,'black_intervals':[],'freeze_intervals_in_gameplay':re.findall(r'freeze_(?:start|end|duration): [\d.]+',motion.stderr),
            'freeze_intervals_in_native_source':re.findall(r'freeze_(?:start|end|duration): [\d.]+',source_motion.stderr),
            'static_segments_intentional':True,'text_bounds_checked':True,'visual_contact_sheet_review':'pending',
            'limits':'技術非靜音檢查不等於人耳抽聽；18 秒操作不代表完整對戰或正式速度驗收',
            'source_sha256':sha(OUT/'source.json'),'script_sha256':sha(Path(__file__))}
    (OUT/'promo-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','render','check']);a=p.parse_args()
    {'prepare':prepare,'render':render,'check':check}[a.stage]()
