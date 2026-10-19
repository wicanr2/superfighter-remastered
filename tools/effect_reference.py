"""依正常原版繪製收據的實際色盤製作 HD 特效參考，不修改生成美術。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--character", choices=["jaan", "frank"], default="jaan")
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    character = 0 if args.character == "jaan" else 4
    slots = [45, 46, 47, 48, 57, 58, 59, 60] if character == 0 else [12, 37, 43, 55, 56, 12, 37, 43]
    original_file = f"SFMAN{character + 1:02d}.DAT"
    source = Path("/orig", original_file).read_bytes()
    assert hashlib.sha256(source).hexdigest() == receipt["inputs"][original_file]
    sheet = Image.new("RGBA", (1536, 768), (19, 27, 43, 255))
    draw = ImageDraw.Draw(sheet)
    cells = []
    args.output.mkdir(exist_ok=False)
    for ordinal, slot in enumerate(slots):
        record = next(item for item in receipt["records"] if item["role"] == "effect" and
                      any(s["character"] == character and s["slot"] == slot for s in item["sources"]))
        assert record["pixel_differences"] == record["mask_differences"] == 0
        location = next(s for s in record["sources"] if s["character"] == character and s["slot"] == slot)
        assert location["bytes_match_source"]
        w, h = record["width"], record["height"]
        at = location["file_offset"]
        raw = source[at:at + 2 + (w + 1) // 2 * h]
        assert hashlib.sha256(raw).hexdigest() == record["source_sha256"]
        palette = [[(v << 2) | (v >> 4) for v in source[0xaf8 + i * 3:0xaf8 + i * 3 + 3]] for i in range(16)]
        assert palette == record["runtime_colors"]
        image = Image.new("RGBA", (w, h))
        for y in range(h):
            for x in range(w):
                packed = raw[2 + y * ((w + 1) // 2) + x // 2]
                value = packed >> 4 if x % 2 == 0 else packed & 15
                if value:
                    image.putpixel((x, y), (*palette[value], 255))
        x, y = ordinal % 4 * 384, ordinal // 4 * 384
        scale = min(5, 330 / w, 300 / h)
        rw, rh = round(w * scale), round(h * scale)
        position = (x + (384 - rw) // 2, y + (384 - rh) // 2)
        sheet.alpha_composite(image.resize((rw, rh), Image.Resampling.NEAREST), position)
        draw.text((x + 12, y + 12), f"{ordinal + 1:02d} / slot {slot:02d} / bank 1", fill="white")
        cells.append({"ordinal": ordinal, "slot": slot, "source_rect": [0, 0, w, h],
                      "source_file_offset": at, "packed_sha256": record["source_sha256"]})
    path = args.output / (args.character + "-effects.png")
    sheet.save(path)
    manifest = {"kind": "normal original effect palette reference", "records": [
        {"character": args.character, "batch": 6, "palette_bank": 1, "original_file": original_file,
         "original_sha256": receipt["inputs"][original_file], "sheet": path.name,
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "grid": [4, 2], "cells": cells}],
        "receipt_sha256": hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"poses": len(slots), "palette_bank": 1, "sheet": str(path)}))


if __name__ == "__main__":
    main()
