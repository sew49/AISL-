# Add database pooling, session handling, retry logic, and fast responses

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update database configuration with pooling
old_db_config = """app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
    print("Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False"""

new_db_config = """app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
    print("Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}"""

content = content.replace(old_db_config, new_db_config)

# 2. Add retry decorator and teardown
old_teardown = """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()"""

# Check if teardown already exists, if not add it
if "@app.teardown_appcontext" not in content:
    content = content.replace(
        "# =====================================================\n# ROUTES",
        """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Retry decorator for database operations
from functools import wraps
import time

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
                    if 'database is locked' in str(e).lower() or 'locked' in str(e).lower():
                        time.sleep(delay * (attempt + 1))
                        db.session.rollback()
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator

# =====================================================
# ROUTES"""
    )

# 3. Update create_attendance to use retry and return immediately
old_create_attendance = """@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    \"\"\"Create new attendance record with Saturday check\"\"\"
    data = request.get_json()"""

new_create_attendance = """@app.route('/api/attendance', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_attendance():
    \"\"\"Create new attendance record with Saturday check\"\"\"
    data = request.get_json()"""

content = content.replace(old_create_attendance, new_create_attendance)

# 4. Update create_leave_request to use retry
old_leave_request = """@app.route('/api/leave-requests', methods=['POST'])
def create_leave_request():"""

new_leave_request = """@app.route('/api/leave-requests', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_leave_request():"""

content = content.replace(old_leave_request, new_leave_request)

# 5. Update create_employee to use retry
old_create_employee = """@app.route('/api/employees', methods=['POST'])
def create_employee():"""

new_create_employee = """@app.route('/api/employees', methods=['POST'])
@retry_on_db_error(max_retries=3)
def create_employee():"""

content = content.replace(old_create_employee, new_create_employee)

# 6. Update update_attendance to use retry
old_update_attendance = """@app.route('/api/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):"""

new_update_attendance = """@app.route('/api/attendance/<int:attendance_id>', methods=['PUT'])
@retry_on_db_error(max_retries=3)
def update_attendance(attendance_id):"""

content = content.replace(old_update_attendance, new_update_attendance)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added database pooling, session handling, and retry logic")
