#!/usr/bin/env bash
set -euo pipefail
cd /repo
tag="${GITHUB_REF_NAME:-snapshot}"
mkdir -p /artifacts

echo "==> backend builder image"
docker build -f backend/Dockerfile --target builder -t yugioh-backend-build ./backend
cid="$(docker create yugioh-backend-build)"
docker cp "$cid:/app/build/libs/." /tmp/jars
docker rm "$cid"
jar="$(find /tmp/jars -name '*.jar' ! -name '*-plain.jar' | head -1)"
cp "$jar" "/artifacts/yugioh-backend-${tag}.jar"

echo "==> frontend builder image"
docker build -f frontend/Dockerfile --target builder -t yugioh-frontend-build ./frontend
cid="$(docker create yugioh-frontend-build)"
docker cp "$cid:/app/dist" /tmp/frontend-dist
docker rm "$cid"

cd /tmp/frontend-dist
zip -r "/artifacts/yugioh-frontend-${tag}.zip" .
