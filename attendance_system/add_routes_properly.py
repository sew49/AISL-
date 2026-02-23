# Script to properly add PDF routes BEFORE app.run()

pdf_routes = '''

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

'''

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the incorrectly placed routes (after app.run)
if "if __name__ == '__main__':" in content:
    # Find the main block
    main_idx = content.find("if __name__ == '__main__':")
    # Find app.run within the main block
    run_idx = content.find("app.run(", main_idx)
    
    if run_idx > 0:
        # Get everything before app.run
        before_run = content[:run_idx]
        # Find the line before app.run - go back to find the closing
        lines_before = before_run.split('\n')
        # Find the last complete route definition before app.run
        # Let's find where the leave route might have been added
        if '# PDF Report Routes' in content:
            # Find where it starts
            pdf_start = content.find('# PDF Report Routes')
            # Find where app.run is
            app_run_start = content.find('app.run(', pdf_start)
            # Find the end of that line
            app_run_end = content.find('\n', app_run_start)
            # Remove the PDF routes that were incorrectly added
            content = content[:pdf_start] + content[app_run_end+1:]
            print("Removed incorrectly placed routes")

# Now add routes before the main block
if "if __name__ == '__main__':" in content:
    content = content.replace("if __name__ == '__main__':", pdf_routes + "\nif __name__ == '__main__':")
    print("Added routes before app.run")
else:
    print("Could not find main block")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
