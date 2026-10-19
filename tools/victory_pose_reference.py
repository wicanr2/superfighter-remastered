"""解碼原 WIN 圖像的 72 個指標、別名與獨立姿勢參考，不改原始 bytes。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image,ImageDraw


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root",type=Path,default=Path("/orig"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    assert not args.output.exists()
    args.output.mkdir()
    records=[]
    for character,name,file,want in [(0,"jaan","AAWIN.FIG","0c332b13bb923116460a7fa8cf474b105d8f1d2b180a8d7ede5af6f92209f8f7"),(4,"frank","FFWIN.FIG","2a353085e1ad73d5521bf1c87e45f5678c2d2cd59148f50e291aad6995b3c9c3")]:
        data=(args.original_root/file).read_bytes()
        assert sha(data)==want
        normal=(args.original_root/f"SFMAN{character+1:02d}.DAT").read_bytes()
        palette=[tuple((v<<2)|(v>>4) for v in normal[0xac8+i*3:0xac8+i*3+3]) for i in range(16)]
        groups={}
        for slot in range(72):
            segment,offset=struct.unpack_from("<HH",data,0x60+slot*4)
            at=0x180+segment*16+offset
            assert 0x180<=at and at+2<=len(data)
            width,height=data[at:at+2]
            end=at+2+(width+1)//2*height
            assert width and height and end<=len(data)
            digest=sha(data[at:end])
            if digest not in groups:
                groups[digest]={"ordinal":len(groups),"slot":slot,"aliases":[],"source_offset":at,"source_rect":[0,0,width,height],"source_sha256":digest}
            groups[digest]["aliases"].append(slot)
        assert len(groups)==(4 if character==0 else 3)
        cells=list(groups.values())
        sheet=Image.new("RGB",(1200,1200),(17,29,44));paint=ImageDraw.Draw(sheet)
        for cell in cells:
            index,at=cell["ordinal"],cell["source_offset"]
            width,height=cell["source_rect"][2:]
            stride=(width+1)//2
            sprite=Image.new("RGBA",(width,height))
            for y in range(height):
                for x in range(width):
                    value=data[at+2+y*stride+x//2]
                    value=(value>>4) if x%2==0 else (value&15)
                    if value:sprite.putpixel((x,y),(*palette[value],255))
            sprite.save(args.output/f"{name}-win-{cell['slot']:02d}.png")
            left,top=(index%2)*600,(index//2)*600
            enlarged=sprite.resize((width*5,height*5),Image.Resampling.NEAREST)
            sheet.paste(enlarged,(left+(600-width*5)//2,top+560-height*5),enlarged)
            paint.text((left+24,top+24),f"{name.upper()} WIN SOURCE SLOT {cell['slot']}  {width}x{height}",fill=(255,225,140))
        filename=f"{name}-win-source.png";sheet.save(args.output/filename)
        records.append({"character":character,"character_name":name,"source_bank":"victory","file":file,"sha256":want,"table_offset":0x60,"payload_offset":0x180,"slots":72,"grid":[2,2],"reference":filename,"reference_sha256":sha((args.output/filename).read_bytes()),"cells":cells})
    result={"kind":"original victory-pose references; not HD or animation acceptance","script_sha256":sha(Path(__file__).read_bytes()),"records":records,"rights":"local-only original assets"}
    (args.output/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"slots":144,"unique_sources":7,"sources":[r["file"] for r in records]}))


if __name__=="__main__":
    main()
