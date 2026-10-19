"""核對勝負 HD 的原檔、來源群組、正常核心／視窗收據及四份編譯。"""
import hashlib
import json
from pathlib import Path

from build_desktop import compiled_inputs


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
    current, prior = [read(work / name) for name in ("dosgolem-patched-manifest.json", "dosgolem-patched-manifest-v2.json")]
    entries = {item["name"]: item["sha256"] for item in current["tracked_files"]}
    assert len(entries) == 1719 and len(prior["tracked_files"]) == 1715
    assert all(entries[item["name"]] == item["sha256"] for item in prior["tracked_files"])
    assert all(sha(work / "dosgolem-source" / name) == expected for name, expected in entries.items())
    baseline = work / "native-display-opening-v2/build-baseline"
    old = read(baseline / "source.json")
    assert old["source_commit"] == "5c1bf7c2121f7bad539e2fdb661f1e385e8607ac"
    assert len(old["compiled_inputs"]) == 30
    assert all(sha(baseline / "inputs" / name) == expected for name, expected in old["compiled_inputs"].items())
    assert all(sha(baseline / "bin" / name) == expected for name, expected in old["binaries"].items())
    build = read(work / "desktop-build.json")
    assert len(build["compiler_receipts"]) == 4
    assert all(sha(root / name) == expected for name, expected in build["inputs"].items())
    binaries = {}
    for name, expected in build["compiler_receipts"].items():
        path = root / name
        assert sha(path) == expected
        receipt = read(path)
        assert receipt["compiled_inputs"] == compiled_inputs(root)
        binary = Path(str(path).removesuffix(".build.json"))
        assert sha(binary) == receipt["binary_sha256"]
        binaries[binary.name] = sha(binary)
    assets = work / "hd-characters-study-v8"
    manifest = read(assets / "manifest.json")
    assert manifest["version"] == 3 and len(manifest["poses"]) == 301
    assert len(manifest["sources"]) == 4 and len(manifest["atlases"]) == 15
    for item in manifest["sources"]:
        assert sha(work / "orig" / item["file"]) == item["sha256"]
    for item in manifest["atlases"]:
        assert sha(assets / item["file"]) == item["sha256"]
    base = read(work / "hd-characters-study-v7/manifest.json")
    assert manifest["poses"][:157] == base["poses"]
    assert manifest["atlases"][:13] == base["atlases"]
    for item in base["atlases"]:
        assert sha(assets / item["file"]) == sha(work / "hd-characters-study-v7" / item["file"])
    wins = [p for p in manifest["poses"] if p.get("source_bank") == "victory"]
    assert len(wins) == 144 and len({(p["character"], p["source_sha256"]) for p in wins}) == 7
    registration = read(assets / "victory-pose-registration.json")
    for field, path in [("script_sha256", root / "tools/prepare_victory_characters.py"),
                        ("base_manifest_sha256", work / "hd-characters-study-v7/manifest.json"),
                        ("art_manifest_sha256", work / "victory-art-v1/manifest.json"),
                        ("requests_sha256", work / "victory-art-v1/requests.json"),
                        ("reference_manifest_sha256", work / "victory-poses-v1/manifest.json")]:
        assert registration[field] == sha(path)
    comparisons = {}

    def checked_comparison(directory):
        comparison = read(directory / "victory-comparison.json")
        assert comparison["script_sha256"] == sha(root / "tools/verify_victory_capture.py")
        assert all(sha(root / "tools" / name) == expected for name, expected in comparison["dependencies"].items())
        assert all(sha(directory / name) == expected for name, expected in comparison["files"].items())
        return comparison

    core = work / "victory-core-compat-v2"
    receipt, comparison = read(core / "receipt.json"), checked_comparison(core)
    assert receipt["checks"] == 1479 and receipt["paired"] and receipt["original_state_and_rgb_unchanged"]
    assert receipt["victory_cleared"] and comparison["next_round_cleared"] and comparison["captures"] == 2
    assert receipt["script_sha256"] == sha(root / "tools/victory_core_receipt.go") == sha(core / "victory_core_receipt.go")
    for name, binary, fallback in [("native-victory-v1", "superfighter-linux-amd64", False),
                                   ("windows-victory-v1", "superfighter-windows-amd64.exe", False),
                                   ("native-victory-legacy-v1", "superfighter-linux-amd64", True)]:
        directory = work / name
        receipt, comparison = read(directory / "receipt.json"), checked_comparison(directory)
        assert receipt["scope"] == "first-victory-message" and receipt["binary_sha256"] == binaries[binary]
        assert receipt["script_sha256"] == sha(root / "tools/desktop_match_smoke.py") == sha(directory / "desktop_match_smoke.py")
        assert receipt["expected_victory_original"] == comparison["expected_original_fallback"] == fallback
        assert len(receipt["events"]) == comparison["captures"] == 7
        assert comparison["paused_restoration_exact"] and comparison["next_round_cleared"]
        assert len(comparison["gpu_text_captures"]) == (0 if fallback else 2)
        comparisons[name] = {"captures": 7, "gpu_text_captures": len(comparison["gpu_text_captures"]),
                             "expected_original_fallback": fallback, "comparison_sha256": sha(directory / "victory-comparison.json")}
    for name in ("016-hd-victory-messages.md", "017-victory-pose-banks.md"):
        assert "狀態：CONFORMED" in (root / "docs/spec" / name).read_text()
    index = (root / "AGENTS.md").read_text()
    assert "docs/spec/006-rooftop-background.md" in index
    assert "tools/audit_native_victory.py" in index and "tools/verify_victory_capture.py" in index
    checks = (work / "victory-checks-v2.log").read_text()
    assert "internal/hd" in checks and "internal/gamecore" in checks and "FAIL" not in checks
    result = {"kind": "normal first-victory source-bank and native HD integration audit",
              "original_files": 128, "dosgolem_files": 1719, "unchanged_prior_files": 1715,
              "compiler_receipts": 4, "paired_core_boundaries": 1479, "paired_core_captures": 2,
              "registered_poses": 301, "victory_source_entries": 144, "unique_victory_sources": 7,
              "gui": comparisons, "checks_log_sha256": sha(work / "victory-checks-v2.log"),
              "build_manifest_sha256": sha(work / "desktop-build.json"), "script_sha256": sha(Path(__file__)),
              "limits": "first Jaan victory only; no full HD, complete victory animation, physical platforms/gamepads or audio/speed claim"}
    (work / "native-victory-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
