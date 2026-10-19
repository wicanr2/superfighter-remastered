"""Docker 內獨立核對原版分層、角色試作素材與證據版本，不宣稱全 HD 完成。"""
import ast
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    root = Path("/project")
    read = lambda name: json.loads((root / name).read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    checks = []
    original = read("workplace/source-manifest.json")
    assert sha(root / original["archive"]) == original["archive_sha256"]
    for item in original["files"]:
        path = root / "workplace" / item["location"]
        assert sha(path) == item["sha256"] and path.stat().st_mode & 0o222 == 0, path
    prior = read("workplace/dosgolem-patched-manifest-v1.json")
    current = read("workplace/dosgolem-patched-manifest.json")
    assert len(prior["tracked_files"]) == 1713 and len(current["tracked_files"]) == 1715
    assert sha(root / "workplace/dosgolem-patched-manifest-v1.json") == current["prior_manifest_sha256"]
    for item in current["tracked_files"]:
        assert sha(root / "workplace/dosgolem-source" / item["name"]) == item["sha256"], item["name"]
    assert current["tracked_files"][:1713] == prior["tracked_files"]
    for name in ["memory_write_observer.go", "memory_write_observer_test.go"]:
        assert sha(root / "tools/dosgolem-observer" / name) == sha(root / "workplace/dosgolem-source/oracle" / name)
    checks.append("128 originals read-only and unchanged; prior 1713 sources unchanged; only two additive observation files")
    a, b = [read("workplace/" + name + "/receipt.json") for name in ["sprite-draw-v1", "sprite-layers-v1"]]
    keys = ["player", "character", "slot", "x", "y", "width", "height", "flags", "counter", "steps", "source_pointer", "source_file_offset"]
    assert [[d[k] for k in keys] for d in a["records"]] == [[d[k] for k in keys] for d in b["records"]]
    assert b["draws"] == b["matched"] == b["source_matches"] == 1432
    layers_root = root / "workplace/sprite-layers-v1"
    assert sha(layers_root / "sprite_draw_receipt.go") == b["script_sha256"]
    frames = b["layer_frames"]
    assert len(frames) == 716 and all(f["matched"] and f["base_coverage"] == 64000 for f in frames)
    replayed = 0
    for frame in frames:
        if not frame.get("fixture"):
            continue
        stem = frame["fixture"]
        layers = json.loads((layers_root / (stem + "-layers.json")).read_text())
        target = bytearray(64000)
        for i, layer in enumerate(layers):
            pixels = (layers_root / f"{stem}-layer-{i:02d}.idx").read_bytes()
            mask = (layers_root / f"{stem}-layer-{i:02d}.mask").read_bytes()
            assert len(mask) == len(pixels) == 64000
            if i == 0:
                assert sum(bool(v) for v in mask) == 64000
            for j, written in enumerate(mask):
                if written:
                    target[j] = pixels[j]
        actual = (layers_root / (stem + ".idx")).read_bytes()
        assert target == actual and hashlib.sha256(actual).hexdigest() == frame["screen_sha256"]
        replayed += 1
    assert replayed == 16
    same = sum(f["same_value_writes"] for f in frames)
    assert same == 37424320
    checks.append("1432 old/new draw states identical; 716 frame receipts match; independent replay of 16 complete layer fixtures")
    events = [json.loads(line) for line in (root / "workplace/write-observer-test.jsonl").read_text().splitlines()]
    passed = {item.get("Test") for item in events if item["Action"] == "pass"}
    assert {"TestObserveWritesIncludesRepeatedStoresAndPreservesMachine", "TestObserveWritesBoundsAndIndependentWatchers"} <= passed
    checks.append("synthetic COM observation, equal stores, independent cancellation and machine-state checks passed")
    art_root = root / "workplace/hd-sprite-art-v1"
    art = read("workplace/hd-sprite-art-v1/manifest.json")
    assert len(art["records"]) == 4 and sum(item["pose_count"] for item in art["records"]) == 48
    for item in art["records"]:
        path = art_root / item["file"]
        assert sha(path) == item["sha256"]
        assert (art_root / item["prompt"]).is_file() and (root / item["reference"]).is_file()
        with Image.open(path) as image:
            assert image.mode == "RGBA" and image.size == tuple(item["size"]) == (1448, 1086)
            alpha = image.getchannel("A")
            assert alpha.getextrema() == (0, 255)
            assert sum(v == 0 for v in alpha.getdata()) == item["transparent_pixels"]
            for y in range(3):
                for x in range(4):
                    assert alpha.crop((x * 362, y * 362, (x + 1) * 362, (y + 1) * 362)).getextrema()[1] == 255
    preview_root = root / "workplace/hd-actor-preview-v3"
    preview = read("workplace/hd-actor-preview-v3/receipt.json")
    assert len(preview["fixtures"]) == 16 and sum(f["hd_active"] for f in preview["fixtures"]) == 15
    assert [f["missing_poses"] for f in preview["fixtures"] if not f["hd_active"]] == [[[0, 56]]]
    for path in preview_root.glob("*.png"):
        with Image.open(path) as image:
            assert image.size == (960, 600)
            image.verify()
    checks.append("four unmodified transparent atlases, 48 cells and prompts present; 15 composed studies and explicit missing slot 56")
    index = (root / "AGENTS.md").read_text()
    assert "[README.md](README.md)" in index
    for name in ["tools/sprite_draw_receipt.go", "tools/hd_actor_preview.go", "tools/hd_sprite_reference.py", "tools/audit_sprite_study.py", "docs/spec/007-memory-write-observation.md", "docs/spec/008-hd-characters.md"]:
        assert name in index and (root / name).is_file(), name
    old = (root / "docs/spec/003-hd-design.md").read_text()
    new = (root / "docs/spec/008-hd-characters.md").read_text()
    assert "008-hd-characters.md" in old
    for name in ["sub_141FA", "sub_1439B", "sub_14665", "sub_146E8", "sub_1477E", "sub_1480A"]:
        assert name in old and name in new
    for path in (root / "tools").glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    for path in [root / "tools/sprite_draw_receipt.go", preview_root / "frame-0386-hd.png", root / "workplace/dosgolem-source/oracle/memory_write_observer.go"]:
        assert (path.stat().st_uid, path.stat().st_gid) == (1000, 1000)
    checks.append("positive-control document index, original-address backlinks, Python syntax and sampled UID/GID valid")
    result = {"kind": "HD character research and redraw study; not native animation or whole-HD completion",
              "checks": checks, "script_sha256": sha(Path(__file__)),
              "layer_receipt_sha256": sha(layers_root / "receipt.json"),
              "art_manifest_sha256": sha(art_root / "manifest.json"),
              "preview_receipt_sha256": sha(preview_root / "receipt.json"),
              "limitations": ["C0h dual flip and top clipping not dynamically covered", "damage palette and complete animations pending", "native desktop still background-only build", "physical controllers and remaining HD screens pending"]}
    (root / "workplace/sprite-study-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
