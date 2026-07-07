#!/bin/bash
# Laboratorio de Inteligencia Pública V3 — Deploy script
# Run from the V3 directory on the server

set -e

echo "=== Laboratorio de Inteligencia Pública V3 — Deploy ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Build and start
echo "Building containers..."
docker compose build --no-cache

echo ""
echo "Starting containers..."
docker compose up -d

echo ""
echo "Waiting for database..."
sleep 5

echo ""
echo "Running database migrations..."
docker compose exec app flask db upgrade 2>/dev/null || docker compose exec app flask init-db

echo ""
echo "Seeding data..."
docker compose exec app flask seed

echo ""
echo "=== Deploy complete ==="
echo ""
echo "App: https://inteligenciapublica.stonelytics.tech"
echo "Admin: https://inteligenciapublica.stonelytics.tech/admin/login"
echo ""
echo "Containers:"
docker compose ps
