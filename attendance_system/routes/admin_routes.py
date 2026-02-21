"""
Admin Routes for the Attendance System
These routes are enabled when running on Render (RENDER env var is set)
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, make_response
from datetime import datetime, date, timedelta
from functools import wraps
import time

# =====================================================
# RETRY DECORATOR
# =====================================================

def retry_on_db_error(max_retries=3, delay=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if 'database is locked' in str(e).lower() or 'locked' in str(e).lower():
                        time.sleep(delay * (attempt + 1))
                        from app import db
                        db.session.rollback()
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator

# =====================================================
# ADMIN BLUEPRINT
# =====================================================

admin_bp = Blueprint('admin', __name__)

# =====================================================
# ADMIN AUTHENTICATION
# =====================================================

@admin_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    from app import db, Employee, LeaveBalance, FiscalYear
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == 'RAV4Adventure2019':
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin.admin_input'))
        else:
            return render_template('admin/admin_login.html', error='Invalid password')
    return render_template('admin/admin_login.html')

@admin_bp.route('/admin-logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin-input')
def admin_input():
    """Render the admin input form for manual attendance entry"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    return render_template('admin/admin_input.html')

# =====================================================
# EMPLOYEE MANAGEMENT
# =====================================================

@admin_bp.route('/api/employees', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_employee():
    """Create new employee"""
    from app import db, Employee, LeaveBalance, FiscalYear, get_fiscal_year_python
    
    data = request.get_json()
    
    if data.get('name'):
        name_parts = data.get('name').strip().split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    else:
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
    
    employee_code = data.get('employee_code')
    if not employee_code:
        last_emp = Employee.query.order_by(Employee.EmpID.desc()).first()
        next_num = (last_emp.EmpID + 1) if last_emp else 1
        employee_code = f"EMP{str(next_num).zfill(3)}"
    
    join_date = data.get('join_date') or datetime.now().strftime('%Y-%m-%d')
    
    new_employee = Employee(
        EmployeeCode=employee_code,
        FirstName=first_name,
        LastName=last_name,
        Email=data.get('email'),
        Phone=data.get('phone'),
        JoinDate=datetime.strptime(join_date, '%Y-%m-%d').date(),
        Department=data.get('department'),
        Designation=data.get('designation')
    )
    
    db.session.add(new_employee)
    db.session.commit()
    
    annual_entitlement = data.get('annual_leave_entitlement')
    if annual_entitlement:
        current_fy = get_fiscal_year_python(datetime.now().date())
        
        fiscal_year = FiscalYear.query.filter_by(FiscalYear=current_fy).first()
        if not fiscal_year:
            fy_start = datetime(datetime.now().year, 10, 1).date() if datetime.now().month >= 10 else datetime(datetime.now().year - 1, 10, 1).date()
            fy_end = datetime(datetime.now().year + 1, 9, 30).date() if datetime.now().month >= 10 else datetime(datetime.now().year, 9, 30).date()
            fiscal_year = FiscalYear(FiscalYear=current_fy, StartDate=fy_start, EndDate=fy_end, IsActive=True)
            db.session.add(fiscal_year)
            db.session.commit()
        
        leave_balance = LeaveBalance(
            EmpID=new_employee.EmpID,
            FiscalYear=current_fy,
            AnnualDays=annual_entitlement,
            SickDays=data.get('sick_leave_entitlement', 10),
            CasualDays=data.get('casual_leave_entitlement', 5)
        )
        db.session.add(leave_balance)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Employee created successfully',
        'employee': new_employee.to_dict()
    }), 201


@admin_bp.route('/api/employees/reset-annual-leave', methods=['POST'])
def reset_annual_leave():
    """Reset all employees' annual leave balance to 21 days"""
    from app import db, Employee
    
    try:
        employees = Employee.query.filter_by(IsActive=True).all()
        
        reset_count = 0
        for emp in employees:
            emp.AnnualLeaveBalance = 21.0
            reset_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully reset annual leave balance for {reset_count} employees to 21 days'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to reset annual leave: {str(e)}'
        }), 500


# =====================================================
# ATTENDANCE MANAGEMENT
# =====================================================

@admin_bp.route('/api/attendance', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_attendance():
    """Create new attendance record with Saturday check"""
    from app import db, Attendance
    
    data = request.get_json()
    
    work_date = datetime.strptime(data.get('work_date'), '%Y-%m-%d').date()
    
    if work_date.weekday() == 6:  # Sunday
        return jsonify({
            'success': False,
            'error': 'Cannot create attendance for Sunday'
        }), 400
    
    is_saturday = work_date.weekday() == 5
    expected_hours = 5 if is_saturday else 8
    day_type = 'Saturday (5hrs)' if is_saturday else 'Full Day (8hrs)'
    
    new_attendance = Attendance(
        EmpID=data.get('emp_id'),
        WorkDate=work_date,
        ClockIn=datetime.strptime(data.get('clock_in'), '%H:%M').time(),
        ClockOut=datetime.strptime(data.get('clock_out'), '%H:%M').time() if data.get('clock_out') else None,
        DayType=day_type,
        ExpectedHours=expected_hours,
        Notes=data.get('notes')
    )
    
    db.session.add(new_attendance)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Attendance recorded',
        'attendance': new_attendance.to_dict()
    }), 201


@admin_bp.route('/api/attendance/<int:attendance_id>', methods=['PUT'])
@retry_on_db_error(max_retries=3)
def update_attendance(attendance_id):
    """Update attendance (clock out)"""
    from app import db, Attendance
    
    attendance = Attendance.query.get_or_404(attendance_id)
    data = request.get_json()
    
    if data.get('clock_out'):
        attendance.ClockOut = datetime.strptime(data.get('clock_out'), '%H:%M').time()
    
    if data.get('notes'):
        attendance.Notes = data.get('notes')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Attendance updated',
        'attendance': attendance.to_dict()
    })


# =====================================================
# LEAVE MANAGEMENT
# =====================================================

@admin_bp.route('/api/leave-requests', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_leave_request():
    """Create leave request (admin version with auto-approve)"""
    from app import db, LeaveRequest, LeaveBalance, get_fiscal_year_python
    
    data = request.get_json()

    emp_id = data.get('emp_id')
    leave_type = data.get('leave_type')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    reason = data.get('reason', '')

    # Auto-approve for manual admin entries
    auto_approve = data.get('auto_approve', False)

    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    if not leave_type:
        return jsonify({'success': False, 'error': 'Leave type is required'}), 400
    
    # Normalize leave type
    if leave_type == 'Sick Leave':
        leave_type = 'Sick'
    elif leave_type == 'Annual Leave':
        leave_type = 'Annual'
    
    # Auto-set reason to Manual Entry if missing for admin entries
    if auto_approve and not reason:
        reason = 'Manual Entry'
    
    if not start_date_str:
        return jsonify({'success': False, 'error': 'Start date is required'}), 400
    if not end_date_str:
        return jsonify({'success': False, 'error': 'End date is required'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': f'Invalid date format. Use YYYY-MM-DD. Error: {str(e)}'}), 400

    try:
        from app import calculate_leave_days_python
        total_days = calculate_leave_days_python(start_date, end_date)

        if leave_type in ['Annual', 'Sick']:
            fiscal_year = get_fiscal_year_python(start_date)
            balance = LeaveBalance.query.filter_by(EmpID=emp_id, FiscalYear=fiscal_year).first()

            if not balance:
                return jsonify({'success': False, 'error': f'No leave balance found for fiscal year {fiscal_year}'}), 400

            if leave_type == 'Annual':
                available = float(balance.AnnualDays - balance.UsedAnnualDays)
                if total_days > available:
                    return jsonify({'success': False, 'error': f'Insufficient annual leave. Available: {available}'}), 400
            elif leave_type == 'Sick':
                available = float(balance.SickDays - balance.UsedSickDays)
                if total_days > available:
                    return jsonify({'success': False, 'error': f'Insufficient sick leave. Available: {available}'}), 400

        department = data.get('department', '')
        
        # Admin always auto-approves
        status = 'Approved'
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Department=department,
            Status=status,
            ApprovedDate=datetime.utcnow()
        )

        db.session.add(new_request)
        db.session.commit()
        
        # Deduct from leave balance immediately for admin entries
        if leave_type in ['Annual', 'Sick']:
            fiscal_year = get_fiscal_year_python(start_date)
            balance = LeaveBalance.query.filter_by(EmpID=emp_id, FiscalYear=fiscal_year).first()
            if balance:
                if leave_type == 'Annual':
                    balance.UsedAnnualDays = float(balance.UsedAnnualDays) + float(total_days)
                elif leave_type == 'Sick':
                    balance.UsedSickDays = float(balance.UsedSickDays) + float(total_days)
                db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Leave request approved',
            'leave_request': new_request.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500


@admin_bp.route('/api/leave-requests/<int:request_id>/approve', methods=['POST'])
def approve_leave_request(request_id):
    """Approve a leave request and deduct from balance"""
    from app import db, LeaveRequest, Employee, LeaveBalance, Notification, get_fiscal_year_python
    
    try:
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        if leave_request.Status != 'Pending':
            return jsonify({'success': False, 'error': 'Leave request is not pending'}), 400
        
        leave_request.Status = 'Approved'
        leave_request.ApprovedDate = datetime.utcnow()
        
        emp = Employee.query.get(leave_request.EmpID)
        
        fiscal_year = get_fiscal_year_python(leave_request.StartDate)
        balance = LeaveBalance.query.filter_by(EmpID=leave_request.EmpID, FiscalYear=fiscal_year).first()
        
        if balance:
            if leave_request.LeaveType == 'Annual':
                balance.UsedAnnualDays = float(balance.UsedAnnualDays) + float(leave_request.TotalDays)
            elif leave_request.LeaveType == 'Sick':
                balance.UsedSickDays = float(balance.UsedSickDays) + float(leave_request.TotalDays)
        
        if leave_request.LeaveType == 'Annual' and emp:
            total_days = float(leave_request.TotalDays)
            current_balance = float(emp.AnnualLeaveBalance) if emp.AnnualLeaveBalance else 21
            new_balance = max(0, current_balance - total_days)
            emp.AnnualLeaveBalance = new_balance
        
        notification = Notification(
            emp_id=leave_request.EmpID,
            message=f'Your leave request for {leave_request.StartDate.strftime("%Y-%m-%d")} has been approved by Aero Instrument.'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request approved',
            'leave_request': leave_request.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/leave-requests/<int:request_id>/reject', methods=['POST'])
def reject_leave_request(request_id):
    """Reject a leave request"""
    from app import db, LeaveRequest
    
    try:
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        if leave_request.Status != 'Pending':
            return jsonify({'success': False, 'error': 'Only pending requests can be rejected'}), 400
        
        leave_request.Status = 'Rejected'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request rejected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/leave-requests/<int:request_id>', methods=['DELETE'])
def delete_leave_request(request_id):
    """Delete a leave request"""
    from app import db, LeaveRequest
    
    try:
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        db.session.delete(leave_request)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Leave request deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/delete_leave/<int:id>', methods=['POST'])
def delete_leave(id):
    """Delete a rejected leave request"""
    from app import db, LeaveRequest
    
    try:
        leave_request = LeaveRequest.query.get(id)
        
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        if leave_request.Status != 'Rejected':
            return jsonify({'success': False, 'error': 'Only rejected requests can be deleted'}), 400
        
        db.session.delete(leave_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# HOLIDAY MANAGEMENT
# =====================================================

@admin_bp.route('/api/holidays', methods=['GET'])
def get_holidays():
    """Get all holidays"""
    from app import Holiday
    
    try:
        holidays = Holiday.query.order_by(Holiday.holiday_date).all()
        return jsonify({
            'success': True,
            'holidays': [h.to_dict() for h in holidays]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/holidays', methods=['POST'])
def add_holiday():
    """Add a new holiday"""
    from app import db, Holiday
    
    try:
        data = request.get_json()
        holiday = Holiday(
            holiday_name=data['holiday_name'],
            holiday_date=datetime.strptime(data['holiday_date'], '%Y-%m-%d').date()
        )
        db.session.add(holiday)
        db.session.commit()
        return jsonify({
            'success': True,
            'holiday': holiday.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    """Delete a holiday"""
    from app import db, Holiday
    
    try:
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({'success': False, 'error': 'Holiday not found'}), 404
        
        db.session.delete(holiday)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Holiday deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# REPORT ROUTES
# =====================================================

@admin_bp.route('/api/reports/attendance-pdf')
def generate_attendance_pdf():
    """Generate attendance PDF report"""
    from app import Attendance, Employee
    from pdf_report import generate_attendance_pdf as gen_att_pdf
    
    try:
        start_date = request.args.get('start_date') or datetime.now().strftime('%Y-%m-01')
        end_date = request.args.get('end_date') or datetime.now().strftime('%Y-%m-%d')
        
        attendance = Attendance.query.filter(
            Attendance.WorkDate >= start_date,
            Attendance.WorkDate <= end_date
        ).order_by(Attendance.WorkDate.desc()).all()
        
        employees = {e.EmpID: f"{e.FirstName} {e.LastName}" for e in Employee.query.all()}
        pdf = gen_att_pdf(attendance, employees, start_date, end_date)
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_report_{start_date}_{end_date}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/reports/leave-pdf')
def generate_leave_pdf():
    """Generate leave PDF report"""
    from app import LeaveRequest, Employee
    from pdf_report import generate_leave_pdf as gen_leave_pdf
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = LeaveRequest.query.filter(LeaveRequest.Status == 'Approved')
        
        if start_date and end_date:
            query = query.filter(
                LeaveRequest.StartDate <= end_date,
                LeaveRequest.EndDate >= start_date
            )
        elif start_date:
            query = query.filter(LeaveRequest.EndDate >= start_date)
        elif end_date:
            query = query.filter(LeaveRequest.StartDate <= end_date)
        
        leave_requests = query.order_by(LeaveRequest.StartDate.desc()).all()
        
        employees = {e.EmpID: f"{e.FirstName} {e.LastName}" for e in Employee.query.all()}
        emp_departments = {e.EmpID: e.Department for e in Employee.query.all()}
        
        for lr in leave_requests:
            if not lr.Department:
                lr.Department = emp_departments.get(lr.EmpID, '')
        
        pdf = gen_leave_pdf(leave_requests, employees, start_date, end_date)
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=leave_report_{start_date or "all"}_{end_date or "all"}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/reports/monthly-attendance-summary')
def get_monthly_attendance_summary():
    """Get monthly attendance summary for all employees"""
    from app import Attendance, Employee, Holiday
    
    try:
        year = request.args.get('year', type=int, default=datetime.now().year)
        month = request.args.get('month', type=int, default=datetime.now().month)
        
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1)
        else:
            last_day = date(year, month + 1, 1)
        
        try:
            employees = Employee.query.filter_by(IsActive=True).all()
        except Exception as e:
            print(f"Error fetching employees: {e}")
            employees = []
        
        try:
            attendance_records = Attendance.query.filter(
                Attendance.WorkDate >= first_day,
                Attendance.WorkDate < last_day,
                Attendance.ClockIn.isnot(None)
            ).all()
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            attendance_records = []
        
        try:
            holidays = Holiday.query.filter(
                Holiday.holiday_date >= first_day,
                Holiday.holiday_date < last_day
            ).all()
            holiday_dates = {h.holiday_date for h in holidays}
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            holiday_dates = set()
        
        target_days = 0
        current = first_day
        while current < last_day:
            if current.weekday() != 6 and current not in holiday_dates:
                target_days += 1
            current = date.fromordinal(current.toordinal() + 1)
        
        summary = []
        
        for emp in employees:
            emp_id = emp.EmpID
            emp_attendance = [a for a in attendance_records if a.EmpID == emp_id and a.ClockIn]
            unique_days = len(set(a.WorkDate for a in emp_attendance))
            
            summary.append({
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'month': f"{first_day.strftime('%B %Y')}",
                'days_present': unique_days,
                'target_days': target_days
            })
        
        return jsonify({
            'success': True,
            'month': first_day.strftime('%B %Y'),
            'year': year,
            'month_num': month,
            'target_days': target_days,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error in monthly attendance summary: {e}")
        return jsonify({'success': True, 'summary': []}), 200


@admin_bp.route('/api/reports/fiscal-year-summary')
def get_fiscal_year_summary():
    """Get Fiscal Year Summary for all employees"""
    from app import Attendance, Employee, LeaveRequest
    
    try:
        fy_start_date = date(2025, 10, 1)
        fy_end_date = date.today()
        
        employees = Employee.query.filter_by(IsActive=True).all()
        
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate >= fy_start_date,
            LeaveRequest.StartDate <= fy_end_date,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        attendance_records = Attendance.query.filter(
            Attendance.WorkDate >= fy_start_date,
            Attendance.WorkDate <= fy_end_date
        ).all()
        
        summary = []
        
        for emp in employees:
            emp_id = emp.EmpID
            
            total_hours = 0.0
            emp_attendance = [a for a in attendance_records if a.EmpID == emp_id]
            
            for att in emp_attendance:
                if att.ClockIn and att.ClockOut:
                    clock_in_mins = att.ClockIn.hour * 60 + att.ClockIn.minute
                    clock_out_mins = att.ClockOut.hour * 60 + att.ClockOut.minute
                    hours_worked = (clock_out_mins - clock_in_mins) / 60.0
                    
                    if att.WorkDate.weekday() == 5:
                        max_hours = 5
                    else:
                        max_hours = 8
                    
                    total_hours += min(hours_worked, max_hours)
            
            emp_leaves = [lr for lr in leave_requests if lr.EmpID == emp_id]
            annual_leave = sum(float(lr.TotalDays) for lr in emp_leaves if lr.LeaveType == 'Annual')
            sick_leave = sum(float(lr.TotalDays) for lr in emp_leaves if lr.LeaveType == 'Sick')
            unpaid_absence = sum(float(lr.TotalDays) for lr in emp_leaves if lr.LeaveType == 'Absent')
            
            summary.append({
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'days_present': len(set(a.WorkDate for a in emp_attendance if a.ClockIn)),
                'annual_leave_taken': round(annual_leave, 1),
                'sick_days_taken': round(sick_leave, 1),
                'unpaid_absences': round(unpaid_absence, 1),
                'annual_leave_remaining': round(21 - annual_leave, 1)
            })
        
        return jsonify({
            'success': True,
            'fiscal_year': 2026,
            'start_date': fy_start_date.isoformat(),
            'end_date': fy_end_date.isoformat(),
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
