"""
Daily Automated Backup Script for Supabase PostgreSQL Database
-------------------------------------------------------------
This script performs a pg_dump of the Supabase database and saves 
the .sql file to a 'backups' folder.

Usage:
    python backup.py

Schedule:
    Run via Cron Job or GitHub Action at 2:00 AM daily
    
Requirements:
    - psycopg2 (already in requirements.txt)
    - python-dotenv (already in requirements.txt)
    - pg_dump must be installed on the system
"""

import os
import subprocess
import datetime
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

# Database connection parameters (from environment or config)
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', 'db.sfwhsgrphfrsckzqquxp.supabase.co')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')

# Backup directory
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

# Backup filename format: backup_YYYYMMDD_HHMMSS.sql
TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP_FILENAME = f'backup_{TIMESTAMP}.sql'
BACKUP_PATH = os.path.join(BACKUP_DIR, BACKUP_FILENAME)


def create_backup_directory():
    """Create backups directory if it doesn't exist"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            print(f"✓ Created backup directory: {BACKUP_DIR}")
        return True
    except Exception as e:
        print(f"✗ Failed to create backup directory: {e}")
        return False


def perform_backup():
    """Perform the database backup using pg_dump"""
    try:
        # Check if pg_dump is available
        pg_dump_path = os.getenv('PG_DUMP_PATH', 'pg_dump')
        
        # Build the pg_dump command
        cmd = [
            pg_dump_path,
            '-h', SUPABASE_DB_HOST,
            '-p', SUPABASE_DB_PORT,
            '-U', SUPABASE_DB_USER,
            '-d', SUPABASE_DB_NAME,
            '-f', BACKUP_PATH,
            '--verbose',
            '--no-password'  # Will use PGPASSWORD environment variable
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = SUPABASE_DB_PASSWORD
        
        print(f"📦 Starting backup to: {BACKUP_PATH}")
        print(f"   Host: {SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}")
        print(f"   Database: {SUPABASE_DB_NAME}")
        
        # Run pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            # Get file size
            file_size = os.path.getsize(BACKUP_PATH)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✓ Backup completed successfully!")
            print(f"   File: {BACKUP_FILENAME}")
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Clean up old backups (keep last 7 days)
            cleanup_old_backups()
            
            return True
        else:
            print(f"✗ Backup failed with return code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("✗ Error: pg_dump not found!")
        print("   Please ensure PostgreSQL client tools are installed.")
        print("   On macOS: brew install postgresql")
        print("   On Ubuntu: sudo apt-get install postgresql-client")
        return False
        
    except subprocess.TimeoutExpired:
        print("✗ Backup timed out after 5 minutes")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error during backup: {e}")
        return False


def cleanup_old_backups():
    """Remove backup files older than 7 days"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return
            
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)
        deleted_count = 0
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.sql'):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"   🗑️  Deleted old backup: {filename}")
        
        if deleted_count > 0:
            print(f"   ✓ Cleaned up {deleted_count} old backup(s)")
            
    except Exception as e:
        print(f"   ⚠️  Warning: Could not cleanup old backups: {e}")


def send_failure_notification(error_message):
    """Send notification if backup fails"""
    # You can implement email/Slack notifications here
    # For now, we'll just print the error
    print("\n" + "="*50)
    print("🔔 BACKUP FAILURE NOTIFICATION")
    print("="*50)
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Error: {error_message}")
    print("="*50 + "\n")
    
    # Optional: Send email notification
    # You can implement this using smtplib or a service like SendGrid
    """
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(f"Database backup failed!\n\nError: {error_message}")
    msg['Subject'] = '⚠️ DATABASE BACKUP FAILED'
    msg['From'] = 'backup@yourdomain.com'
    msg['To'] = 'admin@yourdomain.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')
        server.send_message(msg)
    """


def main():
    """Main function to run the backup"""
    print("="*50)
    print("🚀 DATABASE BACKUP SCRIPT")
    print(f"   Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Validate database credentials
    if not SUPABASE_DB_PASSWORD:
        print("✗ Error: SUPABASE_DB_PASSWORD environment variable not set!")
        print("   Please set the database password in your environment or .env file")
        send_failure_notification("SUPABASE_DB_PASSWORD not set")
        sys.exit(1)
    
    # Create backup directory
    if not create_backup_directory():
        send_failure_notification("Failed to create backup directory")
        sys.exit(1)
    
    # Perform backup
    success = perform_backup()
    
    if success:
        print("\n✅ BACKUP COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        send_failure_notification("pg_dump failed - check error messages above")
        sys.exit(1)


if __name__ == '__main__':
    main()
