"""獨立核對正常比賽的選用原貌、即時原版與原生視窗擷取。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--partial", action="store_true", help="只檢查已完成擷取，不作完整比賽驗收")
    modes.add_argument("--win-markers", action="store_true", help="驗首勝與同狀態勝場切換，不作完整比賽驗收")
    args = parser.parse_args()
    root = args.output
    receipt = None
    expected_names = {
        "normal-battle", "knockout-0", "transition-0", "next-round",
        "knockout-1", "transition-1", "result-newspaper", "after-result-return",
    }
    if args.win_markers:
        expected_names = {"normal-battle", "knockout-0", "transition-0", "next-round", "win-hd", "win-original", "win-restored"}
    if not args.partial:
        assert not (root / "failure.json").exists(), "match has a failure receipt"
        receipt = json.loads((root / "receipt.json").read_text())
        assert receipt["knockout_rounds"] == ([0] if args.win_markers else [0, 1]), "required normal knockout rounds missing"
        assert receipt.get("scope", "complete-match-return") == ("first-round-win-marker" if args.win_markers else "complete-match-return")
        events = receipt["events"]
        names = [event["name"] for event in events]
        assert len(names) == len(set(names)) and set(names) == expected_names, names
        assert receipt["script_sha256"] == hashlib.sha256((root / "desktop_match_smoke.py").read_bytes()).hexdigest()
    records = []
    for path in sorted(root.glob("*.png.capture.json")):
        metadata = json.loads(path.read_text())
        stem = path.name.removesuffix(".capture.json")
        if stem == "capture.png":
            continue
        if receipt is not None:
            event = next(event for event in receipt["events"] if event["name"] + ".png" == stem)
            assert metadata["core"] == event["state"]["core"], (stem, "capture and event core differ")
        selected = Path(str(root / stem) + ".selected.rgb").read_bytes()
        live = Path(str(root / stem) + ".live.rgb").read_bytes()
        w, h = metadata["selected_width"], metadata["selected_height"]
        lw, lh = metadata["live_width"], metadata["live_height"]
        assert len(selected) == w * h * 3 and len(live) == lw * lh * 3
        selected_image = Image.frombytes("RGB", (w, h), selected)
        live_image = Image.frombytes("RGB", (lw, lh), live)
        selected_image.save(root / (stem + ".selected-original.png"))
        live_image.save(root / (stem + ".live-original.png"))
        native = Image.open(root / stem).convert("RGB")
        assert native.size == (1120, 820)
        viewport = native.crop((80, 64, 1040, 664))
        expected = selected_image.resize((960, 600), Image.Resampling.NEAREST)
        changed = sum(a != b for a, b in zip(viewport.getdata(), expected.getdata()))
        if not metadata["hd_active"]:
            assert changed == 0, (stem, "original fallback viewport differs from selected original", changed)
        if not metadata["core"]["battle"]:
            assert metadata["presentation_serial"] == 0 and metadata["original_source"] == "live-original"
            assert not metadata["hd_active"] and selected == live
        replayed_layers = 0
        suffixes = ["", ".capture.json", ".selected.rgb", ".live.rgb"]
        if metadata["presentation_serial"]:
            frame = json.loads((root / (stem + ".frame.json")).read_text())
            assert frame["serial"] == metadata["presentation_serial"] and frame["layers_complete"]
            original = (root / (stem + ".idx")).read_bytes()
            palette = json.loads((root / (stem + ".palette.json")).read_text())
            suffixes += [".frame.json", ".idx", ".palette.json"]
            assert len(original) == 64000 and len(palette) == 256
            replay = bytearray(64000)
            for index, _ in enumerate(frame["layers"]):
                indices = (root / (stem + f".layer-{index:02d}.idx")).read_bytes()
                mask = (root / (stem + f".layer-{index:02d}.mask")).read_bytes()
                suffixes += [f".layer-{index:02d}.idx", f".layer-{index:02d}.mask"]
                assert len(indices) == len(mask) == 64000 and set(mask) <= {0, 1}
                for at, covered in enumerate(mask):
                    if covered:
                        replay[at] = indices[at]
                replayed_layers += 1
            assert replay == original, (stem, "original layers do not replay")
            assert bytes(channel for pixel in original for channel in palette[pixel]) == selected
            if frame.get("hud"):
                suffixes += [".hud.bitmap", ".hud-under.idx", ".hud-under.mask"]
        records.append({"name": stem, "original_source": metadata["original_source"],
                        "core": metadata["core"], "hd_active": metadata["hd_active"],
                        "snapshot_age_steps": metadata["core"]["steps"] - metadata["presentation_steps"] if metadata["presentation_serial"] else None,
                        "live_equals_selected": selected == live, "native_pixels_changed_from_original": changed,
                        "original_layers_replayed": replayed_layers,
                        "files": {stem + suffix: hashlib.sha256((root / (stem + suffix)).read_bytes()).hexdigest() for suffix in suffixes},
                        "live_sha256": hashlib.sha256(live).hexdigest(), "selected_sha256": hashlib.sha256(selected).hexdigest()})
    assert records, "no native match captures"
    if receipt is not None:
        assert {record["name"] for record in records} == {name + ".png" for name in expected_names}
        for record in records:
            if record["name"] in {"result-newspaper.png", "after-result-return.png"}:
                assert not record["core"]["battle"], (record["name"], "still in battle")
    if args.win_markers:
        stems = ["win-hd.png", "win-original.png", "win-restored.png"]
        metadata = [json.loads((root / (stem + ".capture.json")).read_text()) for stem in stems]
        assert metadata[0]["core"] == metadata[1]["core"] == metadata[2]["core"]
        assert metadata[0]["core"]["paused"] and metadata[0]["hd_active"] and not metadata[1]["hd_active"] and metadata[2]["hd_active"]
        for suffix in [".idx", ".palette.json", ".frame.json", ".selected.rgb", ".live.rgb"]:
            sources = [(root / (stem + suffix)).read_bytes() for stem in stems]
            assert sources[0] == sources[1] == sources[2], ("paused source changed", suffix)
        images = [Image.open(root / stem).convert("RGB").crop((80, 64, 1040, 664)) for stem in stems]
        assert images[0].tobytes() == images[2].tobytes(), "restored HD differs"
        frame = json.loads((root / "win-hd.png.frame.json").read_text())
        state = frame["hud"]["state"]
        assert state["display_wins"] == [1, 0]
        rows = state["crtc_rows"]
        marker = (18 * 3, rows * 3, 28 * 3, (rows + 12) * 3)
        hd_marker, original_marker = images[0].crop(marker), images[1].crop(marker)
        changed = sum(a != b for a, b in zip(hd_marker.getdata(), original_marker.getdata()))
        gold_pixels = sum(pixel == (255, 209, 68) for pixel in hd_marker.getdata())
        assert gold_pixels >= 30, "HD thumb ink missing; background differences alone do not prove marker replacement"
        assert all(pixel != (255, 209, 68) for pixel in original_marker.getdata())
    result = {"kind": "native match source-selection and original viewport checks; not complete HD acceptance",
              "scope": "partial captures only" if args.partial else "normal first win and paused HD switch" if args.win_markers else "complete recorded match and return captures",
              "captures": records,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if args.win_markers:
        result["win_marker_region_changed_pixels"] = changed
        result["native_win_marker_gold_pixels"] = gold_pixels
    output_name = "comparison-partial.json" if args.partial else "comparison.json"
    (root / output_name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"scope": result["scope"], "captures": len(records),
                      "original_layers_replayed": sum(record["original_layers_replayed"] for record in records),
                      "native_win_marker_gold_pixels": result.get("native_win_marker_gold_pixels")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
