#!/bin/bash
# Fix script to add missing columns to the staff table
# Run this inside the Docker container

echo "Adding missing columns to staff table..."

# Run SQL to add sick_leave_balance column if it doesn't exist
docker exec attendance-staff python -c "
import sqlite3
import os

db_path = '/app/attendance.db'  # Adjust path as needed
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute('PRAGMA table_info(staff)')
    columns = [col[1] for col in cursor.fetchall()]
    print('Current columns:', columns)
    
    # Add sick_leave_balance if missing
    if 'sick_leave_balance' not in columns:
        cursor.execute('ALTER TABLE staff ADD COLUMN sick_leave_balance REAL DEFAULT 7')
        print('Added sick_leave_balance column')
    
    conn.commit()
    conn.close()
    print('Done!')
else:
    print('Database not found at', db_path)
"
