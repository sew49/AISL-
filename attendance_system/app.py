"""
Hybrid Flask App with Supabase Integration
- Admin Mode (Render): /admin with password protection
- Staff Mode (Local): /staff without password
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sfwhsgrphfrsckzqquxp.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'MRaSgUIhVBNJKyBMAnYnJw_HvGuywcn')

# Admin password from environment
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'RAV4Adventure2019')

# Environment detection
IS_RENDER = os.environ.get('RENDER') is not None

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'aero_instrument_secure_key_2026')

# =====================================================
# SUPABASE HELPER FUNCTIONS
# =====================================================

def fetch_logs_from_supabase():
    """Fetch data from Supabase 'logs' table"""
    try:
        import requests
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/logs',
            headers=headers,
            params={'order': 'created_at.desc', 'limit': 100}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching logs: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception fetching logs: {e}")
        return []

def create_log_in_supabase(log_data):
    """Create a log entry in Supabase"""
    try:
        import requests
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/logs',
            headers=headers,
            json=log_data
        )
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Exception creating log: {e}")
        return False

# =====================================================
# ROUTES
# =====================================================

@app.route('/')
def index():
    """Home page - redirect based on environment"""
    if IS_RENDER:
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('staff_portal'))

# ====================
# ADMIN ROUTES
# ====================

@app.route('/admin')
def admin_login():
    """Admin login page - only active on Render"""
    if not IS_RENDER:
        return redirect(url_for('staff_portal'))
    return render_template('admin/dashboard.html', logged_in=False, logs=[])

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - requires password"""
    if not IS_RENDER:
        return redirect(url_for('staff_portal'))
    
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Fetch logs from Supabase
    logs = fetch_logs_from_supabase()
    
    return render_template('admin/dashboard.html', logged_in=True, logs=logs)

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Process admin login"""
    if not IS_RENDER:
        return redirect(url_for('staff_portal'))
    
    password = request.form.get('password', '')
    
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('admin/dashboard.html', logged_in=False, error='Invalid password', logs=[])

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ====================
# STAFF ROUTES
# ====================

@app.route('/staff')
def staff_portal():
    """Staff portal - only active locally"""
    if IS_RENDER:
        return redirect(url_for('admin_login'))
    return render_template('staff/portal.html')

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"HYBRID FLASK APP STARTUP")
    print(f"{'='*60}")
    print(f"Environment: {'Render (Production)' if IS_RENDER else 'Local (Development)'}")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Admin Password: {'***' if ADMIN_PASSWORD else 'Not set'}")
    print(f"{'='*60}\n")
    
    if IS_RENDER:
        print(">>> Running in ADMIN mode (Render)")
        print(">>> Access: /admin")
    else:
        print(">>> Running in STAFF mode (Local)")
        print(">>> Access: /staff")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
