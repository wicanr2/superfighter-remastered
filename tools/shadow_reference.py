"""從原檔獨立重組陰影寫入，包含同值覆蓋及原版裁切分支。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay_snapshot(original_root, snapshot, under_indices, under_mask):
    source_path = original_root / "SHADOW.XLP"
    source = source_path.read_bytes()
    expected_sha = "a25f777105cc86468c91111152e8ef10dd4911d9b150e3c1a1020e21b7590bf1"
    assert sha(source_path) == expected_sha and len(source) == 533
    assert snapshot["complete"] and len(snapshot["draws"]) == 2
    assert len(under_indices) == len(under_mask) == 64000 and set(under_mask) <= {0, 1}
    indices, mask, replaced = bytearray(under_indices), bytearray(under_mask), bytearray(64000)
    clips = []
    camera = snapshot["camera_x"]
    assert 0 <= camera <= 159
    for player, draw in enumerate(snapshot["draws"]):
        x, left, right = draw["x"], draw["left_clip"], draw["right_clip"]
        assert draw["player"] == player and draw["y"] == 178 and draw["source_sha256"] == expected_sha
        assert -255 <= x <= 319 and left == max(-x, 0)
        end, bound = (x + camera + 61) & 65535, (camera + 319) & 65535
        assert right == ((end - bound) & 255 if end > bound else 0)
        count = (59 - left - right - int(left > 59)) & 255
        if count & 128:
            clips.append(None)
            continue
        assert count and left + count <= 59 and max(x, 0) + count <= 320
        clips.append((max(x, 0), max(x, 0) + count))
        for row in range(9):
            for column in range(count):
                value = source[2 + row * 59 + left + column]
                if value:
                    at = (178 + row) * 320 + max(x, 0) + column
                    indices[at], mask[at], replaced[at] = value | 0xa0, 1, 1
    return bytes(indices), bytes(mask), bytes(replaced), clips


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    source_path = args.project / "workplace/orig/SHADOW.XLP"
    source = source_path.read_bytes()
    assert sha(source_path) == "a25f777105cc86468c91111152e8ef10dd4911d9b150e3c1a1020e21b7590bf1"
    assert len(source) == 533 and source[:2] == bytes([59, 9]) and set(source[2:]) == {0, 7}
    receipt_path = args.evidence / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    assert receipt["script_sha256"] == sha(args.evidence / "shadow_draw_receipt.go")
    assert receipt["inputs"]["SHADOW.XLP"] == sha(source_path)
    assert not receipt["unimplemented"]
    assert receipt["geometry_failures"] == receipt["pixel_failures"] == receipt["mask_failures"] == 0
    palette_bytes = (args.project / "workplace/orig/BOARD.COL").read_bytes()
    expected_color = [(value << 2) | (value >> 4) for value in palette_bytes[21:24]]
    results = []
    for record in receipt["records"]:
        draw = record["draw"]
        assert draw["source_sha256"] == sha(source_path)
        assert draw["player"] in (0, 1) and draw["y"] == 178
        left, right = max(-draw["x"], 0), max(draw["x"] + 61 - 319, 0)
        assert (left, right) == (draw["left_clip"], draw["right_clip"])
        count = (59 - left - right - int(left > 59)) & 255
        visible = -1 if count & 128 else count
        assert visible == draw["visible_width"] and visible != 0
        assert record["pixel_differences"] == record["mask_differences"] == 0
        if not record.get("fixture"):
            continue
        stem = record["fixture"]
        before = (args.evidence / (stem + ".before.idx")).read_bytes()
        after = (args.evidence / (stem + ".after.idx")).read_bytes()
        mask = (args.evidence / (stem + ".mask")).read_bytes()
        assert len(before) == len(after) == len(mask) == 64000
        expected, coverage = bytearray(before), bytearray(64000)
        equal = 0
        if visible > 0:
            assert left + visible <= 59
            for row in range(9):
                for column in range(visible):
                    value = source[2 + row * 59 + left + column]
                    if value:
                        at = (178 + row) * 320 + max(draw["x"], 0) + column
                        equal += expected[at] == value | 0xa0
                        expected[at], coverage[at] = value | 0xa0, 1
        assert expected == after and coverage == mask, stem
        assert sum(coverage) == record["writes"] and equal == record["equal_value_writes"]
        palette = json.loads((args.evidence / (stem + ".palette.json")).read_text())
        assert palette[0xa7] == expected_color
        results.append({"fixture": stem, "draw": draw, "equal_value_writes": equal,
                        "files": {suffix: sha(args.evidence / (stem + suffix))
                                  for suffix in [".before.idx", ".after.idx", ".mask", ".palette.json"]}})
    records = receipt["records"]
    features = {"left_clip": sum(x["draw"]["left_clip"] > 0 for x in records),
                "left_boundary": sum(x["draw"]["x"] == 0 for x in records),
                "right_clip": sum(x["draw"]["right_clip"] > 0 for x in records),
                "skipped_draws": sum(x["draw"]["visible_width"] < 0 for x in records),
                "equal_value_writes": sum(x["equal_value_writes"] for x in records),
                "players": sorted({x["draw"]["player"] for x in records})}
    assert features["left_boundary"] and features["right_clip"] and features["equal_value_writes"] and features["players"] == [0, 1], features
    result = {"kind": "independent original shadow-source replay; not HD acceptance", "inputs": receipt["inputs"],
              "draws": len(records), "fixtures": results, "features": features, "palette_a7": expected_color,
              "receipt_sha256": sha(receipt_path), "script_sha256": sha(Path(__file__)), "python": sys.version,
              "limits": "normal left boundary reaches X=0; negative-X clipping and skipped draws are static branches without dynamic samples"}
    (args.evidence / "reference.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"draws": len(records), "fixtures": len(results), "features": features, "palette_a7": expected_color}))


if __name__ == "__main__":
    main()
