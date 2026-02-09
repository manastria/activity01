#!/usr/bin/env bash
set -euo pipefail

# Charger .env si present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

: "${DEPLOY_HOST:?Variable DEPLOY_HOST non definie (ex: user@host.example.com)}"
: "${DEPLOY_PATH:?Variable DEPLOY_PATH non definie (ex: /web/activity01)}"

echo "-- Build du site..."
npm run build

echo "-- Deploiement vers ${DEPLOY_HOST}:${DEPLOY_PATH}/"
rsync -avz --delete dist/ "${DEPLOY_HOST}:${DEPLOY_PATH}/"

echo "-- Deploiement termine."
