"""Docker 內準備本機 HD 背景素材；只複製原 PNG，不改圖。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    p = Path("/project")
    args.output.mkdir(exist_ok=False)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    ref = Image.open(p / "workplace/hd-source-probe-v3/I2.XGB.png")
    assert ref.mode == "P" and ref.size == (480, 204)
    pixels = ref.tobytes()
    assert sha(pixels) == "eb1207239c06a0e06cd9ecbb697b4cf7e1421c4dd3e6e2a6794774246eafeb15"
    palette = bytes(ref.getpalette()[:128 * 3])
    hd = p / "workplace/hd-layers/rooftop-layer.png"
    assert Image.open(hd).size == (1923, 818)
    shutil.copyfile(hd, args.output / "rooftop.png")
    (args.output / "reference.idx").write_bytes(pixels)
    (args.output / "palette.rgb").write_bytes(palette)
    record = {"version": 1, "kind": "rooftop-background-study", "scene": 4,
              "source": "I2.XGB", "source_sha256": sha((p / "workplace/orig/I2.XGB").read_bytes()),
              "width": 480, "height": 204,
              "reference_file": "reference.idx", "reference_sha256": sha(pixels),
              "palette_file": "palette.rgb", "palette_sha256": sha(palette),
              "image_file": "rooftop.png", "image_sha256": sha(hd.read_bytes()),
              "image_width": 1923, "image_height": 818,
              "evidence": ["workplace/hd-frame-single-v2/receipt.json", "workplace/hd-frame-versus-v2/receipt.json"]}
    (args.output / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
