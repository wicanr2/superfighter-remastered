"""核對兩側勝利姿態來源與第二人 Linux／Wine 正常首勝；缺案例即拒絕。"""
import hashlib
import json
from pathlib import Path

from build_desktop import compiled_inputs


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda path: json.loads(path.read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    original = read(work / "source-manifest.json")
    assert len(original["files"]) == 128 and sha(root / original["archive"]) == original["archive_sha256"]
    for item in original["files"]:
        assert sha(work / item["location"]) == item["sha256"]
    runtime = read(work / "dosgolem-patched-manifest.json")
    assert len(runtime["tracked_files"]) == 1719
    assert all(sha(work / "dosgolem-source" / item["name"]) == item["sha256"] for item in runtime["tracked_files"])
    build = read(work / "desktop-build.json")
    assert len(build["compiler_receipts"]) == 4
    binaries = {}
    for name, expected in build["compiler_receipts"].items():
        assert sha(root / name) == expected
        receipt = read(root / name)
        binary = Path(str(root / name).removesuffix(".build.json"))
        assert receipt["compiled_inputs"] == compiled_inputs(root)
        assert sha(binary) == receipt["binary_sha256"]
        binaries[binary.name] = sha(binary)
    results = {}
    for name, player, checks, samples in [("victory-animation-jaan-v1", 0, 5293, 13),
                                          ("victory-animation-frank-v1", 1, 5534, 8)]:
        directory = work / name
        receipt = read(directory / "receipt.json")
        comparison = read(directory / "animation-comparison.json")
        assert receipt["attacker"] == player and receipt["paired"] and receipt["original_state_and_rgb_unchanged"]
        assert receipt["checks"] == comparison["paired_core_checks"] == checks
        assert len(receipt["pose_trace"]) == comparison["sampled_win_frames"] == samples
        assert receipt["victory_cleared"] and comparison["next_round_cleared"]
        assert all(sha(root / path) == expected for path, expected in receipt["source_inputs"].items())
        assert receipt["script_sha256"] == sha(directory / "victory_core_receipt.go")
        assert comparison["script_sha256"] == sha(root / "tools/verify_victory_animation.py")
        assert all(sha(root / "tools" / path) == expected for path, expected in comparison["dependencies"].items())
        assert all(sha(directory / path) == expected for path, expected in comparison["files"].items())
        results[name] = {"paired_checks": checks, "sampled_win_frames": samples,
                         "source_poses": len(comparison["victory_sources"]),
                         "comparison_sha256": sha(directory / "animation-comparison.json")}
    for name, binary in [("native-frank-victory-v1", "superfighter-linux-amd64"),
                         ("windows-frank-victory-v2", "superfighter-windows-amd64.exe")]:
        directory = work / name
        receipt = read(directory / "receipt.json")
        comparison = read(directory / "animation-comparison.json")
        assert receipt["attacker"] == comparison["attacker"] == 1
        assert receipt["scope"] == "first-victory-message" and receipt["round_finishes"] == {"0": "time-expiry"}
        assert receipt["binary_sha256"] == binaries[binary]
        assert receipt["script_sha256"] == sha(directory / "desktop_match_smoke.py")
        assert len(receipt["events"]) == comparison["captures"] == 7
        assert comparison["paused_restoration_exact"] and comparison["next_round_cleared"]
        assert len(comparison["gpu_text_captures"]) == 2
        assert comparison["script_sha256"] == sha(root / "tools/verify_victory_animation.py")
        assert all(sha(root / "tools" / path) == expected for path, expected in comparison["dependencies"].items())
        assert all(sha(directory / path) == expected for path, expected in comparison["files"].items())
        results[name] = {"captures": 7, "gpu_text_captures": 2, "finish": "time-expiry",
                         "comparison_sha256": sha(directory / "animation-comparison.json")}
    result = {"kind": "both normal first-winner source samples and player-two native victory audit",
              "original_files": 128, "dosgolem_files": 1719, "compiler_receipts": 4,
              "cases": results, "build_manifest_sha256": sha(work / "desktop-build.json"),
              "script_sha256": sha(Path(__file__)),
              "limits": "sampled normal winner sources; not every-frame native animation, all-mode, full HD, physical hardware or speed acceptance"}
    (work / "victory-animation-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
