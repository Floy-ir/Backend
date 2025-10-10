#!/usr/bin/env python3
"""
Production configuration validation script
Validates docker-compose.prod.yml and checks for potential issues
"""

import subprocess
import yaml
import sys
import os

def validate_docker_compose():
    """Validate docker-compose.prod.yml syntax"""
    print("🔍 Validating docker-compose.prod.yml syntax...")
    
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.prod.yml', 'config', '--quiet'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ docker-compose.prod.yml syntax is valid")
            return True
        else:
            print(f"❌ docker-compose.prod.yml syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating docker-compose: {e}")
        return False

def check_memory_settings():
    """Check memory-related settings"""
    print("\n🔍 Checking memory settings...")
    
    try:
        with open('docker-compose.prod.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        issues = []
        
        # Check celery-beat containers
        for service_name in ['celery-beat-three', 'celery-beat-four']:
            if service_name in config['services']:
                service = config['services'][service_name]
                
                # Check mem_limit
                if 'mem_limit' in service:
                    mem_limit = service['mem_limit']
                    if mem_limit == '2g':
                        print(f"✅ {service_name}: mem_limit = {mem_limit}")
                    else:
                        issues.append(f"{service_name}: Expected mem_limit=2g, got {mem_limit}")
                else:
                    issues.append(f"{service_name}: Missing mem_limit")
                
                # Check command for memory settings
                if 'command' in service:
                    cmd = service['command']
                    if '--max-memory-per-child=256000' in cmd:
                        print(f"✅ {service_name}: Has memory-per-child limit")
                    else:
                        issues.append(f"{service_name}: Missing --max-memory-per-child")
                    
                    if '--max-tasks-per-child=50' in cmd:
                        print(f"✅ {service_name}: Has tasks-per-child limit")
                    else:
                        issues.append(f"{service_name}: Missing --max-tasks-per-child")
                
                # Check environment variables
                if 'environment' in service:
                    env_vars = service['environment']
                    memory_vars = [
                        'PYTHONDONTWRITEBYTECODE=1',
                        'MALLOC_TRIM_THRESHOLD_=131072',
                        'MALLOC_MMAP_THRESHOLD_=131072',
                        'MALLOC_MMAP_MAX_=65536'
                    ]
                    
                    for var in memory_vars:
                        if var in env_vars:
                            print(f"✅ {service_name}: Has {var}")
                        else:
                            issues.append(f"{service_name}: Missing {var}")
        
        if issues:
            print("\n❌ Memory configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ All memory settings are properly configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking memory settings: {e}")
        return False

def check_volume_mounts():
    """Check volume mounts for production"""
    print("\n🔍 Checking volume mounts...")
    
    try:
        with open('docker-compose.prod.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        expected_volumes = {
            'backend': ['/data/static:/static/'],
            'db': ['/data/pgdata:/var/lib/postgresql/data'],
            'redis': ['/data/redis_data:/data'],
            'minio': ['/data/minio_data:/data'],
            'celery-beat-three': ['/data/celerybeat_data_three:/app/celerybeat-data'],
            'celery-beat-four': ['/data/celerybeat_data_four:/app/celerybeat-data'],
            'rabbitmq': [
                '/data/rabbitmq/log:/var/log/rabbitmq',
                '/data/rabbitmq/mnesia:/var/lib/rabbitmq/mnesia'
            ]
        }
        
        issues = []
        
        for service_name, expected_vols in expected_volumes.items():
            if service_name in config['services']:
                service = config['services'][service_name]
                if 'volumes' in service:
                    actual_vols = service['volumes']
                    for expected_vol in expected_vols:
                        if expected_vol in actual_vols:
                            print(f"✅ {service_name}: Has volume {expected_vol}")
                        else:
                            issues.append(f"{service_name}: Missing volume {expected_vol}")
                else:
                    issues.append(f"{service_name}: No volumes defined")
        
        if issues:
            print("\n❌ Volume mount issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ All volume mounts are properly configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking volume mounts: {e}")
        return False

def check_network_config():
    """Check network configuration"""
    print("\n🔍 Checking network configuration...")
    
    try:
        with open('docker-compose.prod.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        expected_ips = {
            'backend': '172.20.0.5',
            'db': '172.20.0.2',
            'redis': '172.20.0.3',
            'rabbitmq': '172.20.0.4',
            'minio': '172.20.0.7',
            'celery-beat-three': '172.20.0.6',
            'celery-beat-four': '172.20.0.8'
        }
        
        issues = []
        
        for service_name, expected_ip in expected_ips.items():
            if service_name in config['services']:
                service = config['services'][service_name]
                if 'networks' in service and 'floy_network' in service['networks']:
                    network_config = service['networks']['floy_network']
                    if 'ipv4_address' in network_config:
                        actual_ip = network_config['ipv4_address']
                        if actual_ip == expected_ip:
                            print(f"✅ {service_name}: IP {actual_ip}")
                        else:
                            issues.append(f"{service_name}: Expected IP {expected_ip}, got {actual_ip}")
                    else:
                        issues.append(f"{service_name}: Missing ipv4_address")
                else:
                    issues.append(f"{service_name}: Missing network configuration")
        
        if issues:
            print("\n❌ Network configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ All network configurations are correct")
            return True
            
    except Exception as e:
        print(f"❌ Error checking network configuration: {e}")
        return False

def check_data_directory():
    """Check if /data directory exists and has proper permissions"""
    print("\n🔍 Checking /data directory...")
    
    if os.path.exists('/data'):
        print("✅ /data directory exists")
        
        # Check if it's writable
        if os.access('/data', os.W_OK):
            print("✅ /data directory is writable")
            return True
        else:
            print("❌ /data directory is not writable")
            return False
    else:
        print("❌ /data directory does not exist")
        print("   Please create it with: sudo mkdir -p /data")
        return False

def main():
    """Main validation function"""
    print("🚀 Production Configuration Validation")
    print("=" * 50)
    
    checks = [
        validate_docker_compose,
        check_memory_settings,
        check_volume_mounts,
        check_network_config,
        check_data_directory
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Production configuration is ready.")
        print("\n📋 Next steps:")
        print("1. Ensure /data directory exists and is writable")
        print("2. Deploy with: docker-compose -f docker-compose.prod.yml up -d")
        print("3. Monitor with: python monitor_memory.py")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
