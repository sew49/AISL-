from app import app, db
from sqlalchemy import text

with app.app_context():
    # Alter the column to FLOAT
    result = db.session.execute(text("ALTER TABLE staff ALTER COLUMN leave_balance TYPE FLOAT"))
    db.session.commit()
    print(f'Altered column type')
    
    # Now update Riziki's balance
    result = db.session.execute(text("UPDATE staff SET leave_balance = 12.5 WHERE employee_code = 'EMP006'"))
    db.session.commit()
    print(f'Updated {result.rowcount} row(s)')
    
    # Verify
    result = db.session.execute(text("SELECT employee_code, leave_balance FROM staff WHERE employee_code = 'EMP006'"))
    row = result.fetchone()
    print(f'EMP006 Riziki balance: {row[1]}')
