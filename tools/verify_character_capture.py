"""在 Pillow Docker 內獨立重組原生六層收據並核對同狀態 HD 擷取。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from hud_reference import reconstruct
from shadow_reference import replay_snapshot


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_frame(root, name, reference, original_root=None):
    base = root / name
    raw = Path(str(base) + ".idx").read_bytes()
    palette = json.loads(Path(str(base) + ".palette.json").read_text())
    frame = json.loads(Path(str(base) + ".frame.json").read_text())
    assert len(raw) == 64000 and len(palette) == 256
    assert frame["layers_complete"] and 6 <= len(frame["layers"]) <= 38 and len(frame["layers"]) % 2 == 0
    assert frame["layers"][0]["background"]
    layers, owners, reconstructed = [], bytearray(64000), bytearray(64000)
    players = []
    for ordinal, metadata in enumerate(frame["layers"]):
        indices = Path(str(base) + f".layer-{ordinal:02d}.idx").read_bytes()
        coverage = Path(str(base) + f".layer-{ordinal:02d}.mask").read_bytes()
        assert len(indices) == len(coverage) == 64000
        assert all(value in (0, 1) for value in coverage)
        if ordinal == 0:
            assert all(coverage)
            camera = frame["camera_x"]
            expected = b"".join(reference[y * 480 + camera:y * 480 + camera + 320] for y in range(200))
            assert indices == expected, (name, "pure background differs from original source")
        if "sprite" in metadata and not metadata["sprite"].get("effect"):
            players.append(metadata["sprite"]["player"])
        for i, written in enumerate(coverage):
            if written:
                reconstructed[i], owners[i] = indices[i], ordinal
        layers.append((metadata, indices, coverage))
    assert sorted(players) == [0, 1]
    assert bytes(reconstructed) == raw, (name, "six-layer replay differs from original framebuffer")
    if frame.get("shadows"):
        assert original_root is not None
        shadow = frame["shadows"]
        assert shadow["counter"] == frame["counter"] and shadow["camera_x"] == frame["camera_x"]
        expected, mask, _, _ = replay_snapshot(original_root, shadow,
            Path(str(base) + ".shadow-under.idx").read_bytes(), Path(str(base) + ".shadow-under.mask").read_bytes())
        assert expected == layers[1][1] and mask == layers[1][2], (name, "shadow source does not replay first raster layer")
    if frame.get("hud"):
        assert original_root is not None, "HUD source directory required"
        hud = frame["hud"]
        assert hud["complete"]
        bitmap_path = Path(str(base) + ".hud.bitmap")
        bitmap = bitmap_path.read_bytes()
        assert len(bitmap) == 10240 and digest(bitmap_path) == hud["bitmap_sha256"]
        assert reconstruct(original_root, hud["state"]) == bytes(value & 15 for value in bitmap)
        under_indices = Path(str(base) + ".hud-under.idx").read_bytes()
        under_mask = Path(str(base) + ".hud-under.mask").read_bytes()
        assert len(under_indices) == len(under_mask) == 64000 and set(under_mask) <= {0, 1}
        before = bytearray(64000)
        for _, indices, mask in layers[:-1]:
            for i, written in enumerate(mask):
                if written:
                    before[i] = indices[i]
        for i, written in enumerate(under_mask):
            if written:
                before[i] = under_indices[i]
        for i, value in enumerate(bitmap):
            if value:
                before[hud["state"]["crtc_rows"] * 320 + i] = value | 0xa0
        assert before == raw, (name, "pre-HUD layers plus original HUD differ from final original pixels")
    image = Image.open(base).convert("RGB")
    assert image.size == (1120, 820)
    return raw, palette, frame, layers, owners, image


def viewport(image):
    return image.crop((80, 64, 1040, 664))


def original_image(raw, palette):
    image = Image.new("RGB", (320, 200))
    image.putdata([tuple(palette[value]) for value in raw])
    return image.resize((960, 600), Image.Resampling.NEAREST)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--require-missing", action="store_true")
    parser.add_argument("--original-root", type=Path)
    parser.add_argument("--require-hud", action="store_true")
    args = parser.parse_args()
    root = args.output
    reference = (args.background / "reference.idx").read_bytes()
    assert len(reference) == 480 * 204
    for path in root.glob("*.png"):
        with Image.open(path) as image:
            image.verify()
    replayed = []
    for path in sorted(root.glob("*.png.frame.json")):
        name = path.name.removesuffix(".frame.json")
        if name == "capture.png":
            continue
        read_frame(root, name, reference, args.original_root)
        replayed.append(name)
    assert len(replayed) >= 7, replayed
    names = ["original-paused.png", "hd-paused.png", "hd-restored.png"]
    frames = [read_frame(root, name, reference, args.original_root) for name in names]
    raw, palette, metadata, layers, owners, original = frames[0]
    assert all(frame[:3] == frames[0][:3] for frame in frames[1:])
    expected = original_image(raw, palette)
    assert viewport(original).tobytes() == expected.tobytes()
    hd, restored = frames[1][-1], frames[2][-1]
    assert viewport(hd).tobytes() == viewport(restored).tobytes()
    changed_actor, changed_background, preserved_last_raster = 0, 0, 0
    changed_hud = 0
    hud = metadata.get("hud")
    if args.require_hud:
        assert hud is not None, "native HD HUD capture required"
    hud_rects = []
    if hud:
        import struct
        source = (args.original_root / "NAME.XBB").read_bytes()
        widths = [source[struct.unpack_from("<H", source, character * 2)[0]] for character in hud["state"]["characters"]]
        board = (args.original_root / "BOARD.XBB").read_bytes()
        player_boxes = []
        for left, right in [(0, 18), (302, 320)]:
            points = [(i % 320, i // 320) for i, value in enumerate(board) if value and left <= i % 320 < right]
            player_boxes.append((min(x for x, y in points), min(y for x, y in points), max(x for x, y in points) + 1, max(y for x, y in points) + 1))
        hud_rects = [(145, 9, 175, 24), *player_boxes,
                     (18, 12, 143, 20), (177, 12, 302, 20),
                     (18, 21, 18 + widths[0], 32), (302 - widths[1], 21, 302, 32)]
    bodies = {i for i, (layer, _, _) in enumerate(layers) if layer.get("sprite") and not layer["sprite"].get("effect")}
    changed_top_background = 0
    for i, owner in enumerate(owners):
        x, y = i % 320, i // 320
        hud_y = y - hud["state"]["crtc_rows"] if hud else y
        hud_field = any(left <= x < right and top <= hud_y < bottom for left, top, right, bottom in hud_rects)
        for dy in range(3):
            for dx in range(3):
                position = (80 + x * 3 + dx, 64 + y * 3 + dy)
                a, b = original.getpixel(position), hd.getpixel(position)
                if owner == len(layers) - 1 and not hud_field:
                    assert a == b, (x, y, "last original raster write was covered")
                    preserved_last_raster += 1
                if owner == len(layers) - 1 and hud_field:
                    changed_hud += a != b
                if owner in bodies:
                    changed_actor += a != b
                if owner == 0:
                    changed_background += a != b
                    if y < 48:
                        changed_top_background += a != b
    assert changed_actor > 3000, changed_actor
    assert changed_background > 100000, changed_background
    assert changed_top_background > 1000, changed_top_background
    if hud:
        assert changed_hud > 1000, changed_hud
    else:
        assert preserved_last_raster > 1000, preserved_last_raster
    missing_checked = None
    if (root / "missing-pose-original.png").exists():
        missing = read_frame(root, "missing-pose-original.png", reference, args.original_root)
        assert viewport(missing[-1]).tobytes() == original_image(missing[0], missing[1]).tobytes()
        missing_checked = True
    if args.require_missing:
        assert missing_checked, "missing-pose capture required"
    effect_counts = {}
    for label in ("effect", "frank-effect"):
        if not (root / f"hd-{label}-paused.png").exists():
            continue
        effect_names = [f"original-{label}-paused.png", f"hd-{label}-paused.png", f"hd-{label}-restored.png"]
        effects = [read_frame(root, name, reference, args.original_root) for name in effect_names]
        assert all(frame[:3] == effects[0][:3] for frame in effects[1:])
        original_effect = original_image(effects[0][0], effects[0][1])
        assert viewport(effects[0][-1]).tobytes() == original_effect.tobytes()
        assert viewport(effects[1][-1]).tobytes() == viewport(effects[2][-1]).tobytes()
        effect_layers = {i for i, (layer, _, _) in enumerate(effects[0][3]) if layer.get("sprite", {}).get("effect")}
        assert effect_layers
        effect_pixels = 0
        for i, owner in enumerate(effects[0][4]):
            if owner not in effect_layers:
                continue
            x, y = i % 320, i // 320
            for dy in range(3):
                for dx in range(3):
                    point = (80 + x * 3 + dx, 64 + y * 3 + dy)
                    effect_pixels += effects[0][-1].getpixel(point) != effects[1][-1].getpixel(point)
        assert effect_pixels > 20, effect_pixels
        effect_counts[label] = effect_pixels
    receipt = {"kind": "native ordered-layer independent replay and same-state character/effect GPU capture",
               "replayed_complete_frames": replayed,
               "original_and_hd_source_state_identical": True,
               "restored_hd_viewport_identical": True,
               "missing_pose_entire_viewport_original": missing_checked,
               "changed_original_actor_output_pixels": changed_actor,
               "changed_background_output_pixels": changed_background,
               "changed_top_background_output_pixels": changed_top_background,
               "changed_original_effect_output_pixels": effect_counts.get("effect"),
               "changed_original_frank_effect_output_pixels": effect_counts.get("frank-effect"),
               "changed_original_hud_output_pixels": changed_hud,
               "hud_underlay_and_original_source_replayed": bool(hud),
               "preserved_last_raster_output_pixels": preserved_last_raster,
               "files": {path.name: digest(path) for path in root.iterdir()
                         if path.is_file() and (path.suffix in (".png", ".idx", ".mask", ".bitmap") or path.name.endswith((".frame.json", ".palette.json")))},
               "script_sha256": digest(Path(__file__)),
               "limits": "sampled Jaan/Frank poses; not full animation, HD HUD, physical gamepads or CRTC hardware parity"}
    (root / "comparison.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "files"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
