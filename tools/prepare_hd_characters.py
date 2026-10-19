"""Docker 內準備原生角色素材清單，只複製生成 PNG 並計算透明邊界。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-root", type=Path, default=Path("/orig"))
    parser.add_argument("--art-manifest", type=Path, action="append")
    args = parser.parse_args()
    project = Path("/project")
    sha = lambda data: hashlib.sha256(data).hexdigest()
    manifests = args.art_manifest or [project / "workplace/hd-sprite-art-v1/manifest.json"]
    sources, candidates, atlases, copies = {}, {}, {}, {}
    for path in manifests:
        art = json.loads(path.read_text())
        for record in art["records"]:
            reference_path = project / Path(record["reference"]).parent / "manifest.json"
            reference = json.loads(reference_path.read_text())
            ref = next(item for item in reference["records"] if item["character"] == record["character"] and item.get("batch", 0) == record.get("batch", 0))
            character = int(ref["original_file"][5:7]) - 1
            data = (args.original_root / ref["original_file"]).read_bytes()
            assert sha(data) == ref["original_sha256"]
            sources[character] = (ref["original_file"], data)
            png = path.parent / record["file"]
            assert sha(png.read_bytes()) == record["sha256"]
            image = Image.open(png)
            assert image.mode == "RGBA" and image.size == tuple(record["size"])
            cols, rows = record["grid"]
            assert image.width % cols == image.height % rows == 0
            cw, ch = image.width // cols, image.height // rows
            atlas = {"file": png.name, "sha256": record["sha256"], "width": image.width, "height": image.height}
            assert png.name not in atlases or atlases[png.name] == atlas
            atlases[png.name], copies[png.name] = atlas, png
            alpha = image.getchannel("A")
            for cell in ref["cells"]:
                slot = cell["slot"]
                seg, off = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
                offset = 0xc48 + seg * 16 + off
                w, h = data[offset:offset + 2]
                assert [w, h] == cell["source_rect"][2:]
                end = offset + 2 + ((w + 1) // 2) * h
                assert end <= len(data)
                ordinal = cell["ordinal"]
                x, y = ordinal % cols * cw, ordinal // cols * ch
                box = alpha.crop((x, y, x + cw, y + ch)).point(lambda v: 255 if v >= 16 else 0).getbbox()
                assert box is not None
                rect = [x + box[0], y + box[1], x + box[2], y + box[3]]
                candidates.setdefault((character, sha(data[offset:end])), (png.name, rect))
    poses, source_records = [], []
    for character, (file, data) in sorted(sources.items()):
        source_records.append({"character": character, "file": file, "sha256": sha(data)})
        for slot in range(72):
            seg, off = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
            offset = 0xc48 + seg * 16 + off
            w, h = data[offset:offset + 2]
            end = offset + 2 + ((w + 1) // 2) * h
            digest = sha(data[offset:end])
            choice = candidates.get((character, digest))
            if choice:
                poses.append({"character": character, "slot": slot, "width": w, "height": h,
                              "source_offset": offset, "source_sha256": digest,
                              "atlas": choice[0], "rect": choice[1]})
    manifest = {"version": 1, "kind": "original-draw-characters", "sources": source_records,
                "atlases": list(atlases.values()), "poses": poses,
                "evidence": ["docs/spec/008-hd-characters.md", "workplace/sprite-layers-v1/receipt.json"]}
    args.output.mkdir(exist_ok=False)
    assert args.output.stat().st_uid == 1000
    for name, path in copies.items():
        shutil.copyfile(path, args.output / name)
        assert sha((args.output / name).read_bytes()) == atlases[name]["sha256"]
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"atlases": len(atlases), "mapped_slots": len(poses), "unique_painted_sources": len(candidates)}))


if __name__ == "__main__":
    main()
