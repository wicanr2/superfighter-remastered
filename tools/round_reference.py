"""獨立由原檔重建開場訊息，核對原版的像素與寫入覆蓋。只在 Docker 執行。"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import struct

from PIL import Image, ImageDraw, __version__ as pillow_version


def digest(data):
    return hashlib.sha256(data).hexdigest()


def expected_source(original, state, round_index):
    names = (original / "NAME.XBB").read_bytes()
    assert len(names) == 17474
    slot = 12 if state in (0, 1) else 13
    offset = struct.unpack_from("<H", names, slot * 2)[0]
    width, height = names[offset:offset + 2]
    assert (width, height) == ((78, 15) if slot == 12 else (96, 15))
    result = bytearray(1442)
    result[:2] = bytes((96, 15))
    for row in range(15):
        result[2 + row * 96:2 + row * 96 + width] = names[offset + 2 + row * width:offset + 2 + (row + 1) * width]
    if slot == 12:
        assert 0 <= round_index < 9
        digits = (original / "0-9.XBB").read_bytes()
        for row in range(15):
            start = (round_index + 1) * 210 + row * 14
            result[83 + row * 96:97 + row * 96] = digits[start:start + 14]
    return bytes(result)


def replay_snapshot(original, snapshot, source, under_indices, under_mask):
    assert snapshot["complete"] and 0 <= snapshot["round_index"] < 9
    stage, half = snapshot["stage"], snapshot["half_width"]
    assert stage in range(4) and half in range(4, 69, 4)
    column, width = max(0, 48 - half), min(96, half * 2)
    assert (snapshot["column"], snapshot["width"], snapshot["x"], snapshot["y"]) == (column, width, 112 + column, 56)
    assert source == expected_source(original, stage, snapshot["round_index"])
    assert digest(source) == snapshot["source_sha256"]
    assert len(under_indices) == len(under_mask) == 64000 and set(under_mask) <= {0, 1}
    indices, mask, replace = bytearray(under_indices), bytearray(under_mask), bytearray(64000)
    for row in range(15):
        for col in range(width):
            value = source[2 + row * 96 + column + col]
            if value:
                at = (56 + row) * 320 + 112 + column + col
                indices[at], mask[at], replace[at] = value | 0xa0, 1, 1
    if stage == 1 and half == 4:
        indices[:1442] = expected_source(original, 2, snapshot["round_index"])
        mask[:1442] = bytes([1]) * 1442
    return bytes(indices), bytes(mask), bytes(replace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--original", type=Path, default=Path("/orig"))
    args = parser.parse_args()
    root, original = args.evidence, args.original
    receipt_path = root / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    for name, expected in receipt["inputs"].items():
        assert digest((original / name).read_bytes()) == expected, name
    assert receipt["unimplemented"] in ([], None)
    assert digest((root / "round_draw_receipt.go").read_bytes()) == receipt["script_sha256"]
    records = receipt["records"]
    assert records and receipt["display_frames"]
    routines = sum("routine_complete_steps" in record for record in records)
    if routines:
        assert routines == len(records)
    backgrounds = receipt.get("background_records", [])
    fixture_hashes = {}
    for record in backgrounds:
        fixture = record["fixture"]
        before = (root / (fixture + ".before.idx")).read_bytes()
        after = (root / (fixture + ".after.idx")).read_bytes()
        mask = (root / (fixture + ".mask")).read_bytes()
        source = (root / (fixture + ".source")).read_bytes()
        assert len(before) == len(after) == len(mask) == 64000 and len(source) == 480 * 204
        assert digest(source) == record["source_sha256"]
        expected, expected_mask = bytearray(before), bytearray(64000)
        for row in range(record["rows"], min(200, record["rows"] + 192)):
            camera = record["camera_x"]
            expected[row * 320:(row + 1) * 320] = source[row * 480 + camera:row * 480 + camera + 320]
            expected_mask[row * 320:(row + 1) * 320] = bytes([1]) * 320
        assert after == expected and mask == expected_mask, fixture
        assert record["pixel_differences"] == record["mask_differences"] == 0
        for suffix in (".source", ".before.idx", ".after.idx", ".mask"):
            path = root / (fixture + suffix)
            fixture_hashes[path.name] = digest(path.read_bytes())
    states, widths, same_writes = set(), set(), 0
    sheet = Image.new("RGB", (576 * 4, 125 * ((len(records) + 3) // 4)), "#17202a")
    paint = ImageDraw.Draw(sheet)
    for index, record in enumerate(records):
        fixture = record["fixture"]
        state, half = record["round_state"], record["half_width"]
        states.add(state)
        column = max(0, 48 - half)
        width = 96 if half > 48 else half * 2
        widths.add(width)
        assert state in range(4)
        assert (record["source_si"], record["x"], record["y"], record["width"]) == (column, 112 + column, 56, width)
        assert record["source_ds"] == record["destination_es"]
        source = expected_source(original, state, record["round_index"])
        assert source == (root / (fixture + ".source")).read_bytes(), (fixture, "source")
        assert digest(source) == record["source_sha256"]
        before = (root / (fixture + ".before.idx")).read_bytes()
        after = (root / (fixture + ".after.idx")).read_bytes()
        mask = (root / (fixture + ".mask")).read_bytes()
        assert len(before) == len(after) == len(mask) == 64000
        expected, expected_mask = bytearray(before), bytearray(64000)
        for row in range(15):
            for col in range(width):
                value = source[2 + row * 96 + column + col]
                if value:
                    at = (56 + row) * 320 + 112 + column + col
                    expected[at], expected_mask[at] = value | 0xA0, 1
        assert after == expected, (fixture, "pixels")
        assert mask == expected_mask, (fixture, "mask")
        if "routine_complete_steps" in record:
            if state == 1 and half == 4:
                expected[:1442] = expected_source(original, 2, record["round_index"])
                expected_mask[:1442] = bytes([1]) * 1442
            assert (root / (fixture + ".routine.after.idx")).read_bytes() == expected, (fixture, "post-draw pixels")
            assert (root / (fixture + ".routine.mask")).read_bytes() == expected_mask, (fixture, "post-draw mask")
        assert record["pixel_differences"] == record["mask_differences"] == 0
        assert record["writes"] == sum(mask)
        same = sum(bool(m and a == b) for m, a, b in zip(mask, before, after))
        assert same == record["equal_writes"]
        same_writes += same
        palette = json.loads((root / (fixture + ".palette.json")).read_text())
        image = Image.new("RGB", (96, 15), "#17202a")
        for row in range(15):
            for col in range(width):
                value = source[2 + row * 96 + column + col]
                if value:
                    image.putpixel((column + col, row), tuple(palette[value | 0xA0]))
        sx, sy = index % 4 * 576, index // 4 * 125
        sheet.paste(image.resize((576, 90), Image.Resampling.NEAREST), (sx, sy + 25))
        paint.text((sx + 6, sy + 4), f"{fixture}: state={state} half={half} width={width}", fill="white")
        for suffix in (".source", ".before.idx", ".after.idx", ".mask", ".palette.json"):
            path = root / (fixture + suffix)
            fixture_hashes[path.name] = digest(path.read_bytes())
        if "routine_complete_steps" in record:
            for suffix in (".routine.after.idx", ".routine.mask"):
                path = root / (fixture + suffix)
                fixture_hashes[path.name] = digest(path.read_bytes())
    assert states == {0, 1, 2, 3} and 96 in widths and 8 in widths
    sheet.save(root / "original-round-contact.png")
    result = {"kind": "independent original source, clipping and write replay; not HD verification",
              "receipt_sha256": digest(receipt_path.read_bytes()), "checker_sha256": digest(Path(__file__).read_bytes()),
              "python": platform.python_version(), "pillow": pillow_version,
              "draws": len(records), "display_frames": len(receipt["display_frames"]),
              "full_routine_draws": routines,
              "partial_background_draws": len(backgrounds),
              "round_indices": sorted({r["round_index"] for r in records}), "states": sorted(states),
              "widths": sorted(widths), "equal_writes": same_writes, "files": fixture_hashes,
              "limits": "first round only, no winner/draw/direct-VGA text; no runtime state injection"}
    (root / "reference.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
