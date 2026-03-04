#!/usr/bin/env python3
"""
Simple fix to add sick_leave_balance column to staff table
Run inside Docker container with: docker exec attendance-staff python fix_in_container.py
"""

import sqlite3
import os

# Find the database file
db_files = ['attendance.db', 'attendance_system.db', 'app.db', 'staff.db']
db_path = None

for f in db_files:
    if os.path.exists(f):
        db_path = f
        break

if not db_path:
    # Check in common directories
    for root, dirs, files in os.walk('/app'):
        for f in files:
            if f.endswith('.db'):
                db_path = os.path.join(root, f)
                break
        if db_path:
            break

if not db_path:
    print("ERROR: Could not find database file")
    exit(1)

print(f"Found database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns
cursor.execute('PRAGMA table_info(staff)')
columns = [col[1] for col in cursor.fetchall()]
print(f"Current staff table columns: {columns}")

# Add sick_leave_balance if missing
if 'sick_leave_balance' not in columns:
    cursor.execute('ALTER TABLE staff ADD COLUMN sick_leave_balance REAL DEFAULT 7')
    print("Added sick_leave_balance column with default value 7")
else:
    print("sick_leave_balance column already exists")

conn.commit()
conn.close()
print("Database fix complete!")
