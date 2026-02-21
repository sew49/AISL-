"""
PDF Report Generation Module for Attendance System
Requires: pip install pdfkit
Requires: wkhtmltopdf installed on system
"""

import pdfkit
from flask import make_response

# PDF Report Configuration - Update this path if wkhtmltopdf is installed elsewhere
WKDHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

try:
    config = pdfkit.configuration(wkhtmltopdf=WKDHTMLTOPDF_PATH)
except Exception:
    config = None


def generate_attendance_pdf(attendance_data, employees_dict, start_date, end_date):
    """
    Generate PDF report for attendance records
    
    Args:
        attendance_data: List of Attendance objects
        employees_dict: Dict mapping EmpID to employee name
        start_date: Start date string
        end_date: End date string
    
    Returns:
        PDF bytes
    """
    if config is None:
        raise Exception("PDFKit configuration failed. Make sure wkhtmltopdf is installed.")
    
    # Build HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Attendance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #1e3a8a; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #1e3a8a; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .date-range {{ text-align: center; color: #666; }}
            .summary {{ margin-top: 20px; padding: 10px; background: #e0f2fe; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Attendance Report</h1>
        <p class="date-range">Period: {start_date} to {end_date}</p>
        
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Employee</th>
                    <th>Clock In</th>
                    <th>Clock Out</th>
                    <th>Day Type</th>
                    <th>Status</th>
                    <th>Total Hours</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for att in attendance_data:
        emp_name = employees_dict.get(att.EmpID, 'Unknown')
        clock_in = att.ClockIn.strftime('%H:%M') if att.ClockIn else '-'
        clock_out = att.ClockOut.strftime('%H:%M') if att.ClockOut else '-'
        
        # Calculate total hours
        total_hours = '-'
        if att.ClockIn and att.ClockOut:
            clock_in_mins = att.ClockIn.hour * 60 + att.ClockIn.minute
            clock_out_mins = att.ClockOut.hour * 60 + att.ClockOut.minute
            hours_worked = (clock_out_mins - clock_in_mins) / 60.0
            if att.WorkDate.weekday() == 5:  # Saturday
                max_hours = 5
            else:
                max_hours = 8
            total_hours = min(hours_worked, max_hours)
        
        html_content += f"""
                <tr>
                    <td>{att.WorkDate.strftime('%Y-%m-%d')}</td>
                    <td>{emp_name}</td>
                    <td>{clock_in}</td>
                    <td>{clock_out}</td>
                    <td>{att.DayType}</td>
                    <td>{att.Status}</td>
                    <td>{total_hours}</td>
                </tr>
        """
    
    total_records = len(attendance_data)
    html_content += f"""
            </tbody>
        </table>
        <div class="summary">
            <strong>Total Records:</strong> {total_records}
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    return pdf


def generate_leave_pdf(leave_requests, employees_dict, start_date, end_date):
    """
    Generate PDF report for leave requests
    
    Args:
        leave_requests: List of LeaveRequest objects
        employees_dict: Dict mapping EmpID to employee name
        start_date: Start date string (optional)
        end_date: End date string (optional)
    
    Returns:
        PDF bytes
    """
    if config is None:
        raise Exception("PDFKit configuration failed. Make sure wkhtmltopdf is installed.")
    
    # Build date range display
    if start_date and end_date:
        date_range_text = f"Period: {start_date} to {end_date}"
    elif start_date:
        date_range_text = f"From: {start_date}"
    elif end_date:
        date_range_text = f"Until: {end_date}"
    else:
        date_range_text = "All Records"
    
    # Build HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Leave Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #1e3a8a; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #1e3a8a; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .date-range {{ text-align: center; color: #666; }}
            .summary {{ margin-top: 20px; padding: 10px; background: #e0f2fe; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Leave Report</h1>
        <p class="date-range">{date_range_text}</p>
        
        <table>
            <thead>
                <tr>
                    <th>Employee</th>
                    <th>Department</th>
                    <th>Leave Type</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Total Days</th>
                    <th>Reason</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for lr in leave_requests:
        emp_name = employees_dict.get(lr.EmpID, 'Unknown')
        department = lr.Department or '-'
        total_days = float(lr.TotalDays) if lr.TotalDays else 0
        html_content += f"""
                <tr>
                    <td>{emp_name}</td>
                    <td>{department}</td>
                    <td>{lr.LeaveType}</td>
                    <td>{lr.StartDate.strftime('%Y-%m-%d')}</td>
                    <td>{lr.EndDate.strftime('%Y-%m-%d')}</td>
                    <td>{total_days}</td>
                    <td>{lr.Reason or '-'}</td>
                    <td>{lr.Status}</td>
                </tr>
        """
    
    total_records = len(leave_requests)
    html_content += f"""
            </tbody>
        </table>
        <div class="summary">
            <strong>Total Leave Requests:</strong> {total_records}
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    return pdf
