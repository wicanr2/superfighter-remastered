"""在有 Git 的 Docker 工具鏈中核對 README 的相對連結是否已納入版控。"""
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main():
    root = Path(__file__).resolve().parent.parent
    tracked = {name.decode() for name in subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"]).split(b"\0") if name}
    content = (root / "README.md").read_text()
    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content)
    checked = []
    missing = []
    for target in targets:
        url = urlsplit(target.strip("<>"))
        if url.scheme or not url.path:
            continue
        name = posixpath.normpath(unquote(url.path))
        if name not in tracked or not (root / name).is_file():
            missing.append(name)
        checked.append(name)
    if missing:
        raise SystemExit("README 指向未版控或不存在的檔案：\n" + "\n".join(sorted(set(missing))))
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
    print(f"README 連結通過：{len(checked)} 個相對連結，{len(images)} 張圖片；均已納入 Git。")


if __name__ == "__main__":
    main()
