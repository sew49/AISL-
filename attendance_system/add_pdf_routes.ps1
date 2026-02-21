$pdfRoutes = @'

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
'@

Add-Content -Path "app.py" -Value $pdfRoutes
Write-Host "PDF routes added successfully"
