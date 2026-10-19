"""Docker 核對目前介面切片的原檔、編譯來源、正常 GUI 與獨立重組。"""
import hashlib
import json
import os
from pathlib import Path


def main():
    root, work = Path("/project"), Path("/project/workplace")
    read = lambda p: json.loads(p.read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    source = read(work / "source-manifest.json")
    assert len(source["files"]) == 128 and sha(root / source["archive"]) == source["archive_sha256"]
    for item in source["files"]:
        p = work / item["location"]
        assert sha(p) == item["sha256"] and p.stat().st_mode & 0o222 == 0, item["name"]
    patched, old = read(work / "dosgolem-patched-manifest.json"), read(work / "dosgolem-patched-manifest-v1.json")
    entries = {x["name"]: x["sha256"] for x in patched["tracked_files"]}
    assert len(entries) == 1715 and len(old["tracked_files"]) == 1713
    assert all(entries[x["name"]] == x["sha256"] for x in old["tracked_files"])
    for name, expected in entries.items():
        assert sha(work / "dosgolem-source" / name) == expected, name
    build = read(work / "desktop-build.json")
    for name, expected in build["inputs"].items():
        assert sha(root / name) == expected, name
    assert len(build["compiler_receipts"]) == 4
    binaries = {x["path"]: x["sha256"] for x in build["outputs"]}
    for name, expected in build["compiler_receipts"].items():
        p = root / name
        assert sha(p) == expected
        target = read(p)
        assert sha(Path(str(p).removesuffix(".build.json"))) == target["binary_sha256"]
        for name, expected in target["compiled_inputs"].items():
            assert sha(root / name) == expected, name
    cases = [("native-hud-frank-v2", "superfighter-linux-amd64", 16),
             ("windows-hud-v1", "superfighter-windows-amd64.exe", 16),
             ("windows-hud-frank-v1", "superfighter-windows-amd64.exe", 16),
             ("native-hud-legacy-v1", "superfighter-linux-amd64", 13)]
    gui = {}
    for name, binary, count in cases:
        directory = work / name
        receipt, comparison = read(directory / "receipt.json"), read(directory / "comparison.json")
        assert len(receipt["checks"]) == count and receipt["binary_sha256"] == binaries["workplace/bin/" + binary]
        assert receipt["script_sha256"] == sha(directory / "desktop_smoke.py")
        assert comparison["original_and_hd_source_state_identical"] and comparison["restored_hd_viewport_identical"]
        assert len(comparison["replayed_complete_frames"]) >= 12
        for file, expected in comparison["files"].items():
            assert sha(directory / file) == expected, name + "/" + file
        if "legacy" in name:
            assert comparison["missing_pose_entire_viewport_original"] and not comparison["hud_underlay_and_original_source_replayed"]
        else:
            assert comparison["hud_underlay_and_original_source_replayed"] and comparison["changed_original_hud_output_pixels"] > 1000
            field = "changed_original_frank_effect_output_pixels" if "frank" in name else "changed_original_effect_output_pixels"
            assert comparison[field] > 20
            assert read(directory / "hd-air-kick.png.frame.json")["actors"][0]["slot"] == 25
            assert read(directory / "hd-backstep.png.frame.json")["actors"][0]["slot"] == 56
            if "frank" in name:
                assert read(directory / "hd-hud-damage.png.frame.json")["hud"]["state"]["display_health"][0] < 124
        gui[name] = {"checks": count, "receipt_sha256": sha(directory / "receipt.json"), "comparison_sha256": sha(directory / "comparison.json")}
    review = read(work / "hud-evidence-review.json")
    assert review["result"] == "passed" and review["original_draws"] == 1176 and review["independent_source_and_mask_fixtures"] == 33
    assert review["source_review_sha256"] == sha(work / "hud-reference-v5.json")
    assert review["dynamic_receipt_sha256"] == sha(work / "hud-draw-v3/receipt.json")
    compat = read(work / "hud-core-compat-v1/receipt.json")
    assert compat["hud_enabled"] and compat["compared_step_boundaries"] == 456 and compat["complete_hud_snapshots"] > 0
    assert compat["script_sha256"] == sha(work / "hud-core-compat-v1/effect_core_receipt.go")
    pack_dir = work / "hd-characters-study-v7"
    pack, registration = read(pack_dir / "manifest.json"), read(pack_dir / "registration.json")
    assert pack["version"] == 2 and len(pack["atlases"]) == 13 and len(pack["poses"]) == 157
    assert sum(x.get("palette_bank", 0) == 0 for x in pack["poses"]) == 144
    assert sum(x.get("palette_bank", 0) == 1 for x in pack["poses"]) == 13
    assert registration["script_sha256"] == sha(root / "tools/prepare_hd_characters.py")
    for atlas in pack["atlases"]:
        assert sha(pack_dir / atlas["file"]) == atlas["sha256"]
    log = work / "hud-checks-v2.log"
    checks = log.read_text()
    assert "FAIL" not in checks and "SKIP" not in checks and "go vet -p 1 ./..." in checks
    assert "verified source HUD fixtures: 33" in checks and "verified original effect frames: 19" in checks
    wrong = []
    for directory, directories, files in os.walk(root):
        directories[:] = [n for n in directories if n not in (".git", ".agents", ".aws", ".codex")]
        for name in directories + files:
            p = Path(directory) / name
            if p.lstat().st_uid == 0 or p.is_dir() and p.suffix == ".md":
                wrong.append(str(p))
    assert not wrong, wrong[:20]
    result = {"kind": "current native health/timer/name and effect slice audit; not complete HD acceptance",
              "original_files": 128, "dosgolem_files": 1715, "unchanged_baseline_dosgolem_files": 1713,
              "compiler_receipts": 4, "native_gui": gui, "original_hud_draws": 1176,
              "independent_hud_fixtures": 33, "core_compatibility_boundaries": 456,
              "normal_palette_source_slots": 144, "effect_palette_keys": 13, "atlases": 13,
              "test_and_vet_log_sha256": sha(log), "build_manifest_sha256": sha(work / "desktop-build.json"),
              "script_sha256": sha(Path(__file__)),
              "limits": "partial HD HUD; victory/round art, other actors/scenes/screens, full native round, audio, speed and physical platform/gamepad acceptance remain"}
    (work / "native-hud-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
