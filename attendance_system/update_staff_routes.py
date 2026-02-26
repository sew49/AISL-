# Script to update staff_routes.py with improved attendance logic

# Read the file
with open('routes/staff_routes.py', 'r') as f:
    content = f.read()

# The old function
old_func = '''@staff_bp.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for all employees"""
    from flask import current_app
    db = current_app.db
    Attendance = current_app.Attendance
    Employee = current_app.Employee
    LeaveRequest = current_app.LeaveRequest
    
    try:
    # Use Nairobi timezone for today's date (staff is in Nairobi, server is in Oregon)
        today = get_nairobi_today()
        
        employees = Employee.query.filter_by(IsActive=True).all()
        attendance = db.session.query(Attendance).filter(Attendance.WorkDate == today).all()
        
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        result = []
        emp_attendance = {a.EmpID: a for a in attendance}
        emp_leave = {lr.EmpID: lr for lr in leave_requests}
        
        for emp in employees:
            emp_id = emp.EmpID
            att = emp_attendance.get(emp_id)
            leave = emp_leave.get(emp_id)
            
            if att:
                clock_in = att.ClockIn.strftime('%H:%M') if att.ClockIn else None
                clock_out = att.ClockOut.strftime('%H:%M') if att.ClockOut else None
                
                if clock_in and clock_out:
                    status = 'Clocked Out'
                elif clock_in:
                    status = 'Present'
                else:
                    status = 'Not Clocked In'
            elif leave:
                status = 'On Leave'
                clock_in = leave.LeaveType
                clock_out = None
            else:
                status = 'Not Clocked In'
                clock_in = None
                clock_out = None
            
            result.append({
                'emp_id': emp_id,
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'department': emp.Department or '',
                'status': status,
                'clock_in': clock_in,
                'clock_out': clock_out
            })
        
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'employees': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500'''

# The new function
new_func = '''@staff_bp.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for all employees using flexible matching"""
    from flask import current_app
    db = current_app.db
    Attendance = current_app.Attendance
    Employee = current_app.Employee
    LeaveRequest = current_app.LeaveRequest
    
    try:
        # Use Nairobi timezone for today's date (staff is in Nairobi, server is in Oregon)
        nairobi_tz = pytz.timezone('Africa/Nairobi')
        now_nairobi = datetime.now(nairobi_tz)
        today = now_nairobi.date()
        
        employees = Employee.query.filter_by(IsActive=True).all()
        
        # Get all attendance records for today using Nairobi date = db.session.query(Attendance).filter
        attendance_records(
            Attendance.WorkDate == today
        ).all()
        
        # Get leave requests for today
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        # Build dictionaries for quick lookup
        emp_attendance = {a.EmpID: a for a in attendance_records}
        emp_leave = {lr.EmpID: lr for lr in leave_requests}
        
        result = []
        
        for emp in employees:
            emp_id = emp.EmpID
            att = emp_attendance.get(emp_id)
            leave = emp_leave.get(emp_id)
            
            clock_in = None
            clock_out = None
            status = 'Not Clocked In'
            is_recent = False
            
            if att:
                clock_in = att.ClockIn.strftime('%H:%M') if att.ClockIn else None
                clock_out = att.ClockOut.strftime('%H:%M') if att.ClockOut else None
                
                # Check if this is a recent clock-in (within 14 hours)
                if att.ClockIn:
                    # Combine work date with clock in time
                    clock_in_datetime = datetime.combine(att.WorkDate, att.ClockIn)
                    clock_in_datetime = nairobi_tz.localize(clock_in_datetime)
                    hours_since_clock_in = (now_nairobi - clock_in_datetime).total_seconds() / 3600
                    
                    if hours_since_clock_in <= 14:
                        is_recent = True
                
                if clock_in and clock_out:
                    status = 'Clocked Out'
                    is_recent = False  # Not recent anymore since they clocked out
                elif clock_in and is_recent:
                    status = 'Present'
                elif clock_in:
                    status = 'Clocked In'
                else:
                    status = 'Not Clocked In'
            elif leave:
                status = 'On Leave'
                clock_in = leave.LeaveType
                clock_out = None
            
            result.append({
                'emp_id': emp_id,
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'department': emp.Department or '',
                'status': status,
                'clock_in': clock_in,
                'clock_out': clock_out,
                'is_recent': is_recent  # For UI to apply green color
            })
        
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'nairobi_time': now_nairobi.isoformat(),
            'employees': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500'''

# Replace
new_content = content.replace(old_func, new_func)

# Write the file
with open('routes/staff_routes.py', 'w') as f:
    f.write(new_content)

print('File updated successfully')
