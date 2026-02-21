# Update /api/attendance/today route to include clock_out and fix status logic
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the today route
old_route = '''@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for all employees"""
    try:
        today = date.today().isoformat()
        
        # Get all employees
        employees = Employee.query.filter_by(IsActive=True).all()
        
        # Get today's attendance records
        attendance = Attendance.query.filter_by(WorkDate=today).all()
        
        # Get today's approved leave requests
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        # Build result
        result = []
        emp_attendance = {a.EmpID: a for a in attendance}
        emp_leave = {lr.EmpID: lr for lr in leave_requests}
        
        for emp in employees:
            emp_id = emp.EmpID
            att = emp_attendance.get(emp_id)
            leave = emp_leave.get(emp_id)
            
            if att:
                status = 'Present'
                clock_in = att.ClockIn.strftime('%H:%M') if att.ClockIn else None
            elif leave:
                status = 'On Leave'
                clock_in = leave.LeaveType
            else:
                status = 'Not Clocked In'
                clock_in = None
            
            result.append({
                'emp_id': emp_id,
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'status': status,
                'clock_in': clock_in
            })
        
        return jsonify({
            'success': True,
            'date': today,
            'employees': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500'''

new_route = '''@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for all employees"""
    try:
        today = date.today().isoformat()
        
        # Get all employees
        employees = Employee.query.filter_by(IsActive=True).all()
        
        # Get today's attendance records
        attendance = Attendance.query.filter_by(WorkDate=today).all()
        
        # Get today's approved leave requests
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        # Build result
        result = []
        emp_attendance = {a.EmpID: a for a in attendance}
        emp_leave = {lr.EmpID: lr for lr in leave_requests}
        
        for emp in employees:
            emp_id = emp.EmpID
            att = emp_attendance.get(emp_id)
            leave = emp_leave.get(emp_id)
            
            if att:
                # Check clock in and clock out
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
                'status': status,
                'clock_in': clock_in,
                'clock_out': clock_out
            })
        
        return jsonify({
            'success': True,
            'date': today,
            'employees': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500'''

content = content.replace(old_route, new_route)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated /api/attendance/today route with clock_out and correct status logic")
