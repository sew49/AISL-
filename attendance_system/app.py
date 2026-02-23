import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv() # This must come before using os.getenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'dev_fallback_key_change_in_production'

# Continue with other imports after app and secret_key are defined
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# =====================================================
# CONFIGURATION
# =====================================================

# Database URL - Production (Render) or Local fallback
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')

# Fix for Supabase/Render: replace postgres:// with postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"📊 Database URL: {DATABASE_URL[:50]}...")

# =====================================================
# ENGINE FIX: Configure SSL for Supabase PostgreSQL
# =====================================================
if DATABASE_URL and 'postgresql' in DATABASE_URL:
    # Use Flask-SQLAlchemy's engine_options for SSL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
    print("🔒 SSL mode enabled for PostgreSQL")
else:
    # SQLite configuration (local development)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Add this right after db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# Supabase config
SUPABASE_URL = 'https://sfwhsgrphfrsckzqquxp.supabase.co'
ADMIN_PASSWORD = 'RAV4Adventure2019'

# Late threshold time (08:15 AM)
LATE_THRESHOLD = time(8, 15)

# =====================================================
# DATABASE MODELS (SQLAlchemy 2.0 compatible)
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
    leave_balance = db.Column(db.Integer, default=21)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    
    # Define relationship using string reference to avoid circular import
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
    total_days = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    approved_by = db.Column(db.Integer)
    approved_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship using string reference
    staff = db.relationship('Staff', backref=db.backref('leave_requests', lazy='dynamic'))
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_leave_days(start_date, end_date):
    """Calculate leave days excluding Sundays"""
    total_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() != 6:
            total_days += 1
        current = date.fromordinal(current.toordinal() + 1)
    return total_days


def is_late_arrival(clock_in_time):
    """Check if the clock-in time is after 08:15 AM"""
    if not clock_in_time:
        return False
    return clock_in_time > LATE_THRESHOLD


def seed_staff():
    """Pre-populate 22 staff members"""
    try:
        if Staff.query.count() > 0:
            return
        
        staff_members = [
            "Peter Nyawade", "Tonny Odongo", "Eric Kamau", "Kelvin Omondi",
            "Ottawa Kinsvoscko", "Riziki Merriment", "Margaret Muthoni",
            "Oscar Akala", "Craig Mwendwa", "Mark Okere", "Joash Amutavi",
            "Julius Singila", "Wesonga Wilfred", "Innocent Mogaka",
            "Nelson Kasiki", "Fredrick Owino", "Bentah Akinyi", "Mahmood Mir",
            "Sharon Akinyi", "Kipsang Kipsetim", "Dennis Kipkemoi", "David Makau"
        ]
        
        for i, name in enumerate(staff_members, 1):
            parts = name.strip().split()
            first = parts[0]
            last = ' '.join(parts[1:]) if len(parts) > 1 else ''
            
            staff = Staff(
                employee_code=f"EMP{str(i).zfill(3)}",
                first_name=first,
                last_name=last,
                join_date=date.today(),
                department='Operations',
                leave_balance=21
            )
            db.session.add(staff)
        
        db.session.commit()
        print(f"✅ Seeded {len(staff_members)} staff members")
    except Exception as e:
        print(f"⚠️  Error seeding staff: {e}")
        db.session.rollback()


# =====================================================
# ROUTES
# =====================================================

@app.route('/')
def index():
    """Home page - Staff Clock In/Out and Leave Request"""
    try:
        staff_members = Staff.query.filter_by(is_active=True).all()
        today = date.today()
        
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        attendance_dict = {a.staff_id: a for a in today_attendance}
        
        return render_template('staff/index.html', 
                              staff=staff_members, 
                              today=today,
                              attendance=attendance_dict)
    except Exception as e:
        print(f"❌ ERROR in index: {str(e)}")
        return render_template('staff/index.html', 
                              staff=[], 
                              today=date.today(),
                              attendance={},
                              error=str(e))


@app.route('/debug')
def debug_status():
    """Debug/Status page"""
    db_type = "PostgreSQL (Supabase)" if "postgresql" in DATABASE_URL else "SQLite (Local)"
    return render_template('debug.html', 
                          database_url=DATABASE_URL[:50] + "..." if len(DATABASE_URL) > 50 else DATABASE_URL,
                          db_type=db_type,
                          supabase_url=SUPABASE_URL)


@app.route('/staff')
def staff_portal():
    """Staff portal"""
    return redirect(url_for('index'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    return render_template('admin/admin_login.html')


@app.route('/admin')
def admin_home():
    """Admin home"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - with error handling"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        staff_members = Staff.query.filter_by(is_active=True).all()
        today = date.today()
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        pending_leaves = LeaveRequest.query.filter_by(status='Pending').all()
        
        return render_template('admin/dashboard.html', 
                             staff=staff_members,
                             attendance=today_attendance,
                             pending_leaves=pending_leaves,
                             today=today)
    except Exception as e:
        print(f"❌ ERROR in admin_dashboard: {str(e)}")
        return render_template('admin/dashboard.html', 
                             staff=[],
                             attendance=[],
                             pending_leaves=[],
                             today=date.today(),
                             error=f"Database error: {str(e)}")


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Process admin login"""
    password = request.form.get('password', '')
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/admin_login.html', error='Invalid password')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin-input')
def admin_input():
    """Admin input page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_input.html')


@app.route('/admin/leave')
def admin_leave():
    """Admin leave management - with error handling"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
        return jsonify({
            'success': True,
            'leave_requests': [lr.to_dict() for lr in leave_requests]
        })
    except Exception as e:
        print(f"❌ ERROR loading leave records: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database connection failed: {str(e)}'
        }), 500


# =====================================================
# API ROUTES - WITH ERROR HANDLING
# =====================================================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees - with 08:15 AM late flagging"""
    try:
        staff_members = Staff.query.filter_by(is_active=True).all()
        
        # Check today's attendance for late arrivals
        today = date.today()
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        attendance_dict = {a.staff_id: a for a in today_attendance}
        
        result = []
        for staff in staff_members:
            staff_dict = staff.to_dict()
            
            # Check if late today (after 08:15 AM)
            att = attendance_dict.get(staff.id)
            if att and att.clock_in:
                staff_dict['is_late_today'] = is_late_arrival(att.clock_in)
                if staff_dict['is_late_today']:
                    staff_dict['late_minutes'] = (
                        (datetime.combine(date.today(), att.clock_in) - datetime.combine(date.today(), LATE_THRESHOLD)).total_seconds() / 60
                    )
            else:
                staff_dict['is_late_today'] = False
            
            result.append(staff_dict)
        
        return jsonify({
            'success': True,
            'employees': result
        })
    except Exception as e:
        print(f"❌ ERROR loading employees: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/staff', methods=['GET'])
def get_staff():
    """Get all staff - with 08:15 AM late flagging"""
    try:
        staff_members = Staff.query.filter_by(is_active=True).all()
        
        # Check today's attendance for late arrivals
        today = date.today()
        today_attendance = Attendance.query.filter_by(work_date=today).all()
        attendance_dict = {a.staff_id: a for a in today_attendance}
        
        result = []
        for staff in staff_members:
            staff_dict = staff.to_dict()
            
            # Check if late today (after 08:15 AM)
            att = attendance_dict.get(staff.id)
            if att and att.clock_in:
                staff_dict['is_late_today'] = is_late_arrival(att.clock_in)
            else:
                staff_dict['is_late_today'] = False
            
            result.append(staff_dict)
        
        return jsonify({
            'success': True,
            'staff': result
        })
    except Exception as e:
        print(f"❌ ERROR loading staff: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/attendance', methods=['GET'])
def get_all_attendance():
    """Get all attendance records - with late flagging"""
    start_date = request.args.get('start_date')
    
    try:
        query = Attendance.query
        if start_date:
            query = query.filter(Attendance.work_date >= start_date)
        
        attendance = query.order_by(Attendance.work_date.desc()).all()
        
        # Add late flag to each record (08:15 AM rule)
        result = []
        for att in attendance:
            att_dict = att.to_dict()
            att_dict['is_late'] = is_late_arrival(att.clock_in)
            result.append(att_dict)
        
        return jsonify({
            'success': True,
            'attendance': result
        })
    except Exception as e:
        print(f"❌ ERROR loading attendance: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for all staff - with 08:15 AM late flagging"""
    try:
        today = date.today()
        attendance = Attendance.query.filter_by(work_date=today).all()
        staff_members = Staff.query.filter_by(is_active=True).all()
        
        result = []
        for staff in staff_members:
            att = next((a for a in attendance if a.staff_id == staff.id), None)
            
            if att:
                status = 'Present' if not att.clock_out else 'Clocked Out'
                clock_in = att.clock_in.strftime('%H:%M') if att.clock_in else ''
                clock_out = att.clock_out.strftime('%H:%M') if att.clock_out else ''
                # Check if late based on 08:15 AM threshold
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
        
        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'employees': result
        })
    except Exception as e:
        print(f"❌ ERROR loading today's attendance: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    """Clock in/out - with 08:15 AM late detection"""
    data = request.get_json()
    
    staff_id = data.get('staff_id') or data.get('emp_id')
    work_date = datetime.strptime(data.get('work_date'), '%Y-%m-%d').date()
    clock_in_str = data.get('clock_in')
    clock_out_str = data.get('clock_out')
    
    if not staff_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    clock_in = datetime.strptime(clock_in_str, '%H:%M').time() if clock_in_str else None
    
    # Check if late (after 08:15 AM) - 08:15 AM Logic
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
            return jsonify({
                'success': True, 
                'message': 'Clock out recorded', 
                'attendance': existing.to_dict()
            })
        
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
        print(f"❌ ERROR creating attendance: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/leave-requests', methods=['GET', 'POST'])
def leave_requests():
    """Get or create leave requests"""
    if request.method == 'GET':
        try:
            leave_requests_list = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
            return jsonify({
                'success': True,
                'leave_requests': [lr.to_dict() for lr in leave_requests_list]
            })
        except Exception as e:
            print(f"❌ ERROR loading leave requests: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(e)}'
            }), 500
    
    data = request.get_json()
    
    staff_id = data.get('staff_id') or data.get('emp_id')
    if staff_id:
        staff_id = int(staff_id)
    
    leave_type = data.get('leave_type')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    reason = data.get('reason', '')
    
    if not staff_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    
    try:
        staff = db.session.get(Staff, staff_id)
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404
        
        total_days = calculate_leave_days(start_date, end_date)
        
        if leave_type == 'Annual':
            if staff.leave_balance < total_days:
                return jsonify({
                    'success': False, 
                    'error': f'Insufficient leave balance. Available: {staff.leave_balance} days'
                }), 400
        
        leave_request = LeaveRequest(
            staff_id=staff_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            status='Pending'
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request submitted',
            'leave_request': leave_request.to_dict()
        })
    except Exception as e:
        print(f"❌ ERROR creating leave request: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/leave-requests/<int:request_id>/approve', methods=['POST'])
def approve_leave(request_id):
    """Approve leave"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        leave_request = db.session.get(LeaveRequest, request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        staff = db.session.get(Staff, leave_request.staff_id)
        
        if leave_request.leave_type == 'Annual' and staff:
            staff.leave_balance -= leave_request.total_days
            if staff.leave_balance < 0:
                staff.leave_balance = 0
        
        leave_request.status = 'Approved'
        leave_request.approved_by = 1
        leave_request.approved_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave approved',
            'leave_request': leave_request.to_dict()
        })
    except Exception as e:
        print(f"❌ ERROR approving leave: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/leave-requests/<int:request_id>/reject', methods=['POST'])
def reject_leave(request_id):
    """Reject leave request"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        leave_request = db.session.get(LeaveRequest, request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        leave_request.status = 'Rejected'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave rejected',
            'leave_request': leave_request.to_dict()
        })
    except Exception as e:
        print(f"❌ ERROR rejecting leave: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


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
        print(f"❌ ERROR getting leave balance: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


@app.route('/api/reports/fiscal-year-summary')
def fiscal_year_summary():
    """Get fiscal year summary"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        employees = Staff.query.filter_by(is_active=True).all()
        start_date = date(2025, 10, 1)
        
        summary = []
        for emp in employees:
            attendance_count = Attendance.query.filter(
                Attendance.staff_id == emp.id,
                Attendance.work_date >= start_date
            ).count()
            
            annual_leave = LeaveRequest.query.filter(
                LeaveRequest.staff_id == emp.id,
                LeaveRequest.leave_type == 'Annual',
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date >= start_date
            ).all()
            annual_taken = sum(lr.total_days for lr in annual_leave)
            
            sick_leave = LeaveRequest.query.filter(
                LeaveRequest.staff_id == emp.id,
                LeaveRequest.leave_type == 'Sick',
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date >= start_date
            ).all()
            sick_taken = sum(lr.total_days for lr in sick_leave)
            
            remaining = 21 - annual_taken
            
            summary.append({
                'employee_name': f"{emp.first_name} {emp.last_name}",
                'days_present': attendance_count,
                'annual_leave_taken': annual_taken,
                'annual_leave_remaining': remaining,
                'sick_days_taken': sick_taken,
                'unpaid_absences': 0
            })
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        print(f"❌ ERROR loading fiscal year summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database connection failed: {str(e)}'
        }), 500


@app.route('/api/reports/monthly-attendance-summary')
def monthly_attendance_summary():
    """Get monthly attendance summary"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        year = request.args.get('year', type=int, default=2026)
        month = request.args.get('month', type=int, default=1)
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        target_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:
                target_days += 1
            current += timedelta(days=1)
        
        employees = Staff.query.filter_by(is_active=True).all()
        
        summary = []
        for emp in employees:
            attendance_count = Attendance.query.filter(
                Attendance.staff_id == emp.id,
                Attendance.work_date >= start_date,
                Attendance.work_date <= end_date
            ).count()
            
            month_name = start_date.strftime('%B')
            
            summary.append({
                'employee_name': f"{emp.first_name} {emp.last_name}",
                'month': month_name,
                'days_present': attendance_count,
                'target_days': target_days
            })
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        print(f"❌ ERROR loading monthly summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database connection failed: {str(e)}'
        }), 500


@app.route('/api/employees/reset-annual-leave', methods=['POST'])
def reset_annual_leave():
    """Reset all employees' annual leave to 21 days"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        employees = Staff.query.filter_by(is_active=True).all()
        for emp in employees:
            emp.leave_balance = 21
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All employees annual leave reset to 21 days'
        })
    except Exception as e:
        print(f"❌ ERROR resetting annual leave: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    db_type = "PostgreSQL (Supabase)" if "postgresql" in DATABASE_URL else "SQLite (Local)"
    print(f"\n{'='*60}")
    print("ATTENDANCE SYSTEM STARTUP")
    print(f"{'='*60}")
    print(f"Database: {db_type}")
    print(f"URL: {DATABASE_URL[:50]}...")
    print(f"Late Threshold: {LATE_THRESHOLD}")
    print(f"{'='*60}\n")
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
        seed_staff()
    
    print("🚀 Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
