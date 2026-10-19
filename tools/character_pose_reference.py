"""依已知 SFMAN 格式整理指定角色的原姿態、別名與製作參考。"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", type=int, choices=range(11), required=True)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    name = f"SFMAN{args.character + 1:02d}.DAT"
    data = (args.original_root / name).read_bytes()
    source_manifest = json.loads(args.source_manifest.read_text())
    original = next(item for item in source_manifest["files"] if item["location"] == "orig/" + name)
    assert sha(data) == original["sha256"] and len(data) >= 0xc48
    assert max(data[0xac8:0xaf8]) <= 63
    palette = [tuple((v << 2) | (v >> 4) for v in data[0xac8 + i * 3:0xac8 + i * 3 + 3]) for i in range(16)]
    groups = {}
    for slot in range(72):
        segment, offset = struct.unpack_from("<HH", data, 0xb28 + slot * 4)
        start = 0xc48 + segment * 16 + offset
        assert 0xc48 <= start < len(data) - 2
        width, height = data[start:start + 2]
        end = start + 2 + (width + 1) // 2 * height
        assert width > 0 and height > 0 and end <= len(data)
        digest = sha(data[start:end])
        if digest not in groups:
            groups[digest] = {"ordinal": len(groups), "slot": slot, "aliases": [], "width": width,
                              "height": height, "source_offset": start, "source_sha256": digest}
        groups[digest]["aliases"].append(slot)
    args.output.mkdir()
    cells = list(groups.values())
    sheets = []
    for batch in range(math.ceil(len(cells) / 12)):
        sheet = Image.new("RGB", (1536, 1152), (19, 27, 43))
        draw = ImageDraw.Draw(sheet)
        chosen = cells[batch * 12:(batch + 1) * 12]
        for ordinal, cell in enumerate(chosen):
            width, height, start = cell["width"], cell["height"], cell["source_offset"]
            image = Image.new("RGBA", (width, height))
            stride = (width + 1) // 2
            for y in range(height):
                for x in range(width):
                    value = data[start + 2 + y * stride + x // 2]
                    value = value >> 4 if x % 2 == 0 else value & 15
                    if value:
                        image.putpixel((x, y), (*palette[value], 255))
            filename = f"slot-{cell['slot']:02d}.png"
            image.save(args.output / filename)
            cell["file"] = filename
            cell["png_sha256"] = sha((args.output / filename).read_bytes())
            scale = min(336 / width, 308 / height)
            large = image.resize((round(width * scale), round(height * scale)), Image.Resampling.NEAREST)
            left, top = ordinal % 4 * 384, ordinal // 4 * 384
            sheet.paste(large, (left + (384 - large.width) // 2, top + 352 - large.height), large)
            draw.text((left + 12, top + 12), f"{ordinal + 1:02d} / SLOT {cell['slot']:02d} / {width}x{height}", fill=(255, 225, 140))
        filename = f"poses-{batch:02d}.png"
        sheet.save(args.output / filename)
        sheets.append({"batch": batch, "file": filename, "sha256": sha((args.output / filename).read_bytes()),
                       "grid": [4, 3], "slots": [cell["slot"] for cell in chosen]})
    result = {"kind": "static original SFMAN pose references; not HD or dynamic consumer verification",
              "character": args.character, "file": name, "source_sha256": sha(data), "slots": 72,
              "unique_sources": len(cells), "table_offset": 0xb28, "payload_offset": 0xc48,
              "palette_offset": 0xac8, "source_manifest_sha256": sha(args.source_manifest.read_bytes()),
              "script_sha256": sha(Path(__file__).read_bytes()), "cells": cells, "sheets": sheets,
              "rights": "local-only original assets; excluded from Git and release packages"}
    (args.output / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"character": args.character, "slots": 72, "unique_sources": len(cells), "sheets": len(sheets)}))


if __name__ == "__main__":
    main()
