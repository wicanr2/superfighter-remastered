"""在指定 Docker image 內執行，產生可回查的三平台中間二進位。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def compiled_inputs(project):
    paths = [project / name for name in ["go.mod", "go.sum", "go.work",
             "workplace/dosgolem-patched-manifest.json", "internal/desktop/assets/source.json",
             "internal/desktop/assets/NotoSansCJKtc-Regular.otf"]]
    paths += [path for directory in ("cmd", "internal") for path in sorted((project / directory).rglob("*.go"))
              if not path.name.endswith("_test.go")]
    return {str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["dependencies", "linux", "cross", "verify"])
    parser.add_argument("--output-dir", type=Path, default=Path("/project/workplace/bin"))
    parser.add_argument("--receipt", type=Path, default=Path("/project/workplace/desktop-build.json"))
    args = parser.parse_args()
    stage = args.stage
    p = Path("/project")
    os.chdir(p)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
    if stage == "dependencies":
        cache = p / "workplace/cache/native-go-mod"
        if not cache.exists():
            shutil.copytree("/go/pkg/mod", cache)
        # 主模組已固定所有版本及 go.sum，不使用 latest。
        subprocess.run(["go", "mod", "download"], check=True)
        return
    manifest = json.loads((p / "workplace/dosgolem-patched-manifest.json").read_text())
    for entry in manifest["tracked_files"]:
        assert sha(p / "workplace/dosgolem-source" / entry["name"]) == entry["sha256"], entry["name"]
    font = json.loads((p / "internal/desktop/assets/source.json").read_text())
    for item in font["files"]:
        assert sha(p / "internal/desktop/assets" / item["file"]) == item["sha256"]
    targets = [("linux", "amd64", "1", "gcc", "superfighter-linux-amd64")]
    if stage == "cross":
        targets = [("windows", "amd64", "0", "clang", "superfighter-windows-amd64.exe"),
                   ("darwin", "amd64", "1", "o64-clang", "superfighter-macos-amd64"),
                   ("darwin", "arm64", "1", "oa64-clang", "superfighter-macos-arm64")]
    if stage in ["linux", "cross"]:
        for goos, arch, cgo, cc, name in targets:
            env = dict(os.environ, GOOS=goos, GOARCH=arch, CGO_ENABLED=cgo, CC=cc,
                       MACOSX_DEPLOYMENT_TARGET="11.0")
            command = ["go", "build", "-p", "1", "-mod=readonly", "-buildvcs=false", "-trimpath", "-o", str(out / name), "./cmd/superfighter"]
            print("Building " + name, flush=True)
            before = compiled_inputs(p)
            subprocess.run(command, env=env, check=True)
            assert compiled_inputs(p) == before, "建置期間來源改變，拒絕登錄二進位"
            build = {"kind": "per-target compiler receipt", "goos": goos, "goarch": arch,
                     "cgo": cgo, "cc": cc, "command": command, "compiled_inputs": before,
                     "go_version": subprocess.check_output(["go", "version"], text=True).strip(),
                     "binary_sha256": sha(out / name)}
            (out / (name + ".build.json")).write_text(json.dumps(build, ensure_ascii=False, indent=2) + "\n")
        return
    paths = [out / name for name in ["superfighter-linux-amd64", "superfighter-windows-amd64.exe", "superfighter-macos-amd64", "superfighter-macos-arm64"]]
    linux, windows, intel, arm = [f.read_bytes() for f in paths]
    assert linux[:6] == b"\x7fELF\x02\x01" and int.from_bytes(linux[18:20], "little") == 62
    pe = int.from_bytes(windows[60:64], "little")
    assert windows[:2] == b"MZ" and windows[pe:pe+4] == b"PE\x00\x00" and int.from_bytes(windows[pe+4:pe+6], "little") == 0x8664
    for binary, cpu in [(intel, 0x01000007), (arm, 0x0100000c)]:
        assert binary[:4] == bytes.fromhex("cffaedfe") and int.from_bytes(binary[4:8], "little") == cpu
    compiler_receipts = {}
    for path in paths:
        source = out / (path.name + ".build.json")
        build = json.loads(source.read_text())
        assert build["compiled_inputs"] == compiled_inputs(p), path.name + " 的實際編譯來源已過期"
        assert build["binary_sha256"] == sha(path), path.name + " 的二進位已變動"
        compiler_receipts[str(source.relative_to(p))] = sha(source)
    files = [p / n for n in ["go.mod", "go.sum", "go.work", "docs/spec/005-native-desktop.md", "docs/spec/006-rooftop-background.md", "docs/spec/008-hd-characters.md", "docs/spec/009-hd-effects.md", "docs/spec/010-hd-battle-hud.md", "docs/spec/011-hd-win-markers.md", "docs/spec/012-hd-shadows.md", "tools/prepare_hd_background.py", "tools/prepare_hd_characters.py", "tools/build_desktop.py", "tools/build_desktop.sh"]] + sorted((p / "cmd").rglob("*.go")) + sorted((p / "internal").rglob("*.go"))
    files += [p / name for name in ("docs/spec/013-hd-round-messages.md", "docs/spec/014-mode13-scanout.md", "docs/spec/015-native-scanout.md", "docs/spec/016-hd-victory-messages.md", "docs/spec/017-victory-pose-banks.md", "docs/spec/018-sarkov-hd.md", "docs/spec/019-sarkov-victory.md", "docs/spec/020-bullet-hd.md", "docs/spec/021-phoenix-hd.md", "docs/spec/022-onimaru-hd.md", "docs/spec/023-lan-hd.md", "docs/spec/024-kim-hd.md", "docs/spec/025-boss-selection.md", "docs/spec/026-clown-hd.md")]
    files.append(p / "docs/spec/027-joe-hd.md")
    files.append(p / "docs/spec/028-bullet-victory.md")
    files.append(p / "docs/spec/030-phoenix-victory.md")
    receipt = {"kind": "native intermediate builds; not release packages or macOS hardware acceptance",
               "go_version": subprocess.check_output(["go", "version"], text=True).strip(),
               "images": {"linux": "dosgolem-go-ebiten:1.24-r1", "cross": "tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1"},
               "inputs": {str(f.relative_to(p)): sha(f) for f in files},
               "compiler_receipts": compiler_receipts,
               "font_manifest_sha256": sha(p / "internal/desktop/assets/source.json"),
               "dosgolem_manifest_sha256": sha(p / "workplace/dosgolem-patched-manifest.json"),
               "outputs": [{"path": str(f.relative_to(p)), "sha256": sha(f), "bytes": f.stat().st_size} for f in paths],
               "headers": ["ELF64 x86-64", "PE32+ x86-64", "Mach-O x86_64", "Mach-O arm64"]}
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
