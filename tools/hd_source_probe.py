#!/usr/bin/env python3
"""Docker 內的可丟棄資產蒐證器，非正式格式實作或 HD renderer。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_candidate(data):
    if len(data) < 774:
        raise ValueError("短檔")
    width, height = struct.unpack_from("<HH", data)
    flag = data[4]
    if not 0 < width <= 1024 or not 0 < height <= 1024 or flag != 1:
        raise ValueError("未支援的候選 header")
    palette = data[5:773]
    if max(palette) > 63:
        raise ValueError("不是候選 6-bit 色盤")
    marker = data[773]
    pos, pixels = 774, bytearray()
    while pos < len(data):
        value = data[pos]
        pos += 1
        count = 1
        if value == marker:
            if pos + 2 > len(data):
                raise ValueError("截斷的 run")
            count, value = data[pos:pos + 2]
            pos += 2
            if count == 0:
                raise ValueError("零長度 run 尚未證實")
        if len(pixels) + count > width * height:
            raise ValueError("解碼超出宣告尺寸")
        pixels.extend(bytes([value]) * count)
    if len(pixels) != width * height:
        raise ValueError("解碼尺寸不足")
    return width, height, palette, bytes(pixels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=Path("/orig"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--sprites", action="store_true", help="只蒐證斬與法蘭克的 72 個 sprite 指標槽")
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False, parents=True)
    if args.sprites:
        sprite_evidence(args)
        return
    screen = (args.receipt / "screen.bin").read_bytes()
    assert len(screen) == 64000
    results, thumbs = [], []
    for path in sorted(args.original.iterdir()):
        if path.suffix.upper() not in {".XGB", ".CPM"}:
            continue
        try:
            width, height, palette, pixels = decode_candidate(path.read_bytes())
        except ValueError as exc:
            results.append({"source": path.name, "sha256": digest(path),
                            "level": "unknown", "unsupported_reason": str(exc)})
            continue
        img = Image.frombytes("P", (width, height), pixels)
        img.putpalette([(v << 2) | (v >> 4) for v in palette])
        png = args.output / (path.name + ".png")
        img.save(png)
        record = {"source": path.name, "sha256": digest(path), "size": [width, height],
                  "header_bytes": path.read_bytes()[:5].hex(), "palette_offset": 5,
                  "marker_offset": 773, "marker": path.read_bytes()[773],
                  "rle_offset": 774, "output": png.name, "output_sha256": digest(png),
                  "level": "hypothesis: bounded decode and visual comparison only"}
        if width >= 320 and height >= 200:
            # 避開 HUD 與角色，僅找背景候選；不是整張圖 parity。
            samples = [(x, y) for y in range(45, 155, 4) for x in range(105, 205, 4)]
            best = (0, 0, 0)
            for oy in range(height - 200 + 1):
                for ox in range(width - 320 + 1):
                    matches = sum(pixels[(y + oy) * width + x + ox] == screen[y * 320 + x]
                                  for x, y in samples)
                    if matches > best[0]:
                        best = (matches, ox, oy)
            record["sample_match"] = {"matched": best[0], "total": len(samples),
                                      "crop_origin": list(best[1:]),
                                      "method": "indexed background subset, no character/HUD validation"}
        thumb = img.convert("RGB")
        thumb.thumbnail((360, 160))
        thumbs.append((path.name, thumb))
        results.append(record)
    if not thumbs:
        raise ValueError("沒有成功解碼的圖；停止，不建立空白圖證")
    sheet = Image.new("RGB", (760, ((len(thumbs) + 1) // 2) * 190), "#101522")
    draw = ImageDraw.Draw(sheet)
    for i, (name, thumb) in enumerate(thumbs):
        x, y = (i % 2) * 380 + 10, (i // 2) * 190 + 10
        draw.text((x, y), name, fill="white")
        sheet.paste(thumb, (x, y + 20))
    sheet.save(args.output / "contact-sheet.png")
    evidence = {"kind": "disposable DRAFT source probe, not production decoder",
                "tool": "sc-cht-hdtools:pillow11.3.0-r1", "script_sha256": digest(Path(__file__)),
                "address_space": "source file offsets, not IDA/runtime addresses",
                "reference_receipt": str(args.receipt),
                "reference_screen_sha256": digest(args.receipt / "screen.bin"),
                "files": results}
    (args.output / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))


def sprite_evidence(args):
    records = []
    for name in ["SFMAN01.DAT", "SFMAN05.DAT"]:
        source = args.original / name
        data = source.read_bytes()
        # IDA sub_13C38 的順序讀取：1536 + 1224 + 96 + 288。
        palette = data[0xAC8:0xB28]
        assert len(palette) == 96 and max(palette) <= 63
        frames, unique, thumbnails = [], set(), []
        directory = args.output / name
        directory.mkdir()
        for slot in range(72):
            segment, offset = struct.unpack_from("<HH", data, 0xB28 + slot * 4)
            address = 0xC48 + segment * 16 + offset
            if not 0xC48 <= address < len(data) - 1:
                raise ValueError("sprite 指標越界")
            width, height = data[address:address + 2]
            if not width or not height:
                raise ValueError("零尺寸 sprite")
            stride = (width + 1) // 2
            end = address + 2 + stride * height
            if end > len(data):
                raise ValueError("sprite 像素越界")
            rgba = bytearray()
            for y in range(height):
                row = data[address + 2 + y * stride:address + 2 + (y + 1) * stride]
                for x in range(width):
                    packed = row[x // 2]
                    value = packed >> 4 if x % 2 == 0 else packed & 15
                    color = palette[value * 3:value * 3 + 3]
                    rgba.extend(((v << 2) | (v >> 4) for v in color))
                    rgba.append(255 if value else 0)
            image = Image.frombytes("RGBA", (width, height), bytes(rgba))
            output = directory / f"slot-{slot:02d}.png"
            image.save(output)
            frames.append({"slot": slot, "pointer_segment": segment, "pointer_offset": offset,
                           "file_offset": address, "size": [width, height], "end": end,
                           "file": str(output.relative_to(args.output)), "sha256": digest(output)})
            if address not in unique:
                unique.add(address)
                thumbnails.append((slot, image))
        sheet = Image.new("RGBA", (8 * 130, ((len(thumbnails) + 7) // 8) * 150), "#172036")
        draw = ImageDraw.Draw(sheet)
        for i, (slot, image) in enumerate(thumbnails):
            x, y = i % 8 * 130, i // 8 * 150
            draw.text((x + 6, y + 4), f"{slot:02d}", fill="white")
            sheet.alpha_composite(image, (x + 6, y + 24))
        sheet.save(args.output / (name + "-atlas.png"))
        records.append({"source": name, "sha256": digest(source), "slots": len(frames),
                        "unique_addresses": len(unique), "frames": frames,
                        "level": "strong inference: original source clue, IDA file-read sequence and bounded shape validation; runtime sprite pointer/position not yet closed"})
    evidence = {"kind": "disposable original sprite atlas, not HD art",
                "tool": "sc-cht-hdtools:pillow11.3.0-r1", "script_sha256": digest(Path(__file__)),
                "address_space": "file offsets; pointer segment is relative to payload, not runtime DOS segment",
                "format": {"palette_offset": 0xAC8, "pointer_table_offset": 0xB28,
                           "payload_offset": 0xC48, "pixel_format": "row-padded high-nibble then low-nibble 4bpp, zero transparent"},
                "files": records}
    (args.output / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps([{k: r[k] for k in ["source", "slots", "unique_addresses"]} for r in records]))


if __name__ == "__main__":
    main()
