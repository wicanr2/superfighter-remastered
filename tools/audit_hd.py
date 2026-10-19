"""Docker 內核對目前 HD 切片的來源、收據、文件入口與檔案擁有權。"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote


def main():
    root = Path("/project")
    os.chdir(root)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    read = lambda path: json.loads((root / path).read_text())
    checks = []
    sources = read("workplace/source-manifest.json")
    assert sha(root / sources["archive"]) == sources["archive_sha256"]
    for item in sources["files"]:
        path = root / "workplace" / item["location"]
        assert sha(path) == item["sha256"], path
        assert path.stat().st_mode & 0o222 == 0, path
    checks.append("archive and 128 original files unchanged and read-only")
    snapshot = read("workplace/dosgolem-patched-manifest.json")
    for item in snapshot["tracked_files"]:
        path = root / "workplace/dosgolem-source" / item["name"]
        assert sha(path) == item["sha256"], path
    checks.append(str(len(snapshot["tracked_files"])) + " current dosgolem snapshot file hashes valid")
    build = read("workplace/desktop-build.json")
    native_snapshot = "current snapshot"
    if build["dosgolem_manifest_sha256"] != sha(root / "workplace/dosgolem-patched-manifest.json"):
        prior_file = root / snapshot["prior_manifest_file"]
        assert sha(prior_file) == build["dosgolem_manifest_sha256"], "unresolved native dependency provenance"
        prior = json.loads(prior_file.read_text())
        current_files = {item["name"]: item["sha256"] for item in snapshot["tracked_files"]}
        assert all(current_files.get(item["name"]) == item["sha256"] for item in prior["tracked_files"])
        native_snapshot = "verified prior snapshot; additive research observer is not in native binaries"
        checks.append(native_snapshot)
    for path, want in build["inputs"].items():
        assert sha(root / path) == want, path
    outputs = {item["path"]: item for item in build["outputs"]}
    for path, item in outputs.items():
        assert sha(root / path) == item["sha256"], path
    for path, binary, count in [
        ("workplace/hd-native-v2/receipt.json", "superfighter-linux-amd64", 10),
        ("workplace/hd-fallback-v1/receipt.json", "superfighter-linux-amd64", 9),
        ("workplace/windows-native-v4/receipt.json", "superfighter-windows-amd64.exe", 3),
    ]:
        receipt = read(path)
        assert receipt["binary_sha256"] == outputs["workplace/bin/" + binary]["sha256"]
        script = "tools/windows_native_smoke.py" if "windows" in path else "tools/desktop_smoke.py"
        assert receipt["script_sha256"] == sha(root / script)
        assert len(receipt["checks"]) == count, path
    compare = read("workplace/hd-native-v2/comparison.json")
    assert compare["script_sha256"] == sha(root / "tools/verify_hd_capture.py")
    for name, want in compare["files"].items():
        assert sha(root / "workplace/hd-native-v2" / name) == want
    assert compare["hd_toggle_identical_gameplay_area"]
    checks.append("four current binaries; Linux HD 10, fallback 9, Wine 3 checks; GPU comparison match")
    manifest = read("workplace/hd-rooftop-study/manifest.json")
    for kind in ["reference", "palette", "image"]:
        assert sha(root / "workplace/hd-rooftop-study" / manifest[kind + "_file"]) == manifest[kind + "_sha256"]
    assert sha(root / "workplace/hd-layers/rooftop-layer.png") == manifest["image_sha256"]
    font = read("internal/desktop/assets/source.json")
    for item in font["files"]:
        assert sha(root / "internal/desktop/assets" / item["file"]) == item["sha256"]
    checks.append("local HD bundle, original unedited HD PNG and pinned Noto/OFL hashes match")
    index = (root / "AGENTS.md").read_text()
    assert "[README.md](README.md)" in index  # 已知正對照。
    for path in ["tools/audit_hd.py", "tools/verify_hd_capture.py", "docs/spec/006-rooftop-background.md", "internal/gamecore/presentation.go", "internal/hd/background.go"]:
        assert path in index, path
    documents = list(root.glob("*.md")) + list((root / "docs").rglob("*.md"))
    for document in documents:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if target.startswith(("http:", "https:", "#", "app:")):
                continue
            target = unquote(target.split("#")[0].strip("<>"))
            assert (document.parent / target).exists(), (document.name, target)
    older = (root / "docs/spec/003-hd-design.md").read_text()
    newer = (root / "docs/spec/006-rooftop-background.md").read_text()
    assert "D1 部分閉合回填" in older and "006-rooftop-background.md" in older
    for key in ["sub_13DE4", "sub_13E5C", "0x13E9D", "sub_141FA", "sub_1439B"]:
        assert key in older and key in newer, key
    checks.append("Markdown links, positive-control index and source-address resolution backlinks valid")
    for path in (root / "tools").glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    subprocess.run(["bash", "-n", "tools/build_desktop.sh"], check=True)
    log = (root / "workplace/hd-checks.log").read_text()
    assert "internal/hd" in log and "internal/controls" in log and "FAIL" not in log
    checks.append("native-background Go test/vet log checked; Python and shell syntax valid")
    bad = []
    for directory, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(directory) / name
            stat = path.lstat()
            if stat.st_uid == 0 or path.is_dir() and name.endswith(".md"):
                bad.append(str(path.relative_to(root)))
    assert not bad, bad[:20]
    for path in [root / "README.md", root / "workplace/hd-native-v2/hd-rooftop.png", root / "workplace/bin/superfighter-linux-amd64"]:
        assert (path.stat().st_uid, path.stat().st_gid) == (1000, 1000), path
    checks.append("no root-owned files or Markdown directories; sampled UID/GID 1000:1000")
    receipt = {"kind": "local native HD-background audit; not complete HD or physical gamepad acceptance",
               "checks": checks, "native_snapshot_status": native_snapshot, "script_sha256": sha(Path(__file__)),
               "build_receipt_sha256": sha(root / "workplace/desktop-build.json"),
               "gpu_comparison_sha256": sha(root / "workplace/hd-native-v2/comparison.json")}
    (root / "workplace/hd-audit.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
