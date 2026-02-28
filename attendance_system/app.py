import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv() # This must come before using os.getenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'dev_fallback_key_change_in_production'

# Enable CORS for all domains (needed for Render deployment)
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add cache control headers to prevent caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Continue with other imports after app and secret_key are defined
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
import pytz
from sqlalchemy import func




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
    leave_balance = db.Column(db.Float, default=21)  # Annual leave (21 days)
    sick_leave_balance = db.Column(db.Float, default=7)  # Sick leave (7 days)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Property aliases for uppercase attribute names (used in templates)
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
    total_days = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    approved_by = db.Column(db.Integer)
    approved_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fiscal_year = db.Column(db.Integer, nullable=True)  # Fiscal year for tracking 2021-2025 leave history
    
    # Define relationship using string reference
    staff = db.relationship('Staff', backref=db.backref('leave_requests', lazy='dynamic'))
    
    @staticmethod
    def get_fiscal_year(date):
        """
        Calculate fiscal year based on date.
        If month is 10 (October), 11 (November), or 12 (December), return date.year + 1.
        Otherwise, return date.year.
        """
        if date.month in (10, 11, 12):
            return date.year + 1
        return date.year
    
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


class Holiday(db.Model):
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    holiday_name = db.Column(db.String(100), nullable=False)
    holiday_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'holiday_name': self.holiday_name,
            'holiday_date': self.holiday_date.isoformat() if self.holiday_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_leave_days(start_date, end_date):
    """Calculate leave days excluding Sundays and Kenyan public holidays"""
    # Kenyan public holidays for 2021-2026
    kenyan_holidays = {
        # 2021
        date(2021, 1, 1),   # New Year's Day
        date(2021, 3, 12),  # Eid al-Fitr (approximate)
        date(2021, 4, 2),   # Good Friday
        date(2021, 4, 5),    # Easter Monday
        date(2021, 5, 1),   # Labour Day
        date(2021, 6, 1),   # Madaraka Day
        date(2021, 7, 10),  # Eid al-Adha (approximate)
        date(2021, 8, 20),  # Utamaduni Day
        date(2021, 10, 10), # Huduma Day
        date(2021, 10, 20), # Mashujaa Day
        date(2021, 12, 12), # Jamhuri Day
        date(2021, 12, 25), # Christmas Day
        date(2021, 12, 26), # Boxing Day
        
        # 2022
        date(2022, 1, 1),   # New Year's Day
        date(2022, 3, 18),  # Good Friday
        date(2022, 4, 15),  # Easter Monday
        date(2022, 5, 1),   # Labour Day
        date(2022, 6, 1),   # Madaraka Day
        date(2022, 7, 9),   # Eid al-Adha
        date(2022, 8, 20),  # Utamaduni Day
        date(2022, 10, 10), # Huduma Day
        date(2022, 10, 20), # Mashujaa Day
        date(2022, 12, 12), # Jamhuri Day
        date(2022, 12, 25), # Christmas Day
        date(2022, 12, 26), # Boxing Day
        
        # 2023
        date(2023, 1, 1),   # New Year's Day
        date(2023, 4, 7),   # Good Friday
        date(2023, 4, 10),  # Easter Monday
        date(2023, 5, 1),   # Labour Day
        date(2023, 6, 1),   # Madaraka Day
        date(2023, 6, 28),  # Eid al-Adha
        date(2023, 8, 20),  # Utamaduni Day
        date(2023, 10, 10), # Huduma Day
        date(2023, 10, 20), # Mashujaa Day
        date(2023, 12, 12), # Jamhuri Day
        date(2023, 12, 25), # Christmas Day
        date(2023, 12, 26), # Boxing Day
        
        # 2024
        date(2024, 1, 1),   # New Year's Day
        date(2024, 3, 29),  # Good Friday
        date(2024, 4, 1),   # Easter Monday
        date(2024, 5, 1),   # Labour Day
        date(2024, 6, 1),   # Madaraka Day
        date(2024, 6, 16),  # Eid al-Adha
        date(2024, 8, 20),  # Utamaduni Day
        date(2024, 10, 10), # Huduma Day
        date(2024, 10, 20), # Mashujaa Day
        date(2024, 12, 12), # Jamhuri Day
        date(2024, 12, 25), # Christmas Day
        date(2024, 12, 26), # Boxing Day
        
        # 2025
        date(2025, 1, 1),   # New Year's Day
        date(2025, 4, 18),  # Good Friday
        date(2025, 4, 21),  # Easter Monday
        date(2025, 5, 1),   # Labour Day
        date(2025, 6, 1),   # Madaraka Day
        date(2025, 6, 6),   # Eid al-Adha
        date(2025, 8, 20),  # Utamaduni Day
        date(2025, 10, 10), # Huduma Day
        date(2025, 10, 20), # Mashujaa Day
        date(2025, 12, 12), # Jamhuri Day
        date(2025, 12, 25), # Christmas Day
        date(2025, 12, 26), # Boxing Day
        
        # 2026
        date(2026, 1, 1),   # New Year's Day
        date(2026, 4, 3),   # Good Friday
        date(2026, 4, 6),   # Easter Monday
        date(2026, 5, 1),   # Labour Day
        date(2026, 6, 1),   # Madaraka Day
        date(2026, 6, 27),  # Eid al-Adha
        date(2026, 8, 20),  # Utamaduni Day
        date(2026, 10, 10), # Huduma Day
        date(2026, 10, 20), # Mashujaa Day
        date(2026, 12, 12), # Jamhuri Day
        date(2026, 12, 25), # Christmas Day
        date(2026, 12, 26), # Boxing Day
    }
    
    total_days = 0
    current = start_date
    while current <= end_date:
        # Exclude Sundays (weekday 6) and Kenyan public holidays
        if current.weekday() != 6 and current not in kenyan_holidays:
            # Saturday is half day (0.5), full days are weekdays 0-4
            if current.weekday() == 5:  # Saturday
                total_days += 0.5
            else:  # Monday to Friday
                total_days += 1
        current = date.fromordinal(current.toordinal() + 1)
    return total_days


def calculate_kenyan_leave(start_date, end_date):
    """
    Calculate leave days for Kenyan holidays (2026).
    
    Daily Check:
    - Sunday or Holiday: Add 0.0 days
    - Saturday: Add 0.5 days
    - Monday-Friday: Add 1.0 day
    
    Args:
        start_date: Start date of the leave
        end_date: End date of the leave
    
    Returns:
        float: Total leave days count
    """
    # Kenyan public holidays for 2026
    kenyan_holidays_2026 = {
        date(2026, 1, 1),   # New Year's Day
        date(2026, 4, 3),   # Good Friday
        date(2026, 4, 6),   # Easter Monday
        date(2026, 5, 1),   # Labour Day
        date(2026, 6, 1),   # Madaraka Day
        date(2026, 10, 10), # Huduma Day
        date(2026, 10, 20), # Mashujaa Day
        date(2026, 12, 12), # Jamhuri Day
        date(2026, 12, 25), # Christmas Day
        date(2026, 12, 26), # Boxing Day
    }
    
    total_days = 0.0
    current = start_date
    while current <= end_date:
        # Sunday (weekday 6) or Holiday: Add 0.0 days
        if current.weekday() == 6 or current in kenyan_holidays_2026:
            total_days += 0.0
        # Saturday (weekday 5): Add 0.5 days
        elif current.weekday() == 5:
            total_days += 0.5
        # Monday-Friday (weekday 0-4): Add 1.0 day
        else:
            total_days += 1.0
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
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
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


@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        staff_count = Staff.query.count()
        attendance_count = Attendance.query.filter_by(work_date=date.today()).count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'staff_count': staff_count,
            'today_attendance_count': attendance_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500



@app.route('/staff')
def staff_portal():
    """Staff portal"""
    return redirect(url_for('index'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('employee_code', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/admin_login.html', error='Invalid password')
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
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        # Use Nairobi timezone for today to match staff clock-ins
        nairobi_tz = pytz.timezone('Africa/Nairobi')
        today = datetime.now(nairobi_tz).date()
        
        # Debug: Print what date we're looking for
        print(f"🔍 Admin is looking for: {today}")
        
        # Use func.date() to ensure proper date comparison in PostgreSQL
        # Eager load staff relationship to avoid N+1 query
        from sqlalchemy.orm import joinedload
        today_attendance = Attendance.query.options(joinedload(Attendance.staff)).filter(func.date(Attendance.work_date) == today).all()

        
        # Debug: Print how many records found
        print(f"📊 Found {len(today_attendance)} attendance records for today")


        
        # Handle month filter for leave requests
        selected_month = request.args.get('month_filter', '')
        
        # Get pending leaves
        pending_leaves = LeaveRequest.query.filter_by(status='Pending').all()
        
        # Get approved leaves for the filtered month (for planning)
        if selected_month:
            month_map = {'February': 2, 'March': 3, 'June': 6}
            month_num = month_map.get(selected_month)
            if month_num:
                year = today.year
                start_date = date(year, month_num, 1)
                if month_num == 12:
                    end_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(year, month_num + 1, 1) - timedelta(days=1)
                
                # Get approved leaves in the selected month for planning
                approved_leaves = LeaveRequest.query.filter(
                    LeaveRequest.status == 'Approved',
                    LeaveRequest.start_date <= end_date,
                    LeaveRequest.end_date >= start_date
                ).all()
            else:
                approved_leaves = []
        else:
            # Show all approved leaves for planning
            approved_leaves = LeaveRequest.query.filter_by(status='Approved').all()
        
        # Build employee summary with days worked and leave balances
        current_month = today.strftime('%B %Y')
        
        # Get first and last day of current month
        first_day_of_month = today.replace(day=1)
        if today.month == 12:
            last_day_of_month = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
        else:
            last_day_of_month = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        
        employee_summary = []
        for emp in staff_members:
            # Calculate days worked this month
            days_worked = Attendance.query.filter(
                Attendance.staff_id == emp.id,
                Attendance.work_date >= first_day_of_month,
                Attendance.work_date <= last_day_of_month
            ).count()
            
            employee_summary.append({
                'name': f"{emp.first_name} {emp.last_name}",
                'employee_code': emp.employee_code,
                'department': emp.department or 'Operations',
                'days_worked': days_worked,
                'annual_leave': emp.leave_balance,
                'sick_leave': emp.sick_leave_balance
            })
        
        # Get all approved leaves for "On Leave" status in attendance
        all_approved_leaves = LeaveRequest.query.filter_by(status='Approved').all()
        
        # Get employees who are on approved leave TODAY - create a set of staff_ids for fast lookup
        today_leaves = LeaveRequest.query.filter(
            LeaveRequest.status == 'Approved',
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        ).all()
        
        # Create a set of staff IDs who are on leave today for O(1) lookup
        # Convert to int to ensure proper comparison in Jinja2 templates
        staff_ids_on_leave_today = [leave.staff_id for leave in today_leaves]
        
        print(f"📅 Today: {today}")
        print(f"👥 Employees on leave today: {staff_ids_on_leave_today}")
        
        # Get upcoming approved leaves (future dates) for the schedule table
        upcoming_leaves = LeaveRequest.query.filter(
            LeaveRequest.status == 'Approved',
            LeaveRequest.start_date > today
        ).order_by(LeaveRequest.start_date.asc()).all()
        
        # Get historical leaves (all approved leaves for reference)
        historical_leaves = LeaveRequest.query.filter_by(status='Approved').order_by(LeaveRequest.start_date.desc()).all()
        
        # Create yearly stats - group approved leaves by employee and year
        # Create a lookup dictionary for staff names
        staff_lookup = {s.id: f"{s.first_name} {s.last_name}" for s in staff_members}
        
        # Build yearly_summary dict first
        yearly_summary = {}
        target_years = [2021, 2022, 2023, 2024, 2025, 2026]
        
        for leave in historical_leaves:
            staff_id = leave.staff_id
            if staff_id not in yearly_summary:
                yearly_summary[staff_id] = {
                    'name': staff_lookup.get(staff_id, 'Unknown'),
                    'years': {year: 0 for year in target_years}
                }
            
            # Extract year from start_date and calculate fiscal year (October start)
            # If month >= 10 (Oct, Nov, Dec), fiscal year = year + 1
            if leave.start_date:
                if leave.start_date.month >= 10:
                    year = leave.start_date.year + 1
                else:
                    year = leave.start_date.year
                
                if year in target_years:
                    yearly_summary[staff_id]['years'][year] += leave.total_days if leave.total_days else 0
        
        # Convert yearly_summary dict to yearly_stats list for the template
        # Separate Annual and Sick leave totals
        yearly_stats = []
        for staff_id, data in yearly_summary.items():
            # Initialize separate dictionaries for Annual and Sick leave
            annual_totals = {year: 0.0 for year in target_years}
            sick_totals = {year: 0.0 for year in target_years}
            
            # Get leave requests for this staff member to separate by type
            staff_leaves = LeaveRequest.query.filter(
                LeaveRequest.staff_id == staff_id,
                LeaveRequest.status == 'Approved'
            ).all()
            
            for leave in staff_leaves:
                if leave.start_date:
                    # Calculate fiscal year (October start)
                    if leave.start_date.month >= 10:
                        year = leave.start_date.year + 1
                    else:
                        year = leave.start_date.year
                    
                    if year in target_years:
                        days = float(leave.total_days) if leave.total_days else 0.0
                        # Flexible Matching: Check for both 'Annual' and 'Annual Leave'
                        if leave.leave_type in ['Annual', 'Annual Leave']:
                            annual_totals[year] += days
                        # Flexible Matching: Check for both 'Sick' and 'Sick Leave'
                        elif leave.leave_type in ['Sick', 'Sick Leave']:
                            sick_totals[year] += days
            
            yearly_stats.append({
                'emp_id': staff_id,
                'full_name': data['name'],
                'annual': annual_totals,
                'sick': sick_totals
            })
        
        # Get recent attendance records (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_attendance = Attendance.query.filter(Attendance.created_at >= yesterday).order_by(Attendance.created_at.desc()).all()
        
        return render_template('admin/dashboard.html', 
                             staff=staff_members,
                             attendance=today_attendance,

                             historical_leaves=historical_leaves,
                             pending_leaves=pending_leaves,
                             today=today,
                             employee_summary=employee_summary,
                             current_month=current_month,
                             selected_month=selected_month,
                             approved_leaves=approved_leaves,
                             all_approved_leaves=all_approved_leaves,
                             staff_ids_on_leave_today=staff_ids_on_leave_today,
                             upcoming_leaves=upcoming_leaves,
                             yearly_stats=yearly_stats)
    except Exception as e:
        print(f"❌ ERROR in admin_dashboard: {str(e)}")
        return render_template('admin/dashboard.html', 
                             staff=[],
                             attendance=[],
                             pending_leaves=[],
                             today=date.today(),
                             employee_summary=[],
                             current_month='',
                             selected_month='',
                             approved_leaves=[],
                             all_approved_leaves=[],
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


@app.route('/admin/add-historical-leave', methods=['GET', 'POST'])
def add_historical_leave():
    """Add historical leave entry form and handler"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'GET':
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        return render_template('admin/add_historical_leave.html', employees=employees)
    
    # POST - Handle form submission
    try:
        emp_id = request.form.get('emp_id', type=int)
        leave_type = request.form.get('leave_type')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason', '') or 'Historical Entry'
        
        if not emp_id:
            return render_template('admin/add_historical_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Please select an employee')
        
        if not start_date_str or not end_date_str:
            return render_template('admin/add_historical_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Please select start and end dates')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if end_date < start_date:
            return render_template('admin/add_historical_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='End date must be after start date')
        
        # Get dropdown values
        total_days_str = request.form.get('total_days', '').strip()
        manual_days_str = request.form.get('manual_days', '').strip()
        
        # Calculate date range in days (inclusive)
        date_range_days = (end_date - start_date).days + 1
        
        if total_days_str == 'manual':
            # Manual entry from the manual_days input field
            if not manual_days_str:
                return render_template('admin/add_historical_leave.html', 
                                    employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                    error='Please enter the number of days for manual entry')
            try:
                total_days = float(manual_days_str)
                if total_days <= 0:
                    return render_template('admin/add_historical_leave.html', 
                                        employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                        error='Days must be a positive number')
            except ValueError:
                return render_template('admin/add_historical_leave.html', 
                                    employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                    error='Invalid days value. Please enter a number.')
        else:
            # Use calculate_kenyan_leave function for automatic calculation
            total_days = calculate_kenyan_leave(start_date, end_date)
            
            # Apply multiplier based on dropdown selection
            # Full Day (1.0) = 1.0, Half Day (0.5) = multiply by 0.5
            if total_days_str == '0.5':
                # Manual Override: If Admin selects 'Half Day', multiply by 0.5
                total_days = total_days * 0.5
        
        staff_member = Staff.query.get(emp_id)
        department = staff_member.department if staff_member and staff_member.department else 'Operations'
        
        if leave_type == 'Annual Leave':
            leave_type = 'Annual'
        
        new_request = LeaveRequest(
            staff_id=emp_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            status='Approved',
            approved_date=datetime.utcnow()
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        # Deduct from leave balance
        if staff_member:
            if leave_type == 'Annual':
                staff_member.leave_balance = max(0, staff_member.leave_balance - total_days)
            elif leave_type == 'Sick':
                staff_member.sick_leave_balance = max(0, getattr(staff_member, 'sick_leave_balance', 7) - total_days)
            db.session.commit()
        
        return render_template('admin/add_historical_leave.html', 
                            employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                            success=f'Successfully added historical leave for {staff_member.first_name} {staff_member.last_name}. Duration: {total_days} days')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('admin/add_historical_leave.html', 
                            employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                            error=f'Error: {str(e)}')


@app.route('/admin-input')
def admin_input():
    """Admin input page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_input.html')


# Export Leave Summary to CSV
@app.route('/export_leave_summary')
def export_leave_summary():
    """Export yearly leave summary to CSV"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get all active employees
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        
        # Get all approved leave requests
        historical_leaves = LeaveRequest.query.filter_by(status='Approved').order_by(LeaveRequest.start_date.desc()).all()
        
        # Create name map
        staff_lookup = {s.id: f"{s.first_name} {s.last_name}" for s in employees}
        
        # Target years
        target_years = [2021, 2022, 2023, 2024, 2025, 2026]
        
        # Build yearly stats
        yearly_stats = []
        for emp in employees:
            emp_id = emp.id
            yearly_totals = {year: 0.0 for year in target_years}
            
            for leave in historical_leaves:
                if leave.staff_id == emp_id and leave.start_date:
                    # Calculate fiscal year (October 1st start)
                    if leave.start_date.month >= 10:
                        year = leave.start_date.year + 1
                    else:
                        year = leave.start_date.year
                    
                    if year in target_years:
                        yearly_totals[year] += float(leave.total_days) if leave.total_days else 0.0
            
            yearly_stats.append({
                'emp_id': emp_id,
                'full_name': staff_lookup.get(emp_id, f"{emp.first_name} {emp.last_name}"),
                'years': yearly_totals
            })
        
        # Generate CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow(['Employee ID', 'Staff Name', '2021', '2022', '2023', '2024', '2025', '2026'])
        
        # Data rows
        for row in yearly_stats:
            writer.writerow([
                row['emp_id'],
                row['full_name'],
                row['years'].get(2021, 0),
                row['years'].get(2022, 0),
                row['years'].get(2023, 0),
                row['years'].get(2024, 0),
                row['years'].get(2025, 0),
                row['years'].get(2026, 0)
            ])
        
        # Return as downloadable file
        output.seek(0)
        return make_response(output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=leave_summary.csv'
        })
    
    except Exception as e:
        print(f"❌ ERROR exporting CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('admin_dashboard'))


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


@app.route('/admin/reports')
def admin_reports():
    """
    Admin reports page - Shows leave and attendance summary by fiscal year.
    Queries all LeaveRequest records for a specific fiscal_year.
    Groups them by staff_id to show total days taken per person.
    Calculates 'Days Worked' by taking 260 (total workdays in a year) and subtracting their total leave days.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get the fiscal year from query params, default to current fiscal year
    selected_fiscal_year = request.args.get('fiscal_year', type=int)
    
    # Calculate current fiscal year based on current date
    today = date.today()
    if today.month >= 10:
        current_fiscal_year = today.year + 1
    else:
        current_fiscal_year = today.year
    
    # Use selected fiscal year or default to current
    fiscal_year = selected_fiscal_year if selected_fiscal_year else current_fiscal_year
    
    # Get all active staff members
    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
    
    # Get all approved leave requests for the selected fiscal year
    leave_requests = LeaveRequest.query.filter(
        LeaveRequest.status == 'Approved',
        LeaveRequest.fiscal_year == fiscal_year
    ).all()
    
    # Group leave requests by staff_id and calculate totals
    leave_summary = {}
    for lr in leave_requests:
        staff_id = lr.staff_id
        if staff_id not in leave_summary:
            leave_summary[staff_id] = {
                'annual_leave_days': 0,
                'sick_leave_days': 0,
                'total_leave_days': 0
            }
        
        if lr.leave_type == 'Annual':
            leave_summary[staff_id]['annual_leave_days'] += lr.total_days
        elif lr.leave_type == 'Sick':
            leave_summary[staff_id]['sick_leave_days'] += lr.total_days
        
        leave_summary[staff_id]['total_leave_days'] += lr.total_days
    
    # Build the summary report
    TOTAL_WORKDAYS = 260  # Standard workdays per year
    
    report_data = []
    for staff in staff_members:
        staff_id = staff.id
        
        # Get leave summary for this staff member
        leave_data = leave_summary.get(staff_id, {
            'annual_leave_days': 0,
            'sick_leave_days': 0,
            'total_leave_days': 0
        })
        
        # Calculate days worked
        days_worked = TOTAL_WORKDAYS - leave_data['total_leave_days']
        
        report_data.append({
            'staff_id': staff_id,
            'employee_code': staff.employee_code,
            'employee_name': f"{staff.first_name} {staff.last_name}",
            'department': staff.department or 'Operations',
            'annual_leave_days': leave_data['annual_leave_days'],
            'sick_leave_days': leave_data['sick_leave_days'],
            'total_leave_days': leave_data['total_leave_days'],
            'days_worked': days_worked
        })
    
    # Get available fiscal years for the dropdown (2021-2025 plus current)
    available_fiscal_years = [2021, 2022, 2023, 2024, 2025, current_fiscal_year]
    available_fiscal_years = sorted(set(available_fiscal_years), reverse=True)
    
    return render_template('admin/reports.html',
                         report_data=report_data,
                         selected_fiscal_year=fiscal_year,
                         available_fiscal_years=available_fiscal_years,
                         total_workdays=TOTAL_WORKDAYS)


@app.route('/admin/annual_report')
def annual_report():
    """
    Annual Report - Shows leave summary for each employee by fiscal year.
    Accepts fiscal_year as URL parameter.
    Calculates Estimated Days Worked = 260 - Total Leave Days.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get the fiscal year from query params, default to current fiscal year
    selected_fiscal_year = request.args.get('fiscal_year', type=int)
    
    # Calculate current fiscal year based on current date
    today = date.today()
    if today.month >= 10:
        current_fiscal_year = today.year + 1
    else:
        current_fiscal_year = today.year
    
    # Use selected fiscal year or default to current
    fiscal_year = selected_fiscal_year if selected_fiscal_year else current_fiscal_year
    
    # Get all active staff members
    staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
    
    # Get all approved leave requests for the selected fiscal year
    leave_requests = LeaveRequest.query.filter(
        LeaveRequest.status == 'Approved',
        LeaveRequest.fiscal_year == fiscal_year
    ).all()
    
    # Group leave by staff_id and sum total days
    leave_by_staff = {}
    for lr in leave_requests:
        staff_id = lr.staff_id
        if staff_id not in leave_by_staff:
            leave_by_staff[staff_id] = 0
        leave_by_staff[staff_id] += lr.total_days
    
    # Build report data
    TOTAL_WORKDAYS = 260
    
    report_data = []
    for staff in staff_members:
        staff_id = staff.id
        total_leave_taken = leave_by_staff.get(staff_id, 0)
        estimated_days_worked = TOTAL_WORKDAYS - total_leave_taken
        
        report_data.append({
            'employee_name': f"{staff.first_name} {staff.last_name}",
            'employee_id': staff.employee_code,
            'total_leave_taken': total_leave_taken,
            'estimated_days_worked': estimated_days_worked
        })
    
    # Available fiscal years for dropdown (2021-2026)
    available_fiscal_years = list(range(2021, 2027))
    
    return render_template('admin/annual_report.html',
                         report_data=report_data,
                         selected_fiscal_year=fiscal_year,
                         available_fiscal_years=available_fiscal_years,
                         total_workdays=TOTAL_WORKDAYS)


# =====================================================
# API ROUTES - WITH ERROR HANDLING
# =====================================================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees - with 08:15 AM late flagging"""
    try:
        # Debug: Print total count in database
        total_in_db = Staff.query.count()
        active_in_db = Staff.query.filter_by(is_active=True).count()
        print(f"DEBUG: Total in DB: {total_in_db}, Active: {active_in_db}")
        
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        print(f"DEBUG: Query returned {len(staff_members)} staff members")
        
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
        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        
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
        # Use Nairobi timezone to match admin dashboard
        nairobi_tz = pytz.timezone('Africa/Nairobi')
        today = datetime.now(nairobi_tz).date()
        attendance = Attendance.query.filter(func.date(Attendance.work_date) == today).all()

        staff_members = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        
        # Get approved leaves for today
        approved_leaves_today = LeaveRequest.query.filter(
            LeaveRequest.status == 'Approved',
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        ).all()
        
        # Create a lookup for approved leaves
        emp_on_leave = {leave.staff_id: leave for leave in approved_leaves_today}
        
        result = []
        for staff in staff_members:
            # First check: Is employee on approved leave today?
            leave = emp_on_leave.get(staff.id)
            if leave:
                status = 'On Leave'
                clock_in = ''
                clock_out = ''
                is_late = False
            else:
                # Second check: Check attendance table
                att = next((a for a in attendance if a.staff_id == staff.id), None)
                
                if att:
                    status = 'Present' if not att.clock_out else 'Clocked Out'
                    clock_in = att.clock_in.strftime('%H:%M') if att.clock_in else ''
                    clock_out = att.clock_out.strftime('%H:%M') if att.clock_out else ''
                    # Check if late based on 08:15 AM threshold
                    is_late = is_late_arrival(att.clock_in)
                else:
                    # Third: No leave, no attendance = Not Clocked In
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
    
    # Get the multiplier from the dropdown (Full Day = 1.0, Half Day = 0.5)
    # If day_type is not provided, default to 1.0 (Full Day)
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
        
        # Step 1: Calculate calendar days using the existing logic (Sat=0.5, Sun/Holiday=0)
        calendar_days = calculate_kenyan_leave(start_date, end_date)
        
        # Step 2: Apply the multiplier from the dropdown
        total_days = calendar_days * multiplier
        
        # Debug log
        print(f"DEBUG Leave: Start={start_date}, End={end_date}, Calendar Days={calendar_days}, Multiplier={multiplier}, Final Days={total_days}")
        
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
    """Approve leave - deducts from balance and creates On Leave attendance"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        leave_request = db.session.get(LeaveRequest, request_id)
        if not leave_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        staff = db.session.get(Staff, leave_request.staff_id)
        
        # Deduct leave from appropriate balance
        if staff:
            if leave_request.leave_type == 'Annual':
                staff.leave_balance -= leave_request.total_days
                if staff.leave_balance < 0:
                    staff.leave_balance = 0
            elif leave_request.leave_type == 'Sick':
                staff.sick_leave_balance -= leave_request.total_days
                if staff.sick_leave_balance < 0:
                    staff.sick_leave_balance = 0
        
        # Create "On Leave" attendance records for each day of leave
        current_date = leave_request.start_date
        while current_date <= leave_request.end_date:
            if current_date.weekday() != 6:
                existing_att = Attendance.query.filter_by(
                    staff_id=leave_request.staff_id,
                    work_date=current_date
                ).first()
                
                if not existing_att:
                    leave_attendance = Attendance(
                        staff_id=leave_request.staff_id,
                        work_date=current_date,
                        clock_in=time(0, 0),
                        clock_out=time(0, 0),
                        day_type='On Leave',
                        status='On Leave',
                        is_late=False,
                        notes=f"{leave_request.leave_type} Leave"
                    )
                    db.session.add(leave_attendance)
            
            current_date = current_date + timedelta(days=1)
        
        leave_request.status = 'Approved'
        leave_request.approved_by = 1
        leave_request.approved_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave approved and deducted from balance',
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
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
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
        
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        
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
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
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
    # Get port first - Render requires this
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('PORT') is None
    
    db_type = "PostgreSQL (Supabase)" if "postgresql" in DATABASE_URL else "SQLite (Local)"
    print(f"\n{'='*60}")
    print("ATTENDANCE SYSTEM STARTUP")
    print(f"{'='*60}")
    print(f"Database: {db_type}")
    print(f"URL: {DATABASE_URL[:50]}...")
    print(f"Late Threshold: {LATE_THRESHOLD}")
    print(f"Port: {port}")
    print(f"{'='*60}\n")
    
    # Initialize database before starting server
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created")
            seed_staff()
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
    
    print(f"🚀 Starting server on port {port}...")
    # Start server immediately - Render needs the port open ASAP
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
