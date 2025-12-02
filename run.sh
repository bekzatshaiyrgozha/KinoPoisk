#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -f ".env" ]; then
  cp env.example .env
  echo "Created .env from env.example"
fi

echo "[1/3] Starting database..."
docker compose up -d postgres

echo "[2/3] Applying migrations..."
docker compose run --rm backend python manage.py migrate

echo "[3/3] Starting backend + frontend..."
docker compose up --build backend frontend
