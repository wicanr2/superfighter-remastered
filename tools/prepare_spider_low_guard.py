"""登錄使用者確認的單張蜘蛛女低伏稿；只使用三組已驗來源。"""
import argparse
import copy
import hashlib
import json
import shutil
import struct
from pathlib import Path

from PIL import Image, ImageOps


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "reference", "art", "original-root", "consumer", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir()
    assert a.output.parent.stat().st_uid == 1000
    base = json.loads((a.base / "manifest.json").read_text())
    before = copy.deepcopy(base)
    assert (len(base["poses"]), len(base["atlases"]), len(base["sources"])) == (1381, 64, 19)
    assert not any(s["character"] == 8 for s in base["sources"])
    ref = json.loads((a.reference / "manifest.json").read_text())
    original = a.original_root / "SFMAN09.DAT"
    assert sha(original) == ref["source_sha256"] == "76f1a2484fd551c574279138e16f2f70971c4a7259858406e90c0211a2f3f53e"
    data = original.read_bytes()
    assert a.art.name == "spider-normal-01.png"
    index = json.loads((a.art.parent.parent / "source.json").read_text())
    # 候選索引另核對；原圖 bytes 不覆寫。
    assert sha(a.art) in json.dumps(index)
    consumer = json.loads(a.consumer.read_text())
    assert len(consumer["frames"]) == 124
    seen = set()
    cells = {cell["slot"]: cell for cell in ref["cells"]}
    for f in consumer["frames"]:
        assert f["background_buffer_equals_source"]
        assert [x["character"] for x in f["actors"]] == [8, 4]
        x = f["actors"][0]
        assert x["bytes_match_source"]
        if x["slot"] in (0, 1, 41):
            c = cells[x["slot"]]
            assert x["source_file_offset"] == c["source_offset"]
            assert x["size"] == [c["width"], c["height"]]
            seen.add(x["slot"])
    assert seen == {0, 1, 41}
    with Image.open(a.art) as source:
        assert source.mode == "RGBA" and source.size == (784, 1168)
        assert source.getchannel("A").getextrema() == (0, 255)
        normalized = ImageOps.mirror(source)
        assert ImageOps.mirror(normalized).tobytes() == source.tobytes()
        bbox = normalized.getchannel("A").point(lambda v: 255 if v >= 16 else 0).getbbox()
        assert bbox == (37, 340, 751, 901)
        crop = [bbox[0]-1, bbox[1]-1, bbox[2]+1, bbox[3]+1]
        assert normalized.getchannel("A").getbbox() == bbox
        normalized = normalized.crop(crop)
        rect = [0, 0, normalized.width, normalized.height]
    a.output.mkdir()
    for atlas in base["atlases"]:
        assert Path(atlas["file"]).name == atlas["file"]
        src = a.base / atlas["file"]
        assert sha(src) == atlas["sha256"]
        shutil.copyfile(src, a.output / atlas["file"])
    target = a.output / "spider-low-guard.png"
    normalized.save(target)
    base["atlases"].append({"file": target.name, "sha256": sha(target), "width": normalized.width, "height": normalized.height})
    keys = set()
    for slot in (0, 1, 41):
        cell = cells[slot]
        for alias in cell["aliases"]:
            assert alias not in keys
            keys.add(alias)
            segment, offset = struct.unpack_from("<HH", data, 0xb28 + alias * 4)
            start = 0xc48 + segment * 16 + offset
            w, h = data[start:start+2]
            assert start == cell["source_offset"] and (w, h) == (cell["width"], cell["height"])
            digest = hashlib.sha256(data[start:start+2+(w+1)//2*h]).hexdigest()
            assert digest == cell["source_sha256"]
            base["poses"].append({"character": 8, "slot": alias, "width": w, "height": h,
                                  "source_offset": start, "source_sha256": digest,
                                  "atlas": target.name, "rect": rect})
    assert keys == {0, 1, 41, *range(45, 72)}
    assert base["poses"][:1381] == before["poses"]
    base["sources"].append({"character": 8, "file": original.name, "sha256": sha(original)})
    text = json.dumps(base, ensure_ascii=False, indent=2) + "\n"
    assert len(text.encode()) <= 512 << 10
    (a.output / "manifest.json").write_text(text)
    provenance = {"kind": "approved approximate static low guard, not complete animation",
                  "approval": "ok 同意這版蜘蛛女", "spec": "docs/spec/034-spider-low-guard.md",
                  "input": "assets/hd/candidates/spider/cels-v2/spider-normal-01.png",
                  "input_sha256": sha(a.art), "output_sha256": sha(target),
                  "processing": "exact horizontal RGBA reflection then crop fully transparent margins; candidate unchanged",
                  "source_facing": "left", "crop_after_mirror": crop, "rect": rect, "keys": sorted(keys),
                  "model": "unknown external model supplied by user",
                  "script_sha256": sha(Path(__file__)), "base_manifest_sha256": sha(a.base / "manifest.json"),
                  "reference_manifest_sha256": sha(a.reference / "manifest.json"),
                  "consumer_sha256": sha(a.consumer), "manifest_sha256": sha(a.output / "manifest.json")}
    (a.output / "spider-low-guard-source.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(provenance, ensure_ascii=False))


if __name__ == "__main__":
    main()
