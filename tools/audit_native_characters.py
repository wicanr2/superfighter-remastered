"""Docker 內核對目前原生角色版來源、逐平台編譯收據、GUI 與素材。"""
import hashlib
import json
import os
from pathlib import Path


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda path: json.loads(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = read(work / "source-manifest.json")
    assert sha(root / source["archive"]) == source["archive_sha256"]
    assert len(source["files"]) == 128
    for item in source["files"]:
        path = work / item["location"]
        assert sha(path) == item["sha256"], item["name"]
        assert path.stat().st_mode & 0o222 == 0, item["name"]
    patched = read(work / "dosgolem-patched-manifest.json")
    old = read(work / "dosgolem-patched-manifest-v1.json")
    assert len(patched["tracked_files"]) == 1715 and len(old["tracked_files"]) == 1713
    entries = {item["name"]: item["sha256"] for item in patched["tracked_files"]}
    assert all(entries[item["name"]] == item["sha256"] for item in old["tracked_files"])
    for name, expected in entries.items():
        assert sha(work / "dosgolem-source" / name) == expected, name
    build = read(work / "desktop-build.json")
    assert build["dosgolem_manifest_sha256"] == sha(work / "dosgolem-patched-manifest.json")
    for name, expected in build["inputs"].items():
        assert sha(root / name) == expected, name
    assert len(build["compiler_receipts"]) == 4
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected, name
        target = read(path)
        for dependency, digest in target["compiled_inputs"].items():
            assert sha(root / dependency) == digest, dependency
        binary = Path(str(path).removesuffix(".build.json"))
        assert sha(binary) == target["binary_sha256"], binary.name
    binaries = {item["path"]: item["sha256"] for item in build["outputs"]}
    gui = {}
    for name, target in [("native-actors-v6", "superfighter-linux-amd64"),
                         ("windows-actors-v6", "superfighter-windows-amd64.exe"),
                         ("native-actors-missing-v2", "superfighter-linux-amd64")]:
        directory = work / name
        receipt = read(directory / "receipt.json")
        assert len(receipt["checks"]) == (13 if name == "native-actors-missing-v2" else 14)
        assert receipt["binary_sha256"] == binaries["workplace/bin/" + target]
        assert receipt["script_sha256"] == sha(directory / "desktop_smoke.py")
        comparison = read(directory / "comparison.json")
        assert comparison["original_and_hd_source_state_identical"]
        assert comparison["restored_hd_viewport_identical"]
        assert len(comparison["replayed_complete_frames"]) >= 7
        for file, expected in comparison["files"].items():
            assert sha(directory / file) == expected, file
        if name == "native-actors-missing-v2":
            assert comparison["missing_pose_entire_viewport_original"]
        else:
            frame = read(directory / "hd-air-kick.png.frame.json")
            assert frame["actors"][0]["slot"] == 25
            backstep = read(directory / "hd-backstep.png.frame.json")
            assert backstep["actors"][0]["slot"] == 56
        gui[name] = {"checks": len(receipt["checks"]), "receipt_sha256": sha(directory / "receipt.json"),
                     "comparison_sha256": sha(directory / "comparison.json")}
    keys = read(work / "windows-shift-v1/receipt.json")
    assert keys["states"] == [[False, False], [True, True], [False, True], [False, False]]
    pack = read(work / "hd-characters-study-v5/manifest.json")
    assert len(pack["poses"]) == 144 and len(pack["atlases"]) == 11
    for character in (0, 4):
        assert sorted(pose["slot"] for pose in pack["poses"] if pose["character"] == character) == list(range(72))
    registration = read(work / "hd-characters-study-v5/registration.json")
    assert registration["script_sha256"] == sha(root / "tools/prepare_hd_characters.py")
    for atlas in pack["atlases"]:
        assert sha(work / "hd-characters-study-v5" / atlas["file"]) == atlas["sha256"]
        assert registration["atlases"][atlas["file"]]["sha256"] == atlas["sha256"]
    checks = (work / "native-character-checks.log").read_text()
    assert "FAIL" not in checks and "internal/hd" in checks and "internal/renderdata" in checks
    assert "ok" in checks
    wrong = []
    for directory, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name not in (".git", ".agents", ".aws", ".codex")]
        for name in directories + files:
            path = Path(directory) / name
            if path.lstat().st_uid == 0 or (path.is_dir() and path.suffix == ".md"):
                wrong.append(str(path))
    assert not wrong, wrong[:20]
    receipt = {"kind": "current native character slice audit; not complete HD acceptance",
               "original_files": 128, "dosgolem_files": 1715, "old_dosgolem_files_unchanged": 1713,
               "platform_compiler_receipts": 4, "native_gui": gui,
               "registered_native_pose_slots": 144, "native_atlases": 11,
               "go_test_and_vet_log_sha256": sha(work / "native-character-checks.log"),
               "build_manifest_sha256": sha(work / "desktop-build.json"),
               "script_sha256": sha(Path(__file__)),
               "limits": "sampled poses; HD HUD, effects, other characters/screens, alternate palettes, complete round and hardware acceptance remain"}
    (work / "native-character-audit.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
