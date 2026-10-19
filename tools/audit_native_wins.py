"""核對目前 HD 勝場、歷史完整比賽、編譯輸入及原始資料；不宣稱完整 HD。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda path: json.loads(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = read(work / "source-manifest.json")
    assert len(source["files"]) == 128 and sha(root / source["archive"]) == source["archive_sha256"]
    for item in source["files"]:
        path = work / item["location"]
        assert sha(path) == item["sha256"] and path.stat().st_mode & 0o222 == 0, item["name"]
    patched = read(work / "dosgolem-patched-manifest.json")
    old = read(work / "dosgolem-patched-manifest-v1.json")
    entries = {item["name"]: item["sha256"] for item in patched["tracked_files"]}
    assert len(entries) == 1715 and len(old["tracked_files"]) == 1713
    assert all(entries[item["name"]] == item["sha256"] for item in old["tracked_files"])
    for name, expected in entries.items():
        assert sha(work / "dosgolem-source" / name) == expected, name
    build = read(work / "desktop-build.json")
    for name, expected in build["inputs"].items():
        assert sha(root / name) == expected, name
    assert len(build["compiler_receipts"]) == 4
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected
        target = read(path)
        assert sha(Path(str(path).removesuffix(".build.json"))) == target["binary_sha256"]
        for source_name, digest in target["compiled_inputs"].items():
            assert sha(root / source_name) == digest, source_name
    current = read(work / "bin/superfighter-linux-amd64.build.json")
    baseline = work / "native-match-v2/build-baseline"
    historical = read(baseline / "source.json")
    for name, expected in historical["binaries"].items():
        assert sha(baseline / name) == expected
    for name, expected in historical["compiled_inputs"].items():
        assert sha(baseline / "source" / name) == expected
    changed = {name for name, expected in historical["compiled_inputs"].items()
               if current["compiled_inputs"][name] != expected}
    assert changed == {"internal/desktop/game.go", "internal/desktop/hud.go", "internal/hd/hud.go"}, changed
    assert sha(work / "win-markers-v1/superfighter-linux-amd64") == current["binary_sha256"]
    native = {}
    for name, options, captures, binary in [
        ("native-match-v2", [], 8, baseline / "superfighter-linux-amd64"),
        ("native-win-markers-v1", ["--win-markers"], 7, work / "bin/superfighter-linux-amd64"),
    ]:
        directory = work / name
        command = [sys.executable, str(root / "tools/verify_match_capture.py"), str(directory), *options]
        result = subprocess.run(command, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        receipt = read(directory / "receipt.json")
        comparison = read(directory / "comparison.json")
        assert receipt["binary_sha256"] == sha(binary)
        assert receipt["script_sha256"] == sha(directory / "desktop_match_smoke.py")
        assert comparison["script_sha256"] == sha(root / "tools/verify_match_capture.py")
        assert len(comparison["captures"]) == captures
        for record in comparison["captures"]:
            for file, expected in record["files"].items():
                assert sha(directory / file) == expected, name + "/" + file
        native[name] = {"captures": captures, "receipt_sha256": sha(directory / "receipt.json"),
                        "comparison_sha256": sha(directory / "comparison.json"),
                        "binary_sha256": sha(binary), "scope": comparison["scope"]}
    win_comparison = read(work / "native-win-markers-v1/comparison.json")
    assert win_comparison["native_win_marker_gold_pixels"] >= 30
    review = read(work / "hud-wins-review.json")
    evidence = read(work / "hud-wins-evidence.json")
    assert review["evidence_sha256"] == sha(work / "hud-wins-evidence.json")
    assert evidence["script_sha256"] == sha(root / "tools/hud_wins_evidence.py")
    assert evidence["reconstruction_script_sha256"] == sha(root / "tools/hud_reference.py")
    assert evidence["ida_export_sha256"] == sha(work / "ida-hud-v2.json")
    assert evidence["dynamic_fixture_receipt_sha256"] == sha(work / "hud-draw-v3/receipt.json")
    assert len(evidence["dynamic_fixtures"]) == 33 and evidence["glyph"]["nonzero_pixels"] == 93
    checks = read(work / "win-markers-checks-v2.json")
    log = work / "win-markers-checks-v2.log"
    assert checks["skipped"] == 0 and checks["log_sha256"] == sha(log)
    assert all(check["exit_code"] == 0 for check in checks["checks"])
    assert "SKIP" not in log.read_text() and "verified source HUD fixtures: 33" in log.read_text()
    assert "verified original effect frames: 19" in log.read_text()
    coverage = read(work / "win-marker-coverage-v1.json")
    assert coverage["exit_code"] == 0 and coverage["fixture_count"] == 33
    assert coverage["test_sha256"] == sha(root / "internal/hd/hud_test.go")
    assert coverage["log_sha256"] == sha(work / "win-marker-coverage-v1.log")
    pack_dir = work / "hd-characters-study-v7"
    pack = read(pack_dir / "manifest.json")
    assert pack["version"] == 2 and len(pack["atlases"]) == 13 and len(pack["poses"]) == 157
    for atlas in pack["atlases"]:
        assert sha(pack_dir / atlas["file"]) == atlas["sha256"]
    wrong = []
    for directory, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name not in (".git", ".agents", ".aws", ".codex")]
        for name in directories + files:
            path = Path(directory) / name
            if path.lstat().st_uid == 0 or path.is_dir() and path.suffix == ".md":
                wrong.append(str(path))
    assert not wrong, wrong[:20]
    output = {"kind": "current native HD win marker audit; full match uses separately archived baseline; not complete HD acceptance",
              "original_files": 128, "dosgolem_files": 1715, "unchanged_baseline_dosgolem_files": 1713,
              "compiler_receipts": 4, "native_gui": native, "hud_fixtures": 33, "effect_fixtures": 19,
              "win_marker_region_changed_pixels": win_comparison["win_marker_region_changed_pixels"],
              "native_win_marker_gold_pixels": win_comparison["native_win_marker_gold_pixels"],
              "full_test_and_vet_skipped": 0, "baseline_compiled_files_changed": sorted(changed),
              "build_manifest_sha256": sha(work / "desktop-build.json"),
              "source_evidence_sha256": sha(work / "hud-wins-evidence.json"),
              "script_sha256": sha(Path(__file__)),
              "limits": "normal first-player one-win GUI only; second player and two-marker geometry have static evidence; shadows, round art, remaining actors/scenes/screens, audio, speed and physical devices remain"}
    (work / "native-win-markers-audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
