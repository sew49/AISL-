# =====================================================
# ATTENDANCE SYSTEM - MAIN ENTRY POINT
# =====================================================
"""
This file serves as the main entry point for the Attendance System.

All routes (Admin and Staff) are enabled regardless of environment.
"""

import os
from datetime import datetime, date, timedelta
from functools import wraps

# Import configuration
from config import (
    IS_RENDER,
    APP_MODE,
    SUPABASE_URL,
    SUPABASE_KEY,
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_ENGINE_OPTIONS,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY,
    PERMANENT_SESSION_LIFETIME_HOURS
)

# =====================================================
# FLASK APP SETUP
# =====================================================

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=PERMANENT_SESSION_LIFETIME_HOURS)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    AnnualLeaveBalance = db.Column(db.Numeric(5, 2), default=21)
    
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
            'is_active': self.IsActive,
            'annual_leave_balance': float(self.AnnualLeaveBalance) if self.AnnualLeaveBalance else 21
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
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
            'notes': self.Notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
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
    Department = db.Column(db.String(100), nullable=False)
    Status = db.Column(db.String(20), default='Pending')
    ApprovedBy = db.Column(db.Integer, db.ForeignKey('employees.EmpID'))
    ApprovedDate = db.Column(db.DateTime)
    RequestedAt = db.Column(db.DateTime, default=datetime.utcnow)
    FiscalYear = db.Column(db.Integer, nullable=True)  # Fiscal year for tracking 2021-2025 leave history
    
    employee = db.relationship('Employee', foreign_keys=[EmpID], backref='leave_requests')
    approver = db.relationship('Employee', foreign_keys=[ApprovedBy])
    
    @staticmethod
    def get_fiscal_year(p_date):
        """
        Calculate fiscal year based on date.
        If month is 10 (October), 11 (November), or 12 (December), return date.year + 1.
        Otherwise, return date.year.
        """
        if p_date.month in (10, 11, 12):
            return p_date.year + 1
        return p_date.year
    
    def to_dict(self):
        return {
            'request_id': self.RequestID,
            'emp_id': self.EmpID,
            'leave_type': self.LeaveType,
            'start_date': self.StartDate.isoformat() if self.StartDate else None,
            'end_date': self.EndDate.isoformat() if self.EndDate else None,
            'total_days': float(self.TotalDays),
            'reason': self.Reason,
            'department': self.Department,
            'status': self.Status,
            'approved_by': self.ApprovedBy,
            'approved_date': self.ApprovedDate.isoformat() if self.ApprovedDate else None,
            'requested_at': self.RequestedAt.isoformat() if self.RequestedAt else None,
            'fiscal_year': self.FiscalYear
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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# Attach models to app for access via current_app in routes
app.Attendance = Attendance
app.Employee = Employee
app.LeaveRequest = LeaveRequest
app.LeaveBalance = LeaveBalance
app.Holiday = Holiday
app.Notification = Notification
app.FiscalYear = FiscalYear
app.db = db
app.get_fiscal_year_python = get_fiscal_year_python
app.calculate_leave_days_python = calculate_leave_days_python


# =====================================================
# ALWAYS-ENABLED ROUTES
# =====================================================

print(f"\n{'='*60}")
print(f"ATTENDANCE SYSTEM STARTUP")
print(f"{'='*60}")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"Database: {'PostgreSQL' if 'postgresql' in SQLALCHEMY_DATABASE_URI else 'SQLite'}")
print(f"{'='*60}\n")

# Home route - serves staff portal
@app.route('/')
def index():
    """Home page - staff portal"""
    return render_template('staff/index.html')

# Admin Login route (standalone)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == 'RAV4Adventure2019':
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/admin_login.html', error='Invalid password')
    return render_template('admin/admin_login.html')

# Admin Logout route (standalone)
@app.route('/admin-logout')
def admin_logout():
    """Admin logout - clears session and redirects to login"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Delete Leave route (standalone)
@app.route('/delete_leave/<int:leave_id>', methods=['POST', 'GET'])
def delete_leave(leave_id):
    """Delete a leave request record"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        leave_request = LeaveRequest.query.get(leave_id)
        if not leave_request:
            return redirect(url_for('admin_dashboard'))
        
        # Get employee name before deletion for the message
        employee = Employee.query.get(leave_request.EmpID)
        employee_name = f"{employee.FirstName} {employee.LastName}" if employee else "Unknown"
        
        # Delete the leave request
        db.session.delete(leave_request)
        db.session.commit()
        
        print(f"✅ Deleted leave request {leave_id} for {employee_name}")
        
        return redirect(url_for('admin_dashboard'))
    
    except Exception as e:
        print(f"❌ ERROR deleting leave: {str(e)}")
        db.session.rollback()
        return redirect(url_for('admin_dashboard'))

# Manage Historical Leaves route (standalone)
@app.route('/admin/manage-leaves')
def manage_leaves():
    """View and manage historical leave records"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get all leave requests
        all_leaves = LeaveRequest.query.order_by(LeaveRequest.StartDate.desc()).all()
        
        # Get all employees for name lookup
        employees = Employee.query.all()
        name_map = {e.EmpID: f"{e.FirstName} {e.LastName}" for e in employees}
        
        return render_template('admin/manage_leaves.html',
                            leaves=all_leaves,
                            name_map=name_map)
    
    except Exception as e:
        print(f"❌ ERROR loading leaves: {str(e)}")
        return render_template('admin/manage_leaves.html',
                            leaves=[],
                            name_map={},
                            error=str(e))

# Export Leave Summary to CSV
@app.route('/export_leave_summary')
def export_leave_summary():
    """Export yearly leave summary to CSV"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get all active employees
        employees = Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all()
        
        # Get all approved leave requests
        historical_leaves = LeaveRequest.query.filter_by(Status='Approved').order_by(LeaveRequest.StartDate.desc()).all()
        
        # Create name map
        staff_list = Employee.query.all()
        name_map = {s.EmpID: f"{s.FirstName} {s.LastName}" for s in staff_list}
        
        # Target years
        target_years = [2021, 2022, 2023, 2024, 2025, 2026]
        
        # Build yearly stats
        yearly_stats = []
        for emp in employees:
            emp_id = emp.EmpID
            yearly_totals = {year: 0.0 for year in target_years}
            
            for leave in historical_leaves:
                if leave.EmpID == emp_id and leave.StartDate:
                    # Calculate fiscal year (October 1st start)
                    if leave.StartDate.month >= 10:
                        year = leave.StartDate.year + 1
                    else:
                        year = leave.StartDate.year
                    
                    if year in target_years:
                        yearly_totals[year] += float(leave.TotalDays) if leave.TotalDays else 0.0
            
            yearly_stats.append({
                'emp_id': emp_id,
                'full_name': name_map.get(emp_id, f"{emp.FirstName} {emp.LastName}"),
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

# Admin Dashboard route (standalone)
@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - displays today's attendance and leave status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        today = date.today()
        
        # Debug: Print database connection info
        print(f"🔍 Database connection: {SQLALCHEMY_DATABASE_URI[:30]}...")
        
        employees = Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all()
        print(f"👥 Active employees found: {len(employees)}")
        
        # Get last 100 attendance records ordered by timestamp (most recent first)
        # No date filter - get all recent records
        attendance = Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all()
        print(f"📋 Recent attendance records: {len(attendance)}")
        
        # Debug: Also get all attendance to see if there are any records at all
        all_attendance_count = Attendance.query.count()
        print(f"📊 Total attendance records in database: {all_attendance_count}")
        
        # Get approved leaves for today
        approved_leaves_today = LeaveRequest.query.filter(
            LeaveRequest.Status == 'Approved',
            LeaveRequest.StartDate <= today,
            LeaveRequest.EndDate >= today
        ).all()
        
        # Create a set of employee IDs who are on leave today
        emp_ids_on_leave = {leave.EmpID for leave in approved_leaves_today}
        
        # Get pending leave requests
        pending_leaves = LeaveRequest.query.filter_by(Status='Pending').order_by(LeaveRequest.RequestedAt.desc()).all()
        
        # Get year filter from query params
        selected_year = request.args.get('year_filter', '')
        
        # Get all approved leaves (for planning) - filtered by year if selected
        if selected_year:
            fy_start = date(int(selected_year), 10, 1)
            fy_end = date(int(selected_year) + 1, 9, 30)
            
            all_approved_leaves = LeaveRequest.query.filter(
                LeaveRequest.Status == 'Approved',
                LeaveRequest.StartDate >= fy_start,
                LeaveRequest.StartDate <= fy_end
            ).order_by(LeaveRequest.StartDate.desc()).all()
        else:
            all_approved_leaves = LeaveRequest.query.filter_by(Status='Approved').order_by(LeaveRequest.StartDate.desc()).all()
        
        # Get upcoming leaves (future dates)
        upcoming_leaves = LeaveRequest.query.filter(
            LeaveRequest.Status == 'Approved',
            LeaveRequest.StartDate > today
        ).order_by(LeaveRequest.StartDate.asc()).all()
        
        # Get historical leaves (Status='Approved' with capital A)
        historical_leaves = LeaveRequest.query.filter_by(Status='Approved').order_by(LeaveRequest.StartDate.desc()).all()
        
        # Fetch all staff for name mapping
        staff_list = Employee.query.all()
        
        # Create name map: staff_id -> "first_name last_name"
        name_map = {s.EmpID: f"{s.FirstName} {s.LastName}" for s in staff_list}
        
        # Create yearly stats object: each row contains Employee ID, Full Name, and total days for each year (2021-2026)
        yearly_stats = []
        target_years = [2021, 2022, 2023, 2024, 2025, 2026]
        
        for emp in employees:
            emp_id = emp.EmpID
            # Initialize yearly totals for this employee as floats
            yearly_totals = {year: 0.0 for year in target_years}
            
            # Calculate totals from historical leaves for this employee
            for leave in historical_leaves:
                if leave.EmpID == emp_id and leave.StartDate:
                    # Calculate fiscal year (October 1st start)
                    # If month is October(10), November(11), or December(12), fiscal year = year + 1
                    if leave.StartDate.month >= 10:
                        year = leave.StartDate.year + 1
                    else:
                        year = leave.StartDate.year
                    
                    if year in target_years:
                        yearly_totals[year] += float(leave.TotalDays) if leave.TotalDays else 0.0
            
            # Build the row with Employee ID, Full Name (using name_map), and yearly totals
            row = {
                'emp_id': emp_id,
                'full_name': name_map.get(emp_id, f"{emp.FirstName} {emp.LastName}"),
                'years': yearly_totals
            }
            yearly_stats.append(row)
        
        print(f"📅 Today: {today}")
        print(f"👥 Employees on leave today: {emp_ids_on_leave}")
        print(f"📋 Historical leaves found: {len(historical_leaves)}")
        print(f"📊 Yearly stats computed for {len(yearly_stats)} employees")
        
        return render_template('admin/dashboard.html',
                            staff=employees,
                            attendance=attendance,
                            pending_leaves=pending_leaves,
                            today=today,
                            employee_summary=[],
                            current_month=today.strftime('%B %Y'),
                            selected_month='',
                            selected_year=selected_year,
                            approved_leaves=all_approved_leaves,
                            all_approved_leaves=all_approved_leaves,
                            staff_ids_on_leave_today=list(emp_ids_on_leave),
                            upcoming_leaves=upcoming_leaves,
                            historical_leaves=historical_leaves,
                            staff_lookup=name_map,
                            yearly_stats=yearly_stats)
    except Exception as e:
        print(f"❌ ERROR in admin_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('admin/dashboard.html',
                            staff=[],
                            attendance=[],
                            pending_leaves=[],
                            today=date.today(),
                            employee_summary=[],
                            current_month='',
                            selected_month='',
                            selected_year='',
                            approved_leaves=[],
                            all_approved_leaves=[],
                            error=f"Database error: {str(e)}")

# Add Historical Leave route (standalone)
@app.route('/admin/add-historical-leave', methods=['GET', 'POST'])
def add_historical_leave():
    """Add historical leave entry form and handler"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'GET':
        employees = Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all()
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
                                employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                                error='Please select an employee')
        
        if not start_date_str or not end_date_str:
            return render_template('admin/add_historical_leave.html', 
                                employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                                error='Please select start and end dates')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if end_date < start_date:
            return render_template('admin/add_historical_leave.html', 
                                employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                                error='End date must be after start date')
        
        # Check if manual days input is provided
        total_days_str = request.form.get('total_days', '').strip()
        if total_days_str:
            # Use manual input as float
            try:
                total_days = float(total_days_str)
                if total_days <= 0:
                    return render_template('admin/add_historical_leave.html', 
                                        employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                                        error='Days must be a positive number')
            except ValueError:
                return render_template('admin/add_historical_leave.html', 
                                    employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                                    error='Invalid days value. Please enter a number.')
        else:
            # Auto-calculate from dates
            total_days = calculate_leave_days_python(start_date, end_date)
        
        fiscal_year = get_fiscal_year_python(start_date)
        
        employee = Employee.query.get(emp_id)
        department = employee.Department if employee and employee.Department else 'Operations'
        
        if leave_type == 'Annual Leave':
            leave_type = 'Annual'
        elif leave_type == 'Sick Leave':
            leave_type = 'Sick'
        
        balance = LeaveBalance.query.filter_by(EmpID=emp_id, FiscalYear=fiscal_year).first()
        
        if not balance:
            balance = LeaveBalance(
                EmpID=emp_id,
                FiscalYear=fiscal_year,
                AnnualDays=21,
                SickDays=10,
                CasualDays=5,
                UsedAnnualDays=0,
                UsedSickDays=0,
                UsedCasualDays=0
            )
            db.session.add(balance)
            db.session.commit()
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Department=department,
            Status='Approved',
            ApprovedDate=datetime.utcnow()
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        if leave_type in ['Annual', 'Sick', 'Casual']:
            if leave_type == 'Annual':
                balance.UsedAnnualDays = float(balance.UsedAnnualDays) + float(total_days)
            elif leave_type == 'Sick':
                balance.UsedSickDays = float(balance.UsedSickDays) + float(total_days)
            elif leave_type == 'Casual':
                balance.UsedCasualDays = float(balance.UsedCasualDays) + float(total_days)
            db.session.commit()
        
        return render_template('admin/add_historical_leave.html', 
                            employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                            success=f'Successfully added historical leave for {employee.FirstName} {employee.LastName}. Duration: {total_days} days')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('admin/add_historical_leave.html', 
                            employees=Employee.query.filter_by(IsActive=True).order_by(Employee.EmployeeCode.asc()).all(),
                            error=f'Error: {str(e)}')

# Load Staff routes (no prefix - at root)
print(">>> Loading Staff Routes <<<")
from routes.staff_routes import staff_bp
app.register_blueprint(staff_bp)
print(">>> Staff Routes Registered Successfully <<<\n")

# Load Admin routes
print(">>> Loading Admin Routes <<<")
from routes.admin_routes import admin_bp
app.register_blueprint(admin_bp)
print(">>> Admin Routes Registered Successfully <<<\n")


# =====================================================
# MAIN
# =====================================================

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
                    JoinDate=datetime.now().date(),
                    AnnualLeaveBalance=21
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
            
            print(f"\n🎉 Successfully added {len(employees)} employees!")
        else:
            print("Database already has employees, checking for leave balance updates...")
            
            employees_without_balance = Employee.query.filter(
                db.or_(
                    Employee.AnnualLeaveBalance == None,
                    Employee.AnnualLeaveBalance == 0
                )
            ).all()
            
            for emp in employees_without_balance:
                emp.AnnualLeaveBalance = 21
            
            if employees_without_balance:
                db.session.commit()
                print(f"✅ Updated {len(employees_without_balance)} existing employees with 21 days leave balance")
            else:
                print("All employees already have leave balance set.")
    
    print(f"\n🚀 Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
