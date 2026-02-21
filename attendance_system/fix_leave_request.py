"""
Script to add department parameter to LeaveRequest creation in app.py
"""

import re

# Read the file
with open('attendance_system/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the LeaveRequest creation
old_code = '''        # Set status - auto-approve for admin manual entries
        status = 'Approved' if auto_approve else 'Pending'
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Status=status,
            ApprovedDate=datetime.utcnow() if auto_approve else None
        )'''

new_code = '''        # Get department from request data
        department = data.get('department', '')
        
        # Set status - auto-approve for admin manual entries
        status = 'Approved' if auto_approve else 'Pending'
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Department=department,
            Status=status,
            ApprovedDate=datetime.utcnow() if auto_approve else None
        )'''

content = content.replace(old_code, new_code)

# Write the file
with open('attendance_system/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed LeaveRequest creation to include Department parameter")
