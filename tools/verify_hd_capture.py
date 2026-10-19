"""在 Pillow Docker 內核對原生同狀態擷取，不修改遊戲或 HD 美術。"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.output
    for path in root.glob("*.png"):
        with Image.open(path) as image:
            image.verify()
    names = ["original-paused.png", "hd-paused.png", "hd-restored.png"]
    raw = [(root / (name + ".idx")).read_bytes() for name in names]
    palettes = [json.loads((root / (name + ".palette.json")).read_text()) for name in names]
    assert raw[0] == raw[1] == raw[2] and len(raw[0]) == 64000
    assert palettes[0] == palettes[1] == palettes[2]
    images = [Image.open(root / name).convert("RGB") for name in names]
    assert all(image.size == (1120, 820) for image in images)
    preserved, changed = 0, 0
    for y in range(200):
        for x in range(320):
            value = raw[0][y * 320 + x]
            expected = tuple(palettes[0][value])
            for dy in range(3):
                for dx in range(3):
                    position = (80 + x * 3 + dx, 64 + y * 3 + dy)
                    original, hd, restored = [image.getpixel(position) for image in images]
                    assert original == expected, (x, y, original, expected)
                    assert hd == restored, (x, y, "HD toggle is not reproducible")
                    if y < 48 or value >= 128:
                        assert original == hd, (x, y, "foreground changed")
                        preserved += 1
                    changed += hd != original
    assert changed > 200000, changed
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {"kind": "native GPU same-state screenshot comparison; background slice only",
               "source_pixels_sha256": hashlib.sha256(raw[0]).hexdigest(),
               "preserved_hud_and_high_palette_pixels": preserved,
               "changed_background_output_pixels": changed,
               "hd_toggle_identical_gameplay_area": True,
               "files": {name: sha(root / name) for name in names},
               "script_sha256": sha(Path(__file__)),
               "limits": "not physical gamepad, CRTC hardware parity or complete character HD"}
    (root / "comparison.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
