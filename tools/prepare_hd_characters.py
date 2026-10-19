"""Docker 內準備原生角色素材清單，只複製生成 PNG 並計算透明邊界。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from PIL import Image


def atlas_regions(image, cols, rows):
    """沿實際透明間隔登錄圖像，避免生成圖略偏格線時截斷肢體。"""
    alpha = image.getchannel("A").point(lambda v: 255 if v >= 16 else 0)
    w, h = image.size

    def separators(length, count, empty):
        result = [0]
        for boundary in range(1, count):
            ideal = length * boundary // count
            radius = length // count // 3
            choices = [p for p in range(max(result[-1] + 1, ideal - radius), min(length, ideal + radius)) if empty(p)]
            assert choices, "圖集人物無完整透明間隔，不能安全登錄"
            result.append(min(choices, key=lambda p: (abs(p - ideal), p)))
        result.append(length)
        return result

    ys = separators(h, rows, lambda y: alpha.crop((0, y, w, y + 1)).getbbox() is None)
    regions = []
    for row in range(rows):
        top, bottom = ys[row:row + 2]
        xs = separators(w, cols, lambda x: alpha.crop((x, top, x + 1, bottom)).getbbox() is None)
        for column in range(cols):
            left, right = xs[column:column + 2]
            bounds = (left, top, right, bottom)
            box = alpha.crop(bounds).getbbox()
            assert box is not None, "圖集姿態缺少圖像"
            rect = [left + box[0], top + box[1], left + box[2], top + box[3]]
            opaque = image.getchannel("A").crop(tuple(rect)).point(lambda v: 255 if v >= 128 else 0).getbbox()
            assert opaque is not None
            assert rect[0] + opaque[0] > 0 and rect[1] + opaque[1] > 0
            assert rect[0] + opaque[2] < w and rect[1] + opaque[3] < h, "圖像碰到圖集外緣，須重新產圖"
            regions.append({"region": list(bounds), "rect": rect})
    for i, a in enumerate(regions):
        for b in regions[i + 1:]:
            ra, rb = a["rect"], b["rect"]
            assert max(ra[0], rb[0]) >= min(ra[2], rb[2]) or max(ra[1], rb[1]) >= min(ra[3], rb[3])
    return regions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-root", type=Path, default=Path("/orig"))
    parser.add_argument("--art-manifest", type=Path, action="append")
    args = parser.parse_args()
    project = Path("/project")
    sha = lambda data: hashlib.sha256(data).hexdigest()
    manifests = args.art_manifest or [project / "workplace/hd-sprite-art-v1/manifest.json"]
    sources, candidates, atlases, copies, registrations = {}, {}, {}, {}, {}
    for path in manifests:
        art = json.loads(path.read_text())
        for record in art["records"]:
            reference_path = project / Path(record["reference"]).parent / "manifest.json"
            reference = json.loads(reference_path.read_text())
            ref = next(item for item in reference["records"] if item["character"] == record["character"] and item.get("batch", 0) == record.get("batch", 0))
            character = int(ref["original_file"][5:7]) - 1
            bank = record.get("palette_bank", 0)
            assert bank in (0, 1) and bank == ref.get("palette_bank", 0)
            data = (args.original_root / ref["original_file"]).read_bytes()
            assert sha(data) == ref["original_sha256"]
            sources[character] = (ref["original_file"], data)
            png = path.parent / record["file"]
            assert sha(png.read_bytes()) == record["sha256"]
            image = Image.open(png)
            assert image.mode == "RGBA" and image.size == tuple(record["size"])
            cols, rows = record["grid"]
            assert cols > 0 and rows > 0
            regions = atlas_regions(image, cols, rows)
            registrations[png.name] = {"sha256": record["sha256"], "regions": regions}
            atlas = {"file": png.name, "sha256": record["sha256"], "width": image.width, "height": image.height}
            assert png.name not in atlases or atlases[png.name] == atlas
            atlases[png.name], copies[png.name] = atlas, png
            for cell in ref["cells"]:
                slot = cell["slot"]
                seg, off = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
                offset = 0xc48 + seg * 16 + off
                w, h = data[offset:offset + 2]
                assert [w, h] == cell["source_rect"][2:]
                end = offset + 2 + ((w + 1) // 2) * h
                assert end <= len(data)
                ordinal = cell["ordinal"]
                rect = regions[ordinal]["rect"]
                candidates.setdefault((character, bank, sha(data[offset:end])), (png.name, rect))
    poses, source_records = [], []
    for character, (file, data) in sorted(sources.items()):
        source_records.append({"character": character, "file": file, "sha256": sha(data)})
        for slot in range(72):
            seg, off = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
            offset = 0xc48 + seg * 16 + off
            w, h = data[offset:offset + 2]
            end = offset + 2 + ((w + 1) // 2) * h
            digest = sha(data[offset:end])
            for bank in (0, 1):
                choice = candidates.get((character, bank, digest))
                if not choice:
                    continue
                pose = {"character": character, "slot": slot, "width": w, "height": h,
                              "source_offset": offset, "source_sha256": digest,
                              "atlas": choice[0], "rect": choice[1]}
                if bank:
                    pose["palette_bank"] = bank
                poses.append(pose)
    version = 2 if any(p.get("palette_bank", 0) for p in poses) else 1
    manifest = {"version": version, "kind": "original-draw-characters", "sources": source_records,
                "atlases": list(atlases.values()), "poses": poses,
                "evidence": ["docs/spec/008-hd-characters.md", "workplace/sprite-layers-v1/receipt.json", "registration.json"]}
    if version == 2:
        manifest["evidence"].append("docs/spec/009-hd-effects.md")
    args.output.mkdir(exist_ok=False)
    assert args.output.stat().st_uid == 1000
    for name, path in copies.items():
        shutil.copyfile(path, args.output / name)
        assert sha((args.output / name).read_bytes()) == atlases[name]["sha256"]
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (args.output / "registration.json").write_text(json.dumps({"kind": "read-only atlas registration; original PNG bytes unchanged",
        "script_sha256": sha(Path(__file__).read_bytes()), "atlases": registrations}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"atlases": len(atlases), "mapped_slots": len(poses), "unique_painted_sources": len(candidates)}))


if __name__ == "__main__":
    main()
