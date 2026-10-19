#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
test -d "$project_root/workplace/dosgolem-source"
test -f "$project_root/workplace/dosgolem-patched-manifest.json"
exec docker run --rm --user "$(id -u):$(id -g)" \
  --memory 1g --cpus 1 --pids-limit 64 --network none \
  --mount "type=bind,source=$project_root,target=/project" \
  -e GOCACHE=/project/workplace/cache/go-build \
  -e GOMODCACHE=/project/workplace/cache/go-mod \
  -e GOPROXY=off -e GOSUMDB=off -e GOMAXPROCS=2 -e CGO_ENABLED=0 \
  -w /project/workplace/dosgolem-source dosgolem-go-ebiten:1.24-r1 \
  timeout 90s python3 -c '
from pathlib import Path
import hashlib, json, subprocess
p=Path("/project")
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest=p/"workplace/dosgolem-patched-manifest.json"
source=json.loads(manifest.read_text())
for item in source["tracked_files"]:
    f=p/"workplace/dosgolem-source"/item["name"]
    assert f.is_file() and sha(f)==item["sha256"],item["name"]
command=["go","build","-p","1","-trimpath","-o","/project/workplace/bin/kdzz-play","/project/tools/play_server.go"]
subprocess.run(command,check=True)
record={"kind":"local interactive prototype, not release package","command":command,
        "go_version":subprocess.check_output(["go","version"],text=True).strip(),
        "tool_image":"dosgolem-go-ebiten:1.24-r1","source_head":source["head"],
        "dosgolem_manifest_sha256":sha(manifest),
        "inputs":{n:sha(p/n) for n in ["tools/play_server.go","tools/live-play.html","tools/quick-moves.js"]},
        "binary_sha256":sha(p/"workplace/bin/kdzz-play")}
(p/"workplace/live-build.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(record,ensure_ascii=False,indent=2))
'
