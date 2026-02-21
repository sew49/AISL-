"""
Script to add Leave Approval functionality
1. Add Approve button to admin leave table
2. Create API route for leave approval
3. Add Notifications table and functionality
4. Add notification bell to main index.html
"""

# =====================================================
# PART 1: Update app.py with new routes and model
# =====================================================

app_py_content = '''# =====================================================
# ATTENDANCE SYSTEM - FLASK API
# =====================================================

from flask import Flask, request, jsonify, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)

# Database Configuration
db_type = os.getenv('DB_TYPE', 'sqlite')

if db_type == 'postgresql':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/attendance_system'
    )
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
    print("Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =====================================================
# DATABASE MODELS
# =====================================================

class FiscalYear(db.Model):
    __tablename__ = 'fiscalyears'
    
    FiscalYearID = db.Column(db.Integer, primary_key=True)
    FiscalYear = db.Column(db.Integer, unique=True, nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    IsActive = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'fiscal_year_id': self.FiscalYearID,
            'fiscal_year': self.FiscalYear,
            'start_date': self.StartDate.isoformat(),
            'end_date': self.EndDate.isoformat(),
            'is_active': self.IsActive
        }


class Employee(db.Model):
    __tablename__ = 'employees'
    
    EmpID = db.Column(db.Integer, primary_key=True)
    EmployeeCode = db.Column(db.String(10), unique=True, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True)
    Phone = db.Column(db.String(20))
    JoinDate = db.Column(db.Date, nullable=False)
    Department = db.Column(db.String(50))
    Designation = db.Column(db.String(50))
    IsActive = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'emp_id': self.EmpID,
            'employee_code': self.EmployeeCode,
            'first_name': self.FirstName,
            'last_name': self.LastName,
            'email': self.Email,
            'phone': self.Phone,
            'join_date': self.JoinDate.isoformat() if self.JoinDate else None,
            'department': self.Department,
            'designation': self.Designation,
            'is_active': self.IsActive
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    AttendanceID = db.Column(db.Integer, primary_key=True)
    EmpID = db.Column(db.Integer, db.ForeignKey('employees.EmpID'), nullable=False)
    WorkDate = db.Column(db.Date, nullable=False)
    ClockIn = db.Column(db.Time, nullable=False)
    ClockOut = db.Column(db.Time)
    DayType = db.Column(db.String(20), default='Full Day')
    ExpectedHours = db.Column(db.Integer, default=8)
    WorkHours = db.Column(db.Numeric(4, 2), default=0)
    Status = db.Column(db.String(20), default='Present')
    Notes = db.Column(db.Text)
    
    employee = db.relationship('Employee', backref='attendance_records')
    
    def to_dict(self):
        return {
            'attendance_id': self.AttendanceID,
            'emp_id': self.EmpID,
            'work_date': self.WorkDate.isoformat() if self.WorkDate else None,
            'clock_in': self.ClockIn.strftime('%H:%M') if self.ClockIn else None,
            'clock_out': self.ClockOut.strftime('%H:%M') if self.ClockOut else None,
            'day_type': self.DayType,
            'expected_hours': self.ExpectedHours,
            'work_hours': float(self.WorkHours) if self.WorkHours else 0,
            'status': self.Status,
            'notes': self.Notes
        }


class LeaveBalance(db.Model):
    __tablename__ = 'leavebalances'
    
    BalanceID = db.Column(db.Integer, primary_key=True)
    EmpID = db.Column(db.Integer, db.ForeignKey('employees.EmpID'), nullable=False)
    FiscalYear = db.Column(db.Integer, db.ForeignKey('fiscalyears.FiscalYear'), nullable=False)
    AnnualDays = db.Column(db.Numeric(5, 2), default=0)
    SickDays = db.Column(db.Numeric(5, 2), default=0)
    AbsentDays = db.Column(db.Numeric(5, 2), default=0)
    CasualDays = db.Column(db.Numeric(5, 2), default=0)
    UsedAnnualDays = db.Column(db.Numeric(5, 2), default=0)
    UsedSickDays = db.Column(db.Numeric(5, 2), default=0)
    UsedCasualDays = db.Column(db.Numeric(5, 2), default=0)
    CarryForwardDays = db.Column(db.Numeric(5, 2), default=0)
    
    employee = db.relationship('Employee', backref='leave_balances')
    fiscal_year = db.relationship('FiscalYear')
    
    def to_dict(self):
        return {
            'balance_id': self.BalanceID,
            'emp_id': self.EmpID,
            'fiscal_year': self.FiscalYear,
            'annual_days': float(self.AnnualDays),
            'sick_days': float(self.SickDays),
            'absent_days': float(self.AbsentDays),
            'casual_days': float(self.CasualDays),
            'used_annual_days': float(self.UsedAnnualDays),
            'used_sick_days': float(self.UsedSickDays),
            'used_casual_days': float(self.UsedCasualDays),
            'carry_forward_days': float(self.CarryForwardDays),
            'remaining_annual': float(self.AnnualDays - self.UsedAnnualDays),
            'remaining_sick': float(self.SickDays - self.UsedSickDays),
            'total_available_annual': float(self.AnnualDays - self.UsedAnnualDays + self.CarryForwardDays)
        }


class LeaveRequest(db.Model):
    __tablename__ = 'leaverequests'
    
    RequestID = db.Column(db.Integer, primary_key=True)
    EmpID = db.Column(db.Integer, db.ForeignKey('employees.EmpID'), nullable=False)
    LeaveType = db.Column(db.String(20), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    TotalDays = db.Column(db.Numeric(5, 2), nullable=False)
    Reason = db.Column(db.Text)
    Status = db.Column(db.String(20), default='Pending')
    ApprovedBy = db.Column(db.Integer, db.ForeignKey('employees.EmpID'))
    ApprovedDate = db.Column(db.DateTime)
    RequestedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', foreign_keys=[EmpID], backref='leave_requests')
    approver = db.relationship('Employee', foreign_keys=[ApprovedBy])
    
    def to_dict(self):
        return {
            'request_id': self.RequestID,
            'emp_id': self.EmpID,
            'leave_type': self.LeaveType,
            'start_date': self.StartDate.isoformat() if self.StartDate else None,
            'end_date': self.EndDate.isoformat() if self.EndDate else None,
            'total_days': float(self.TotalDays),
            'reason': self.Reason,
            'status': self.Status,
            'approved_by': self.ApprovedBy,
            'approved_date': self.ApprovedDate.isoformat() if self.ApprovedDate else None,
            'requested_at': self.RequestedAt.isoformat() if self.RequestedAt else None
        }


class Holiday(db.Model):
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    holiday_name = db.Column(db.String(100), nullable=False)
    holiday_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'holiday_name': self.holiday_name,
            'holiday_date': self.holiday_date.isoformat() if self.holiday_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.EmpID'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# ROUTES
# =====================================================

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')


@app.route('/admin-input')
def admin_input():
    """Render the admin input form for manual attendance entry"""
    return render_template('admin_input.html')


@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    employees = Employee.query.filter_by(IsActive=True).all()
    return jsonify({
        'success': True,
        'count': len(employees),
        'employees': [e.to_dict() for e in employees]
    })


@app.route('/api/employees', methods=['POST'])
def create_employee():
    """Create new employee"""
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


@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records"""
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


@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    """Create new attendance record with Saturday check"""
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


@app.route('/api/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    """Update attendance (clock out)"""
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


@app.route('/api/leave-balances', methods=['GET'])
def get_leave_balances():
    """Get leave balances"""
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


@app.route('/api/leave-requests', methods=['POST'])
def create_leave_request():
    """Create leave request"""
    data = request.get_json()

    emp_id = data.get('emp_id')
    leave_type = data.get('leave_type')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    reason = data.get('reason', '')

    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    if not leave_type:
        return jsonify({'success': False, 'error': 'Leave type is required'}), 400
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

        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Status='Pending'
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


@app.route('/api/leave-requests', methods=['GET'])
def get_leave_requests():
    """Get all leave requests"""
    try:
        leave_requests = LeaveRequest.query.order_by(LeaveRequest.StartDate.desc()).all()
        return jsonify({
            'success': True,
            'leave_requests': [lr.to_dict() for lr in leave_requests]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leave-requests/<int:request_id>', methods=['DELETE'])
def delete_leave_request(request_id):
    """Delete a leave request"""
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


@app.route('/api/leave-requests/<int:request_id>/approve', methods=['POST'])
def approve_leave_request(request_id):
    """Approve a leave request and deduct from balance"""
    try:
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        if leave_request.Status != 'Pending':
            return jsonify({'success': False, 'error': 'Leave request is not pending'}), 400
        
        # Update status to Approved
        leave_request.Status = 'Approved'
        leave_request.ApprovedDate = datetime.utcnow()
        
        # Deduct from leave balance
        fiscal_year = get_fiscal_year_python(leave_request.StartDate)
        balance = LeaveBalance.query.filter_by(EmpID=leave_request.EmpID, FiscalYear=fiscal_year).first()
        
        if balance:
            if leave_request.LeaveType == 'Annual':
                balance.UsedAnnualDays = float(balance.UsedAnnualDays) + float(leave_request.TotalDays)
            elif leave_request.LeaveType == 'Sick':
                balance.UsedSickDays = float(balance.UsedSickDays) + float(leave_request.TotalDays)
        
        # Create notification for employee
        emp = Employee.query.get(leave_request.EmpID)
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


# =====================================================
# NOTIFICATION ROUTES
# =====================================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for an employee"""
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


@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notifications/unread-count', methods=['GET'])
def get_unread_count():
    """Get count of unread notifications for an employee"""
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


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_leave_days_python(start_date, end_date):
    """Calculate leave days excluding Sundays"""
    total_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        dow = current_date.weekday()
        if dow == 6:  # Sunday
            pass
        elif dow == 5:  # Saturday
            total_days += 0.5
        else:
            total_days += 1
        current_date = date.fromordinal(current_date.toordinal() + 1)
    
    return total_days


def get_fiscal_year_python(p_date):
    """Get fiscal year (October start)"""
    if p_date.month >= 10:
        return p_date.year + 1
    else:
        return p_date.year


# =====================================================
# MAIN
# =====================================================



# PDF Report Routes
@app.route('/api/reports/attendance-pdf')
def generate_attendance_pdf():
    try:
        from pdf_report import generate_attendance_pdf as gen_att_pdf
        
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


@app.route('/api/reports/leave-pdf')
def generate_leave_pdf():
    try:
        from pdf_report import generate_leave_pdf as gen_leave_pdf
        
        start_date = request.args.get('start_date') or datetime.now().strftime('%Y-%m-01')
        end_date = request.args.get('end_date') or datetime.now().strftime('%Y-%m-%d')
        
        leave_requests = LeaveRequest.query.filter(
            LeaveRequest.StartDate >= start_date,
            LeaveRequest.StartDate <= end_date
        ).order_by(LeaveRequest.StartDate.desc()).all()
        
        employees = {e.EmpID: f"{e.FirstName} {e.LastName}" for e in Employee.query.all()}
        pdf = gen_leave_pdf(leave_requests, employees, start_date, end_date)
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=leave_report_{start_date}_{end_date}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




# Holiday Management Routes
@app.route('/api/holidays', methods=['GET'])
def get_holidays():
    """Get all holidays"""
    try:
        holidays = Holiday.query.order_by(Holiday.holiday_date).all()
        return jsonify({
            'success': True,
            'holidays': [h.to_dict() for h in holidays]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays', methods=['POST'])
def add_holiday():
    """Add a new holiday"""
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

@app.route('/api/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    """Delete a holiday"""
    try:
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({'success': False, 'error': 'Holiday not found'}), 404
        
        db.session.delete(holiday)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Holiday deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays/check/<date>')
def check_holiday(date):
    """Check if a specific date is a holiday"""
    try:
        holiday = Holiday.query.filter_by(holiday_date=date).first()
        if holiday:
            return jsonify({
                'success': True,
                'is_holiday': True,
                'holiday_name': holiday.holiday_name
            })
        return jsonify({
            'success': True,
            'is_holiday': False,
            'holiday_name': None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/fiscal-year-summary')
def get_fiscal_year_summary():
    """Get Fiscal Year Summary for all employees"""
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
                'total_hours_worked': round(total_hours, 2),
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Seed employees if none exist
        if Employee.query.count() == 0:
            print("Seeding employees...")
            employees = [
                "Peter Nyawade", "Tonny Odongo", "Eric Kamau", "Kelvin Omondi",
                "Ottawa Kinsvoscko", "Riziki Merriment", "Margaret Muthoni",
                "Oscar Akala", "Craig Mwendwa", "Mark Okere", "Joash Amutavi",
                "Julius Singila", "Wesonga Wilfred", "Innocent Mogaka",
                "Nelson Kasiki", "Fredrick Owino", "Bentah Akinyi", "Mahmood Mir",
                "Sharon Akinyi", "Kipsang Kipsetim", "Dennis Kipkemoi", "David Makau"
            ]
            
            # Create fiscal year
            current_fy = get_fiscal_year_python(datetime.now().date())
            fy_start = datetime(datetime.now().year, 10, 1).date() if datetime.now().month >= 10 else datetime(datetime.now().year - 1, 10, 1).date()
            fy_end = datetime(datetime.now().year + 1, 9, 30).date() if datetime.now().month >= 10 else datetime(datetime.now().year, 9, 30).date()
            
            fiscal_year = FiscalYear(
                FiscalYear=current_fy,
                StartDate=fy_start,
                EndDate=fy_end,
                IsActive=True
            )
            db.session.add(fiscal_year)
            db.session.commit()
            
            for name in employees:
                name_parts = name.strip().split()
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                new_emp = Employee(
                    EmployeeCode=f"EMP{str(Employee.query.count() + 1).zfill(3)}",
                    FirstName=first_name,
                    LastName=last_name,
                    JoinDate=datetime.now().date()
                )
                db.session.add(new_emp)
                db.session.commit()
                
                leave_balance = LeaveBalance(
                    EmpID=new_emp.EmpID,
                    FiscalYear=current_fy,
                    AnnualDays=21,
                    SickDays=10,
                    CasualDays=5
                )
                db.session.add(leave_balance)
                db.session.commit()
                print(f"✅ Added: {name}")
            
            print(f"\\n🎉 Successfully added {len(employees)} employees!")
        else:
            print("Database already has employees, skipping seed.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# Write the updated app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py_content)

print("✅ Updated app.py with Notifications model and API routes")

# =====================================================
# PART 2: Update admin_input.html with Approve button
# =====================================================

admin_html_path = 'templates/admin_input.html'
with open(admin_html_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

# Update the Actions column in the leave table to include Approve button
old_actions = '''<td class="px-3 py-2">
                                    <button onclick="deleteLeaveRequest(${leave.id})" class="text-red-600 hover:text-red-800 text-sm font-medium">
                                        Delete
                                    </button>
                                </td>'''

new_actions = '''<td class="px-3 py-2">
                                    ${leave.status === 'Pending' ? `
                                        <button onclick="approveLeaveRequest(${leave.id})" class="text-green-600 hover:text-green-800 text-sm font-medium mr-2">
                                            <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                            </svg>
                                            Approve
                                        </button>
                                        <button onclick="deleteLeaveRequest(${leave.id})" class="text-red-600 hover:text-red-800 text-sm font-medium">
                                            Delete
                                        </button>
                                    ` : `
                                        <span class="text-green-600 text-sm font-medium">Approved</span>
                                    `}
                                </td>'''

admin_content = admin_content.replace(old_actions, new_actions)

# Add the approve function
old_js_section = '''        // Delete leave request
        async function deleteLeaveRequest(id) {'''

new_js_section = '''        // Approve leave request
        async function approveLeaveRequest(id) {
            if (!confirm('Are you sure you want to approve this leave request?')) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/leave-requests/${id}/approve`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ Leave request approved successfully', 'success');
                    fetchLeaveRecords();
                } else {
                    showAlert(`❌ ${data.error || 'Failed to approve leave request'}`, 'error');
                }
            } catch (error) {
                console.error('Error approving leave request:', error);
                showAlert('❌ Failed to connect to server', 'error');
            }
        }

        // Delete leave request
        async function deleteLeaveRequest(id) {'''

admin_content = admin_content.replace(old_js_section, new_js_section)

with open(admin_html_path, 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("✅ Updated admin_input.html with Approve button")

# =====================================================
# PART 3: Update main index.html with Notification bell
# =====================================================

index_html_path = 'templates/index.html'
with open(index_html_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Add notification bell in the header
old_header = '''<div class="text-right">
                    <p id="currentDate" class="text-lg font-semibold"></p>
                    <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                </div>'''

new_header = '''<div class="text-right flex items-center gap-3">
                    <!-- Notification Bell -->
                    <div class="relative">
                        <button id="notificationBell" class="relative p-2 text-white hover:bg-white/20 rounded-full transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                            </svg>
                            <span id="notificationBadge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">0</span>
                        </button>
                        <!-- Notification Dropdown -->
                        <div id="notificationDropdown" class="hidden absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50 border border-gray-200">
                            <div class="p-3 border-b border-gray-200">
                                <h3 class="font-semibold text-gray-800">Notifications</h3>
                            </div>
                            <div id="notificationList" class="max-h-64 overflow-y-auto">
                                <p class="p-4 text-gray-500 text-sm text-center">No notifications</p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <p id="currentDate" class="text-lg font-semibold"></p>
                        <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                    </div>
                </div>'''

index_content = index_header.replace(old_header, new_header)

# Add notification JavaScript
old_script = '''        let employees = [];
        let selectedEmployeeId = null;'''

new_script = '''        let employees = [];
        let selectedEmployeeId = null;
        
        // Notification functions
        async function fetchNotifications() {
            if (!selectedEmployeeId) return;
            
            try {
                const response = await fetch(`${API_BASE}/api/notifications?emp_id=${selectedEmployeeId}`);
                const data = await response.json();
                
                if (data.success && data.notifications) {
                    // Update badge count
                    const unreadCount = data.notifications.filter(n => !n.is_read).length;
                    const badge = document.getElementById('notificationBadge');
                    if (unreadCount > 0) {
                        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
                        badge.classList.remove('hidden');
                    } else {
                        badge.classList.add('hidden');
                    }
                    
                    // Update notification list
                    const listEl = document.getElementById('notificationList');
                    if (data.notifications.length > 0) {
                        listEl.innerHTML = data.notifications.slice(0, 10).map(n => `
                            <div class="p-3 border-b border-gray-100 hover:bg-gray-50 ${n.is_read ? 'opacity-60' : ''}">
                                <p class="text-sm text-gray-800">${n.message}</p>
                                <p class="text-xs text-gray-500 mt-1">${new Date(n.created_at).toLocaleString()}</p>
                            </div>
                        `).join('');
                    } else {
                        listEl.innerHTML = '<p class="p-4 text-gray-500 text-sm text-center">No notifications</p>';
                    }
                }
            } catch (error) {
                console.error('Error fetching notifications:', error);
            }
        }
        
        // Toggle notification dropdown
        document.addEventListener('click', (e) => {
            const bell = document.getElementById('notificationBell');
            const dropdown = document.getElementById('notificationDropdown');
            
            if (bell.contains(e.target)) {
                dropdown.classList.toggle('hidden');
                if (!dropdown.classList.contains('hidden') && selectedEmployeeId) {
                    fetchNotifications();
                }
            } else if (!dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });'''

index_content = index_content.replace(old_script, new_script)

# Update employee selection to also fetch notifications
old_emp_select = '''        // Also update selectedEmployeeId when select changes
        employeeSelect.addEventListener('change', (e) => {
            selectedEmployeeId = e.target.value;
            if (selectedEmployeeId) {
                const emp = employees.find(em => em.emp_id == selectedEmployeeId);
                if (emp) {
                    employeeSearch.value = `${emp.first_name} ${emp.last_name}`;
                }
            }
        });'''

new_emp_select = '''        // Also update selectedEmployeeId when select changes
        employeeSelect.addEventListener('change', (e) => {
            selectedEmployeeId = e.target.value;
            if (selectedEmployeeId) {
                const emp = employees.find(em => em.emp_id == selectedEmployeeId);
                if (emp) {
                    employeeSearch.value = `${emp.first_name} ${emp.last_name}`;
                }
                // Fetch notifications when employee is selected
                fetchNotifications();
            }
        });
        
        // When clicking on dropdown item, also fetch notifications
        document.querySelectorAll('#employeeDropdown > div[data-id]').forEach(item => {
            item.addEventListener('click', () => {
                const empId = item.dataset.id;
                selectedEmployeeId = empId;
                const empName = item.dataset.name;
                employeeSearch.value = empName;
                employeeDropdown.classList.add('hidden');
                // Fetch notifications
                fetchNotifications();
            });
        });'''

index_content = index_content.replace(old_emp_select, new_emp_select)

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print("✅ Updated index.html with notification bell")

print("\\n✅ All updates completed successfully!")
print("\\nChanges made:")
print("1. Added Notification model to database")
print("2. Created API routes: /api/leave-requests/<id>/approve, /api/notifications, /api/notifications/unread-count")
print("3. Added Approve button (green checkmark) to admin leave table")
print("4. Added notification bell icon to main index.html")
