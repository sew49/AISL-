"""
Staff Routes for the Attendance System
These routes are enabled when running locally (no RENDER env var)
"""
import pytz
from flask import Blueprint, request, jsonify, render_template, session
from datetime import datetime, date, timezone, timedelta
from functools import wraps

# Nairobi timezone (Africa/Nairobi - UTC+3)
NAIROBI_TIMEZONE = pytz.timezone('Africa/Nairobi')

def get_nairobi_now():
    """Get current datetime in Nairobi timezone"""
    return datetime.now(NAIROBI_TIMEZONE)

def get_nairobi_today():
    """Get today's date in Nairobi timezone"""
    return get_nairobi_now().date()

# =====================================================
# STAFF BLUEPRINT
# =====================================================

staff_bp = Blueprint('staff', __name__)

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
                        import time
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator

# =====================================================
# STAFF ROUTES
# =====================================================

@staff_bp.route('/')
def index():
    """Render the main dashboard for staff"""
    return render_template('staff/index.html')


# =====================================================
# ATTENDANCE (CLOCK IN/OUT)
# =====================================================

@staff_bp.route('/api/attendance', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_attendance():
    """Staff clock in"""
    from flask import current_app
    db = current_app.db
    LeaveRequest = current_app.LeaveRequest
    
    data = request.get_json()
    
    work_date = datetime.strptime(data.get('work_date'), '%Y-%m-%d').date()
    emp_id = data.get('emp_id')
    
    # Check if employee has an approved leave request for this date
    leave_check = LeaveRequest.query.filter(
        LeaveRequest.EmpID == emp_id,
        LeaveRequest.StartDate <= work_date,
        LeaveRequest.EndDate >= work_date,
        LeaveRequest.Status == 'Approved'
    ).first()
    
    if leave_check:
        return jsonify({
            'success': False,
            'error': 'Access Denied: You are currently on an approved leave.'
        }), 403
    
    if work_date.weekday() == 6:  # Sunday
        return jsonify({
            'success': False,
            'error': 'Cannot create attendance for Sunday'
        }), 400
    
    is_saturday = work_date.weekday() == 5
    expected_hours = 5 if is_saturday else 8
    day_type = 'Saturday (5hrs)' if is_saturday else 'Full Day (8hrs)'
    
    # Get model class from current app
    Attendance = current_app.Attendance
    
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


@staff_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records"""
    from flask import current_app
    Attendance = current_app.Attendance
    
    emp_id = request.args.get('emp_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Attendance.query
    
    if emp_id:
        query = query.filter_by(EmpID=emp_id)
    if start_date:
        query = query.filter(Attendance.WorkDate >= start_date)
    if end_date:
        query = query.filter(Attendance.WorkDate <= end_date)
    
    attendance = query.order_by(Attendance.WorkDate.desc()).all()
    
    return jsonify({
        'success': True,
        'count': len(attendance),
        'attendance': [a.to_dict() for a in attendance]
    })


@staff_bp.route('/api/attendance/<int:attendance_id>', methods=['PUT'])
@retry_on_db_error(max_retries=3)
def update_attendance(attendance_id):
    """Update attendance (clock out)"""
    from flask import current_app
    db = current_app.db
    Attendance = current_app.Attendance
    
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


@staff_bp.route('/api/attendance/today', methods=['GET'])
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
        
        # Get all attendance records for the last 7 days (to handle flexible matching)
        # This allows showing recent clock-ins even if recorded on previous day
        from datetime import timedelta
        week_ago = today - timedelta(days=7)
        all_recent_attendance = Attendance.query.filter(
            Attendance.WorkDate >= week_ago,
            Attendance.WorkDate <= today
        ).order_by(Attendance.WorkDate.desc()).all()
        
        # Get leave requests for today
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today,
            LeaveRequest.Status == 'Approved'
        ).all()
        
        # Build dictionaries for quick lookup - get most recent record per employee
        emp_latest_attendance = {}
        for att in all_recent_attendance:
            if att.EmpID not in emp_latest_attendance:
                emp_latest_attendance[att.EmpID] = att
        
        emp_leave = {lr.EmpID: lr for lr in leave_requests}
        
        result = []
        
        for emp in employees:
            emp_id = emp.EmpID
            att = emp_latest_attendance.get(emp_id)
            leave = emp_leave.get(emp_id)
            
            clock_in = None
            clock_out = None
            status = 'Not Clocked In'
            is_recent = False
            
            if att:
                clock_in = att.ClockIn.strftime('%H:%M') if att.ClockIn else None
                clock_out = att.ClockOut.strftime('%H:%M') if att.ClockOut else None
                
                # Check if this is a recent clock-in (within 14 hours from Nairobi time)
                if att.ClockIn and not att.ClockOut:
                    # Combine work date with clock in time
                    clock_in_datetime = datetime.combine(att.WorkDate, att.ClockIn)
                    clock_in_datetime = nairobi_tz.localize(clock_in_datetime)
                    hours_since_clock_in = (now_nairobi - clock_in_datetime).total_seconds() / 3600
                    
                    if hours_since_clock_in <= 14:
                        is_recent = True
                
                if clock_in and clock_out:
                    status = 'Clocked Out'
                    is_recent = False
                elif clock_in and is_recent:
                    status = 'Present'  # GREEN status
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
                'is_recent': is_recent,  # For UI to apply green color
                'work_date': att.WorkDate.isoformat() if att else None
            })
        
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'nairobi_time': now_nairobi.isoformat(),
            'employees': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# EMPLOYEE (READ ONLY FOR STAFF)
# =====================================================

@staff_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    from flask import current_app
    Employee = current_app.Employee
    
    employees = Employee.query.filter_by(IsActive=True).all()
    return jsonify({
        'success': True,
        'count': len(employees),
        'employees': [e.to_dict() for e in employees]
    })


# =====================================================
# LEAVE REQUESTS (STAFF)
# =====================================================

@staff_bp.route('/api/leave-requests', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_leave_request():
    """Create leave request (staff version - always pending)"""
    from flask import current_app
    db = current_app.db
    LeaveRequest = current_app.LeaveRequest
    LeaveBalance = current_app.LeaveBalance
    get_fiscal_year_python = current_app.get_fiscal_year_python
    calculate_leave_days_python = current_app.calculate_leave_days_python
    
    data = request.get_json()

    emp_id = data.get('emp_id')
    leave_type = data.get('leave_type')
    day_type = data.get('day_type', '1.0')  # Default to Full Day (1.0)
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    reason = data.get('reason', '')

    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    if not leave_type:
        return jsonify({'success': False, 'error': 'Leave type is required'}), 400
    
    # Normalize leave type
    if leave_type == 'Sick Leave':
        leave_type = 'Sick'
    elif leave_type == 'Annual Leave':
        leave_type = 'Annual'
    
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
        # Get the multiplier from the dropdown (Full Day = 1.0, Half Day = 0.5)
        # Default to 1.0 if not provided
        try:
            multiplier = float(day_type) if day_type else 1.0
        except (ValueError, TypeError):
            multiplier = 1.0
        
        # Step 1: Calculate calendar days using the existing logic
        # (Mon-Fri: 1.0, Sat: 0.5, Sun: 0.0)
        calendar_days = calculate_leave_days_python(start_date, end_date)
        
        # Step 2: Apply the multiplier from the dropdown
        total_days = calendar_days * multiplier
        
        print(f"DEBUG Leave: Start={start_date}, End={end_date}, Calendar Days={calendar_days}, Multiplier={multiplier}, Final Days={total_days}")

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
        
        # Staff always submits as Pending
        status = 'Pending'
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Department=department,
            Status=status
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Leave request submitted',
            'leave_request': new_request.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500


@staff_bp.route('/api/leave-requests', methods=['GET'])
def get_leave_requests():
    """Get all leave requests"""
    from flask import current_app
    LeaveRequest = current_app.LeaveRequest
    
    try:
        leave_requests = LeaveRequest.query.order_by(LeaveRequest.StartDate.desc()).all()
        return jsonify({
            'success': True,
            'leave_requests': [lr.to_dict() for lr in leave_requests]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# LEAVE BALANCES (STAFF)
# =====================================================

@staff_bp.route('/api/leave-balances', methods=['GET'])
def get_leave_balances():
    """Get leave balances"""
    from flask import current_app
    LeaveBalance = current_app.LeaveBalance
    
    emp_id = request.args.get('emp_id', type=int)
    fiscal_year = request.args.get('fiscal_year', type=int)
    
    query = LeaveBalance.query
    
    if emp_id:
        query = query.filter_by(EmpID=emp_id)
    if fiscal_year:
        query = query.filter_by(FiscalYear=fiscal_year)
    
    balances = query.all()
    
    return jsonify({
        'success': True,
        'count': len(balances),
        'leave_balances': [b.to_dict() for b in balances]
    })


# =====================================================
# NOTIFICATIONS (STAFF)
# =====================================================

@staff_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for an employee"""
    from flask import current_app
    Notification = current_app.Notification
    
    emp_id = request.args.get('emp_id', type=int)
    
    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    try:
        notifications = Notification.query.filter_by(emp_id=emp_id).order_by(Notification.created_at.desc()).all()
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@staff_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    from flask import current_app
    db = current_app.db
    Notification = current_app.Notification
    
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@staff_bp.route('/api/notifications/unread-count', methods=['GET'])
def get_unread_count():
    """Get count of unread notifications for an employee"""
    from flask import current_app
    Notification = current_app.Notification
    
    emp_id = request.args.get('emp_id', type=int)
    
    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    try:
        count = Notification.query.filter_by(emp_id=emp_id, is_read=False).count()
        return jsonify({
            'success': True,
            'unread_count': count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
