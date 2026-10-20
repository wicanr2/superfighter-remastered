"""在 Docker 內移除淺灰棋盤底，只改 alpha，保留原 RGB、尺寸及檔名。"""

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import zipfile

from PIL import Image


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_background(image, minimum=170, tolerance=24):
    """從既有透明點及外框連通到淺灰背景，不移除封閉的人物內部。"""
    assert image.mode == "RGBA"
    width, height = image.size
    rgba = image.tobytes()
    eligible = bytearray(width * height)
    removed = bytearray(width * height)
    queue = deque()
    for at in range(width * height):
        offset = at * 4
        red, green, blue, alpha = rgba[offset:offset + 4]
        neutral = min(red, green, blue) >= minimum and max(red, green, blue) - min(red, green, blue) <= tolerance
        eligible[at] = not alpha or neutral
        if not alpha or (neutral and (at < width or at >= width * (height - 1) or at % width in (0, width - 1))):
            removed[at] = 1
            queue.append(at)
    while queue:
        at = queue.popleft()
        x = at % width
        neighbors = []
        if x:
            neighbors.append(at - 1)
        if x + 1 < width:
            neighbors.append(at + 1)
        if at >= width:
            neighbors.append(at - width)
        if at + width < width * height:
            neighbors.append(at + width)
        for adjacent in neighbors:
            if eligible[adjacent] and not removed[adjacent]:
                removed[adjacent] = 1
                queue.append(adjacent)
    result = bytearray(rgba)
    changed = 0
    for at, is_background in enumerate(removed):
        if is_background:
            offset = at * 4 + 3
            changed += bool(result[offset])
            result[offset] = 0
    assert changed and any(result[3::4])
    # 前景及背景的 RGB 都維持原值，已存在的透明點也不回填。
    for channel in range(3):
        assert result[channel::4] == rgba[channel::4]
    assert all(new == old or new == 0 for old, new in zip(rgba[3::4], result[3::4]))
    return Image.frombytes("RGBA", image.size, bytes(result)), changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.input.is_dir() and args.output.parent.is_dir()
    assert args.output.parent.stat().st_uid == 1000
    assert not args.output.exists(), "輸出已存在，不覆寫"
    archive = args.output.with_suffix(".zip")
    assert not archive.exists()
    inputs = sorted(args.input.glob("*.png"))
    assert inputs
    before = {p.name: sha256(p) for p in inputs}
    args.output.mkdir()
    records = []
    for path in inputs:
        with Image.open(path) as image:
            result, changed = remove_background(image)
            destination = args.output / path.name
            result.save(destination, format="PNG")
            with Image.open(destination) as loaded:
                loaded.load()
                assert loaded.mode == "RGBA" and loaded.size == image.size
                assert loaded.tobytes() == result.tobytes()
            records.append({"file": path.name, "input_sha256": before[path.name],
                            "output_sha256": sha256(destination), "size": list(result.size),
                            "newly_transparent_pixels": changed, "rgb_unchanged": True,
                            "input_alpha_zero_pixels": image.getchannel("A").histogram()[0],
                            "output_alpha_zero_pixels": result.getchannel("A").histogram()[0]})
            print(path.name, changed, "background pixels removed", flush=True)
    assert before == {p.name: sha256(p) for p in inputs}, "原圖不應改變"
    manifest = {"kind": "alpha-only checkerboard removal", "script_sha256": sha256(Path(__file__)),
                "input_directory": str(args.input), "algorithm": {
                    "connectivity": 4, "minimum_rgb": 170, "maximum_rgb_spread": 24,
                    "seeds": "existing alpha-zero pixels and eligible border pixels",
                    "change": "connected background alpha becomes zero; RGB unchanged"},
                "user_authorized_python": True, "original_files_unchanged": True,
                "runtime_integration": False, "files": records}
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (args.output / "README.txt").write_text(
        "蜘蛛女透明 PNG\n\n"
        f"共 {len(records)} 張圖，沿用原檔名與尺寸，只改背景 alpha，不重畫、不縮放，也不更動 RGB。\n"
        "原始輸入檔案均未修改。逐檔雜湊與處理方式見 manifest.json。\n"
        "這份是去背素材，尚未接入遊戲；圖格數、檔名及姿勢仍須對照原版。\n",
        encoding="utf-8-sig", newline="\r\n")
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(args.output.iterdir()):
            info = zipfile.ZipInfo(path.name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist()) == len(records) + 2
    assert all(p.stat().st_uid == 1000 for p in args.output.iterdir())
    assert archive.stat().st_uid == 1000
    print(json.dumps({"archive": str(archive), "sha256": sha256(archive), "files": len(records)}))


if __name__ == "__main__":
    main()
