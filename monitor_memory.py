#!/usr/bin/env python3
"""
Memory monitoring script for celery-beat containers
Usage: python monitor_memory.py
"""

import subprocess
import time
import json
from datetime import datetime

def get_container_memory_usage():
    """Get memory usage for celery-beat containers"""
    try:
        # Get memory usage for celery-beat containers
        cmd = [
            'docker', 'stats', 
            'celery-beat-three', 'celery-beat-four',
            '--format', 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}',
            '--no-stream'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                print(f"\n=== Memory Usage Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                print("Container\t\tCPU%\tMemory Usage\tMemory%")
                print("-" * 60)
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(line)
                return True
        else:
            print(f"Error getting container stats: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error monitoring containers: {e}")
        return False

def get_detailed_memory_info():
    """Get detailed memory information"""
    containers = ['celery-beat-three', 'celery-beat-four']
    
    for container in containers:
        try:
            # Get detailed memory info
            cmd = ['docker', 'exec', container, 'cat', '/proc/meminfo']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n=== Detailed Memory Info for {container} ===")
                lines = result.stdout.strip().split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    if 'MemTotal' in line or 'MemFree' in line or 'MemAvailable' in line or 'Buffers' in line or 'Cached' in line:
                        print(line)
                        
            # Get Python process memory
            cmd = ['docker', 'exec', container, 'ps', 'aux']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n=== Process Memory for {container} ===")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'celery' in line.lower() or 'python' in line.lower():
                        print(line)
                        
        except Exception as e:
            print(f"Error getting detailed info for {container}: {e}")

def main():
    """Main monitoring loop"""
    print("Starting memory monitoring for celery-beat containers...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            success = get_container_memory_usage()
            if success:
                get_detailed_memory_info()
            
            print("\n" + "="*80)
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Monitoring error: {e}")

if __name__ == "__main__":
    main()
