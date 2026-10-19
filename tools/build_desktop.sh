#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
test -d "$project_root/workplace/dosgolem-source"
test -f "$project_root/go.sum"
test -f "$project_root/internal/desktop/assets/NotoSansCJKtc-Regular.otf"
common=(--rm --user "$(id -u):$(id -g)" --memory 1536m --cpus 2 --pids-limit 128
  --mount "type=bind,source=$project_root,target=/project" -w /project
  -e GOCACHE=/project/workplace/cache/native-go-build
  -e GOMODCACHE=/project/workplace/cache/native-go-mod -e GOMAXPROCS=2)
docker run "${common[@]}" --network bridge -e GOPROXY=https://proxy.golang.org -e GOSUMDB=sum.golang.org \
  tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1 timeout 120s python3 tools/build_desktop.py dependencies
docker run "${common[@]}" --network none -e GOPROXY=off -e GOSUMDB=off \
  dosgolem-go-ebiten:1.24-r1 timeout 180s python3 tools/build_desktop.py linux
docker run "${common[@]}" --network none -e GOPROXY=off -e GOSUMDB=off \
  tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1 timeout 480s python3 tools/build_desktop.py cross
docker run "${common[@]}" --network none \
  tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1 timeout 30s python3 tools/build_desktop.py verify
