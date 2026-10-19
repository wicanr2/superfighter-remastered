"""獨立核對原版陰影來源與原生柔邊 alpha／實際 GPU 合成。"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from shadow_reference import replay_snapshot
from verify_character_capture import source_y


def verify_all(root, original_root):
    results = []
    for path in sorted(root.glob("*.png.shadow-render.json")):
        stem = path.name.removesuffix(".shadow-render.json")
        if stem == "capture.png":
            continue
        base = root / stem
        frame = json.loads(Path(str(base) + ".frame.json").read_text())
        snapshot = frame["shadows"]
        metadata = json.loads(path.read_text())
        assert snapshot["counter"] == frame["counter"] and snapshot["camera_x"] == frame["camera_x"]
        assert metadata == {"serial": frame["serial"], "width": 960, "height": 27, "x": 80, "y": source_y(178,frame)}
        indices, mask, replaced, clips = replay_snapshot(original_root, snapshot,
            Path(str(base) + ".shadow-under.idx").read_bytes(), Path(str(base) + ".shadow-under.mask").read_bytes())
        assert indices == Path(str(base) + ".layer-01.idx").read_bytes()
        assert mask == Path(str(base) + ".layer-01.mask").read_bytes()
        alpha = Path(str(base) + ".shadow-alpha.rgba").read_bytes()
        before = Path(str(base) + ".shadow-render-before.rgba").read_bytes()
        after = Path(str(base) + ".shadow-render-after.rgba").read_bytes()
        assert len(alpha) == len(before) == len(after) == 960 * 27 * 4
        expected = bytearray(len(alpha))
        individual = []
        for draw, clip in zip(snapshot["draws"], clips):
            field = bytearray(960 * 27)
            if clip is not None:
                for y in range(27):
                    v = ((y + .5) / 3 - 4.5) / 4.5
                    for x in range(clip[0] * 3, clip[1] * 3):
                        u = ((x + .5) / 3 - draw["x"] - 29.5) / 29.5
                        value = math.floor(128 * min(1, max(0, (1 - u * u - v * v) * 3)) + .5)
                        field[y * 960 + x] = value
                        at = (y * 960 + x) * 4 + 3
                        expected[at] = max(expected[at], value)
            individual.append(field)
        assert alpha == expected, (stem, "native alpha differs from independent geometry/max-overlap reconstruction")
        changed = 0
        for at in range(0, len(before), 4):
            a = alpha[at + 3]
            assert before[at + 3] == after[at + 3] == 255
            for channel in range(3):
                numerator = before[at + channel] * (255 - a)
                # RGBA8 quantization may choose either adjacent integer. Paused restoration remains exact.
                assert numerator // 255 <= after[at + channel] <= (numerator + 254) // 255, (stem, at, channel, a)
            changed += before[at:at + 3] != after[at:at + 3]
        assert changed > 200
        results.append({"name": stem, "original_shadow_pixels": sum(replaced), "gpu_darkened_pixels": changed,
                        "overlap_pixels": sum(a > 0 and b > 0 for a, b in zip(*individual)),
                        "files": {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                                  for file in root.glob(stem + ".shadow-*") if file.is_file()}})
    assert results, "no native shadow GPU captures"
    return {"kind": "shadow source, exact procedural alpha and black GPU compositing checks",
            "captures": results, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "limits": "RGBA8 blend quantization interval only; exact paused viewport restoration is checked separately"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--original-root", type=Path, required=True)
    args = parser.parse_args()
    result = verify_all(args.output, args.original_root)
    (args.output / "shadow-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"captures": len(result["captures"]), "overlap_captures": sum(x["overlap_pixels"] > 0 for x in result["captures"])}))


if __name__ == "__main__":
    main()
