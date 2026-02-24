import sqlite3

# Check both databases
db_files = [
    'attendance_system.db',
    'instance/attendance_system.db', 
    'instance/attendance.db'
]

for db_file in db_files:
    print(f"\n{'='*60}")
    print(f"DATABASE: {db_file}")
    print('='*60)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found")
            conn.close()
            continue
            
        print("Tables:", [t[0] for t in tables])
        
        for table in tables:
            table_name = table[0]
            if table_name == 'sqlite_sequence':
                continue
                
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n--- {table_name}: {count} rows ---")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
            rows = cursor.fetchall()
            if rows:
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"Columns: {columns}")
                for row in rows:
                    print(f"  {row}")
        
        conn.close()
    except Exception as e:
        print(f"Error accessing {db_file}: {e}")
    tables = cursor.fetchall()

    print("=== LOCAL DATABASE TABLES ===")
    for table in tables:
        table_name = table[0]
        print(f"\n--- {table_name} ---")
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Columns:", [col[1] for col in columns])
        
        # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Row count: {count}")
    
    # Show sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close()
