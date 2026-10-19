"""準備其他角色的一般姿態候選群組，保留既有 PNG 與格式。"""
import argparse
import copy
import hashlib
import json
import shutil
import struct
from pathlib import Path

from PIL import Image
from prepare_hd_characters import atlas_regions


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basename(name):
    assert name and Path(name).name == name and not any(c in name for c in ("/", "\\", ":"))
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--art", type=Path, required=True)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and args.output.parent.is_dir() and args.output.parent.stat().st_uid == 1000
    base = json.loads((args.base / "manifest.json").read_text())
    reference = json.loads((args.reference / "manifest.json").read_text())
    art = json.loads((args.art / "manifest.json").read_text())
    assert base["version"] == 3 and base["kind"] == "original-draw-characters"
    character = reference["character"]
    assert 0 <= character <= 10 and reference["slots"] == 72
    assert art["source_reference_sha256"] == sha(args.reference / "manifest.json")
    assert not any(s["character"] == character and not s.get("source_bank") for s in base["sources"])
    original = args.original_root / f"SFMAN{character + 1:02d}.DAT"
    assert sha(original) == reference["source_sha256"]
    data = original.read_bytes()
    before = copy.deepcopy(base)
    copies = {}
    for atlas in base["atlases"]:
        path = args.base / basename(atlas["file"])
        assert path.is_file() and sha(path) == atlas["sha256"]
        copies[atlas["file"]] = path
    lookup = {}
    for record in art["records"]:
        assert record["character"] == character
        path = args.art / basename(record["file"])
        assert path.is_file() and sha(path) == record["sha256"]
        with Image.open(path) as image:
            assert image.mode == "RGBA" and list(image.size) == record["size"]
            assert image.getchannel("A").getextrema() == (0, 255)
            assert atlas_regions(image, *record["grid"]) == record["regions"]
        assert len(record["slots"]) == len(record["regions"])
        for slot, region in zip(record["slots"], record["regions"]):
            assert slot not in lookup
            lookup[slot] = (record["file"], region["rect"])
        assert record["file"] not in copies
        copies[record["file"]] = path
        base["atlases"].append({"file": record["file"], "sha256": record["sha256"],
                                "width": record["size"][0], "height": record["size"][1]})
    assert len(lookup) == len(reference["cells"]) == reference["unique_sources"]
    poses = {}
    for cell in reference["cells"]:
        atlas, rect = lookup[cell["slot"]]
        for slot in cell["aliases"]:
            assert 0 <= slot < 72 and slot not in poses
            segment, offset = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
            start = 0xc48 + segment * 16 + offset
            assert start == cell["source_offset"] and 0xc48 <= start < len(data) - 2
            width, height = data[start:start + 2]
            end = start + 2 + (width + 1) // 2 * height
            assert (width, height) == (cell["width"], cell["height"]) and end <= len(data)
            assert hashlib.sha256(data[start:end]).hexdigest() == cell["source_sha256"]
            poses[slot] = {"character": character, "slot": slot, "width": width, "height": height,
                           "source_offset": start, "source_sha256": cell["source_sha256"], "atlas": atlas, "rect": rect}
    assert set(poses) == set(range(72))
    base["sources"].append({"character": character, "file": original.name, "sha256": sha(original)})
    base["poses"].extend(poses[slot] for slot in range(72))
    assert base["poses"][:len(before["poses"])] == before["poses"]
    provenance = {"kind": "candidate normal-character registration; not native acceptance",
                  "character": character, "source_slots": 72, "unique_art": len(lookup),
                  "script_sha256": sha(Path(__file__)), "base_manifest_sha256": sha(args.base / "manifest.json"),
                  "reference_manifest_sha256": sha(args.reference / "manifest.json"),
                  "art_manifest_sha256": sha(args.art / "manifest.json"),
                  "rights": "local-only derivative art; not release assets"}
    args.output.mkdir()
    for name, source in copies.items():
        target = args.output / name
        shutil.copyfile(source, target)
        assert sha(target) == sha(source) and target.stat().st_uid == 1000
    (args.output / "manifest.json").write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n")
    (args.output / "character-extension-registration.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"character": character, "poses": len(base["poses"]), "new_slots": 72, "unique_art": len(lookup)}))


if __name__ == "__main__":
    main()
