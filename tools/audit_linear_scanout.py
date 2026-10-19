"""核對候選顯示 API、正常原版視窗與正式執行器保持不變的界線。"""
import hashlib
import json
from pathlib import Path


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda path: json.loads(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    production_path = work / "dosgolem-patched-manifest.json"
    assert sha(production_path) == "6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732"
    production = read(production_path)
    assert len(production["tracked_files"]) == 1715
    for item in production["tracked_files"]:
        assert sha(work / "dosgolem-source" / item["name"]) == item["sha256"]
    study = work / "display-runtime-study-v1"
    candidate_path = study / "candidate-manifest.json"
    candidate = read(candidate_path)
    assert candidate["parent_manifest_sha256"] == sha(production_path)
    assert candidate["unchanged_files"] == 1715 and len(candidate["files"]) == 1719 and len(candidate["additions"]) == 4
    assert candidate["prepare_script_sha256"] == sha(root / "tools/prepare_linear_scanout.py")
    for name, expected in candidate["files"].items():
        assert sha(study / "dosgolem-source" / name) == expected, name
    pairs = {"machine_linear_scanout.go": "internal/machine/linear_scanout.go",
             "machine_linear_scanout_test.go": "internal/machine/linear_scanout_test.go",
             "oracle_linear_scanout.go": "oracle/linear_scanout.go",
             "oracle_linear_scanout_test.go": "oracle/linear_scanout_test.go"}
    assert all(sha(root / "tools/dosgolem-display" / name) == candidate["additions"][target] for name, target in pairs.items())
    log = (study / "tests.log").read_text()
    assert "FAIL" not in log and "SKIP" not in log
    for name in ["StartPitchHeightAndLegacy", "RejectsUnsupportedMappings", "BothSavePaths", "PublicReadOnlyCopy"]:
        assert "--- PASS: TestLinearScanout" + name in log
    baseline_dir = work / "display-ports-v1"
    baseline_path = baseline_dir / "receipt.json"
    baseline, reference = read(baseline_path), read(baseline_dir / "reference.json")
    assert reference["script_sha256"] == sha(root / "tools/display_reference.py")
    assert baseline["script_sha256"] == sha(baseline_dir / "display_receipt.go")
    assert reference["receipt_sha256"] == sha(baseline_path) and len(reference["frames"]) == 67
    for name, expected in reference["files"].items():
        assert sha(baseline_dir / name) == expected, name
    directory = work / "linear-scanout-api-v2"
    receipt = read(directory / "receipt.json")
    assert receipt["frames"] == baseline["frames"] and receipt["legacy_and_original_unchanged"]
    assert receipt["candidate_manifest_sha256"] == sha(candidate_path)
    assert receipt["baseline_receipt_sha256"] == sha(baseline_path)
    assert receipt["script_sha256"] == sha(directory / "linear_scanout_receipt.go") == sha(root / "tools/linear_scanout_receipt.go")
    background = (work / "hd-rooftop-study/reference.idx").read_bytes()
    assert hashlib.sha256(background).hexdigest() == "eb1207239c06a0e06cd9ecbb697b4cf7e1421c4dd3e6e2a6794774246eafeb15"
    files, tails = {}, 0
    for expected in reference["frames"]:
        stem = expected["fixture"]
        display = read(directory / (stem + ".api.json"))
        assert all(display[key] == expected[key] for key in ["start_byte", "pitch_byte", "width", "height"])
        pixels = (directory / (stem + ".api.idx")).read_bytes()
        assert hashlib.sha256(pixels).hexdigest() == expected["scanout_sha256"]
        assert pixels == (baseline_dir / (stem + ".scanout.idx")).read_bytes()
        game = read(directory / (stem + ".game.json"))
        assert game["scene"] == 4 and game["background_sha256"] == hashlib.sha256(background).hexdigest()
        camera = game["camera_x"]
        assert 0 <= camera <= 159
        vram = (baseline_dir / (stem + ".vram")).read_bytes()
        for y in range(200, 204):
            assert vram[y * 320:(y + 1) * 320] == background[y * 480 + camera:y * 480 + camera + 320], (stem, y)
        tails += 1
        for suffix in (".api.json", ".api.idx", ".game.json"):
            path = directory / (stem + suffix)
            files[path.name] = sha(path)
    build = read(work / "desktop-build.json")
    for name, expected in build["inputs"].items():
        assert sha(root / name) == expected, name
    binaries = {}
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected
        compiler = read(path)
        assert all(sha(root / n) == h for n, h in compiler["compiled_inputs"].items())
        binary = Path(str(path).removesuffix(".build.json"))
        assert sha(binary) == compiler["binary_sha256"]
        binaries[binary.name] = sha(binary)
    result = {"kind": "candidate VGA linear scanout audit; native player path not migrated",
              "formal_runtime_unchanged_files": 1715, "candidate_added_files": 4, "normal_scanout_frames": 67,
              "height": 192, "start_byte": 3840, "last_byte": 65279, "confirmed_background_tails": tails,
              "legacy_and_original_unchanged": True, "native_projection_integrated": False,
              "candidate_manifest_sha256": sha(candidate_path), "tests_log_sha256": sha(study / "tests.log"),
              "baseline_reference_sha256": sha(baseline_dir / "reference.json"), "api_receipt_sha256": sha(directory / "receipt.json"),
              "api_files": files, "native_binaries_unchanged": binaries, "script_sha256": sha(Path(__file__)),
              "limits": "hardware-spec approximation, fixed chained profile; no native UI, physical hardware or full-HD completion claim"}
    (work / "linear-scanout-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("api_files", "native_binaries_unchanged")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
