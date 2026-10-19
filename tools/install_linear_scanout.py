"""將已驗四份顯示 API 加入本專案獨立執行器；不改原有來源或共用專案。"""
import hashlib
import json
from pathlib import Path
import shutil


def main():
    root = Path("/project")
    work = root / "workplace"
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path = work / "dosgolem-patched-manifest.json"
    assert sha(manifest_path) == "6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732"
    original = manifest_path.read_bytes()
    manifest = json.loads(original)
    assert len(manifest["tracked_files"]) == 1715
    candidate_path = work / "display-runtime-study-v1/candidate-manifest.json"
    candidate = json.loads(candidate_path.read_text())
    assert sha(candidate_path) == "a417626f34117b9bb3d8f7e0594e8a5368cf080219d0d8987c50989f30dd3835"
    assert candidate["parent_manifest_sha256"] == sha(manifest_path)
    source = work / "dosgolem-source"
    assert source.stat().st_uid == manifest_path.stat().st_uid == 1000
    for item in manifest["tracked_files"]:
        assert sha(source / item["name"]) == item["sha256"]
    backup = work / "dosgolem-patched-manifest-v2.json"
    assert not backup.exists()
    shutil.copy2(manifest_path, backup)
    for name, expected in candidate["additions"].items():
        origin = work / "display-runtime-study-v1/dosgolem-source" / name
        target = source / name
        assert sha(origin) == expected and not target.exists() and target.parent.stat().st_uid == 1000
        shutil.copy2(origin, target)
        manifest["tracked_files"].append({"name": name, "sha256": expected})
    manifest["prior_manifest_file"] = "workplace/dosgolem-patched-manifest-v2.json"
    manifest["prior_manifest_sha256"] = hashlib.sha256(original).hexdigest()
    manifest["scope"] = "isolated snapshot; queued-entry IF, ordinary-RAM observation and additive bounded linear scanout; shared source unchanged"
    manifest["linear_scanout"] = {"spec": "docs/spec/015-native-scanout.md", "candidate_manifest_sha256": sha(candidate_path),
                                  "install_script_sha256": sha(Path(__file__))}
    manifest["tracked_files_digest"] = hashlib.sha256(json.dumps(manifest["tracked_files"], sort_keys=True).encode()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"files": len(manifest["tracked_files"]), "unchanged": 1715, "manifest_sha256": sha(manifest_path)}))


if __name__ == "__main__":
    main()
