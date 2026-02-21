"""
Setup Script for Attendance Management System
Creates the project structure and initializes the database
"""
import os
import shutil

# Create directory structure
def create_directories():
    """Create project directories"""
    dirs = ['templates', 'static']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name)
        print(f"✅ Created /{dir_name} folder")

# Create app.py
def create_app_py():
    """Create the main Flask application"""
    app_py_content = '''# =====================================================
# ATTENDANCE SYSTEM - FLASK API
# =====================================================

from flask import Flask, request, jsonify, render_template
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


# =====================================================
# ROUTES
# =====================================================

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')


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
    
    # Support simple format: {"name": "John Doe", "annual_leave_entitlement": 21}
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
    
    # Create leave balance if annual_leave_entitlement provided
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
    
    # Saturday check: 5 hours (8am-1pm), otherwise 8 hours
    if work_date.weekday() == 6:  # Sunday
        return jsonify({
            'success': False,
            'error': 'Cannot create attendance for Sunday'
        }), 400
    
    # Check if Saturday
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
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    reason = data.get('reason', '')
    
    try:
        total_days = calculate_leave_days_python(start_date, end_date)
        
        if leave_type in ['Annual', 'Sick']:
            fiscal_year = get_fiscal_year_python(start_date)
            balance = LeaveBalance.query.filter_by(EmpID=emp_id, FiscalYear=fiscal_year).first()
            
            if not balance:
                return jsonify({'success': False, 'error': 'No leave balance found'}), 400
            
            if leave_type == 'Annual':
                available = float(balance.AnnualDays - balance.UsedAnnualDays)
                if total_days > available:
                    return jsonify({'success': False, 'error': f'Insufficient annual leave. Available: {available}'}), 400
                balance.UsedAnnualDays += total_days
            elif leave_type == 'Sick':
                available = float(balance.SickDays - balance.UsedSickDays)
                if total_days > available:
                    return jsonify({'success': False, 'error': f'Insufficient sick leave. Available: {available}'}), 400
                balance.UsedSickDays += total_days
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Status='Pending'
 db.session.add(new        )
        
       _request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request submitted',
            'leave_request': new_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
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
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_py_content)
    print("✅ Created app.py")


def create_index_html():
    """Create the index.html template"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white py-4 px-4">
        <div class="max-w-4xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 class="text-2xl font-bold">Attendance System</h1>
                    <p class="text-blue-200">Fiscal Year 2026</p>
                </div>
                <div class="text-right mt-2 md:mt-0">
                    <p id="currentDate" class="text-lg font-semibold"></p>
                    <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full"></p>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto p-4 pb-20">
        <!-- Alert -->
        <div id="alertMessage" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 hidden">
            <div id="alertContent" class="bg-white rounded-lg shadow-xl p-4 max-w-md border-l-4"></div>
        </div>

        <!-- Attendance Section -->
        <section class="bg-white rounded-xl shadow-lg p-6 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">🕐 Clock In / Out</h2>
            
            <div class="space-y-4">
                <select id="employeeSelect" class="w-full px-4 py-3 border border-gray-300 rounded-lg text-base">
                    <option value="">-- Select Your Name --</option>
                </select>
                
                <div class="flex flex-col sm:flex-row gap-3">
                    <button id="clockInBtn" class="flex-1 py-4 bg-green-500 hover:bg-green-600 text-white font-bold rounded-lg text-lg">
                        Clock In
                    </button>
                    <button id="clockOutBtn" class="flex-1 py-4 bg-red-500 hover:bg-red-600 text-white font-bold rounded-lg text-lg">
                        Clock Out
                    </button>
                </div>
            </div>
        </section>

        <!-- Leave Balance -->
        <section class="bg-white rounded-xl shadow-lg p-6 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">📊 Leave Balance</h2>
            <div id="leaveBalance" class="text-center py-4 text-gray-500">Select an employee to view balance</div>
        </section>

        <!-- Today's Status -->
        <section class="bg-white rounded-xl shadow-lg p-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold text-gray-800">📋 Today's Status</h2>
                <button id="refreshStatus" class="p-2 text-gray-500 hover:text-blue-600">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                </button>
            </div>
            <div id="statusTable" class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left">Employee</th>
                            <th class="px-3 py-2 text-left">Time In</th>
                            <th class="px-3 py-2 text-left">Status</th>
                        </tr>
                    </thead>
                    <tbody id="statusTableBody">
                        <tr><td colspan="3" class="px-3 py-8 text-center text-gray-500">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
            <div id="emptyStatus" class="hidden text-center py-8 text-gray-500">No one clocked in today</div>
        </section>
    </main>

    <script>
        const API_BASE = 'http://192.168.8.74:5000';
        
        // Set header date
        function setHeaderDate() {
            const now = new Date();
            document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            
            const dayOfWeek = now.getDay();
            const dayTypeEl = document.getElementById('dayType');
            
            if (dayOfWeek === 6) {
                dayTypeEl.textContent = 'Saturday (5hrs) - 8am to 1pm';
                dayTypeEl.className = 'text-sm bg-yellow-500/30 px-3 py-1 rounded-full';
            } else if (dayOfWeek === 0) {
                dayTypeEl.textContent = 'Sunday (No Work)';
                dayTypeEl.className = 'text-sm bg-red-500/30 px-3 py-1 rounded-full';
            } else {
                dayTypeEl.textContent = 'Standard Day (8hrs) - 8am to 5pm';
                dayTypeEl.className = 'text-sm bg-green-500/30 px-3 py-1 rounded-full';
            }
        }

        // Show alert
        function showAlert(message, type = 'success') {
            const alertEl = document.getElementById('alertMessage');
            const alertContent = document.getElementById('alertContent');
            alertContent.className = type === 'success-green-100 border' ? 'bg-green-500 text-green-800' : 'bg-red-100 border-red-500 text-red-800';
            alertContent.innerHTML = message;
            alertEl.classList.remove('hidden');
            setTimeout(() => alertEl.classList.add('hidden'), 5000);
        }

        // Fetch employees
        async function fetchEmployees() {
            try {
                const response = await fetch(API_BASE + '/api/employees');
                const data = await response.json();
                if (data.success) {
                    const options = '<option value="">-- Select Your Name --</option>' + 
                        data.employees.map(emp => 
                            `<option value="${emp.emp_id}">${emp.first_name} ${emp.last_name}</option>`
                        ).join('');
                    document.getElementById('employeeSelect').innerHTML = options;
                }
            } catch (error) {
                showAlert('Failed to connect to server', 'error');
            }
        }

        // Fetch leave balance
        async function fetchLeaveBalance(empId) {
            if (!empId) {
                document.getElementById('leaveBalance').innerHTML = 'Select an employee to view balance';
                return;
            }
            try {
                const response = await fetch(API_BASE + '/api/leave-balances?emp_id=' + empId);
                const data = await response.json();
                if (data.success && data.leave_balances.length > 0) {
                    const b = data.leave_balances[0];
                    document.getElementById('leaveBalance').innerHTML = `
                        <div class="grid grid-cols-3 gap-4 text-center">
                            <div class="bg-blue-50 p-3 rounded-lg">
                                <div class="text-2xl font-bold text-blue-600">${b.remaining_annual}</div>
                                <div class="text-xs text-gray-600">Annual Leave</div>
                            </div>
                            <div class="bg-green-50 p-3 rounded-lg">
                                <div class="text-2xl font-bold text-green-600">${b.remaining_sick}</div>
                                <div class="text-xs text-gray-600">Sick Leave</div>
                            </div>
                            <div class="bg-yellow-50 p-3 rounded-lg">
                                <div class="text-2xl font-bold text-yellow-600">${b.remaining_casual || 5}</div>
                                <div class="text-xs text-gray-600">Casual Leave</div>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error(error);
            }
        }

        // Clock In
        document.getElementById('clockInBtn').addEventListener('click', async () => {
            const empId = document.getElementById('employeeSelect').value;
            if (!empId) { showAlert('Please select an employee', 'error'); return; }
            
            const today = new Date().toISOString().split('T')[0];
            const now = new Date().toTimeString().slice(0, 5);
            
            try {
                const response = await fetch(API_BASE + '/api/attendance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emp_id: parseInt(empId), work_date: today, clock_in: now })
                });
                const data = await response.json();
                if (data.success) {
                    showAlert('✅ Clocked in at ' + now, 'success');
                    fetchTodayStatus();
                } else {
                    showAlert('❌ ' + (data.error || 'Failed'), 'error');
                }
            } catch (error) {
                showAlert('❌ Connection error', 'error');
            }
        });

        // Clock Out
        document.getElementById('clockOutBtn').addEventListener('click', async () => {
            const empId = document.getElementById('employeeSelect').value;
            if (!empId) { showAlert('Please select an employee', 'error'); return; }
            
            try {
                const today = new Date().toISOString().split('T')[0];
                const response = await fetch(API_BASE + '/api/attendance?emp_id=' + empId + '&start_date=' + today + '&end_date=' + today);
                const data = await response.json();
                
                if (data.success && data.attendance.length > 0) {
                    const att = data.attendance[0];
                    if (att.clock_out) { showAlert('⚠️ Already clocked out', 'error'); return; }
                    
                    const now = new Date().toTimeString().slice(0, 5);
                    const update = await fetch(API_BASE + '/api/attendance/' + att.attendance_id, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ clock_out: now })
                    });
                    const updateData = await update.json();
                    if (updateData.success) {
                        showAlert('✅ Clocked out at ' + now, 'success');
                        fetchTodayStatus();
                    }
                } else {
                    showAlert('❌ No clock-in record. Clock in first.', 'error');
                }
            } catch (error) {
                showAlert('❌ Connection error', 'error');
            }
        });

        // Fetch today's status
        async function fetchTodayStatus() {
            try {
                const today = new Date().toISOString().split('T')[0];
                const response = await fetch(API_BASE + '/api/attendance?start_date=' + today + '&end_date=' + today);
                const data = await response.json();
                
                const empResponse = await fetch(API_BASE + '/api/employees');
                const empData = await empResponse.json();
                const empMap = {};
                if (empData.success) empData.employees.forEach(e => empMap[e.emp_id] = e.first_name + ' ' + e.last_name);
                
                if (data.success && data.attendance.length > 0) {
                    const rows = data.attendance.map(att => {
                        const status = att.clock_out ? 'Out' : 'In';
                        const cls = att.clock_out ? 'bg-gray-100 text-gray-800' : 'bg-green-100 text-green-800';
                        return '<tr class="hover:bg-gray-50"><td class="px-3 py-2 font-medium">' + (empMap[att.emp_id] || 'Unknown') + '</td><td class="px-3 py-2">' + (att.clock_in || '-') + '</td><td class="px-3 py-2"><span class="px-2 py-1 text-xs rounded-full ' + cls + '">' + status + '</span></td></tr>';
                    }).join('');
                    document.getElementById('statusTableBody').innerHTML = rows;
                    document.getElementById('emptyStatus').classList.add('hidden');
                } else {
                    document.getElementById('statusTableBody').innerHTML = '';
                    document.getElementById('emptyStatus').classList.remove('hidden');
                }
            } catch (error) {
                console.error(error);
            }
        }

        // Event listeners
        document.getElementById('employeeSelect').addEventListener('change', (e) => fetchLeaveBalance(e.target.value));
        document.getElementById('refreshStatus').addEventListener('click', fetchTodayStatus);

        // Init
        setHeaderDate();
        fetchEmployees();
        fetchTodayStatus();
        setInterval(fetchTodayStatus, 30000);
    </script>
</body>
</html>
'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Created templates/index.html")


def main():
    """Main setup function"""
    print("\n" + "="*50)
    print("🎯 Setting up Attendance System Project")
    print("="*50 + "\n")
    
    create_directories()
    create_app_py()
    create_index_html()
    
    print("\n" + "="*50)
    print("✅ Project structure created successfully!")
    print("="*50)
    print("\nTo run the application:")
    print("  python app.py")
    print("\nThen open: http://192.168.8.74:5000")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()
