#!/usr/bin/env python3
"""
Staff Portal Only - For Contabo VPS Deployment
=============================================
This version contains ONLY staff-facing features:
- Staff Clock In/Out
- Casual Worker Clock In/Out with Total Hours
- Leave Request Submission

Admin Dashboard stays on Render: https://aisl-cimr.onrender.com/admin-login
Both connect to the SAME Supabase database.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'dev_fallback_key_change_in_production'

# Enable CORS
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cache control
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Imports
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import pytz
from sqlalchemy import func

# =====================================================
# CONFIGURATION
# =====================================================

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')

# Fix for Supabase
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"📊 Database URL: {DATABASE_URL[:50]}...")

# SSL for Supabase
if DATABASE_URL and 'postgresql' in DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require', 'connect_timeout': 10}
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Late threshold (08:15 AM)
LATE_THRESHOLD = time(8, 15)

# Email config
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@attendance.com')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'Attendance System')


# =====================================================
# DATABASE MODELS
# =====================================================

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(50))
    join_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    leave_balance = db.Column(db.Float, default=21)
    sick_leave_balance = db.Column(db.Float, default=7)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def EmpID(self):
        return self.id
    
    @property
    def EmployeeCode(self):
        return self.employee_code
    
    @property
    def FirstName(self):
        return self.first_name
    
    @property
    def LastName(self):
        return self.last_name
    
    def to_dict(self):
        return {
            'id': self.id,
            'emp_id': self.id,
            'employee_code': self.employee_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'is_active': self.is_active,
            'leave_balance': self.leave_balance,
            'annual_leave_balance': self.leave_balance
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    clock_in = db.Column(db.Time, nullable=False)
    clock_out = db.Column(db.Time)
    day_type = db.Column(db.String(20), default='Full Day')
    status = db.Column(db.String(20), default='Present')
    is_late = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    staff = db.relationship('Staff', backref=db.backref('attendance_records', lazy='dynamic'))
    
    def to_dict(self):
        staff_name = None
        if self.staff:
            staff_name = f"{self.staff.first_name} {self.staff.last_name}"
        return {
            'id': self.id,
            'emp_id': self.staff_id,
            'staff_id': self.staff_id,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'clock_in': self.clock_in.strftime('%H:%M') if self.clock_in else None,
            'clock_out': self.clock_out.strftime('%H:%M') if self.clock_out else None,
            'day_type': self.day_type,
            'status': self.status,
            'is_late': self.is_late,
            'notes': self.notes,
            'staff_name': staff_name
        }


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    approved_by = db.Column(db.Integer)
    approved_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fiscal_year = db.Column(db.Integer, nullable=True)
    
    staff = db.relationship('Staff', backref=db.backref('leave_requests', lazy='dynamic'))
    
    @staticmethod
    def get_fiscal_year(d):
        if d.month in (10, 11, 12):
            return d.year + 1
        return d.year
    
    def to_dict(self):
        staff_name = None
        if self.staff:
            staff_name = f"{self.staff.first_name} {self.staff.last_name}"
        return {
            'id': self.id,
            'request_id': self.id,
            'emp_id': self.staff_id,
            'staff_id': self.staff_id,
            'staff_name': staff_name,
            'leave_type': self.leave_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_days': self.total_days,
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'fiscal_year': self.fiscal_year
        }


class CasualAttendance(db.Model):
    __tablename__ = 'casual_attendance'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    work_type = db.Column(db.String(50), nullable=False)
    clock_in = db.Column(db.Time, nullable=False)
    clock_out = db.Column(db.Time)
    work_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'work_type': self.work_type,
            'clock_in': self.clock_in.strftime('%H:%M') if self.clock_in else None,
            'clock_out': self.clock_out.strftime('%H:%M') if self.clock_out else None,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_kenyan_leave(start_date, end_date):
    """Calculate leave days excluding Sundays"""
    kenyan_holidays_2026 = {
        date(2026, 1, 1), date(2026, 4, 3), date(2026, 4, 6),
        date(2026, 5, 1), date(2026, 6, 1), date(2026, 10, 10),
        date(2026, 10, 20), date(2026, 12, 12), date(2026, 12, 25),
        date(2026, 12, 26),
    }
    total_days = 0.0
    current = start_date
    while current <= end_date:
        if current.weekday() == 6 or current in kenyan_holidays_2026:
            total_days += 0.0
        elif current.weekday() == 5:
            total_days += 0.5
        else:
            total_days += 1.0
        current = date.fromordinal(current.toordinal() + 1)
    return total_days


def is_late_arrival(clock_in_time):
    if not clock_in_time:
        return False
    return clock_in_time > LATE_THRESHOLD


# =====================================================
# STAFF PORTAL ROUTES (NO ADMIN)
# =====================================================

@app.route('/')
def index():
    """Staff Clock In/Out and Leave Request"""
    try:
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        today = date.today()
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        attendance_dict = {a.staff_id: a for a in today_attendance}
        return render_template('staff/index.html', 
                              staff=staff_members, today=today, attendance=attendance_dict)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return render_template('staff/index.html', staff=[], today=date.today(), attendance={}, error=str(e))


@app.route('/casual')
def casual_page():
    """Casual worker attendance page"""
    return render_template('casual.html')


# =====================================================
# API ROUTES
# =====================================================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        today = date.today()
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        attendance_dict = {a.staff_id: a for a in today_attendance}
        
        result = []
        for staff in staff_members:
            staff_dict = staff.to_dict()
            att = attendance_dict.get(staff.id)
            if att and att.clock_in:
                staff_dict['is_late_today'] = is_late_arrival(att.clock_in)
            else:
                staff_dict['is_late_today'] = False
            result.append(staff_dict)
        
        return jsonify({'success': True, 'employees': result})
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance"""
    try:
        nairobi_tz = pytz.timezone('Africa/Nairobi')
        today = datetime.now(nairobi_tz).date()
        attendance = Attendance.query.filter(func.date(Attendance.work_date) == today).all()
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        
        approved_leaves_today = LeaveRequest.query.filter(
            LeaveRequest.status == 'Approved',
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        ).all()
        emp_on_leave = {leave.staff_id: leave for leave in approved_leaves_today}
        
        result = []
        for staff in staff_members:
            leave = emp_on_leave.get(staff.id)
            if leave:
                status = 'On Leave'
                clock_in = ''
                clock_out = ''
                is_late = False
            else:
                att = next((a for a in attendance if a.staff_id == staff.id), None)
                if att:
                    status = 'Present' if not att.clock_out else 'Clocked Out'
                    clock_in = att.clock_in.strftime('%H:%M') if att.clock_in else ''
                    clock_out = att.clock_out.strftime('%H:%M') if att.clock_out else ''
                    is_late = is_late_arrival(att.clock_in)
                else:
                    status = 'Not Clocked In'
                    clock_in = ''
                    clock_out = ''
                    is_late = False
            
            result.append({
                'id': staff.id,
                'emp_id': staff.id,
                'employee_name': f"{staff.first_name} {staff.last_name}",
                'employee_code': staff.employee_code,
                'status': status,
                'clock_in': clock_in,
                'clock_out': clock_out,
                'is_late': is_late,
                'leave_balance': staff.leave_balance
            })
        
        return jsonify({'success': True, 'date': today.isoformat(), 'employees': result})
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    """Clock in/out"""
    data = request.get_json()
    staff_id = data.get('staff_id') or data.get('emp_id')
    work_date = datetime.strptime(data.get('work_date'), '%Y-%m-%d').date()
    clock_in_str = data.get('clock_in')
    clock_out_str = data.get('clock_out')
    
    if not staff_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    clock_in = datetime.strptime(clock_in_str, '%H:%M').time() if clock_in_str else None
    is_late = is_late_arrival(clock_in)
    is_saturday = work_date.weekday() == 5
    day_type = 'Saturday Half Day' if is_saturday else 'Full Day'
    
    try:
        existing = Attendance.query.filter_by(staff_id=staff_id, work_date=work_date).first()
        if existing:
            if clock_out_str:
                existing.clock_out = datetime.strptime(clock_out_str, '%H:%M').time()
            existing.status = 'Present'
            db.session.commit()
            return jsonify({'success': True, 'message': 'Clock out recorded', 'attendance': existing.to_dict()})
        
        attendance = Attendance(
            staff_id=staff_id,
            work_date=work_date,
            clock_in=clock_in,
            day_type=day_type,
            is_late=is_late,
            status='Present' if not is_late else 'Late'
        )
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Clock in recorded' + (' (LATE - After 08:15 AM)' if is_late else ''),
            'attendance': attendance.to_dict(),
            'is_late': is_late
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leave-requests', methods=['GET', 'POST'])
def leave_requests():
    """Get or create leave requests"""
    if request.method == 'GET':
        try:
            leave_requests_list = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
            return jsonify({'success': True, 'leave_requests': [lr.to_dict() for lr in leave_requests_list]})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    data = request.get_json()
    staff_id = data.get('staff_id') or data.get('emp_id')
    if staff_id:
        staff_id = int(staff_id)
    
    leave_type = data.get('leave_type')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    reason = data.get('reason', '')
    
    multiplier_str = data.get('day_type', '1.0')
    try:
        multiplier = float(multiplier_str)
    except (ValueError, TypeError):
        multiplier = 1.0
    
    if not staff_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    try:
        staff = db.session.get(Staff, staff_id)
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404
        
        calendar_days = calculate_kenyan_leave(start_date, end_date)
        total_days = calendar_days * multiplier
        
        if leave_type == 'Annual':
            if staff.leave_balance < total_days:
                return jsonify({
                    'success': False, 
                    'error': f'Insufficient leave balance. Available: {staff.leave_balance} days'
                }), 400
        
        # Calculate fiscal year
        fiscal_year = LeaveRequest.get_fiscal_year(start_date)
        
        leave_request = LeaveRequest(
            staff_id=staff_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            status='Pending',
            fiscal_year=fiscal_year
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request submitted',
            'leave_request': leave_request.to_dict()
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leave/balance/<int:staff_id>', methods=['GET'])
def get_leave_balance(staff_id):
    """Get staff leave balance"""
    try:
        staff = db.session.get(Staff, staff_id)
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404
        
        return jsonify({
            'success': True,
            'staff_id': staff_id,
            'leave_balance': staff.leave_balance,
            'is_low': staff.leave_balance <= 3
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# CASUAL WORKER API
# =====================================================

@app.route('/api/casual/clock-in', methods=['POST'])
def casual_clock_in():
    """Casual worker clock in"""
    data = request.get_json()
    name = data.get('name')
    phone_number = data.get('phone_number')
    work_type = data.get('work_type')
    
    if not name or not phone_number or not work_type:
        return jsonify({'success': False, 'error': 'Name, phone number, and work type are required'}), 400
    
    today = date.today()
    now = datetime.now().time()
    
    try:
        casual = CasualAttendance(
            name=name,
            phone_number=phone_number,
            work_type=work_type,
            clock_in=now,
            work_date=today
        )
        db.session.add(casual)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Clocked in at {now.strftime("%H:%M")}',
            'casual': casual.to_dict()
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/casual/clock-out', methods=['POST'])
def casual_clock_out():
    """Casual worker clock out"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'success': False, 'error': 'Phone number is required'}), 400
    
    today = date.today()
    now = datetime.now().time()
    
    try:
        latest = CasualAttendance.query.filter(
            CasualAttendance.phone_number == phone_number,
            CasualAttendance.work_date == today,
            CasualAttendance.clock_out == None
        ).order_by(CasualAttendance.clock_in.desc()).first()
        
        if not latest:
            return jsonify({'success': False, 'error': 'No open clock-in found for today'}), 404
        
        latest.clock_out = now
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Clocked out at {now.strftime("%H:%M")}',
            'casual': latest.to_dict()
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/casual/today', methods=['GET'])
def casual_today():
    """Get all casual attendance for today"""
    today = date.today()
    
    try:
        casuals = CasualAttendance.query.filter_by(work_date=today).order_by(CasualAttendance.clock_in.desc()).all()
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'casuals': [c.to_dict() for c in casuals]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health_check():
    """Health check"""
    try:
        staff_count = Staff.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'staff_count': staff_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('PORT') is None
    
    print(f"\n{'='*60}")
    print("STAFF PORTAL (Contabo Deployment)")
    print(f"{'='*60}")
    print(f"Database: {DATABASE_URL[:50]}...")
    print(f"Port: {port}")
    print(f"{'='*60}\n")
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created")
        except Exception as e:
            print(f"⚠️ Database warning: {e}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
