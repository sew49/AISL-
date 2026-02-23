import psycopg2

SUPABASE_URL = "postgresql://postgres.sfwhsgrphfrsckzqquxp:ra6oj7UV7X76FQEl@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

conn = psycopg2.connect(SUPABASE_URL)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM staff')
print(f"Staff: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM attendance')
print(f"Attendance: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM leave_requests')
print(f"Leave Requests: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT a.id, s.first_name, s.last_name, a.work_date, a.clock_in, a.is_late
    FROM attendance a
    JOIN staff s ON a.staff_id = s.id
    WHERE a.is_late = TRUE
    ORDER BY a.work_date DESC
    LIMIT 5
""")
print("\nLate arrivals:")
for la in cursor.fetchall():
    print(f"   - {la[1]} {la[2]}: {la[3]} at {la[4]} (marked late: {la[5]})")

conn.close()
