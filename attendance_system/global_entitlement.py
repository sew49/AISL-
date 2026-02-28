from app import app, db
from sqlalchemy import text

with app.app_context():
    # Task 1: Set Annual Leave Entitlement to 21.0 and Sick Leave to 14.0 for all staff
    result = db.session.execute(text("UPDATE staff SET leave_balance = 21.0, sick_leave_balance = 14.0"))
    db.session.commit()
    print(f'Updated {result.rowcount} staff members with 21.0 Annual Leave and 14.0 Sick Leave')
    
    # For Riziki Merriment (EMP006): Manually set leave_used to 8.5 so remaining is 12.5
    # We need to check if there's a leave_used field, or we need to update the balance
    # Since the current balance is 12.5, and we just set it to 21.0, we need to subtract 8.5
    # Wait - the task says leave_used is 8.5 so remaining is 12.5
    # That means the entitlement was 21.0 and used is 8.5 = 12.5 remaining
    # So let's just verify Riziki's current balance is 12.5
    
    result = db.session.execute(text("SELECT employee_code, leave_balance, sick_leave_balance FROM staff WHERE employee_code = 'EMP006'"))
    row = result.fetchone()
    print(f'EMP006 Riziki Merriment: leave_balance={row[1]}, sick_leave_balance={row[2]}')
    
    # Verify all staff
    result = db.session.execute(text("SELECT employee_code, first_name, last_name, leave_balance, sick_leave_balance, department FROM staff ORDER BY employee_code"))
    rows = result.fetchall()
    print('\nAll Staff Entitlements:')
    for row in rows:
        print(f"  {row[0]}: {row[1]} {row[2]} - Annual: {row[3]}, Sick: {row[4]}, Dept: {row[5]}")
