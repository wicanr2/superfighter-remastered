"""Docker 內製作原版姿態參考表，只供 HD 重繪與定位，不生成 HD 美術。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch", type=int, choices=range(4), default=0)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    source = Path("/project/workplace/sprite-source-v1")
    evidence = json.loads((source / "evidence.json").read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    records = []
    jaan = [list(range(10)) + [11, 12], list(range(13, 25)),
            list(range(25, 37)), list(range(37, 45)) + list(range(49, 53))]
    frank = [list(range(12)), list(range(13, 25)),
             list(range(25, 37)), list(range(38, 43)) + list(range(44, 51))]
    for file, name, slots in [("SFMAN01.DAT", "jaan", jaan[args.batch]),
                              ("SFMAN05.DAT", "frank", frank[args.batch])]:
        original = next(item for item in evidence["files"] if item["source"] == file)
        sheet = Image.new("RGBA", (1536, 1152), (19, 27, 43, 255))
        draw = ImageDraw.Draw(sheet)
        cells = []
        for ordinal, slot in enumerate(slots):
            frame = next(item for item in original["frames"] if item["slot"] == slot)
            path = source / frame["file"]
            assert sha(path) == frame["sha256"]
            image = Image.open(path).convert("RGBA")
            assert image.size == tuple(frame["size"])
            x, y = ordinal % 4 * 384, ordinal // 4 * 384
            w, h = image.size
            scale = min(3, 336 / w, 312 / h)
            rw, rh = round(w * scale), round(h * scale)
            position = (x + (384 - rw) // 2, y + 348 - rh)
            sheet.alpha_composite(image.resize((rw, rh), Image.Resampling.NEAREST), position)
            draw.text((x + 12, y + 12), f"{ordinal + 1:02d} / slot {slot:02d}", fill="white")
            cells.append({"ordinal": ordinal, "slot": slot, "cell": [x, y, 384, 384],
                          "reference_rect": [*position, rw, rh],
                          "source_rect": [0, 0, w, h], "source_file_offset": frame["file_offset"],
                          "source_png": frame["file"], "source_sha256": frame["sha256"]})
        output = args.output / (name + f"-poses-{args.batch:02d}.png")
        sheet.save(output)
        records.append({"character": name, "batch": args.batch, "original_file": file, "original_sha256": original["sha256"],
                        "sheet": output.name, "sha256": sha(output), "cells": cells})
    manifest = {"kind": "original pose reference, not HD assets", "tool": "sc-cht-hdtools:pillow11.3.0-r1",
                "script_sha256": sha(Path(__file__)), "evidence_sha256": sha(source / "evidence.json"),
                "records": records}
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"sheets": [item["sheet"] for item in records], "poses": 24}))


if __name__ == "__main__":
    main()
