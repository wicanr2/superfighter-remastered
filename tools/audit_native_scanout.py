"""核對原生顯示映射、來源不變、完整尾列與目前四份實際編譯。"""
import hashlib
import json
from pathlib import Path

from build_desktop import compiled_inputs
from display_reference import geometry


def main():
    root = Path("/project")
    work = root / "workplace"
    read = lambda p: json.loads(p.read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    source = read(work / "source-manifest.json")
    assert len(source["files"]) == 128
    assert sha(root / source["archive"]) == source["archive_sha256"]
    for item in source["files"]:
        path = work / item["location"]
        assert sha(path) == item["sha256"] and path.stat().st_mode & 0o222 == 0
    old = read(work / "dosgolem-patched-manifest-v2.json")
    current = read(work / "dosgolem-patched-manifest.json")
    entries = {v["name"]: v["sha256"] for v in current["tracked_files"]}
    assert len(entries) == 1719 and len(old["tracked_files"]) == 1715
    assert current["prior_manifest_sha256"] == sha(work / "dosgolem-patched-manifest-v2.json")
    assert all(entries[v["name"]] == v["sha256"] for v in old["tracked_files"])
    assert all(sha(work / "dosgolem-source" / n) == h for n, h in entries.items())
    for target, original in [("internal/machine/linear_scanout.go", "machine_linear_scanout.go"),
                             ("internal/machine/linear_scanout_test.go", "machine_linear_scanout_test.go"),
                             ("oracle/linear_scanout.go", "oracle_linear_scanout.go"),
                             ("oracle/linear_scanout_test.go", "oracle_linear_scanout_test.go")]:
        assert entries[target] == sha(root / "tools/dosgolem-display" / original)
    build = read(work / "desktop-build.json")
    assert len(build["compiler_receipts"]) == 4
    assert all(sha(root / n) == h for n, h in build["inputs"].items())
    binaries = {}
    for n, h in build["compiler_receipts"].items():
        assert sha(root / n) == h
        receipt = read(root / n)
        binary = Path(str(root / n).removesuffix(".build.json"))
        assert receipt["compiled_inputs"] == compiled_inputs(root)
        assert sha(binary) == receipt["binary_sha256"]
        binaries[binary.name] = sha(binary)
    compat = work / "display-core-compat-v1"
    receipt, replay = read(compat / "receipt.json"), read(compat / "round-comparison.json")
    assert receipt["display_observation"] and receipt["checks"] == 1508
    assert len(receipt["round_fixtures"]) == replay["frames"] == 66
    assert receipt["round_cleared_after_opening"] and replay["post_copy"] == 1
    assert receipt["script_sha256"] == sha(root / "tools/round_core_receipt.go")
    assert replay["script_sha256"] == sha(root / "tools/verify_round_capture.py")
    assert all(sha(compat / n) == h for n, h in replay["files"].items())
    gui, evidence = {}, {}
    cases = [("native-display-opening-v2", "superfighter-linux-amd64", 7, "round-comparison.json"),
             ("windows-display-opening-v1", "superfighter-windows-amd64.exe", 7, "round-comparison.json"),
             ("native-display-battle-v2", "superfighter-linux-amd64", 17, "comparison.json"),
             ("native-display-legacy-v2", "superfighter-linux-amd64", 13, "comparison.json")]
    for case, binary, count, comparison_name in cases:
        directory = work / case
        receipt, comparison = read(directory / "receipt.json"), read(directory / comparison_name)
        assert len(receipt["checks"]) == count and receipt["binary_sha256"] == binaries[binary]
        assert receipt["script_sha256"] == sha(root / "tools/desktop_smoke.py") == sha(directory / "desktop_smoke.py")
        if count == 7:
            assert comparison["captures"] == 10 and len(comparison["gpu_text_captures"]) == 6
            verifier = "verify_round_capture.py"
        else:
            assert comparison["original_and_hd_source_state_identical"] and comparison["restored_hd_viewport_identical"]
            verifier = "verify_character_capture.py"
            if count == 13:
                assert comparison["missing_pose_entire_viewport_original"]
            else:
                shadows = read(directory / "shadow-comparison.json")
                assert len(shadows["captures"]) == 12
                assert shadows["script_sha256"] == sha(root / "tools/verify_shadow_capture.py")
        assert comparison["script_sha256"] == sha(root / "tools" / verifier)
        assert all(sha(directory / n) == h for n, h in comparison["files"].items())
        mapped, starts, tail_rows = 0, set(), set()
        for p in directory.glob("*.png.frame.json"):
            if p.name.startswith("capture.png."):
                continue
            base = Path(str(p).removesuffix(".frame.json"))
            frame = read(p)
            s = frame["scanout"]
            capture = read(Path(str(base) + ".capture.json"))
            assert capture["display_applied"] and capture["scanout"] == s
            start,pitch,height = geometry(s["crtc"])
            assert (s["width"],s["height"],s["start_byte"],s["pitch_byte"]) == (320,height,start,pitch)
            assert height == 192 and pitch == 320 and start == frame["crtc_rows_not_applied_by_oracle"]*320
            raw = Path(str(base) + ".idx").read_bytes() + Path(str(base) + ".vram-tail").read_bytes()
            assert len(raw) == 65536
            visible = Path(str(base) + ".display.idx").read_bytes()
            end=start+height*320
            assert visible == raw[start:end]
            if end>64000: assert visible[-(end-64000):] == raw[64000:end]
            starts.add(start//320)
            tail_rows.add(max(0,(end-64000)//320))
            mapped += 1
        assert mapped == (10 if count == 7 else len(comparison["replayed_complete_frames"]))
        gui[case] = {"checks": count, "mapped_captures": mapped, "start_rows":sorted(starts), "visible_tail_rows":sorted(tail_rows), "comparison_sha256": sha(directory / comparison_name)}
        # 尾端與顯示側檔也納入身分，不只保存 PNG。
        evidence[case] = {p.name: sha(p) for p in directory.iterdir() if p.is_file()}
    baseline = work / "native-rounds-v1/build-baseline"
    prior_build = read(baseline / "source.json")
    assert prior_build["source_commit"] == "9623266b031d4835a966ed044baec4741395e9b9"
    assert all(sha(baseline / "inputs" / n) == h for n, h in prior_build["compiled_inputs"].items())
    assert all(sha(baseline / "bin" / n) == h for n, h in prior_build["binaries"].items())
    log = work / "display-checks-v1.log"
    text = log.read_text()
    assert "['go', 'vet', '-p', '1', './...']" in text and "FAIL" not in text
    runtime_log = work / "display-runtime-installed-tests.log"
    runtime_text = runtime_log.read_text()
    assert "PASS" in runtime_text and "FAIL" not in runtime_text and "SKIP" not in runtime_text
    for n in ("006-rooftop-background.md", "013-hd-round-messages.md", "014-mode13-scanout.md"):
        assert "015-native-scanout.md" in (root / "docs/spec" / n).read_text()
    assert "狀態：CONFORMED" in (root / "docs/spec/015-native-scanout.md").read_text()
    # 用既有背景規格作索引正對照，再驗新增入口。
    index = (root / "AGENTS.md").read_text()
    assert "docs/spec/006-rooftop-background.md" in index and "tools/audit_native_scanout.py" in index
    result = {"kind": "native bounded scanout and full-layer HD projection audit; hardware-spec approximation",
              "original_files": 128, "dosgolem_files": 1719, "unchanged_prior_files": 1715,
              "compiler_receipts": 4, "core_boundaries": 1508, "paired_core_frames": 66,
              "gui": gui, "evidence": evidence, "checks_log_sha256": sha(log), "runtime_tests_sha256":sha(runtime_log),
              "build_manifest_sha256": sha(work / "desktop-build.json"), "script_sha256": sha(Path(__file__)),
              "verifiers": {n: sha(root / "tools" / n) for n in ("verify_character_capture.py", "verify_round_capture.py", "verify_shadow_capture.py", "display_reference.py")},
              "limits": "bounded scanout; first round; no full HD, physical Windows/macOS/gamepads, audio/speed or scanline parity claim"}
    (work / "native-display-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "evidence"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
