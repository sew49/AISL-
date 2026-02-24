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

# =====================================================
# FISCAL YEAR UTILITY
# =====================================================

def calculate_fiscal_year(input_date):
    """Calculate fiscal year based on input date. Fiscal year starts October 1st."""
    if input_date.month >= 10:
        return f"{input_date.year}/{input_date.year + 1}"
    else:
        return f"{input_date.year - 1}/{input_date.year}"


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
    # Import from main which has the models attached
    from app import db, Staff, LeaveRequest, Holiday
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
