"""驗舊來源後，只在獨立 dosgolem 副本新增規格 007 的薄觀測介面。"""
import hashlib
import json
from pathlib import Path
import shutil


root = Path("/project")
work = root / "workplace"
source = work / "dosgolem-source"
manifest = work / "dosgolem-patched-manifest.json"
raw = manifest.read_bytes()
base = json.loads(raw)
sha = lambda data: hashlib.sha256(data).hexdigest()
for item in base["tracked_files"]:
    assert sha((source / item["name"]).read_bytes()) == item["sha256"], item["name"]
names = ["memory_write_observer.go", "memory_write_observer_test.go"]
for name in names:
    assert not (source / "oracle" / name).exists(), name
backup = work / "dosgolem-patched-manifest-v1.json"
assert not backup.exists()
shutil.copyfile(manifest, backup)
for name in names:
    origin = root / "tools/dosgolem-observer" / name
    target = source / "oracle" / name
    assert target.parent.stat().st_uid == 1000
    shutil.copyfile(origin, target)
    base["tracked_files"].append({"name": "oracle/" + name, "sha256": sha(target.read_bytes())})
base["prior_manifest_sha256"] = sha(raw)
base["prior_manifest_file"] = str(backup.relative_to(root))
base["scope"] = "isolated snapshot; queued-entry IF patch and additive public ordinary-RAM observation; shared source unchanged"
base["write_observer"] = {"spec": "docs/spec/007-memory-write-observation.md",
                          "script_sha256": sha(Path(__file__).read_bytes()),
                          "source_directory": "tools/dosgolem-observer"}
base["tracked_files_digest"] = sha(json.dumps(base["tracked_files"], sort_keys=True).encode())
manifest.write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"files": len(base["tracked_files"]), "prior_manifest_sha256": base["prior_manifest_sha256"]}))
