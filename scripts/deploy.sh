#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch origin master
git reset --hard origin/master
cd docker
docker compose up -d --build
docker image prune -f
docker compose ps