"""
Seed local SQLite database with sample staff and attendance data
"""
import sqlite3
from datetime import date, time, timedelta
import random

LOCAL_DB_PATH = "attendance_system.db"

def seed_data():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Create staff table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            department TEXT,
            join_date DATE NOT NULL,
            is_active INTEGER DEFAULT 1,
            leave_balance INTEGER DEFAULT 21,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            work_date DATE NOT NULL,
            clock_in TIME NOT NULL,
            clock_out TIME,
            day_type TEXT DEFAULT 'Full Day',
            status TEXT DEFAULT 'Present',
            is_late INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff (id),
            UNIQUE(staff_id, work_date)
        )
    """)
    
    # Create leave_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_days INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            approved_by INTEGER,
            approved_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
    """)
    
    # Seed staff members
    staff_members = [
        ("EMP001", "Peter", "Nyawade", "peter@company.com", "0712345678", "Operations"),
        ("EMP002", "Tonny", "Odongo", "tonny@company.com", "0712345679", "Operations"),
        ("EMP003", "Eric", "Kamau", "eric@company.com", "0712345680", "Operations"),
        ("EMP004", "Kelvin", "Omondi", "kelvin@company.com", "0712345681", "Operations"),
        ("EMP005", "Ottawa", "Kinsvoscko", "ottawa@company.com", "0712345682", "Operations"),
    ]
    
    cursor.execute("DELETE FROM staff")
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM leave_requests")
    
    staff_ids = []
    for emp_code, first, last, email, phone, dept in staff_members:
        cursor.execute("""
            INSERT INTO staff (employee_code, first_name, last_name, email, phone, department, join_date, is_active, leave_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 21)
        """, (emp_code, first, last, email, phone, dept, date.today()))
        staff_ids.append(cursor.lastrowid)
    
    # Seed attendance for last 7 days with some late arrivals
    today = date.today()
    for i in range(7):
        work_date = today - timedelta(days=i)
        if work_date.weekday() == 6:  # Skip Sundays
            continue
            
        for staff_id in staff_ids:
            # Random clock-in time: some before 8:15, some after (late)
            if random.random() < 0.3:  # 30% chance of being late
                hour = random.randint(8, 9)
                minute = random.randint(16, 59)
            else:
                hour = random.randint(7, 8)
                minute = random.randint(0, 14)
            
            clock_in_str = f"{hour:02d}:{minute:02d}"
            is_late = 1 if hour > 8 or (hour == 8 and minute > 15) else 0
            
            # Random clock-out time
            clock_out_hour = random.randint(16, 18)
            clock_out_str = f"{clock_out_hour:02d}:{random.randint(0, 59):02d}"
            
            cursor.execute("""
                INSERT INTO attendance (staff_id, work_date, clock_in, clock_out, day_type, status, is_late)
                VALUES (?, ?, ?, ?, 'Full Day', 'Present', ?)
            """, (staff_id, work_date, clock_in_str, clock_out_str, is_late))
    
    # Seed some leave requests
    cursor.execute("""
        INSERT INTO leave_requests (staff_id, leave_type, start_date, end_date, total_days, reason, status)
        VALUES (?, 'Annual', ?, ?, 2, 'Family vacation', 'Pending')
    """, (staff_ids[0], today + timedelta(days=5), today + timedelta(days=6)))
    
    cursor.execute("""
        INSERT INTO leave_requests (staff_id, leave_type, start_date, end_date, total_days, reason, status)
        VALUES (?, 'Sick', ?, ?, 1, 'Not feeling well', 'Approved')
    """, (staff_ids[1], today - timedelta(days=2), today - timedelta(days=2)))
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM staff")
    print(f"✅ Staff: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    print(f"✅ Attendance: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    print(f"✅ Leave Requests: {cursor.fetchone()[0]} records")
    
    # Show late arrivals
    cursor.execute("""
        SELECT s.first_name, a.work_date, a.clock_in, a.is_late 
        FROM attendance a 
        JOIN staff s ON a.staff_id = s.id 
        WHERE a.is_late = 1
    """)
    late_arrivals = cursor.fetchall()
    print(f"\n🔴 Late arrivals (after 08:15 AM):")
    for la in late_arrivals[:5]:
        print(f"   - {la[0]}: {la[1]} at {la[2]}")
    
    conn.close()
    print("\n✅ Local database seeded successfully!")

if __name__ == "__main__":
    seed_data()
