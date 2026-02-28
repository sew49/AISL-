import sqlite3

conn = sqlite3.connect('attendance_system.db')
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(attendance)")
columns = cursor.fetchall()
print('Current attendance table columns:')
for col in columns:
    print(f'  {col[1]} - {col[2]}')

# Add timestamp column if it doesn't exist
try:
    cursor.execute('ALTER TABLE attendance ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    print('\nAdded timestamp column to attendance table')
except Exception as e:
    print(f'\nColumn check: {e}')

conn.commit()
conn.close()
print('\nDone!')
