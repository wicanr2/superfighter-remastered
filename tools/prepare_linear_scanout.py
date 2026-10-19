"""核對正式副本後，建立獨立的 mode 13h 顯示候選來源；不改正式副本。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/project/workplace/display-runtime-study-v1"))
    args = parser.parse_args()
    project = Path("/project")
    work = project / "workplace"
    output = args.output
    output.relative_to(work)
    assert work.stat().st_uid == 1000 and not output.exists()
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path = work / "dosgolem-patched-manifest.json"
    assert sha(manifest_path) == "6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732"
    manifest = json.loads(manifest_path.read_text())
    assert len(manifest["tracked_files"]) == 1715
    source = work / "dosgolem-source"
    for item in manifest["tracked_files"]:
        relative = Path(item["name"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert sha(source / relative) == item["sha256"], relative
    output.mkdir()
    copied = output / "dosgolem-source"
    copied.mkdir()
    for item in manifest["tracked_files"]:
        target = copied / item["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / item["name"], target)
    additions = {}
    for origin_name, target_name in [
        ("machine_linear_scanout.go", "internal/machine/linear_scanout.go"),
        ("machine_linear_scanout_test.go", "internal/machine/linear_scanout_test.go"),
        ("oracle_linear_scanout.go", "oracle/linear_scanout.go"),
        ("oracle_linear_scanout_test.go", "oracle/linear_scanout_test.go"),
    ]:
        origin = project / "tools/dosgolem-display" / origin_name
        target = copied / target_name
        assert origin.stat().st_uid == 1000 and not target.exists()
        shutil.copy2(origin, target)
        additions[target_name] = sha(target)
    assert all(sha(copied / item["name"]) == item["sha256"] for item in manifest["tracked_files"])
    shutil.copy2(manifest_path, output / "parent-manifest.json")
    result = {"kind": "isolated linear-scanout candidate; not the production runtime",
              "parent_manifest_sha256": sha(manifest_path), "unchanged_files": 1715,
              "additions": additions, "files": {item["name"]: item["sha256"] for item in manifest["tracked_files"]} | additions,
              "prepare_script_sha256": sha(Path(__file__)), "spec": "docs/spec/014-mode13-scanout.md"}
    (output / "candidate-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (output / "go.work").write_text(f"go 1.24.0\n\nuse (\n /project\n {copied}\n)\n")
    print(json.dumps({"output": str(output), "unchanged": 1715, "added": len(additions)}))


if __name__ == "__main__":
    main()
