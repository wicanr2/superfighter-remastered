"""從 NAME 原檔獨立重組勝負文字，核對實際 STOSB、同值寫入與顯示視窗。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image
from display_reference import geometry
from hud_reference import reconstruct
from round_reference import expected_source


def digest(data):
    return hashlib.sha256(data).hexdigest()


def glyph(names, slot):
    assert 0 <= slot < 22 and len(names) == 17474
    at = struct.unpack_from("<H", names, slot * 2)[0]
    width, height = names[at:at + 2]
    assert at >= 46 and width > 0 and height > 0 and at + 2 + width * height <= len(names)
    return at, width, height, names[at:at + 2 + width * height]


def layout(names, state):
    if state["health"][0] == state["health"][1]:
        return [(16, 110, 54, 0x3984)]
    if 4 not in state["flags_3eb7_3eb8"]:
        character = state["winner_word"] & 255
        assert 0 <= character <= 10
        _, width, _, _ = glyph(names, character)
        x = 160 - (width + 40) // 2
        return [(character, x, 54, 0x39dc), (17, x + width + 9, 54, 0x39f9)]
    slot = 14 if state["winner_word"] == state["characters"][0] else 15
    _, width, _, _ = glyph(names, slot)
    return [(slot, 160 - width // 2, 54, 0x3a32)]


def replay(names, state, before):
    assert len(before) == 65536
    after, coverage, runs = bytearray(before), bytearray(65536), []
    for slot, x, y, caller in layout(names, state):
        offset, width, height, source = glyph(names, slot)
        assert x >= 0 and x + width <= 320 and y + height <= 200
        mask, equal = bytearray(65536), 0
        for row in range(height):
            for col in range(width):
                value = source[2 + row * width + col]
                if value & 15:
                    at = (y + row) * 320 + x + col
                    equal += after[at] == value | 0xa0
                    after[at], mask[at], coverage[at] = value | 0xa0, 1, 1
        runs.append({"slot": slot, "x": x, "y": y, "width": width, "height": height,
                     "caller_ip": caller, "source_si": offset, "source_sha256": digest(source),
                     "writes": sum(mask), "equal_writes": equal,
                     "source": source, "mask": bytes(mask), "after": bytes(after)})
    return bytes(after), bytes(coverage), runs


def replay_snapshot(original, snapshot, sources, under_indices, under_mask):
    names=(original/"NAME.XBB").read_bytes()
    assert digest(names)=="60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82"
    assert snapshot["complete"] and len(under_indices)==len(under_mask)==64000 and set(under_mask)<={0,1}
    runs=layout(names,snapshot["state"])
    assert len(runs)==len(snapshot["draws"])==len(sources)
    indices,coverage,replace=bytearray(under_indices),bytearray(under_mask),bytearray(64000)
    boxes=[]
    for (slot,x,y,caller),d,source in zip(runs,snapshot["draws"],sources):
        offset,width,height,expected=glyph(names,slot)
        assert source==expected and digest(source)==d["source_sha256"]
        assert (d["slot"],d["x"],d["y"],d["width"],d["height"],d["caller_ip"],d["source_si"],d["palette"])==(slot,x,y,width,height,caller,offset,0xa0)
        for row in range(height):
            for col in range(width):
                value=source[2+row*width+col]
                if value&15:
                    at=(y+row)*320+x+col
                    indices[at],coverage[at],replace[at]=value|0xa0,1,1
        boxes.append((x,y,x+width,y+height))
    return bytes(indices),bytes(coverage),bytes(replace),boxes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--partial", action="store_true", help="explicitly verify completed groups from a failed or running experiment")
    args = parser.parse_args()
    root = args.output
    names = (args.original_root / "NAME.XBB").read_bytes()
    assert digest(names) == "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82"
    if args.partial:
        records = [json.loads(p.read_text()) for p in sorted(root.glob("victory-??.json"))]
        assert records
    else:
        receipt = json.loads((root / "receipt.json").read_text())
        assert receipt["script_sha256"] == digest((root / "victory_draw_receipt.go").read_bytes())
        assert receipt["inputs"]["NAME.XBB"] == digest(names)
        assert not receipt["unimplemented"]
        records = receipt["records"]
        assert len(records) == receipt.get("requested_messages", 2)
        for refresh in receipt.get("hud_refreshes", []):
            base = root / refresh["fixture"]
            read_refresh = lambda suffix: Path(str(base) + suffix).read_bytes()
            before = read_refresh(".before.idx")
            bitmap = read_refresh(".bitmap")
            last_copy = read_refresh(".last-copy.idx")
            prefix = expected_source(args.original_root,0,refresh["state"]["round_index"]) + expected_source(args.original_root,2,refresh["state"]["round_index"])
            assert len(prefix)==2884 and before[:2884]==prefix and before[2884:]==last_copy[2884:]
            if "setup_base_matches_last_copy" in refresh:
                assert refresh["setup_base_matches_last_copy"] and read_refresh(".setup-before.idx")==last_copy
            assert reconstruct(args.original_root, refresh["hud_state"]) == bytes(v & 15 for v in bitmap)
            after = bytearray(before)
            for i,v in enumerate(bitmap):
                if v: after[refresh["state"]["crtc_rows"]*320+i]=v|0xa0
            assert bytes(after) == read_refresh(".after.idx")
            assert digest(after) == refresh["after_sha256"]
            if "setup_base_matches_last_copy" in refresh:
                mask=bytearray(64000)
                mask[:2884]=bytes([1])*2884
                for i,v in enumerate(bitmap):
                    if v:mask[refresh["state"]["crtc_rows"]*320+i]=1
                assert read_refresh(".setup.mask")==mask
    results, files = [], {}
    for record in records:
        stem = record["fixture"]
        read = lambda suffix: (root / (stem + suffix)).read_bytes()
        before = read(".before.vram")
        if "base_matches_last_copy" in record: assert record["base_matches_last_copy"]
        after, mask, runs = replay(names, record["state"], before)
        assert after == read(".after.vram") and mask == read(".mask")
        assert digest(before) == record["before_sha256"] and digest(after) == record["after_sha256"]
        assert len(runs) == len(record["draws"])
        prior = before
        for index, (run, observed) in enumerate(zip(runs, record["draws"])):
            base = root / f"{stem}-draw-{index:02d}"
            for key in ("slot", "x", "y", "width", "height", "caller_ip", "source_si", "source_sha256", "writes", "equal_writes"):
                assert observed[key] == run[key], (stem, index, key)
            assert observed["palette"] == 0xa0
            for suffix, expected in [(".source", run["source"]), (".before.vram", prior),
                                     (".after.vram", run["after"]), (".mask", run["mask"])]:
                assert Path(str(base) + suffix).read_bytes() == expected, (stem, index, suffix)
            prior = run["after"]
        scanout = json.loads(read(".scanout.json"))
        start, pitch, height = geometry(scanout["crtc"])
        assert (start, pitch, height) == (scanout["start_byte"], scanout["pitch_byte"], scanout["height"])
        visible = b"".join(after[start + y * pitch:start + y * pitch + 320] for y in range(height))
        assert visible == read(".display.idx") and digest(visible) == record["display_sha256"]
        palette = json.loads(read(".palette.json"))
        image = Image.new("RGB", (320, height))
        image.putdata([tuple(palette[v]) for v in visible])
        image.save(root / (stem + ".original-display.png"))
        results.append({"fixture": stem, "winner_word": record["state"]["winner_word"],
                        "slots": [run["slot"] for run in runs], "coverage": sum(mask),
                        "equal_writes": sum(run["equal_writes"] for run in runs),
                        "display_height": height, "start_row": start // 320})
        for path in root.glob(stem + ".*"):
            if path.is_file():
                files[path.name] = digest(path.read_bytes())
        for path in root.glob(stem + "-draw-*"):
            if path.is_file():
                files[path.name] = digest(path.read_bytes())
    result = {"kind": "independent original victory source, STOSB coverage and visible display replay",
              "partial": args.partial, "records": results, "files": files,
              "script_sha256": digest(Path(__file__).read_bytes()),
              "dependencies": {n: digest(Path(__file__).with_name(n).read_bytes()) for n in ("display_reference.py","hud_reference.py","round_reference.py")},
              "limits": "normal sampled victory groups only; no HD, all-mode, draw-game or special-branch dynamic acceptance"}
    if not args.partial:
        result["hud_refreshes"] = len(receipt.get("hud_refreshes", []))
        for path in root.glob("hud-refresh-*"):
            if path.is_file(): files[path.name] = digest(path.read_bytes())
    name = "victory-reference-partial.json" if args.partial else "victory-reference.json"
    (root / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
