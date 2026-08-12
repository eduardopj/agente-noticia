#!/usr/bin/env bash
set -euo pipefail

SSH_HOST="${RADAR_SSH_HOST:?Set RADAR_SSH_HOST, for example ubuntu@server-ip}"
SSH_KEY="${RADAR_SSH_KEY:-$HOME/.ssh/ovh-acp}"
REMOTE_DIR="${RADAR_REMOTE_DIR:-/opt/radar-tech-ia}"
ARCHIVE_NAME="radar-tech-ia.tar.gz"
ARCHIVE_PATH="${TMPDIR:-/tmp}/$ARCHIVE_NAME"
API_PORT="${RADAR_API_PORT:-4211}"
WEB_PORT="${RADAR_WEB_PORT:-4210}"
API_URL="${RADAR_API_URL:?Set RADAR_API_URL, for example https://api-radar.example.com}"
WEB_URL="${RADAR_WEB_URL:?Set RADAR_WEB_URL, for example https://radar.example.com}"

echo "==> Building Radar Tech IA locally"
python -m compileall -q apps/api/src

pushd apps/web >/dev/null
npm ci
npm run build
popd >/dev/null

echo "==> Creating deployment artifact"
tar \
  --exclude=".git" \
  --exclude=".env" \
  --exclude="apps/api/.venv" \
  --exclude="apps/web/node_modules" \
  --exclude="apps/web/.next/cache" \
  --exclude="storage" \
  --exclude="radar.db" \
  -czf "$ARCHIVE_PATH" .

echo "==> Uploading artifact to $SSH_HOST"
scp -i "$SSH_KEY" "$ARCHIVE_PATH" "$SSH_HOST:/tmp/$ARCHIVE_NAME"

echo "==> Installing on server"
ssh -i "$SSH_KEY" "$SSH_HOST" bash -s <<EOF
set -euo pipefail

sudo mkdir -p "$REMOTE_DIR"
sudo chown -R ubuntu:ubuntu "$REMOTE_DIR"

tar -xzf "/tmp/$ARCHIVE_NAME" -C "$REMOTE_DIR"
rm -f "/tmp/$ARCHIVE_NAME"

cd "$REMOTE_DIR/apps/api"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .

cd "$REMOTE_DIR/apps/web"
npm ci

cd "$REMOTE_DIR"
if [ ! -f ecosystem.config.cjs ]; then
  cp ecosystem.config.example.cjs ecosystem.config.cjs
  echo "Created $REMOTE_DIR/ecosystem.config.cjs. Review env/secrets before first start."
fi

pm2 startOrReload ecosystem.config.cjs --update-env
pm2 save
EOF

rm -f "$ARCHIVE_PATH"

echo "==> Deploy finished"
echo "API: $API_URL/health"
echo "Web: $WEB_URL"
echo "Internal ports: API $API_PORT, Web $WEB_PORT"
