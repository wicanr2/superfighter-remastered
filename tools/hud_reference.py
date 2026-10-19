"""由原版檔案獨立重組介面 bitmap，核對正常輸入收據；不猜測數值。"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(root, state, wins=None):
    board = bytearray((root / "BOARD.XBB").read_bytes())
    names = (root / "NAME.XBB").read_bytes()
    digits = (root / "0-9.XBB").read_bytes()
    assert len(board) == 320 * 32 and len(digits) == 10 * 14 * 15

    def draw(data, width, height, x, y):
        assert len(data) == width * height and 0 <= x <= 320 - width and 0 <= y <= 32 - height
        for row in range(height):
            start = (row + y) * 320 + x
            board[start:start + width] = data[row * width:(row + 1) * width]

    def label(slot, x, y, right=False):
        offset = struct.unpack_from("<H", names, slot * 2)[0]
        w, h = names[offset:offset + 2]
        draw(names[offset + 2:offset + 2 + w * h], w, h, x - w if right else x, y)

    for player, character in enumerate(state["characters"]):
        assert 0 <= character <= 10
        label(character, 18 if player == 0 else 302, 21, right=player == 1)
    for player, count in enumerate(state.get("display_wins", state["wins"]) if wins is None else wins):
        assert 0 <= count <= 2
        for ordinal in range(1, count + 1):
            label(11, 6 + ordinal * 12 if player == 0 else 304 - ordinal * 12, 0)
    timer = state["timer"]
    assert 0 <= timer <= 99
    for digit, x in [(timer // 10, 145), (timer % 10, 161)]:
        draw(digits[digit * 210:(digit + 1) * 210], 14, 15, x, 9)
    for y in range(13, 19):
        for player, health in enumerate(state["display_health"]):
            assert 0 <= health <= 124
            if player == 0:
                for x in range(19, 143 - health):
                    board[y * 320 + x] = 13
            else:
                for x in range(177 + health, 301):
                    board[y * 320 + x] = 13
    return bytes(board)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = ["SF.EXE", "BOARD.XBB", "NAME.XBB", "0-9.XBB", "BOARD.COL"]
    source = {name: digest(args.root / name) for name in names}
    raw = (args.root / "SF.EXE").read_bytes()
    assert source["SF.EXE"] == "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300"
    assert struct.unpack_from("<10H", raw, 0xa610 + 0x2f12) == tuple(i * 210 for i in range(10))
    colors = (args.root / "BOARD.COL").read_bytes()
    # BOARD.COL 實檔 768 bytes；01B9:3D64 只讀前 96 bytes 到 A0h 起的色盤。
    assert len(colors) == 768 and max(colors) <= 63
    palette = [tuple((value << 2) | (value >> 4) for value in colors[i:i + 3]) for i in range(0, 48, 3)]
    results = []
    for directory in sorted(args.fixtures.glob("hud-draw-v*")):
        probe = directory.name
        if not (directory / "receipt.json").exists():
            continue
        receipt = json.loads((directory / "receipt.json").read_text())
        assert not receipt["unimplemented"]
        for record in receipt["records"]:
            assert record["pixel_differences"] == record["mask_differences"] == 0
            if "fixture" not in record:
                continue
            stem = record["fixture"]
            bitmap = (directory / (stem + ".bitmap")).read_bytes()
            assert set(bitmap) <= set(range(16)) | {0xad, 0xae}
            canonical = bytes(value & 15 for value in bitmap)
            assert [tuple(x) for x in json.loads((directory / (stem + ".palette.json")).read_text())[0xa0:0xb0]] == palette
            expected = reconstruct(args.root, record["state"])
            differences = sum(a != b for a, b in zip(expected, canonical))
            before = (directory / (stem + ".before.idx")).read_bytes()
            after = (directory / (stem + ".after.idx")).read_bytes()
            actual_mask = (directory / (stem + ".mask")).read_bytes()
            assert len(before) == len(after) == len(actual_mask) == 64000
            replay, mask = bytearray(before), bytearray(64000)
            for offset, value in enumerate(bitmap):
                if value:
                    at = record["state"]["crtc_rows"] * 320 + offset
                    assert 0 <= at < 64000
                    replay[at], mask[at] = value | 0xa0, 1
            assert replay == after and mask == actual_mask, (probe, stem)
            results.append({"probe": probe, "fixture": stem, "state": record["state"],
                            "bitmap_differences": differences, "draw_and_mask_replayed": True,
                            "bitmap_sha256": digest(directory / (stem + ".bitmap"))})
    result = {"kind": "independent original-source HUD reconstruction; not native HD acceptance", "inputs": source,
              "script_sha256": digest(Path(__file__)), "fixtures": results,
              "limits": "direct raw win count can lead visible bitmap during round transition; any differences remain unaccepted"}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"fixtures": len(results), "exact": sum(x["bitmap_differences"] == 0 for x in results),
                      "different": [{k: v for k, v in x.items() if k in ["probe", "fixture", "bitmap_differences"]} for x in results if x["bitmap_differences"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
