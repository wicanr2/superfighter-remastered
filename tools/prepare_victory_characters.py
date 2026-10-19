"""在既有角色群組加入獨立 WIN 圖像來源，原 PNG bytes 與舊群組保持不變。"""
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

from PIL import Image
from prepare_hd_characters import atlas_regions


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root",type=Path,default=Path("/orig"))
    parser.add_argument("--base",type=Path,required=True)
    parser.add_argument("--art",type=Path,required=True)
    parser.add_argument("--reference",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    assert not args.output.exists() and args.output.parent.stat().st_uid==1000
    base=json.loads((args.base/"manifest.json").read_text())
    assert base["version"]==2 and base["kind"]=="original-draw-characters"
    references=json.loads((args.reference/"manifest.json").read_text())
    art=json.loads((args.art/"manifest.json").read_text())
    records={r["character"]:r for r in art["records"]}
    for source in base["sources"]:
        assert digest(args.original_root/source["file"])==source["sha256"]
    for atlas in base["atlases"]:
        assert digest(args.base/atlas["file"])==atlas["sha256"]
    base["version"]=3
    copies={a["file"]:args.base/a["file"] for a in base["atlases"]}
    registrations=[]
    for reference in references["records"]:
        character,name=reference["character"],reference["character_name"]
        source_path=args.original_root/reference["file"]
        assert digest(source_path)==reference["sha256"]
        source=source_path.read_bytes()
        record=records[name]
        image_path=args.art/record["file"]
        assert digest(image_path)==record["sha256"]
        with Image.open(image_path) as image:
            assert image.mode=="RGBA" and list(image.size)==record["size"] and image.getchannel("A").getextrema()==(0,255)
            regions=atlas_regions(image,*record["grid"])
            assert regions==record["regions"] and len(regions)==len(reference["cells"])
        choices={cell["source_sha256"]:regions[cell["ordinal"]]["rect"] for cell in reference["cells"]}
        assert record["file"] not in copies
        copies[record["file"]]=image_path
        base["atlases"].append({"file":record["file"],"sha256":record["sha256"],"width":record["size"][0],"height":record["size"][1]})
        base["sources"].append({"character":character,"source_bank":"victory","file":reference["file"],"sha256":reference["sha256"]})
        for slot in range(72):
            segment,offset=struct.unpack_from("<HH",source,0x60+slot*4)
            at=0x180+segment*16+offset
            assert 0x180<=at and at+2<=len(source)
            width,height=source[at:at+2];end=at+2+(width+1)//2*height
            assert width and height and end<=len(source)
            sha=hashlib.sha256(source[at:end]).hexdigest()
            assert sha in choices
            base["poses"].append({"character":character,"source_bank":"victory","slot":slot,
                "width":width,"height":height,"source_offset":at,"source_sha256":sha,"atlas":record["file"],"rect":choices[sha]})
        registrations.append({"character":character,"source_bank":"victory","slots":72,"unique_sources":len(choices),"regions":regions})
    assert len(registrations)==2 and len(base["poses"])==301
    provenance={"script_sha256":digest(Path(__file__)),"base_manifest_sha256":digest(args.base/"manifest.json"),
        "art_manifest_sha256":digest(args.art/"manifest.json"),"requests_sha256":digest(args.art/"requests.json"),
        "reference_manifest_sha256":digest(args.reference/"manifest.json"),"registrations":registrations,
        "rights":"local-only original references and derivative art; not release assets"}
    base["evidence"]=base.get("evidence",[])+["docs/spec/017-victory-pose-banks.md","victory-pose-registration.json"]
    args.output.mkdir()
    for name,source in copies.items():
        shutil.copy2(source,args.output/name)
        assert digest(args.output/name)==digest(source) and (args.output/name).stat().st_uid==1000
    (args.output/"manifest.json").write_text(json.dumps(base,ensure_ascii=False,indent=2)+"\n")
    (args.output/"victory-pose-registration.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":3,"poses":len(base["poses"]),"sources":len(base["sources"]),"new_unique_poses":7}))


if __name__=="__main__":
    main()
