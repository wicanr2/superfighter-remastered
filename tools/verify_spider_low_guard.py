"""以原檔獨立重組蜘蛛女原生低伏、移動回退及切換擷取。"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_character_capture import read_frame, original_image, viewport, source_y
from verify_victory_capture import check_sprite_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    p.add_argument("--original-root", type=Path, required=True)
    p.add_argument("--background", type=Path, required=True)
    a = p.parse_args()
    root = a.output
    receipt = json.loads((root / "receipt.json").read_text())
    assert receipt["scope"] == "spider-low-guard" and len(receipt["checks"]) == 4
    assert sha(root / "desktop_smoke.py") == receipt["script_sha256"]
    names = ["hd-paused.png", "original-paused.png", "hd-restored.png", "walk.png", "released.png"]
    reference = (a.background / "reference.idx").read_bytes()
    frames = {name: read_frame(root, name, reference, a.original_root) for name in names}
    sources = {name: check_sprite_sources(a.original_root, f[2]) for name, f in frames.items()}
    missing = receipt["expected_missing"]
    for name, f in frames.items():
        assert f[2]["hud"]["state"]["characters"] == [8, 4]
        assert {s["file"] for s in sources[name]} == {"SFMAN09.DAT", "SFMAN05.DAT"}
        assert all(not s["source_bank"] for s in sources[name])
        body = next(s for s in sources[name] if s["player"] == 0)
        idle = body["slot"] in (0, 1, 41)
        assert idle == (name != "walk.png"), (name, body)
        capture = json.loads((root / (name + ".capture.json")).read_text())
        expected_hd = not missing and name not in ("walk.png", "original-paused.png")
        assert capture["hd_active"] == expected_hd, name
        if not expected_hd:
            assert viewport(f[-1]).tobytes() == original_image(f[0], f[1], f[2]).tobytes(), name
    selected = [frames[name] for name in names[:3]]
    assert selected[0][:3] == selected[1][:3] == selected[2][:3]
    assert viewport(selected[0][-1]).tobytes() == viewport(selected[2][-1]).tobytes()
    events = {key: value for event in receipt["events"] for key, value in event.items()}
    for field in ("core", "presentation", "settings", "assigned"):
        assert events["paused"][field] == events["original"][field] == events["restored"][field], field
    assert all(events[key]["core"]["paused"] for key in ("paused", "original", "restored"))
    assert events["released"]["core"]["key_values"][0] == 0
    assert not any(events["walk"]["core"]["quick"])
    changed = {"spider": 0, "name": 0, "background": 0}
    if not missing:
        _, _, f, layers, owners, hd = selected[0]
        original = selected[1][-1]
        spider_layer = next(i for i, (m, _, _) in enumerate(layers)
                            if m.get("sprite", {}).get("player") == 0 and not m["sprite"].get("effect"))
        assert layers[spider_layer][0]["sprite"]["flags"] & 64, "P1 source must use normal original mirror"
        for i, owner in enumerate(owners):
            x, y = i % 320, i // 320
            physical_y = source_y(y, f)
            if physical_y is None:
                continue
            for dy in range(3):
                for dx in range(3):
                    at = (80+x*3+dx, physical_y+dy)
                    differs = hd.getpixel(at) != original.getpixel(at)
                    if owner == spider_layer:
                        changed["spider"] += differs
                    if owner == 0:
                        changed["background"] += differs
                    if 18 <= x < 75 and f["hud"]["state"]["crtc_rows"]+21 <= y < f["hud"]["state"]["crtc_rows"]+32:
                        changed["name"] += differs
        assert changed["spider"] > 1000 and changed["name"] > 100 and changed["background"] > 100000, changed
    result = {"kind": "independent original data, full layers, HUD, scanout and native GPU comparison",
              "captures": names, "sources": sources, "expected_missing": missing,
              "same_state_switch_unchanged": True, "restored_HD_identical": True,
              "unknown_walk_entire_frame_original": True, "released_idle_recovered": True,
              "changed_output_pixels": changed, "script_sha256": sha(Path(__file__)),
              "files": {p.name: sha(p) for p in root.iterdir() if p.is_file()
                        and (p.name in ("receipt.json", "desktop_smoke.py") or any(p.name.startswith(n) for n in names))},
              "limits": "Linux player1 low guard and one ordinary walk; static approved approximation, not full animation, WIN, other palettes, physical pads or OS hardware"}
    (root / "spider-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "sources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
