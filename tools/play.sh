#!/usr/bin/env bash
set -euo pipefail

# 主機只做必要的掛載檢查及 Docker 啟動；遊戲在容器內執行。
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
test -d "$project_root/workplace/orig"
test -f "$project_root/workplace/orig/SF.EXE"
test -f "$project_root/workplace/bin/kdzz-play"
exec docker run --rm --init --name kdzz-live-play \
  --user "$(id -u):$(id -g)" --memory 1g --cpus 1 --pids-limit 64 \
  --network bridge -p 127.0.0.1:8086:8086 \
  --mount "type=bind,source=$project_root,target=/project" \
  --mount "type=bind,source=$project_root/workplace/orig,target=/orig,readonly" \
  dosgolem-go-ebiten:1.24-r1 timeout "${KDZZ_SESSION_SECONDS:-3600}s" \
  /project/workplace/bin/kdzz-play -root /orig \
  -scratch /project/workplace/live-play-scratch -listen 0.0.0.0:8086
