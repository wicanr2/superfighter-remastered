"""核對九景原生成 PNG 並收錄候選；不改圖或啟用未確認的多場景格式。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

ROOT=Path('/project')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--requests',type=Path,required=True)
    p.add_argument('--generated-root',type=Path,required=True)
    a=p.parse_args();request=json.loads(a.requests.read_text())
    dest=ROOT/'assets/hd/candidates';assert dest.is_dir() and dest.stat().st_uid==1000
    expected={'I1.XGB','I3.XGB','I4.XGB','I7.XGB','I8.XGB','I9.XGB','I10.XGB','I12.XGB','I13.XGB'}
    assert len(request['records'])==9 and {x['source'] for x in request['records']}==expected
    originals={x['name']:x['sha256'] for x in json.loads((ROOT/'workplace/source-manifest.json').read_text())['files']}
    records=[]
    # 全批先驗證；成功後才寫候選目錄。
    for item in request['records']:
        source=ROOT/'workplace/orig'/item['source'];assert sha(source)==originals[item['source']]
        image=a.generated_root/Path(item['generatedPath']).name;assert image.is_file() and not image.is_symlink()
        file=item['file'];assert Path(file).name==file and not (dest/file).exists()
        with Image.open(image) as verified:verified.verify()
        with Image.open(image) as im:
            assert im.width>=1600 and im.height>=650 and abs(im.width/im.height-480/204)<.01
            assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
            size=list(im.size)
        reference=ROOT/'workplace/hd-source-probe-v3'/(item['source']+'.png')
        records.append({'file':file,'sha256':sha(image),'bytes':image.stat().st_size,'size':size,'tool':'built-in image_gen',
                        'source_file':item['source'],'source_sha256':sha(source),'reference_png_sha256':sha(reference),
                        'prompt':item['prompt'],'transparent_background':False,'status':'candidate; not native integration',
                        'limits':'normal scene mapping, scroll alignment and production loading not yet verified; scene 029 format decision pending'})
    for item,record in zip(request['records'],records):
        src=a.generated_root/Path(item['generatedPath']).name;shutil.copyfile(src,dest/record['file'])
        assert sha(dest/record['file'])==record['sha256'] and (dest/record['file']).stat().st_uid==1000
    record={'kind':'nine first-pass HD background candidates; original references remain local','tool_sha256':sha(Path(__file__)),
            'requests_sha256':sha(a.requests),'authorization':'user requested first HD pass and generated HD assets in existing repository; visibility unchanged',
            'records':records,'review':'geometry and decoration remain candidate approximations; not original pixel parity or automatic scene selection',
            'prompt_correction':'I3 prompt called the central animal a lion; the reference and generated candidate depict elephants. Prompt kept verbatim, its wording is not evidence.'}
    (dest/'backgrounds-source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'backgrounds':len(records),'bytes':sum(x['bytes'] for x in records),'source':'assets/hd/candidates/backgrounds-source.json'}))

if __name__=='__main__':main()
