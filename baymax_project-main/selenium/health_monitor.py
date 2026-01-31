#!/usr/bin/env python3
"""
Stock Screener Health Monitor
Checks all system components and alerts on failures
"""

import os
import sys
import json
import requests
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
API_URL = os.getenv('API_URL', 'http://localhost:5000')
DATABASE_URL = os.getenv('DATABASE_URL')

class HealthMonitor:
    def __init__(self):
        self.status = {
            'timestamp': datetime.now().isoformat(),
            'overall': 'UNKNOWN',
            'components': {}
        }
    
    def check_api(self):
        """Check backend API health"""
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                self.status['components']['api'] = {
                    'status': 'HEALTHY',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'message': 'API responding normally'
                }
                logger.info("✓ API: HEALTHY")
                return True
            else:
                self.status['components']['api'] = {
                    'status': 'DEGRADED',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'message': f'API returned status {response.status_code}'
                }
                logger.warning(f"⚠ API: Status {response.status_code}")
                return False
        except Exception as e:
            self.status['components']['api'] = {
                'status': 'FAILED',
                'message': str(e)
            }
            logger.error(f"✗ API: {e}")
            return False
    
    def check_database(self):
        """Check database connectivity and recent data"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Check table exists
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'stocks'
            """)
            if cursor.fetchone()[0] == 0:
                raise Exception("Table 'stocks' not found")
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM stocks")
            total_records = cursor.fetchone()[0]
            
            # Check latest data age
            cursor.execute("""
                SELECT EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) 
                FROM stocks
            """)
            latest_age_seconds = cursor.fetchone()[0]
            
            # Count records in last hour
            cursor.execute("""
                SELECT COUNT(*) FROM stocks 
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            records_last_hour = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            latest_age_minutes = int(latest_age_seconds / 60)
            
            if latest_age_seconds < 120:  # Less than 2 minutes
                status = 'HEALTHY'
            elif latest_age_seconds < 600:  # Less than 10 minutes
                status = 'DEGRADED'
            else:
                status = 'STALE'
            
            self.status['components']['database'] = {
                'status': status,
                'total_records': total_records,
                'records_last_hour': records_last_hour,
                'latest_data_age_minutes': latest_age_minutes,
                'message': f'Last data: {latest_age_minutes} minutes ago'
            }
            
            if status == 'HEALTHY':
                logger.info(f"✓ Database: HEALTHY ({total_records} records, latest {latest_age_minutes}m ago)")
            elif status == 'DEGRADED':
                logger.warning(f"⚠ Database: DEGRADED (latest {latest_age_minutes}m ago)")
            else:
                logger.error(f"✗ Database: STALE (latest {latest_age_minutes}m ago)")
            
            return status == 'HEALTHY'
            
        except Exception as e:
            self.status['components']['database'] = {
                'status': 'FAILED',
                'message': str(e)
            }
            logger.error(f"✗ Database: {e}")
            return False
    
    def check_scraper_logs(self):
        """Check if scraper is running (via log file recency)"""
        try:
            log_dir = 'selenium/logs'
            if not os.path.exists(log_dir):
                self.status['components']['scraper'] = {
                    'status': 'UNKNOWN',
                    'message': 'Log directory not found'
                }
                logger.warning("⚠ Scraper: No logs directory")
                return None
            
            # Get latest log file
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if not log_files:
                self.status['components']['scraper'] = {
                    'status': 'IDLE',
                    'message': 'No log files found'
                }
                logger.warning("⚠ Scraper: No log files")
                return None
            
            latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
            log_path = os.path.join(log_dir, latest_log)
            
            # Check log age
            log_age_seconds = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(log_path))).total_seconds()
            log_age_minutes = int(log_age_seconds / 60)
            
            # Read last few lines
            with open(log_path, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-5:] if lines else []
            
            if log_age_seconds < 300:  # Less than 5 minutes
                status = 'RUNNING'
            elif log_age_seconds < 3600:  # Less than 1 hour
                status = 'IDLE'
            else:
                status = 'STALE'
            
            self.status['components']['scraper'] = {
                'status': status,
                'latest_log': latest_log,
                'log_age_minutes': log_age_minutes,
                'recent_activity': recent_lines[-1].strip() if recent_lines else 'N/A'
            }
            
            if status == 'RUNNING':
                logger.info(f"✓ Scraper: RUNNING (updated {log_age_minutes}m ago)")
            elif status == 'IDLE':
                logger.warning(f"⚠ Scraper: IDLE (not updated for {log_age_minutes}m)")
            else:
                logger.error(f"✗ Scraper: STALE (not updated for {log_age_minutes}m)")
            
            return status == 'RUNNING'
            
        except Exception as e:
            self.status['components']['scraper'] = {
                'status': 'ERROR',
                'message': str(e)
            }
            logger.error(f"✗ Scraper: {e}")
            return None
    
    def determine_overall_status(self):
        """Determine overall system status"""
        statuses = [
            self.status['components'].get(comp, {}).get('status', 'UNKNOWN')
            for comp in self.status['components']
        ]
        
        if all(s == 'HEALTHY' for s in statuses):
            self.status['overall'] = 'HEALTHY'
        elif any(s == 'FAILED' for s in statuses):
            self.status['overall'] = 'FAILED'
        elif any(s == 'STALE' for s in statuses):
            self.status['overall'] = 'WARNING'
        else:
            self.status['overall'] = 'DEGRADED'
    
    def run(self):
        """Run all health checks"""
        print("\n" + "="*60)
        print("Stock Screener Health Monitor")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Run checks
        self.check_api()
        self.check_database()
        self.check_scraper_logs()
        
        # Determine overall status
        self.determine_overall_status()
        
        # Print summary
        print("\n" + "="*60)
        print(f"Overall Status: {self.status['overall']}")
        print("="*60)
        
        # Print detailed status
        print("\nComponent Details:")
        for component, details in self.status['components'].items():
            print(f"\n{component.upper()}:")
            for key, value in details.items():
                print(f"  {key}: {value}")
        
        # Alert if unhealthy
        if self.status['overall'] in ['DEGRADED', 'WARNING', 'FAILED']:
            print("\n⚠️  SYSTEM NOT FULLY HEALTHY - Check components above")
            return False
        else:
            print("\n✅ All systems operational")
            return True
    
    def get_json(self):
        """Return status as JSON"""
        return json.dumps(self.status, indent=2)

if __name__ == '__main__':
    monitor = HealthMonitor()
    success = monitor.run()
    
    # Optional: Output JSON if requested
    if '--json' in sys.argv:
        print("\nJSON Output:")
        print(monitor.get_json())
    
    sys.exit(0 if success else 1)
