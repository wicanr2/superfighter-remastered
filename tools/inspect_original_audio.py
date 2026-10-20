"""只讀盤點 SF000.MUS 的 MIDI 與 PPM 的 Compact PCM 記錄；原音訊只存本機。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir()
    a.output.mkdir()
    sha=lambda b:hashlib.sha256(b).hexdigest()
    b=(a.original_root/"SF000.MUS").read_bytes()
    assert sha(b)=="78af89020939bc7f2013f3869332aae1a67a2600c14ec7820146599e31cdaeda"
    cursor=0
    midi=[]
    while cursor<len(b):
        start=cursor
        assert b[cursor:cursor+4]==b"MThd"
        length=struct.unpack_from(">I",b,cursor+4)[0]
        assert length==6
        fmt,tracks,division=struct.unpack_from(">HHH",b,cursor+8)
        assert fmt==0 and tracks==1 and division==240
        cursor+=8+length
        for _ in range(tracks):
            assert b[cursor:cursor+4]==b"MTrk"
            length=struct.unpack_from(">I",b,cursor+4)[0]
            cursor+=8+length
            assert cursor<=len(b)
        payload=b[start:cursor]
        name=f"original-{len(midi):02d}.mid"
        (a.output/name).write_bytes(payload)
        midi.append({"index":len(midi),"offset":start,"bytes":len(payload),"sha256":sha(payload),"file":name,"format":fmt,"tracks":tracks,"ticks_per_quarter":division})
    assert len(midi)==15
    pcm=[]
    for path in sorted(a.original_root.glob("FIV-*.PPM")):
        data=path.read_bytes()
        first=struct.unpack_from("<H",data)[0]
        assert first>0 and first%2==0 and first<len(data)
        offsets=list(struct.unpack_from("<"+"H"*(first//2),data))
        assert offsets==sorted(set(offsets)) and offsets[0]==first
        records=[]
        for i,offset in enumerate(offsets):
            end=offsets[i+1] if i+1<len(offsets) else len(data)
            assert offset<end and data[offset:offset+17]==b"Compact PCM File\x1a"
            payload=data[offset:end]
            records.append({"index":i,"offset":offset,"bytes":len(payload),"sha256":sha(payload),"header_hex":payload[:32].hex()})
        pcm.append({"file":path.name,"sha256":sha(data),"records":records})
    result={"kind":"read-only original music and Compact PCM inventory; no hardware timing claims", "address_space":"source file byte offsets", "source":"SF000.MUS", "source_sha256":sha(b),"midi":midi,"pcm":pcm,
            "pcm_records":sum(len(x["records"]) for x in pcm),"script_sha256":sha(Path(__file__).read_bytes()),
            "rights":"original audio and extracted MIDI remain local; not Release or Git assets", "limits":"MIDI track purpose and in-game song routing unverified; PCM codec/rate/voice labels not confirmed"}
    (a.output/"inventory.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"midi_songs":len(midi),"pcm_containers":len(pcm),"pcm_records":result["pcm_records"]}))


if __name__=="__main__":main()
