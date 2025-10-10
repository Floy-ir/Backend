#!/bin/bash

# Restart celery-beat containers in production with memory fixes
# Usage: ./restart_celery_prod.sh

echo "Stopping celery-beat containers in production..."
docker-compose -f docker-compose.prod.yml stop celery-beat-three celery-beat-four

echo "Waiting 10 seconds for graceful shutdown..."
sleep 10

echo "Starting celery-beat containers with new configuration..."
docker-compose -f docker-compose.prod.yml up -d celery-beat-three celery-beat-four

echo "Waiting 30 seconds for containers to start..."
sleep 30

echo "Checking container status..."
docker-compose -f docker-compose.prod.yml ps celery-beat-three celery-beat-four

echo "Checking logs for any startup issues..."
echo "=== celery-beat-three logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=20 celery-beat-three

echo "=== celery-beat-four logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=20 celery-beat-four

echo "Checking memory usage..."
docker stats --no-stream celery-beat-three celery-beat-four

echo "Restart completed. Monitor memory usage with: python monitor_memory.py"
