#!/bin/bash

# Restart celery-beat containers to apply memory fixes
# Usage: ./restart_celery.sh

echo "Stopping celery-beat containers..."
docker-compose stop celery-beat-three celery-beat-four

echo "Waiting 10 seconds for graceful shutdown..."
sleep 10

echo "Starting celery-beat containers with new configuration..."
docker-compose up -d celery-beat-three celery-beat-four

echo "Waiting 30 seconds for containers to start..."
sleep 30

echo "Checking container status..."
docker-compose ps celery-beat-three celery-beat-four

echo "Checking logs for any startup issues..."
echo "=== celery-beat-three logs ==="
docker-compose logs --tail=20 celery-beat-three

echo "=== celery-beat-four logs ==="
docker-compose logs --tail=20 celery-beat-four

echo "Restart completed. Monitor memory usage with: python monitor_memory.py"
