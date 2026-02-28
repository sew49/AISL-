from app import app, db
from app import Staff

with app.app_context():
    # Test the exact query used in the API
    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
    print(f"Total active staff: {len(staff_members)}")
    for s in staff_members:
        print(f"  {s.employee_code}: {s.first_name} {s.last_name} - is_active: {s.is_active}")
