# Script to update app.py with new features
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the validation section
old_validation = """    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    if not leave_type:
        return jsonify({'success': False, 'error': 'Leave type is required'}), 400
    if not start_date_str:
        return jsonify({'success': False, 'error': 'Start date is required'}), 400
    if not end_date_str:
        return jsonify({'success': False, 'error': 'End date is required'}), 400"""

new_validation = """    # Auto-approve for manual admin entries
    auto_approve = data.get('auto_approve', False)

    if not emp_id:
        return jsonify({'success': False, 'error': 'Employee ID is required'}), 400
    if not leave_type:
        return jsonify({'success': False, 'error': 'Leave type is required'}), 400
    
    # Normalize leave type - accept Sick Leave, Annual Leave
    if leave_type == 'Sick Leave':
        leave_type = 'Sick'
    elif leave_type == 'Annual Leave':
        leave_type = 'Annual'
    
    # Auto-set reason to Manual Entry if missing for admin entries
    if auto_approve and not reason:
        reason = 'Manual Entry'
    
    if not start_date_str:
        return jsonify({'success': False, 'error': 'Start date is required'}), 400
    if not end_date_str:
        return jsonify({'success': False, 'error': 'End date is required'}), 400"""

content = content.replace(old_validation, new_validation)

# Replace the leave request creation
old_create = """        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Status='Pending'
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Leave request submitted',
            'leave_request': new_request.to_dict()
        }), 201"""

new_create = """        # Set status - auto-approve for admin manual entries
        status = 'Approved' if auto_approve else 'Pending'
        
        new_request = LeaveRequest(
            EmpID=emp_id,
            LeaveType=leave_type,
            StartDate=start_date,
            EndDate=end_date,
            TotalDays=total_days,
            Reason=reason,
            Status=status,
            ApprovedDate=datetime.utcnow() if auto_approve else None
        )

        db.session.add(new_request)
        db.session.commit()
        
        # If auto-approved, deduct from leave balance immediately
        if auto_approve and leave_type in ['Annual', 'Sick']:
            fiscal_year = get_fiscal_year_python(start_date)
            balance = LeaveBalance.query.filter_by(EmpID=emp_id, FiscalYear=fiscal_year).first()
            if balance:
                if leave_type == 'Annual':
                    balance.UsedAnnualDays = float(balance.UsedAnnualDays) + float(total_days)
                elif leave_type == 'Sick':
                    balance.UsedSickDays = float(balance.UsedSickDays) + float(total_days)
                db.session.commit()

        message = 'Leave request approved' if auto_approve else 'Leave request submitted'
        
        return jsonify({
            'success': True,
            'message': message,
            'leave_request': new_request.to_dict()
        }), 201"""

content = content.replace(old_create, new_create)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done: Updated app.py with auto-approve and Sick Leave support')
