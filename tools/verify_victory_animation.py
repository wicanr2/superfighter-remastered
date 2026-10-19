"""核對兩側正常勝利姿態取樣、原檔圖層及第二人原生首勝。"""
import argparse
import hashlib
import json
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
    parser.add_argument("--core", action="store_true")
    parser.add_argument("--partial-native", action="store_true",
                        help="只核對失敗檔中的六張首勝及切換擷取，明示下一回合未驗，不產生完整通過收據")
    args = parser.parse_args()
    root = args.output
    if args.core and args.partial_native:
        parser.error("partial native evidence cannot be used as paired core acceptance")
    source_file = "failure.json" if args.partial_native else "receipt.json"
    receipt = json.loads((root / source_file).read_text())
    if args.partial_native:
        assert not (root / "receipt.json").exists()
        last = receipt["state"]
        assert last["hd_active"] and last["presentation"]["victory"]["complete"]
        winner = last["presentation"]["victory"]["state"]["winner_word"]
        assert winner & 0x7f00 == 0
        player = (winner >> 15) & 1
        characters = last["core"]["fighters"]
    else:
        player = receipt["attacker"]
        characters = [receipt.get("player0", 0), 4]
    assert player in (0, 1)
    character = characters[player]
    wins = [0, 0]
    wins[player] = 1
    reference = (args.background / "reference.idx").read_bytes()
    if args.core:
        assert receipt["paired"] and receipt["original_state_and_rgb_unchanged"] and receipt["victory_cleared"]
        assert receipt["script_sha256"] == sha(root / "victory_core_receipt.go")
        project = Path(__file__).parent.parent
        assert receipt["source_inputs"] and all(sha(project / name) == expected for name, expected in receipt["source_inputs"].items())
        names = receipt["captures"]
        assert set(names) == {*receipt["pose_captures"], "victory-frame", "after-victory"}
        assert len(names) == len(set(names)) and receipt["pose_trace"]
        assert all(row["complete"] and row["characters_selected"] for row in receipt["pose_trace"])
        serials = [row["serial"] for row in receipt["pose_trace"]]
        assert serials == sorted(set(serials))
    else:
        if not args.partial_native:
            assert receipt["scope"] == "first-victory-message" and receipt["knockout_rounds"] == [0]
        assert receipt["script_sha256"] == sha(root / "desktop_match_smoke.py")
        expected_original = False if args.partial_native else receipt["expected_victory_original"]
        names = [event["name"] + ".png" for event in receipt["events"]]
        finish = ("knockout" if "knockout-0.png" in names else "time-expiry") if args.partial_native else receipt["round_finishes"]["0"]
        assert finish in ("knockout", "time-expiry")
        expected_names = ["normal-battle.png", f"{finish}-0.png", "transition-0.png", "victory-hd.png",
                          "victory-original.png", "victory-restored.png"]
        assert names == expected_names + ([] if args.partial_native else ["after-victory.png"])
    frames = {name: read_frame(root, name, reference, args.original_root, image_required=not args.core) for name in names}
    sources = {name: check_sprite_sources(args.original_root, frame[2]) for name, frame in frames.items()}
    victory_name = "victory-frame" if args.core else "victory-hd.png"
    victory = frames[victory_name][2]["victory"]
    assert victory["complete"] and victory["state"]["winner_word"] & 255 == character
    assert [d["slot"] for d in victory["draws"]] == [character, 17]
    assert any(s["player"] == player and s["source_bank"] == "victory" for s in sources[victory_name])
    if not args.core:
        state = victory["state"]
        if finish == "knockout":
            assert state["health"][1 - player] == 0
        else:
            assert state["timer"] == 0 and 0 < state["health"][1 - player] < state["health"][player]
    if not args.partial_native:
        after = frames["after-victory" if args.core else "after-victory.png"][2]
        assert after.get("victory") is None and after["hud"]["state"]["display_wins"] == wins
        assert after["hud"]["state"]["round_state"] == 0
    unique = sorted({(s["player"], s["slot"], s["source_sha256"]) for values in sources.values()
                     for s in values if s["source_bank"] == "victory"})
    result = {"kind": "independent normal victory animation source samples and lifecycle",
              "attacker": player, "captures": len(names), "victory_sources": unique,
              "partial_native": args.partial_native, "full_scenario_complete": not args.partial_native,
              "next_round_cleared": None if args.partial_native else True,
              "limits": "requested normal first-victory samples; no all-mode or every-frame native animation claim"}
    if args.core:
        result["paired_core_checks"] = receipt["checks"]
        result["sampled_win_frames"] = len(receipt["pose_trace"])
    else:
        events = {event["name"]: event["state"] for event in receipt["events"]}
        assert events["normal-battle"]["hd_active"]
        if not args.partial_native:
            assert events["after-victory"]["hd_active"]
        group = [frames[f"victory-{mode}.png"] for mode in ("hd", "original", "restored")]
        assert group[0][:3] == group[1][:3] == group[2][:3]
        states = [events[f"victory-{mode}"] for mode in ("hd", "original", "restored")]
        for field in ("core", "presentation", "settings", "assigned"):
            assert states[0][field] == states[1][field] == states[2][field], field
        assert all(state["core"]["paused"] for state in states)
        assert viewport(group[1][-1]).tobytes() == original_image(group[1][0], group[1][1], group[1][2]).tobytes()
        assert viewport(group[0][-1]).tobytes() == viewport(group[2][-1]).tobytes()
        gpu = {}
        for mode, selected, state in zip(("hd", "original", "restored"), group, states):
            base = root / f"victory-{mode}.png"
            capture = json.loads(Path(str(base) + ".capture.json").read_text())
            for field in ("core", "hd_active", "hd_enabled"):
                assert capture[field] == state[field]
            if mode == "original" or expected_original:
                assert not state["hd_active"] and state["hd_enabled"] == (mode != "original")
                assert viewport(selected[-1]).tobytes() == original_image(selected[0], selected[1], selected[2]).tobytes()
                assert not Path(str(base) + ".victory-render-after.rgba").exists()
                continue
            assert state["hd_active"] and state["hd_enabled"] and "勝負文字" in state["hd_reason"]
            before = Path(str(base) + ".victory-render-before.rgba").read_bytes()
            output = Path(str(base) + ".victory-render-after.rgba").read_bytes()
            assert len(before) == len(output) == 960 * 600 * 4
            screenshot = viewport(selected[-1]).tobytes()
            frame = selected[2]
            boxes = [(d["x"] * 3, source_y(d["y"], frame) - 64, (d["x"] + d["width"]) * 3,
                      source_y(d["y"], frame) - 64 + d["height"] * 3) for d in victory["draws"]]
            changed = gold = 0
            for i in range(960 * 600):
                at = i * 4
                x, y = i % 960, i // 960
                inside = any(left <= x < right and top <= y < bottom for left, top, right, bottom in boxes)
                if not inside:
                    assert before[at:at + 4] == output[at:at + 4], (mode, x, y)
                assert output[at:at + 3] == screenshot[i * 3:i * 3 + 3]
                changed += before[at:at + 4] != output[at:at + 4]
                gold += inside and output[at:at + 3] == bytes((255, 209, 68))
            assert changed > 20 and gold > 10
            gpu[mode] = {"changed_pixels": changed, "gold_pixels": gold, "rectangles": boxes}
        result["gpu_text_captures"] = gpu
        result["expected_victory_original"] = expected_original
        result["paused_restoration_exact"] = True
    result["files"] = {p.name: sha(p) for p in root.iterdir() if p.is_file()
                       and p.name not in ("animation-comparison.json", "animation-comparison-partial.json", "capture.png")
                       and not p.name.startswith("capture.png.")}
    result["script_sha256"] = sha(Path(__file__))
    result["dependencies"] = {name: sha(Path(__file__).with_name(name)) for name in
                              ("verify_character_capture.py", "verify_victory_capture.py", "victory_reference.py",
                               "hud_reference.py", "shadow_reference.py", "round_reference.py", "display_reference.py")}
    if args.partial_native:
        result["kind"] = "independent partial native victory and paused switching; scenario remains incomplete"
        result["limits"] += "; next-round lifecycle not observed before failure deadline"
    output_name = "animation-comparison-partial.json" if args.partial_native else "animation-comparison.json"
    (root / output_name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "dependencies")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
