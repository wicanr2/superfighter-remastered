"""獨立重組薩爾可夫正常視窗擷取，核對人物來源、姓名、切換與整格回退。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from verify_character_capture import read_frame, original_image, viewport, source_y
from verify_victory_capture import check_sprite_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--background", type=Path, required=True)
    args = parser.parse_args()
    root = args.output
    receipt = json.loads((root / "receipt.json").read_text())
    assert receipt["scope"] == "normal-sarkov" and len(receipt["checks"]) == 7
    assert sha(root / "desktop_smoke.py") == receipt["script_sha256"]
    reference = (args.background / "reference.idx").read_bytes()
    names = ["normal-versus.png", "hd-rooftop.png", "walk.png", "crouch.png",
             "jump.png", "punch.png", "hd-paused.png", "original-paused.png", "hd-restored.png"]
    frames = {name: read_frame(root, name, reference, args.original_root) for name in names}
    sources = {name: check_sprite_sources(args.original_root, frame[2]) for name, frame in frames.items()}
    for name, frame in frames.items():
        assert frame[2]["hud"]["state"]["characters"] == [1, 4], name
        assert {s["file"] for s in sources[name]} == {"SFMAN02.DAT", "SFMAN05.DAT"}, name
        assert all(not s["source_bank"] for s in sources[name]), name
    events = {key: value for event in receipt["events"] for key, value in event.items()}
    for label, slots in [("crouch", (14,)), ("jump", (19, 20, 21)), ("punch", (5, 9, 10))]:
        event = events["sarkov_" + label]
        assert event["presentation"]["actors"][0]["slot"] in slots, label
        assert not any(event["core"]["quick"]), label
    assert events["sarkov_walk"]["presentation"]["actors"][0]["x"] > events["normal_battle"]["presentation"]["actors"][0]["x"] + 4
    selected = [frames[name] for name in ("hd-paused.png", "original-paused.png", "hd-restored.png")]
    assert selected[0][:3] == selected[1][:3] == selected[2][:3]
    for field in ("core", "presentation", "settings", "assigned"):
        assert events["sarkov_paused"][field] == events["original"][field] == events["restored"][field], field
    assert all(events[key]["core"]["paused"] for key in ("sarkov_paused", "original", "restored"))
    assert viewport(selected[0][-1]).tobytes() == viewport(selected[2][-1]).tobytes()
    missing = receipt["expected_missing"]
    for name, frame in frames.items():
        capture = json.loads((root / (name + ".capture.json")).read_text())
        original = missing or name in ("normal-versus.png", "original-paused.png")
        assert capture["hd_active"] == (not original), name
        if original:
            assert viewport(frame[-1]).tobytes() == original_image(frame[0], frame[1], frame[2]).tobytes(), name
    raw, palette, frame, layers, owners, image = selected[0]
    name_source = (args.original_root / "NAME.XBB").read_bytes()
    at = struct.unpack_from("<H", name_source, 2)[0]
    assert tuple(name_source[at:at + 2]) == (88, 11)
    changed = {"player0": 0, "player1": 0, "background": 0, "name": 0}
    if not missing:
        original = selected[1][-1]
        body_layers = {i: metadata["sprite"]["player"] for i, (metadata, _, _) in enumerate(layers)
                       if metadata.get("sprite") and not metadata["sprite"].get("effect")}
        for i, owner in enumerate(owners):
            x, y = i % 320, i // 320
            physical_y = source_y(y, frame)
            if physical_y is None:
                continue
            for dy in range(3):
                for dx in range(3):
                    point = (80 + x * 3 + dx, physical_y + dy)
                    differs = image.getpixel(point) != original.getpixel(point)
                    if owner in body_layers:
                        changed["player" + str(body_layers[owner])] += differs
                    elif owner == 0:
                        changed["background"] += differs
                    if 18 <= x < 106 and frame["hud"]["state"]["crtc_rows"] + 21 <= y < frame["hud"]["state"]["crtc_rows"] + 32:
                        changed["name"] += differs
        assert changed["player0"] > 1000 and changed["player1"] > 1000, changed
        assert changed["background"] > 100000 and changed["name"] > 100, changed
    result = {"kind": "independent normal Sarorkov/Frank source, HUD and GPU capture comparison",
              "captures": names, "sprite_sources": sources, "expected_missing": missing,
              "all_original_layers_and_hud_replayed": True, "paused_original_state_identical": True,
              "restored_hd_viewport_identical": True, "changed_output_pixels": changed,
              "script_sha256": sha(Path(__file__)),
              "files": {p.name: sha(p) for p in root.iterdir() if p.is_file() and p.name != "sarkov-comparison.json"
                        and (p.name in ["receipt.json", "desktop_smoke.py"] or any(p.name.startswith(n) for n in names))},
              "limits": "sampled normal poses and palette; not all animations, WIN, shortcuts, physical gamepads or native OS hardware"}
    (root / "sarkov-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "sprite_sources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
