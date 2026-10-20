"""獨立核對十一人介面擷取、BIGFIG 肖像與原生控制收據。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.output
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = json.loads((root / "receipt.json").read_text())
    assert receipt["scope"] == "boss-selection"
    assert sha(root / "desktop_smoke.py") == receipt["script_sha256"]
    assert len(receipt["checks"]) == (5 if receipt["single"] else 6)
    archive = (args.original_root / "BIGFIG.XBB").read_bytes()
    assert len(archive) == 11 * 8689
    portraits = []
    top_rows = []
    for character, slug in [(8, "spider"), (9, "clown"), (10, "joe")]:
        name = "selection-" + slug + ".png"
        metadata = json.loads((root / (name + ".capture.json")).read_text())
        assert metadata["original_source"] == "selection-filtered-original"
        state = metadata["core"]["selection"]
        assert state["cursor"] == character and state["target"] == -1 and state["player"] == 0
        assert metadata["selected_width"] == 320 and metadata["selected_height"] == 200
        selected = (root / (name + ".selected.rgb")).read_bytes()
        indices = (root / (name + ".display.idx")).read_bytes()
        assert len(selected) == 64000 * 3 and len(indices) == 64000
        record = archive[character * 8689:(character + 1) * 8689]
        palette = [tuple((v << 2) | (v >> 4) for v in record[i:i + 3]) for i in range(0, 96, 3)]
        for y in range(89):
            for x in range(89):
                source = record[768 + y * 89 + x]
                pos = (15 + y) * 320 + 11 + x
                assert indices[pos] == source + 160, (name, x, y)
                assert selected[pos * 3:pos * 3 + 3] == bytes(palette[source]), (name, "palette", x, y)
        # 原版灰色頂列不應留下非法縮圖框的直線。
        assert len(set(selected[i:i + 3] for i in range(0, 320 * 3, 3))) == 1, name
        top_rows.append(selected[:960])
        image = Image.open(root / name).convert("RGB")
        assert image.size == (1120, 820)
        crop = image.crop((80, 64, 1040, 664))
        expected = Image.frombytes("RGB", (320, 200), selected).resize((960, 600), Image.Resampling.NEAREST)
        assert crop.tobytes() == expected.tobytes(), name
        portraits.append({"character": character, "pixels": 89 * 89, "capture": name})
    assert top_rows[0] == top_rows[1] == top_rows[2]
    battle = next(event["battle"] for event in receipt["events"] if "battle" in event)
    assert battle["core"]["mode"] == (0 if receipt["single"] else 1)
    assert battle["core"]["fighters"][0] == receipt["requested"][0]
    if not receipt["single"]:
        assert battle["core"]["fighters"][1] == receipt["requested"][1]
    assert "selection" not in battle["core"]
    files = {p.name: sha(p) for p in root.iterdir() if p.is_file() and
             (p.suffix == ".png" or ".png." in p.name or p.name in ("receipt.json", "desktop_smoke.py"))}
    result = {"kind": "independent original portrait and filtered native selection comparison",
              "script_sha256": sha(Path(__file__)), "portraits": portraits,
              "all_portraits_match_original": True, "invalid_top_border_absent": True,
              "native_viewport_matches_selected_rgb": True, "files": files,
              "limits": "sampled normal selection and basic controls; no complete single-player progression or physical gamepad acceptance"}
    (root / "boss-comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": root.name, "portraits": len(portraits), "passed": True}))


if __name__ == "__main__":
    main()
