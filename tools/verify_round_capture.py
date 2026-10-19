"""獨立核對開場原檔、完整圖層、原生文字窗口及暫停切換。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame, original_image, viewport


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--core", action="store_true")
    args = parser.parse_args()
    root = args.output
    reference = (args.background / "reference.idx").read_bytes()
    receipt = json.loads((root / "receipt.json").read_text())
    if args.core:
        fixtures = receipt["round_fixtures"]
        assert len(fixtures) == 66 and receipt["checks"] == 1508 and receipt["round_cleared_after_opening"]
        stages, widths, post_copy = set(), set(), 0
        for stem in fixtures:
            frame = read_frame(root, stem, reference, args.original_root, image_required=False)[2]
            s = frame["round_message"]
            stages.add(s["stage"])
            widths.add(s["width"])
            post_copy += s["stage"] == 1 and s["half_width"] == 4
        assert stages == {0, 1, 2, 3} and widths == set(range(8, 97, 8)) and post_copy == 1
        result = {"kind": "independent original opening sources and complete-layer replay; no native GUI claim",
                  "frames": len(fixtures), "stages": sorted(stages), "widths": sorted(widths), "post_copy": post_copy}
    else:
        assert receipt["scope"] == "round-opening" and len(receipt["checks"]) == 7
        names = [f"{label}-{mode}.png" for label in ("round-partial", "round", "fight") for mode in ("hd", "original", "restored")]
        names += ["after-opening.png"]
        frames = {name: read_frame(root, name, reference, args.original_root) for name in names}
        changed = {}
        for label in ("round-partial", "round", "fight"):
            hd, original, restored = [frames[f"{label}-{mode}.png"] for mode in ("hd", "original", "restored")]
            assert hd[:3] == original[:3] == restored[:3], (label, "source state changed")
            assert viewport(original[-1]).tobytes() == original_image(original[0], original[1]).tobytes()
            assert viewport(hd[-1]).tobytes() == viewport(restored[-1]).tobytes(), (label, "restoration differs")
            snapshots = [json.loads((root / f"{label}-{mode}.png.capture.json").read_text()) for mode in ("hd", "original", "restored")]
            assert snapshots[0]["core"] == snapshots[1]["core"] == snapshots[2]["core"]
            assert all(s["core"]["paused"] for s in snapshots)
            message = hd[2]["round_message"]
            assert (message["stage"] >= 2) == (label == "fight")
            assert message["width"] < 96 if label == "round-partial" else message["width"] == 96
            for mode in ("hd", "restored"):
                stem = root / f"{label}-{mode}.png"
                before = Path(str(stem) + ".round-render-before.rgba").read_bytes()
                after = Path(str(stem) + ".round-render-after.rgba").read_bytes()
                assert len(before) == len(after) == 960 * 600 * 4
                png = viewport(frames[stem.name][-1]).tobytes()
                pixels, gold = 0, 0
                for i in range(960 * 600):
                    at = i * 4
                    x, y = i % 960, i // 960
                    inside = message["x"] * 3 <= x < (message["x"] + message["width"]) * 3 and 168 <= y < 213
                    if not inside:
                        assert before[at:at + 4] == after[at:at + 4], (stem.name, "text escaped original reveal window", x, y)
                    assert after[at:at + 3] == png[i * 3:i * 3 + 3], (stem.name, "GPU capture differs from screenshot")
                    pixels += before[at:at + 4] != after[at:at + 4]
                    gold += inside and after[at:at + 3] == bytes((255, 209, 68))
                assert pixels > 20 and gold > 10, (stem.name, pixels, gold)
                changed[stem.name] = {"native_text_changed_pixels": pixels, "solid_gold_pixels": gold, "source_window": [message["x"], message["y"], message["width"], 15]}
        final = frames["after-opening.png"][2]
        assert final.get("round_message") is None and final.get("retained_background_rows", 0) == 0
        result = {"kind": "normal native opening source replay, GPU window containment and exact paused restoration",
                  "captures": len(names), "gpu_text_captures": changed, "limits": "first round; Wine is not physical Windows; no other messages or full-HD claim"}
    files = [f for f in root.iterdir() if f.is_file() and f.name not in ("comparison.json", "round-comparison.json", "capture.png") and not f.name.startswith("capture.png.")]
    result["files"] = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["dependencies"] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                              for name in ("verify_character_capture.py", "round_reference.py", "hud_reference.py", "shadow_reference.py")}
    (root / "round-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "gpu_text_captures")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
