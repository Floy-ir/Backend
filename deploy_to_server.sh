#!/bin/bash

# Quick deployment script for production server
# Usage: ./deploy_to_server.sh [server-ip] [username]

set -e

SERVER_IP=${1:-"your-server-ip"}
USERNAME=${2:-"ubuntu"}
PROJECT_DIR="/opt/floy-backend"

echo "🚀 Deploying Floy Backend to Production Server"
echo "Server: $SERVER_IP"
echo "User: $USERNAME"
echo "Project Directory: $PROJECT_DIR"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with production configuration"
    exit 1
fi

# Validate configuration
echo "🔍 Validating configuration..."
python3 validate_prod_config.py

if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed!"
    exit 1
fi

echo "✅ Configuration validated"
echo

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf floy-backend-deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env.local' \
    --exclude='*.log' \
    .

echo "✅ Deployment package created: floy-backend-deploy.tar.gz"
echo

# Upload to server
echo "📤 Uploading to server..."
scp floy-backend-deploy.tar.gz $USERNAME@$SERVER_IP:/tmp/

echo "✅ Upload completed"
echo

# Deploy on server
echo "🔧 Deploying on server..."
ssh $USERNAME@$SERVER_IP << EOF
set -e

echo "📁 Setting up project directory..."
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "📦 Extracting deployment package..."
sudo tar -xzf /tmp/floy-backend-deploy.tar.gz -C .
sudo chown -R $USERNAME:$USERNAME .

echo "📁 Creating data directories..."
sudo mkdir -p /data/{pgdata,redis_data,minio_data,celerybeat_data_three,celerybeat_data_four,rabbitmq/{log,mnesia},static}

echo "🔐 Setting permissions..."
sudo chown -R 999:999 /data/pgdata
sudo chown -R 999:999 /data/redis_data
sudo chown -R 1000:1000 /data/minio_data
sudo chown -R 1000:1000 /data/celerybeat_data_three
sudo chown -R 1000:1000 /data/celerybeat_data_four
sudo chown -R 999:999 /data/rabbitmq
sudo chown -R 1000:1000 /data/static
sudo chmod -R 755 /data

echo "🐳 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo "📊 Checking memory usage..."
python3 monitor_memory.py

echo "✅ Deployment completed!"
EOF

# Cleanup
rm floy-backend-deploy.tar.gz

echo
echo "🎉 Deployment completed successfully!"
echo
echo "📋 Next steps:"
echo "1. SSH to server: ssh $USERNAME@$SERVER_IP"
echo "2. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "3. Monitor memory: python3 monitor_memory.py"
echo "4. Access backend: http://$SERVER_IP:8000"
echo
echo "🔧 Management commands:"
echo "- Restart: docker-compose -f docker-compose.prod.yml restart"
echo "- Stop: docker-compose -f docker-compose.prod.yml down"
echo "- Update: git pull && docker-compose -f docker-compose.prod.yml up -d --build"
