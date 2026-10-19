"""核對回合開場切片的來源、四平台編譯、原版重組與正常原生視窗。"""
import hashlib
import json
from pathlib import Path


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda path: json.loads(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = read(work / "source-manifest.json")
    assert len(source["files"]) == 128 and sha(root / source["archive"]) == source["archive_sha256"]
    for item in source["files"]:
        path = work / item["location"]
        assert sha(path) == item["sha256"] and path.stat().st_mode & 0o222 == 0
    patched, prior = [read(work / name) for name in ("dosgolem-patched-manifest.json", "dosgolem-patched-manifest-v1.json")]
    entries = {item["name"]: item["sha256"] for item in patched["tracked_files"]}
    assert len(entries) == 1715 and len(prior["tracked_files"]) == 1713
    assert all(entries[item["name"]] == item["sha256"] for item in prior["tracked_files"])
    assert all(sha(work / "dosgolem-source" / name) == value for name, value in entries.items())
    build = read(work / "desktop-build.json")
    assert all(sha(root / name) == expected for name, expected in build["inputs"].items())
    assert len(build["compiler_receipts"]) == 4
    binaries = {}
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected
        binary = Path(str(path).removesuffix(".build.json"))
        receipt = read(path)
        assert sha(binary) == receipt["binary_sha256"]
        assert all(sha(root / n) == h for n, h in receipt["compiled_inputs"].items())
        binaries[binary.name] = receipt["binary_sha256"]
    dynamic_dir = work / "round-draw-v3"
    dynamic, reference = read(dynamic_dir / "receipt.json"), read(dynamic_dir / "reference.json")
    assert dynamic["script_sha256"] == sha(dynamic_dir / "round_draw_receipt.go")
    assert reference["checker_sha256"] == sha(root / "tools/round_reference.py")
    assert reference["receipt_sha256"] == sha(dynamic_dir / "receipt.json")
    assert reference["full_routine_draws"] == reference["partial_background_draws"] == reference["draws"] == 66
    assert all("routine_complete_steps" in r for r in dynamic["records"])
    assert reference["round_indices"] == [0] and reference["states"] == [0, 1, 2, 3]
    for name, expected in reference["files"].items():
        assert sha(dynamic_dir / name) == expected
    for record in dynamic["background_records"]:
        assert record["rows"] == 12 and record["pixel_differences"] == record["mask_differences"] == 0
        assert record["source_sha256"] == sha(work / "hd-rooftop-study/reference.idx")
    review = read(work / "round-evidence-review.json")
    assert all(sha(work / name) == expected for name, expected in review["evidence"].items())
    core_dir = work / "round-core-compat-v1"
    compat, comparison = read(core_dir / "receipt.json"), read(core_dir / "round-comparison.json")
    assert compat["checks"] == 1508 and len(compat["round_fixtures"]) == comparison["frames"] == 66
    assert compat["round_cleared_after_opening"] and comparison["post_copy"] == 1
    assert compat["script_sha256"] == sha(core_dir / "round_core_receipt.go")
    assert comparison["script_sha256"] == sha(root / "tools/verify_round_capture.py")
    assert all(sha(root / "tools" / name) == expected for name, expected in comparison["dependencies"].items())
    assert all(sha(core_dir / name) == expected for name, expected in comparison["files"].items())
    gui = {}
    for case, binary in [("native-rounds-v1", "superfighter-linux-amd64"), ("windows-rounds-v1", "superfighter-windows-amd64.exe")]:
        directory = work / case
        receipt, comparison = read(directory / "receipt.json"), read(directory / "round-comparison.json")
        assert len(receipt["checks"]) == 7 and receipt["scope"] == "round-opening"
        assert receipt["binary_sha256"] == binaries[binary]
        assert receipt["script_sha256"] == sha(directory / "desktop_smoke.py")
        assert comparison["captures"] == 10 and len(comparison["gpu_text_captures"]) == 6
        assert comparison["script_sha256"] == sha(root / "tools/verify_round_capture.py")
        assert all(sha(root / "tools" / name) == expected for name, expected in comparison["dependencies"].items())
        assert all(sha(directory / name) == expected for name, expected in comparison["files"].items())
        gui[case] = {"checks": 7, "captures": 10, "gpu_text_captures": 6, "comparison_sha256": sha(directory / "round-comparison.json")}
    for case, count in [("native-round-battle-v1", 17), ("native-round-legacy-v1", 13)]:
        directory = work / case
        receipt, comparison = read(directory / "receipt.json"), read(directory / "comparison.json")
        assert len(receipt["checks"]) == count and receipt["binary_sha256"] == binaries["superfighter-linux-amd64"]
        assert receipt["script_sha256"] == sha(directory / "desktop_smoke.py")
        assert comparison["original_and_hd_source_state_identical"] and comparison["restored_hd_viewport_identical"]
        assert comparison["script_sha256"] == sha(root / "tools/verify_character_capture.py")
        assert all(sha(directory / name) == expected for name, expected in comparison["files"].items())
        if "legacy" in case:
            assert comparison["missing_pose_entire_viewport_original"]
            assert not list(directory.glob("*.png.round-render-after.rgba"))
        else:
            shadow = read(directory / "shadow-comparison.json")
            assert len(shadow["captures"]) == 12 and shadow["script_sha256"] == sha(root / "tools/verify_shadow_capture.py")
            for capture in shadow["captures"]:
                assert all(sha(directory / name) == expected for name, expected in capture["files"].items())
        gui[case] = {"checks": count, "captures": len(comparison["replayed_complete_frames"]), "comparison_sha256": sha(directory / "comparison.json")}
    checks = read(work / "round-checks-v3.json")
    assert checks["skipped"] == 0 and all(item["exit_code"] == 0 for item in checks["checks"])
    assert checks["log_sha256"] == sha(work / "round-checks-v3.log")
    evidence_spec = (root / "docs/spec/013-hd-round-messages.md").read_text()
    for name, address in [("008-hd-characters.md", "3E09h"), ("010-hd-battle-hud.md", "3570h"), ("003-hd-design.md", "3570h")]:
        older = (root / "docs/spec" / name).read_text()
        assert address in evidence_spec and address in older and "013-hd-round-messages.md" in older, name
    baseline = work / "native-shadows-v1/build-baseline"
    old = read(baseline / "source.json")
    assert old["source_commit"] == "d04670ddf671c51a8b0837b48d43693b52402d28"
    assert all(sha(baseline / "inputs" / name) == expected for name, expected in old["compiled_inputs"].items())
    assert all(sha(baseline / "bin" / name) == expected for name, expected in old["binaries"].items())
    result = {"kind": "native first-round HD slice audit; not complete HD or physical platform acceptance",
              "original_files": 128, "dosgolem_files": 1715, "unchanged_prior_files": 1713, "compiler_receipts": 4,
              "original_round_draws": 66, "original_background_draws": 66, "complete_routine_replays": 66,
              "paired_core_frames": 66, "core_compatibility_boundaries": 1508, "gui": gui,
              "historical_shadow_source_commit": old["source_commit"], "build_manifest_sha256": sha(work / "desktop-build.json"),
              "script_sha256": sha(Path(__file__)),
              "limits": "first round sampled; later round numbers have static source composition only; victory/draw text, other actors/scenes/screens, full animation, CRTC display start, audio, speed and physical devices remain"}
    (work / "native-rounds-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
