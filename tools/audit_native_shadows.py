"""核對目前陰影版的原檔、編譯輸入、正常視窗與逐點重組證據。"""
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
    patched = read(work / "dosgolem-patched-manifest.json")
    prior = read(work / "dosgolem-patched-manifest-v1.json")
    entries = {item["name"]: item["sha256"] for item in patched["tracked_files"]}
    assert len(entries) == 1715 and len(prior["tracked_files"]) == 1713
    assert all(entries[item["name"]] == item["sha256"] for item in prior["tracked_files"])
    for name, expected in entries.items():
        assert sha(work / "dosgolem-source" / name) == expected
    build = read(work / "desktop-build.json")
    for name, expected in build["inputs"].items():
        assert sha(root / name) == expected, name
    assert len(build["compiler_receipts"]) == 4
    binaries = {}
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected
        binary = Path(str(path).removesuffix(".build.json"))
        receipt = read(path)
        assert sha(binary) == receipt["binary_sha256"]
        for name, expected in receipt["compiled_inputs"].items():
            assert sha(root / name) == expected, name
        binaries[binary.name] = receipt["binary_sha256"]
    compat_dir = work / "shadow-core-compat-v1"
    compat = read(compat_dir / "receipt.json")
    assert compat["shadows_enabled"] and compat["complete_shadow_snapshots"] > 0
    assert compat["compared_step_boundaries"] == 456 and len(compat["shadow_fixtures"]) == 24
    assert compat["script_sha256"] == sha(compat_dir / "effect_core_receipt.go")
    dynamic_dir = work / "shadow-draw-v1"
    dynamic, reference = read(dynamic_dir / "receipt.json"), read(dynamic_dir / "reference.json")
    assert len(dynamic["records"]) == reference["draws"] == 772
    assert len(reference["fixtures"]) == 19 and reference["features"]["equal_value_writes"] == 5002
    assert dynamic["script_sha256"] == sha(dynamic_dir / "shadow_draw_receipt.go")
    assert reference["receipt_sha256"] == sha(dynamic_dir / "receipt.json")
    for fixture in reference["fixtures"]:
        for suffix, expected in fixture["files"].items():
            assert sha(dynamic_dir / (fixture["fixture"] + suffix)) == expected
    gui = {}
    for case, binary, checks in [("native-shadows-v1", "superfighter-linux-amd64", 17),
                                 ("windows-shadows-v1", "superfighter-windows-amd64.exe", 17),
                                 ("native-shadow-overlap-v1", "superfighter-linux-amd64", 7),
                                 ("native-shadow-legacy-v1", "superfighter-linux-amd64", 13)]:
        directory = work / case
        receipt, comparison = read(directory / "receipt.json"), read(directory / "comparison.json")
        assert len(receipt["checks"]) == checks and receipt["binary_sha256"] == binaries[binary]
        assert receipt["script_sha256"] == sha(directory / "desktop_smoke.py")
        assert comparison["original_and_hd_source_state_identical"] and comparison["restored_hd_viewport_identical"]
        assert comparison["script_sha256"] == sha(root / "tools/verify_character_capture.py")
        for name, expected in comparison["files"].items():
            assert sha(directory / name) == expected
        if "legacy" in case:
            assert comparison["missing_pose_entire_viewport_original"]
            assert not list(directory.glob("*.png.shadow-render.json"))
        else:
            shadow = read(directory / "shadow-comparison.json")
            assert shadow["script_sha256"] == sha(root / "tools/verify_shadow_capture.py")
            assert len(shadow["captures"]) >= (5 if "overlap" in case else 12)
            for capture in shadow["captures"]:
                assert capture["gpu_darkened_pixels"] > 200
                for name, expected in capture["files"].items():
                    assert sha(directory / name) == expected
            if "overlap" in case:
                assert sum(capture["overlap_pixels"] > 0 for capture in shadow["captures"]) >= 3
        gui[case] = {"checks": checks, "named_captures": len(comparison["replayed_complete_frames"]),
                     "receipt_sha256": sha(directory / "receipt.json"), "comparison_sha256": sha(directory / "comparison.json")}
    checks = read(work / "shadow-checks-v1.json")
    assert checks["skipped"] == 0 and all(item["exit_code"] == 0 for item in checks["checks"])
    assert checks["log_sha256"] == sha(work / "shadow-checks-v1.log")
    lifecycle_dir = work / "shadow-match-core-v1"
    lifecycle = read(lifecycle_dir / "receipt.json")
    assert lifecycle["script_sha256"] == sha(lifecycle_dir / "match_core_receipt.go")
    names = {event["name"]: event for event in lifecycle["events"]}
    for name in ["normal-battle", "knockout-0", "next-round", "knockout-1"]:
        assert names[name]["presentation"]["shadows"]["complete"]
    assert not names["post-match-wait"]["core"]["battle"]
    assert names["post-match-wait"]["presentation"]["serial"] == 0
    assert "shadows" not in names["post-match-wait"]["presentation"]
    result = {"kind": "native HD shadow slice audit; not complete HD or physical platform acceptance",
              "original_files": 128, "dosgolem_files": 1715, "unchanged_prior_files": 1713,
              "compiler_receipts": 4, "original_shadow_draws": 772, "independent_draw_fixtures": 19,
              "paired_core_fixtures": 24, "core_compatibility_boundaries": 456,
              "gui": gui, "full_match_core_lifecycle": True,
              "build_manifest_sha256": sha(work / "desktop-build.json"),
              "script_sha256": sha(Path(__file__)),
              "limits": "negative-X and skipped clipping branches have static tests; round art, other actors/scenes/screens, full animation, audio, speed and physical devices remain"}
    (work / "native-shadows-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
