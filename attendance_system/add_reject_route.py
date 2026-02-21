# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The reject endpoint to add
reject_endpoint = '''

@app.route('/api/leave-requests/<int:request_id>/reject', methods=['POST'])
def reject_leave_request(request_id):
    """Reject a leave request"""
    try:
        leave_request = LeaveRequest.query.get(request_id)
        
        if not leave_request:
            return jsonify({'success': False, 'error': 'Leave request not found'}), 404
        
        if leave_request.Status != 'Pending':
            return jsonify({'success': False, 'error': 'Only pending requests can be rejected'}), 400
        
        # Reject the request
        leave_request.Status = 'Rejected'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Leave request rejected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

'''

# Check if the endpoint already exists
if 'def reject_leave_request' not in content:
    # Find the end of approve_leave_request function and add the reject endpoint after it
    # We'll insert before the if __name__ == '__main__' block
    if "if __name__ == '__main__':" in content:
        content = content.replace("if __name__ == '__main__':", reject_endpoint + "if __name__ == '__main__':")
        print("Added reject_leave_request endpoint")
    else:
        content += reject_endpoint
        print("Added reject_leave_request endpoint at end of file")
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("reject_leave_request endpoint already exists")
