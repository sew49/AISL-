"""
Script to add Holidays table and update logic to exclude holidays from absent calculations
"""

import sqlite3
import os

def add_holidays_table():
    db_path = 'attendance_system.db'
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Holidays table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holidays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            holiday_name TEXT NOT NULL,
            holiday_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if table was created (not exists before)
    cursor.execute("SELECT COUNT(*) FROM holidays")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add some sample holidays for 2025-2026 fiscal year
        holidays = [
            ('New Year Day', '2026-01-01'),
            ('Good Friday', '2026-04-03'),
            ('Easter Monday', '2026-04-06'),
            ('Labour Day', '2026-05-01'),
            ('Madaraka Day', '2026-06-01'),
            ('Independence Day', '2026-07-12'),
            ('Eid al-Fitr', '2026-03-20'),
            ('Eid al-Adha', '2026-06-06'),
            ('Halloween', '2026-10-31'),
            ('Christmas Day', '2026-12-25'),
            ('Boxing Day', '2026-12-26'),
        ]
        
        cursor.executemany('INSERT INTO holidays (holiday_name, holiday_date) VALUES (?, ?)', holidays)
        print(f"✅ Added {len(holidays)} sample holidays to the database")
    else:
        print(f"📋 Holidays table already has {count} records")
    
    conn.commit()
    conn.close()
    print("✅ Holidays table created successfully!")
    return True

def update_app_for_holidays():
    """Update app.py to add Holiday model and API endpoints"""
    
    # Read current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Holiday model already exists
    if 'class Holiday' in content:
        print("ℹ️ Holiday model already exists in app.py")
        return
    
    # Find where to insert the Holiday model (after LeaveRequest class)
    # Look for the LeaveRequest class and add after it
    
    # Add Holiday model after LeaveRequest
    holiday_model = '''

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
'''
    
    # Find position after LeaveRequest class (before the last API route section)
    if 'class LeaveRequest' in content:
        # Find the end of LeaveRequest class (look for next class or route)
        content = content.replace('class LeaveRequest(db.Model):', 
                                 'class LeaveRequest(db.Model):' + holiday_model)
        print("✅ Added Holiday model to app.py")
    
    # Add API routes for holidays
    holiday_routes = '''

# Holiday Management Routes
@app.route('/api/holidays', methods=['GET'])
def get_holidays():
    """Get all holidays"""
    try:
        holidays = Holiday.query.order_by(Holiday.holiday_date).all()
        return jsonify({
            'success': True,
            'holidays': [h.to_dict() for h in holidays]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays', methods=['POST'])
def add_holiday():
    """Add a new holiday"""
    try:
        data = request.get_json()
        holiday = Holiday(
            holiday_name=data['holiday_name'],
            holiday_date=datetime.strptime(data['holiday_date'], '%Y-%m-%d').date()
        )
        db.session.add(holiday)
        db.session.commit()
        return jsonify({
            'success': True,
            'holiday': holiday.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    """Delete a holiday"""
    try:
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({'success': False, 'error': 'Holiday not found'}), 404
        
        db.session.delete(holiday)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Holiday deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays/check/<date>')
def check_holiday(date):
    """Check if a specific date is a holiday"""
    try:
        holiday = Holiday.query.filter_by(holiday_date=date).first()
        if holiday:
            return jsonify({
                'success': True,
                'is_holiday': True,
                'holiday_name': holiday.holiday_name
            })
        return jsonify({
            'success': True,
            'is_holiday': False,
            'holiday_name': None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    # Add routes before the main block
    if "if __name__ == '__main__':" in content:
        content = content.replace("if __name__ == '__main__':", 
                                  holiday_routes + "\nif __name__ == '__main__':")
        print("✅ Added Holiday API routes to app.py")
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated app.py with holiday functionality")

def is_holiday(date_str, db_path='attendance_system.db'):
    """Check if a date is a holiday"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT holiday_name FROM holidays WHERE holiday_date = ?', (date_str,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

if __name__ == '__main__':
    print("Setting up Holidays table...")
    add_holidays_table()
    update_app_for_holidays()
    print("\n✅ Holidays setup complete!")
    print("The system will now exclude holidays when calculating 'Absent' days.")
