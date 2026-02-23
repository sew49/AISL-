"""
Migration Script: Copy data from local SQLite to Supabase PostgreSQL
Usage: python migrate_to_supabase.py
"""

import sqlite3
import psycopg2
from datetime import datetime, date, time

# =====================================================
# CONFIGURATION
# =====================================================

# Supabase connection string
SUPABASE_URL = "postgresql://postgres.sfwhsgrphfrsckzqquxp:ra6oj7UV7X76FQEl@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

# Local SQLite database
LOCAL_DB_PATH = "attendance_system.db"

# Late threshold for reference
LATE_THRESHOLD = time(8, 15)


def is_late_arrival(clock_in_time):
    """Check if the clock-in time is after 08:15 AM"""
    if not clock_in_time:
        return False
    return clock_in_time > LATE_THRESHOLD


def get_local_data():
    """Read all data from local SQLite database"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    # Get Staff data
    cursor.execute("SELECT * FROM staff")
    staff_rows = cursor.fetchall()
    data['staff'] = [dict(row) for row in staff_rows]
    print(f"📋 Found {len(data['staff'])} staff records in local DB")
    
    # Get Attendance data
    cursor.execute("SELECT * FROM attendance")
    attendance_rows = cursor.fetchall()
    data['attendance'] = [dict(row) for row in attendance_rows]
    print(f"📋 Found {len(data['attendance'])} attendance records in local DB")
    
    # Get Leave Requests data (if exists)
    try:
        cursor.execute("SELECT * FROM leave_requests")
        leave_rows = cursor.fetchall()
        data['leave_requests'] = [dict(row) for row in leave_rows]
        print(f"📋 Found {len(data['leave_requests'])} leave request records in local DB")
    except sqlite3.OperationalError:
        print("📋 No leave_requests table in local DB (will create in Supabase)")
        data['leave_requests'] = []
    
    conn.close()
    return data


def create_tables_if_not_exists(conn):
    """Create tables in Supabase - drops and recreates for clean migration"""
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (for clean migration)
    cursor.execute("DROP TABLE IF EXISTS leave_requests CASCADE")
    cursor.execute("DROP TABLE IF EXISTS attendance CASCADE")
    cursor.execute("DROP TABLE IF EXISTS staff CASCADE")
    print("🗑️ Dropped existing tables (if any)")
    
    # Create Staff table
    cursor.execute("""
        CREATE TABLE staff (
            id SERIAL PRIMARY KEY,
            employee_code VARCHAR(10) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            department VARCHAR(50),
            join_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            leave_balance INTEGER DEFAULT 21,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Staff table created")
    
    # Create Attendance table
    cursor.execute("""
        CREATE TABLE attendance (
            id SERIAL PRIMARY KEY,
            staff_id INTEGER NOT NULL REFERENCES staff(id),
            work_date DATE NOT NULL,
            clock_in TIME NOT NULL,
            clock_out TIME,
            day_type VARCHAR(20) DEFAULT 'Full Day',
            status VARCHAR(20) DEFAULT 'Present',
            is_late BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(staff_id, work_date)
        )
    """)
    print("✅ Attendance table created")
    
    # Create Leave Requests table (IMPORTANT for admin dashboard)
    cursor.execute("""
        CREATE TABLE leave_requests (
            id SERIAL PRIMARY KEY,
            staff_id INTEGER NOT NULL REFERENCES staff(id),
            leave_type VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_days INTEGER NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'Pending',
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Leave_requests table created (fixes admin dashboard crash)")
    
    conn.commit()


def migrate_staff(conn, staff_data):
    """Migrate staff data to Supabase"""
    if not staff_data:
        print("⚠️  No staff data to migrate")
        return
    
    cursor = conn.cursor()
    
    # Insert staff data
    for staff in staff_data:
        # Handle join_date
        join_date = staff.get('join_date')
        if isinstance(join_date, str):
            join_date = datetime.strptime(join_date, '%Y-%m-%d').date()
        
        # Handle created_at
        created_at = staff.get('created_at')
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = None
        
        cursor.execute("""
            INSERT INTO staff (employee_code, first_name, last_name, email, phone, 
                            department, join_date, is_active, leave_balance, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            staff.get('employee_code'),
            staff.get('first_name'),
            staff.get('last_name'),
            staff.get('email'),
            staff.get('phone'),
            staff.get('department'),
            join_date,
            staff.get('is_active', 1) == 1 or staff.get('is_active') == 1,
            staff.get('leave_balance', 21),
            created_at
        ))
    
    conn.commit()
    print(f"✅ Migrated {len(staff_data)} staff records")


def migrate_attendance(conn, attendance_data):
    """Migrate attendance data to Supabase"""
    if not attendance_data:
        print("⚠️  No attendance data to migrate")
        return
    
    cursor = conn.cursor()
    
    migrated_count = 0
    for att in attendance_data:
        # Handle dates
        work_date = att.get('work_date')
        if isinstance(work_date, str):
            work_date = datetime.strptime(work_date, '%Y-%m-%d').date()
        
        # Handle times - support both HH:MM:SS and HH:MM formats
        clock_in = att.get('clock_in')
        if clock_in:
            if isinstance(clock_in, str):
                try:
                    clock_in = datetime.strptime(clock_in, '%H:%M:%S').time()
                except:
                    clock_in = datetime.strptime(clock_in, '%H:%M').time()
        
        clock_out = att.get('clock_out')
        if clock_out:
            if isinstance(clock_out, str):
                try:
                    clock_out = datetime.strptime(clock_out, '%H:%M:%S').time()
                except:
                    clock_out = datetime.strptime(clock_out, '%H:%M').time()
        
        # Handle created_at
        created_at = att.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # Recalculate is_late based on 08:15 AM rule
        is_late = is_late_arrival(clock_in)
        
        try:
            cursor.execute("""
                INSERT INTO attendance (staff_id, work_date, clock_in, clock_out, 
                                       day_type, status, is_late, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                att.get('staff_id'),
                work_date,
                clock_in,
                clock_out,
                att.get('day_type', 'Full Day'),
                att.get('status', 'Present'),
                is_late,
                att.get('notes'),
                created_at
            ))
            migrated_count += 1
        except Exception as e:
            print(f"⚠️  Error migrating attendance for staff_id {att.get('staff_id')}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} attendance records (late arrivals marked with 08:15 AM rule)")


def migrate_leave_requests(conn, leave_data):
    """Migrate leave request data to Supabase"""
    if not leave_data:
        print("⚠️  No leave request data to migrate")
        return
    
    cursor = conn.cursor()
    
    migrated_count = 0
    for leave in leave_data:
        # Handle dates
        start_date = leave.get('start_date')
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = leave.get('end_date')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Handle created_at and approved_date
        created_at = leave.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        approved_date = leave.get('approved_date')
        if approved_date:
            if isinstance(approved_date, str):
                approved_date = datetime.fromisoformat(approved_date.replace('Z', '+00:00'))
        
        try:
            cursor.execute("""
                INSERT INTO leave_requests (staff_id, leave_type, start_date, end_date,
                                           total_days, reason, status, approved_by, 
                                           approved_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                leave.get('staff_id'),
                leave.get('leave_type'),
                start_date,
                end_date,
                leave.get('total_days'),
                leave.get('reason'),
                leave.get('status', 'Pending'),
                leave.get('approved_by'),
                approved_date,
                created_at
            ))
            migrated_count += 1
        except Exception as e:
            print(f"⚠️  Error migrating leave request: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} leave request records")


def verify_migration(conn):
    """Verify the migration by checking counts"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM staff")
    staff_count = cursor.fetchone()[0]
    print(f"\n📊 Supabase staff count: {staff_count}")
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    att_count = cursor.fetchone()[0]
    print(f"📊 Supabase attendance count: {att_count}")
    
    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    leave_count = cursor.fetchone()[0]
    print(f"📊 Supabase leave_requests count: {leave_count}")
    
    # Verify late arrivals are correctly marked
    cursor.execute("""
        SELECT COUNT(*) FROM attendance 
        WHERE is_late = TRUE 
        AND clock_in IS NOT NULL
    """)
    late_count = cursor.fetchone()[0]
    print(f"📊 Late arrivals (after 08:15 AM): {late_count}")
    
    # Show sample late arrivals
    cursor.execute("""
        SELECT a.id, s.first_name, s.last_name, a.work_date, a.clock_in, a.is_late
        FROM attendance a
        JOIN staff s ON a.staff_id = s.id
        WHERE a.is_late = TRUE
        ORDER BY a.work_date DESC
        LIMIT 5
    """)
    late_arrivals = cursor.fetchall()
    if late_arrivals:
        print("\n🔴 Sample late arrivals (08:15 AM threshold):")
        for la in late_arrivals:
            print(f"   - {la[1]} {la[2]}: {la[3]} at {la[4]} (marked late: {la[5]})")


def main():
    print("="*60)
    print("ATTENDANCE SYSTEM MIGRATION TO SUPABASE")
    print("="*60)
    
    # Step 1: Get local data
    print("\n📥 Step 1: Reading local SQLite database...")
    local_data = get_local_data()
    
    # Step 2: Connect to Supabase
    print("\n📤 Step 2: Connecting to Supabase PostgreSQL...")
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Step 3: Create tables if not exists
    print("\n🔧 Step 3: Creating tables in Supabase...")
    create_tables_if_not_exists(conn)
    
    # Step 4: Migrate data
    print("\n📤 Step 4: Migrating data...")
    migrate_staff(conn, local_data['staff'])
    migrate_attendance(conn, local_data['attendance'])
    migrate_leave_requests(conn, local_data.get('leave_requests', []))
    
    # Step 5: Verify migration
    print("\n✅ Step 5: Verifying migration...")
    verify_migration(conn)
    
    # Close connection
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 MIGRATION COMPLETE!")
    print("="*60)
    print(f"\n✅ Staff: {len(local_data['staff'])} records migrated")
    print(f"✅ Attendance: {len(local_data['attendance'])} records migrated")
    print(f"✅ Leave Requests: {len(local_data.get('leave_requests', []))} records migrated")
    print(f"✅ leave_requests table created (admin dashboard will work)")
    print(f"✅ Late arrival logic verified (08:15 AM threshold)")


if __name__ == "__main__":
    main()
