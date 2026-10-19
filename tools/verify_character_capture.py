"""在 Pillow Docker 內獨立重組原生六層收據並核對同狀態 HD 擷取。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_frame(root, name, reference):
    base = root / name
    raw = Path(str(base) + ".idx").read_bytes()
    palette = json.loads(Path(str(base) + ".palette.json").read_text())
    frame = json.loads(Path(str(base) + ".frame.json").read_text())
    assert len(raw) == 64000 and len(palette) == 256
    assert frame["layers_complete"] and len(frame["layers"]) == 6
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
        if "sprite" in metadata:
            players.append(metadata["sprite"]["player"])
        for i, written in enumerate(coverage):
            if written:
                reconstructed[i], owners[i] = indices[i], ordinal
        layers.append((metadata, indices, coverage))
    assert sorted(players) == [0, 1]
    assert bytes(reconstructed) == raw, (name, "six-layer replay differs from original framebuffer")
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
        read_frame(root, name, reference)
        replayed.append(name)
    assert len(replayed) >= 7, replayed
    names = ["original-paused.png", "hd-paused.png", "hd-restored.png"]
    frames = [read_frame(root, name, reference) for name in names]
    raw, palette, metadata, layers, owners, original = frames[0]
    assert all(frame[:3] == frames[0][:3] for frame in frames[1:])
    expected = original_image(raw, palette)
    assert viewport(original).tobytes() == expected.tobytes()
    hd, restored = frames[1][-1], frames[2][-1]
    assert viewport(hd).tobytes() == viewport(restored).tobytes()
    changed_actor, changed_background, preserved_last_raster = 0, 0, 0
    changed_top_background = 0
    for i, owner in enumerate(owners):
        x, y = i % 320, i // 320
        for dy in range(3):
            for dx in range(3):
                position = (80 + x * 3 + dx, 64 + y * 3 + dy)
                a, b = original.getpixel(position), hd.getpixel(position)
                if owner == 5:
                    assert a == b, (x, y, "last original raster write was covered")
                    preserved_last_raster += 1
                if owner in (2, 4):
                    changed_actor += a != b
                if owner == 0:
                    changed_background += a != b
                    if y < 48:
                        changed_top_background += a != b
    assert changed_actor > 3000, changed_actor
    assert changed_background > 100000, changed_background
    assert changed_top_background > 1000, changed_top_background
    assert preserved_last_raster > 1000, preserved_last_raster
    missing_checked = None
    if (root / "missing-pose-original.png").exists():
        missing = read_frame(root, "missing-pose-original.png", reference)
        assert viewport(missing[-1]).tobytes() == original_image(missing[0], missing[1]).tobytes()
        missing_checked = True
    if args.require_missing:
        assert missing_checked, "missing-pose capture required"
    receipt = {"kind": "native six-layer independent replay and same-state character GPU capture",
               "replayed_complete_frames": replayed,
               "original_and_hd_source_state_identical": True,
               "restored_hd_viewport_identical": True,
               "missing_pose_entire_viewport_original": missing_checked,
               "changed_original_actor_output_pixels": changed_actor,
               "changed_background_output_pixels": changed_background,
               "changed_top_background_output_pixels": changed_top_background,
               "preserved_last_raster_output_pixels": preserved_last_raster,
               "files": {path.name: digest(path) for path in root.iterdir()
                         if path.is_file() and (path.suffix in (".png", ".idx", ".mask") or path.name.endswith((".frame.json", ".palette.json")))},
               "script_sha256": digest(Path(__file__)),
               "limits": "sampled Jaan/Frank poses; not full animation, HD HUD, physical gamepads or CRTC hardware parity"}
    (root / "comparison.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "files"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
