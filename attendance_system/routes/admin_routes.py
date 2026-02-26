"""
Admin Routes for the Attendance System
These routes are enabled when running on Render (RENDER env var is set)
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, make_response
from datetime import datetime, date, timedelta
from functools import wraps
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Staff and Holiday from ..app as required
try:
    from ..app import db, Staff, LeaveRequest, Holiday
except ImportError:
    # Fallback for module not found
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    db = app_module.db
    Staff = app_module.Staff
    LeaveRequest = app_module.LeaveRequest
    Holiday = app_module.Holiday

# =====================================================
# FISCAL YEAR UTILITY
# =====================================================

def calculate_fiscal_year(input_date):
    """Calculate fiscal year based on input date. Fiscal year starts October 1st."""
    if input_date.month >= 10:
        return f"{input_date.year}/{input_date.year + 1}"
    else:
        return f"{input_date.year - 1}/{input_date.year}"


def calculate_fiscal_year_int(input_date):
    """
    Calculate fiscal year as integer based on October 1st Fiscal Year.
    If month >= 10 (October onwards), fiscal year = year + 1
    Otherwise, fiscal year = year
    """
    if input_date.month >= 10:
        return input_date.year + 1
    else:
        return input_date.year


# =====================================================
# LEAVE CALCULATION UTILITY
# =====================================================

def calculate_actual_leave_days(start_date, end_date):
    """
    Calculate actual leave days excluding Sundays, Saturdays (0.5), and holidays.
    
    Args:
        start_date: Start date of the leave
        end_date: End date of the leave
    
    Returns:
        float: Actual leave days count
    """
    # Fetch all holidays from the Holiday table
    holidays = [h.holiday_date for h in Holiday.query.all()]
    
    # Generate all dates in the range
    total_days = (end_date - start_date).days + 1
    actual_count = 0
    
    for i in range(total_days):
        current_day = start_date + timedelta(days=i)
        # Check if it's not a Sunday (weekday 6) and not a holiday
        if current_day.weekday() != 6 and current_day not in holidays:
            if current_day.weekday() == 5:  # Saturday
                actual_count += 0.5
            else:  # Monday to Friday (weekday 0-4)
                actual_count += 1
            
    return actual_count


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
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    continue
            raise last_exception
        return wrapper
    return decorator


# =====================================================
# ADMIN BLUEPRINT
# =====================================================

admin_bp = Blueprint('admin', __name__)


# =====================================================
# ADMIN ROUTES - These are NOT used, standalone routes are in main.py
# =====================================================

# Note: The standalone admin routes in main.py take precedence
# This blueprint is kept for reference but is NOT registered


@admin_bp.route('/admin/add_manual_leave', methods=['GET', 'POST'])
def add_manual_leave():
    """
    Add manual leave entry via form.
    Uses October 1st Fiscal Year logic:
    - if start_date.month >= 10, fiscal_year = start_date.year + 1
    - otherwise fiscal_year = start_date.year
    Calculates actual_days by excluding weekends and holidays from Holiday table.
    """
    from ..app import db, Staff, LeaveRequest, Holiday
    
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'GET':
        employees = Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all()
        return render_template('admin/add_manual_leave.html', employees=employees)
    
    # POST - Handle form submission
    try:
        staff_id = request.form.get('staff_id', type=int)
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        leave_type = request.form.get('leave_type')
        reason = request.form.get('reason', '') or 'Manual Entry'
        
        if not staff_id:
            return render_template('admin/add_manual_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Please select an employee')
        
        if not start_date_str or not end_date_str:
            return render_template('admin/add_manual_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Please select start and end dates')
        
        if not leave_type:
            return render_template('admin/add_manual_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Please select leave type')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if end_date < start_date:
            return render_template('admin/add_manual_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='End date must be after start date')
        
        # Calculate actual days excluding weekends and holidays
        actual_days = calculate_actual_leave_days(start_date, end_date)
        
        # DEBUG: Print the actual days calculation
        print(f"DEBUG: Start date: {start_date}, End date: {end_date}")
        print(f"DEBUG: Date range days (inclusive): {(end_date - start_date).days + 1}")
        print(f"DEBUG: Calculated actual_days: {actual_days}")
        
        # Calculate fiscal year using October 1st logic
        if start_date.month >= 10:
            fiscal_year = start_date.year + 1
        else:
            fiscal_year = start_date.year
        
        staff_member = Staff.query.get(staff_id)
        if not staff_member:
            return render_template('admin/add_manual_leave.html', 
                                employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                                error='Staff member not found')
        
        # Normalize leave type
        if leave_type == 'Annual Leave':
            leave_type = 'Annual'
        
        # Create the leave request
        new_request = LeaveRequest(
            staff_id=staff_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=actual_days,
            reason=reason,
            status='Approved',
            approved_date=datetime.utcnow(),
            fiscal_year=fiscal_year
        )
        
        db.session.add(new_request)
        
        # Deduct from leave balance
        if leave_type == 'Annual':
            staff_member.leave_balance = max(0, staff_member.leave_balance - actual_days)
        elif leave_type == 'Sick':
            staff_member.sick_leave_balance = max(0, getattr(staff_member, 'sick_leave_balance', 7) - actual_days)
        
        db.session.commit()
        
        return render_template('admin/add_manual_leave.html', 
                            employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                            success=f'Successfully added leave for {staff_member.first_name} {staff_member.last_name}. Duration: {actual_days} days (Fiscal Year: {fiscal_year})')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('admin/add_manual_leave.html', 
                            employees=Staff.query.filter_by(is_active=True).order_by(Staff.employee_code.asc()).all(),
                            error=f'Error: {str(e)}')
