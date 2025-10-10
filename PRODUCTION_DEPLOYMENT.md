# Production Deployment Guide

## Memory Leak Fixes Applied

This production configuration includes comprehensive memory leak fixes for celery-beat containers that were consuming 5GB+ RAM after 3 days.

### Key Fixes Implemented:

1. **Celery Worker Recycling**: Workers restart every 50 tasks with 256MB memory limit
2. **Memory Management**: Added memory optimization environment variables
3. **Connection Pooling**: Redis and HTTP connections use proper pooling
4. **Resource Cleanup**: Explicit cleanup in tasks and services
5. **Container Limits**: 4GB memory limit with 1GB deploy limit

## Production Configuration

### File Structure:
- `docker-compose.prod.yml` - Production docker-compose configuration
- `restart_celery_prod.sh` - Production restart script
- `monitor_memory.py` - Memory monitoring script

### Volume Mounts:
All data is persisted to `/data/` directory:
- `/data/pgdata` - PostgreSQL data
- `/data/redis_data` - Redis data  
- `/data/minio_data` - MinIO data
- `/data/celerybeat_data_three` - Celery beat three data
- `/data/celerybeat_data_four` - Celery beat four data
- `/data/rabbitmq/log` - RabbitMQ logs
- `/data/rabbitmq/mnesia` - RabbitMQ data
- `/data/static` - Static files

## Deployment Commands

### 1. Deploy Production Stack:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Restart Celery Workers (with memory fixes):
```bash
./restart_celery_prod.sh
```

### 3. Monitor Memory Usage:
```bash
python monitor_memory.py
```

### 4. Check Container Status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 5. View Logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f celery-beat-three
```

## Memory Monitoring

### Expected Memory Usage:
- **celery-beat-three**: Should stay under 2GB (was 5GB+ before fixes)
- **celery-beat-four**: Should stay under 2GB (was 5GB+ before fixes)
- **Workers restart**: Every 50 tasks to prevent memory accumulation

### Monitoring Commands:
```bash
# Real-time memory usage
docker stats celery-beat-three celery-beat-four

# Detailed memory info
python monitor_memory.py

# Container resource usage
docker-compose -f docker-compose.prod.yml top
```

## Configuration Details

### Celery Beat Settings:
- **Worker Recycling**: `--max-tasks-per-child=50`
- **Memory Limit**: `--max-memory-per-child=256000` (256MB)
- **Concurrency**: 1 for three_days, 2 for four_plus
- **Memory Environment**: Optimized malloc settings

### Container Resources:
- **Memory Limit**: 2GB per container
- **Restart Policy**: `always` for celery-beat containers

### Network Configuration:
- **Subnet**: 172.20.0.0/16
- **Backend**: 172.20.0.5
- **Database**: 172.20.0.2
- **Redis**: 172.20.0.3
- **RabbitMQ**: 172.20.0.4
- **MinIO**: 172.20.0.7
- **Celery-three**: 172.20.0.6
- **Celery-four**: 172.20.0.8

## Troubleshooting

### High Memory Usage:
1. Check if workers are recycling: `docker-compose -f docker-compose.prod.yml logs celery-beat-three | grep "worker"`
2. Monitor memory: `python monitor_memory.py`
3. Restart if needed: `./restart_celery_prod.sh`

### Container Issues:
1. Check status: `docker-compose -f docker-compose.prod.yml ps`
2. Check logs: `docker-compose -f docker-compose.prod.yml logs [service-name]`
3. Restart service: `docker-compose -f docker-compose.prod.yml restart [service-name]`

### Data Persistence:
- All data is stored in `/data/` directory
- Ensure `/data/` has sufficient disk space
- Backup `/data/` directory regularly

## Performance Optimization

### PostgreSQL Settings:
- Shared buffers: 512MB
- Effective cache size: 1GB
- Work memory: 4MB
- Max connections: 100

### Redis Settings:
- Append-only file enabled
- Health checks every 10 seconds

### RabbitMQ Settings:
- Consumer timeout: 2 hours
- Persistent logs and mnesia data

## Security Notes

- All services use internal network (172.20.0.0/16)
- External ports: 8000 (backend), 5432 (postgres), 6379 (redis), 9000/9001 (minio), 5672/15672 (rabbitmq)
- Use environment variables for sensitive data
- Ensure proper firewall configuration

## Backup Strategy

### Daily Backups:
```bash
# Database backup
docker exec floy_db pg_dump -U $POSTGRES_USER $POSTGRES_DB > /data/backup_$(date +%Y%m%d).sql

# Data directory backup
tar -czf /data/backup_data_$(date +%Y%m%d).tar.gz /data/
```

### Restore:
```bash
# Database restore
docker exec -i floy_db psql -U $POSTGRES_USER $POSTGRES_DB < backup_file.sql

# Data restore
tar -xzf backup_data_file.tar.gz -C /
```
