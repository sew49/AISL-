from app import app, db
from sqlalchemy import text

with app.app_context():
    # Set Riziki's remaining balance to 12.5
    result = db.session.execute(text("UPDATE staff SET leave_balance = 12.5 WHERE employee_code = 'EMP006'"))
    db.session.commit()
    print(f'Updated {result.rowcount} row(s)')
    
    # Verify
    result = db.session.execute(text("SELECT employee_code, first_name, last_name, leave_balance, sick_leave_balance FROM staff WHERE employee_code = 'EMP006'"))
    row = result.fetchone()
    print(f'EMP006 {row[1]} {row[2]}: leave_balance={row[3]}, sick_leave_balance={row[4]}')
    print(f'(This means {21.0 - row[3]} days have been used from the 21.0 entitlement)')
