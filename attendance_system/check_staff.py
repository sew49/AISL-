from app import app, db

with app.app_context():
    from sqlalchemy import text
    result = db.session.execute(text('SELECT employee_code, first_name, last_name, annual_leave_balance FROM staff ORDER BY employee_code'))
    print("All Staff in database:")
    for row in result:
        print(f'{row[0]}: {row[1]} {row[2]} - Balance: {row[3]}')
