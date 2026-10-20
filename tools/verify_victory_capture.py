"""獨立核對正常勝利的原檔、完整圖層、WIN 圖像群組與原生字圖。"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from verify_character_capture import read_frame, original_image, viewport, source_y


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sprite_sources(original, frame):
    sources = []
    victory_files = ["AA", "BB", "CC", "EE", "FF", "GG", "HH", "II", "JJ", "DD", "KK"]
    for layer in frame["layers"]:
        sprite = layer.get("sprite")
        if not sprite:
            continue
        character, slot = sprite["character"], sprite["slot"]
        assert 0 <= character <= 10 and 0 <= slot < 72
        bank = sprite.get("source_bank", "")
        assert bank in ("", "victory"), bank
        if bank == "victory":
            name, table, payload = victory_files[character] + "WIN.FIG", 0x60, 0x180
            assert not sprite.get("effect")
        else:
            name, table, payload = f"SFMAN{character + 1:02d}.DAT", 0xb28, 0xc48
        data = (original / name).read_bytes()
        segment, offset = struct.unpack_from("<HH", data, table + slot * 4)
        start = payload + segment * 16 + offset
        assert payload <= start < len(data) - 2
        width, height = data[start:start + 2]
        end = start + 2 + (width + 1) // 2 * height
        assert width > 0 and height > 0 and end <= len(data)
        assert (width, height) == (sprite["width"], sprite["height"])
        assert hashlib.sha256(data[start:end]).hexdigest() == sprite["source_sha256"]
        sources.append({"player": sprite["player"], "file": name, "slot": slot,
                        "source_bank": bank, "source_sha256": sprite["source_sha256"]})
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--core", action="store_true")
    args = parser.parse_args()
    root = args.output
    receipt = json.loads((root / "receipt.json").read_text())
    attacker, player0 = receipt.get("attacker", 0), receipt.get("player0", 0)
    assert attacker in (0, 1) and 0 <= player0 <= 10
    winner = player0 if attacker == 0 else 4
    wins = [0, 0]
    wins[attacker] = 1
    reference = (args.background / "reference.idx").read_bytes()
    if args.core:
        assert receipt["paired"] and receipt["original_state_and_rgb_unchanged"]
        assert receipt["checks"] > 1000 and receipt["victory_cleared"]
        assert receipt["captures"] == receipt.get("pose_captures", []) + ["victory-frame", "after-victory"]
        names = receipt["captures"]
    else:
        assert receipt["scope"] == "first-victory-message" and receipt["knockout_rounds"] == [0]
        finish = receipt.get("round_finishes", {}).get("0", "knockout")
        assert finish in ("knockout", "time-expiry")
        names = ["normal-battle", finish + "-0", "transition-0", "victory-hd",
                 "victory-original", "victory-restored", "after-victory"]
        assert [event["name"] for event in receipt["events"]] == names
        names = [name + ".png" for name in names]
    frames = {name: read_frame(root, name, reference, args.original_root, image_required=not args.core)
              for name in names}
    sources = {name: check_sprite_sources(args.original_root, frame[2]) for name, frame in frames.items()}
    victory_name = "victory-frame" if args.core else "victory-hd.png"
    frame = frames[victory_name][2]
    victory = frame["victory"]
    assert victory["complete"] and victory["state"]["winner_word"] == winner | (attacker << 15)
    assert victory["state"]["characters"] == [player0, 4]
    assert [d["slot"] for d in victory["draws"]] == [winner, 17]
    assert any(s["player"] == attacker and s["source_bank"] == "victory" for s in sources[victory_name])
    final = frames["after-victory" if args.core else "after-victory.png"][2]
    assert final.get("victory") is None and final["hud"]["state"]["display_wins"] == wins
    assert final["hud"]["state"]["round_state"] == 0
    result = {"kind": "independent normal victory original-source and complete-layer replay",
              "captures": len(names), "sprite_sources": sources, "next_round_cleared": True,
              "winner_character": winner, "winner_player": attacker,
              "limits": "sampled normal first victory; special branches and complete victory animation remain separate"}
    if args.core:
        samples = receipt.get("pose_captures", [])
        result["pose_sources"] = {
            name: check_sprite_sources(args.original_root, read_frame(
                root, name, reference, args.original_root, image_required=False)[2]) for name in samples}
    if not args.core:
        modes = ["hd", "original", "restored"]
        group = [frames[f"victory-{mode}.png"] for mode in modes]
        assert group[0][:3] == group[1][:3] == group[2][:3]
        captures = [json.loads((root / f"victory-{mode}.png.capture.json").read_text()) for mode in modes]
        events = {event["name"]: event["state"] for event in receipt["events"]}
        snapshots = [events[f"victory-{mode}"] for mode in modes]
        for capture, snapshot in zip(captures, snapshots):
            for field in ("core", "hd_active", "hd_enabled"):
                assert capture[field] == snapshot[field], field
            assert capture["presentation_serial"] == snapshot["presentation"]["serial"]
        for field in ("core", "presentation", "settings", "assigned"):
            assert snapshots[0][field] == snapshots[1][field] == snapshots[2][field], field
        assert all(s["core"]["paused"] for s in snapshots)
        assert not snapshots[1]["hd_active"] and not snapshots[1]["hd_enabled"]
        assert viewport(group[1][-1]).tobytes() == original_image(group[1][0], group[1][1], group[1][2]).tobytes()
        assert viewport(group[0][-1]).tobytes() == viewport(group[2][-1]).tobytes()
        fallback = receipt["expected_victory_original"]
        result["expected_original_fallback"] = fallback
        changed = {}
        for mode, selected, snapshot in zip(modes, group, snapshots):
            base = root / f"victory-{mode}.png"
            if fallback or mode == "original":
                assert not snapshot["hd_active"]
                assert viewport(selected[-1]).tobytes() == original_image(selected[0], selected[1], selected[2]).tobytes()
                assert not Path(str(base) + ".victory-render-after.rgba").exists()
                continue
            assert snapshot["hd_enabled"] and snapshot["hd_active"] and "勝負文字" in snapshot["hd_reason"]
            before = Path(str(base) + ".victory-render-before.rgba").read_bytes()
            after = Path(str(base) + ".victory-render-after.rgba").read_bytes()
            assert len(before) == len(after) == 960 * 600 * 4
            screenshot = viewport(selected[-1]).tobytes()
            boxes = [(d["x"] * 3, source_y(d["y"], frame) - 64,
                      (d["x"] + d["width"]) * 3, source_y(d["y"], frame) - 64 + d["height"] * 3)
                     for d in victory["draws"]]
            pixels = gold = 0
            for i in range(960 * 600):
                at = i * 4
                x, y = i % 960, i // 960
                inside = any(left <= x < right and top <= y < bottom for left, top, right, bottom in boxes)
                if not inside:
                    assert before[at:at + 4] == after[at:at + 4], (mode, "victory text escaped source rectangles", x, y)
                assert after[at:at + 3] == screenshot[i * 3:i * 3 + 3], (mode, "GPU differs from screenshot")
                pixels += before[at:at + 4] != after[at:at + 4]
                gold += inside and after[at:at + 3] == bytes((255, 209, 68))
            assert pixels > 20 and gold > 10, (mode, pixels, gold)
            changed[mode] = {"native_text_changed_pixels": pixels, "solid_gold_pixels": gold, "rectangles": boxes}
        result["gpu_text_captures"] = changed
        result["paused_restoration_exact"] = True
    result["files"] = {p.name: sha(p) for p in root.iterdir() if p.is_file()
                       and p.name not in ("victory-comparison.json", "capture.png")
                       and not p.name.startswith("capture.png.")}
    result["script_sha256"] = sha(Path(__file__))
    result["dependencies"] = {name: sha(Path(__file__).with_name(name)) for name in
                              ("verify_character_capture.py", "victory_reference.py", "hud_reference.py",
                               "shadow_reference.py", "round_reference.py", "display_reference.py")}
    (root / "victory-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "sprite_sources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
