# Deploy to Production Server

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 7+
- **RAM**: Minimum 8GB (recommended 16GB+)
- **Storage**: Minimum 50GB free space
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Required Software
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

## Step-by-Step Deployment

### 1. Prepare Server Environment

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create project directory
sudo mkdir -p /opt/floy-backend
cd /opt/floy-backend

# Clone your repository (replace with your actual repo)
git clone <your-repository-url> .

# Or upload files via SCP
# scp -r /path/to/local/Backend/* user@server:/opt/floy-backend/
```

### 2. Setup Production Environment

```bash
# Create data directories
sudo mkdir -p /data/{pgdata,redis_data,minio_data,celerybeat_data_three,celerybeat_data_four,rabbitmq/{log,mnesia},static}

# Set proper permissions
sudo chown -R 999:999 /data/pgdata
sudo chown -R 999:999 /data/redis_data
sudo chown -R 1000:1000 /data/minio_data
sudo chown -R 1000:1000 /data/celerybeat_data_three
sudo chown -R 1000:1000 /data/celerybeat_data_four
sudo chown -R 999:999 /data/rabbitmq
sudo chown -R 1000:1000 /data/static
sudo chmod -R 755 /data
```

### 3. Configure Environment Variables

```bash
# Create .env file
sudo nano /opt/floy-backend/.env
```

**Example .env file:**
```env
# Database Configuration
POSTGRES_DB=floy_db
POSTGRES_USER=floy_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# MinIO Configuration
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=your_minio_password
MINIO_BUCKET_NAME=floy-bucket
MINIO_HOST=172.20.0.7
MINIO_PORT=9000
MINIO_SECURE=false
MINIO_PUBLIC_URL=http://172.20.0.7:9000

# Celery/RabbitMQ Configuration
BROKER_URL=amqp://rabbitmq:5672

# Django Configuration
DEBUG=False
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=your-server-ip,your-domain.com

# Other Configuration
PYTHONUNBUFFERED=1
```

### 4. Validate Configuration

```bash
# Validate production configuration
python3 validate_prod_config.py

# Check Docker Compose syntax
docker-compose -f docker-compose.prod.yml config --quiet
```

### 5. Deploy Services

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 6. Verify Deployment

```bash
# Check if all containers are running
docker ps

# Test backend service
curl http://localhost:8000/health

# Check memory usage
python3 monitor_memory.py

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Production Management Commands

### Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Restart Celery Workers (with memory fixes)
```bash
./restart_celery_prod.sh
```

### Update Services
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery-beat-three
docker-compose -f docker-compose.prod.yml logs -f celery-beat-four
```

### Monitor Resources
```bash
# Memory usage
python3 monitor_memory.py

# Container stats
docker stats

# Disk usage
df -h
du -sh /data/*
```

## Firewall Configuration

```bash
# Allow required ports
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 5432/tcp  # PostgreSQL (if external access needed)
sudo ufw allow 6379/tcp  # Redis (if external access needed)
sudo ufw allow 9000/tcp  # MinIO
sudo ufw allow 9001/tcp  # MinIO Console
sudo ufw allow 5672/tcp  # RabbitMQ
sudo ufw allow 15672/tcp # RabbitMQ Management

# Enable firewall
sudo ufw enable
```

## SSL/HTTPS Setup (Optional)

### Using Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/floy
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/floy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Backup Strategy

### Database Backup
```bash
# Create backup script
sudo nano /opt/floy-backend/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker exec floy_db pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/db_backup_$DATE.sql

# Data directory backup
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz /data/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable
chmod +x /opt/floy-backend/backup_db.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /opt/floy-backend/backup_db.sh
```

## Troubleshooting

### Common Issues

**1. Permission Issues**
```bash
# Fix data directory permissions
sudo chown -R 999:999 /data/pgdata
sudo chown -R 1000:1000 /data/celerybeat_data_*
```

**2. Memory Issues**
```bash
# Check memory usage
python3 monitor_memory.py

# Restart celery workers
./restart_celery_prod.sh
```

**3. Container Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Check configuration
docker-compose -f docker-compose.prod.yml config
```

**4. Database Connection Issues**
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test database connection
docker exec -it floy_db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Health Checks

```bash
# Create health check script
sudo nano /opt/floy-backend/health_check.sh
```

```bash
#!/bin/bash
echo "=== Floy Backend Health Check ==="
echo "Date: $(date)"
echo

# Check containers
echo "Container Status:"
docker-compose -f docker-compose.prod.yml ps
echo

# Check memory usage
echo "Memory Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Check disk usage
echo "Disk Usage:"
df -h
echo

# Check backend health
echo "Backend Health:"
curl -s http://localhost:8000/health || echo "Backend not responding"
echo
```

## Monitoring Setup

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs
```

### Log Monitoring
```bash
# Install log monitoring
sudo apt install logrotate

# Configure log rotation
sudo nano /etc/logrotate.d/floy
```

```bash
/data/rabbitmq/log/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 rabbitmq rabbitmq
}
```

## Security Considerations

1. **Change default passwords** in .env file
2. **Use strong passwords** for all services
3. **Configure firewall** to only allow necessary ports
4. **Regular updates** of system and Docker images
5. **Monitor logs** for suspicious activity
6. **Backup data** regularly
7. **Use HTTPS** in production
8. **Restrict database access** to internal network only

## Performance Optimization

### System Level
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Docker Level
```bash
# Configure Docker daemon
sudo nano /etc/docker/daemon.json
```

```json
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2"
}
```

This comprehensive guide will help you deploy your Floy backend to a production server with proper memory management and monitoring.
