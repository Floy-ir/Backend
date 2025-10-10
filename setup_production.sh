#!/bin/bash

# Production environment setup script
# Usage: sudo ./setup_production.sh

echo "🚀 Setting up production environment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Create /data directory structure
echo "📁 Creating /data directory structure..."
mkdir -p /data/{pgdata,redis_data,minio_data,celerybeat_data_three,celerybeat_data_four,rabbitmq/{log,mnesia},static}

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R 999:999 /data/pgdata  # PostgreSQL user
chown -R 999:999 /data/redis_data  # Redis user
chown -R 1000:1000 /data/minio_data  # MinIO user
chown -R 1000:1000 /data/celerybeat_data_three
chown -R 1000:1000 /data/celerybeat_data_four
chown -R 999:999 /data/rabbitmq  # RabbitMQ user
chown -R 1000:1000 /data/static  # Static files

# Set proper permissions
chmod -R 755 /data

echo "✅ Production environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your .env file to the project directory"
echo "2. Deploy with: docker-compose -f docker-compose.prod.yml up -d"
echo "3. Monitor with: python3 monitor_memory.py"
echo ""
echo "🔍 Validate configuration: python3 validate_prod_config.py"
