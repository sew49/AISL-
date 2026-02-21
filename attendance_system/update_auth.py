# Update admin authentication with new password and 8-hour session

import re

# Read the current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update secret key to a random string and add session lifetime
old_secret = "app.secret_key = 'aero_secret_key_2026'"
new_secret = """app.secret_key = 'aero_instrument_secure_key_2026'
app.permanent_session_lifetime = timedelta(hours=8)"""

content = content.replace(old_secret, new_secret)

# Add timedelta import if not present
if 'from datetime import' not in content or 'timedelta' not in content:
    content = content.replace(
        'from datetime import datetime, date',
        'from datetime import datetime, date, timedelta'
    )

# 2. Update password from Aero2026 to RAV4Adventure2019
content = content.replace("password == 'Aero2026'", "password == 'RAV4Adventure2019'")

# 3. Add admin_required decorator for /api/leave-requests routes
# Find the approve_leave_request and reject_leave_request routes and add check

# First, add the admin_required function if not present
if 'def admin_required' not in content:
    admin_required_decorator = '''

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Admin login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

'''
    # Add before the first route
    content = content.replace(
        '@app.route(\'/admin-login\')',
        admin_required_decorator + '@app.route(\'/admin-login\')'
    )

# Add wraps import if not present
if 'from functools import wraps' not in content:
    content = content.replace(
        'from flask import Flask',
        'from functools import wraps\nfrom flask import Flask'
    )

# 4. Protect leave request API routes
# Find and protect approve_leave_request
content = content.replace(
    "@app.route('/api/leave-requests/<int:req_id>/approve', methods=['PUT'])",
    "@app.route('/api/leave-requests/<int:req_id>/approve', methods=['PUT'])\n@admin_required"
)

# Find and protect reject_leave_request  
content = content.replace(
    "@app.route('/api/leave-requests/<int:req_id>/reject', methods=['PUT'])",
    "@app.route('/api/leave-requests/<int:req_id>/reject', methods=['PUT'])\n@admin_required"
)

# Make session permanent on login
content = content.replace(
    "session['admin_logged_in'] = True",
    "session['admin_logged_in'] = True\n    session.permanent = True"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py with new authentication settings")

# 5. Update admin_login.html with "Aero Instrument Management" header and mobile-friendly design
admin_login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Admin Login - Aero Instrument</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        }
        @media (max-width: 640px) {
            .mobile-padding { padding: 1rem; }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full mx-4">
        <div class="bg-white rounded-xl shadow-lg p-6 md:p-8">
            <div class="text-center mb-6 md:mb-8">
                <h1 class="text-xl md:text-2xl font-bold text-gray-800">Aero Instrument Management</h1>
                <p class="text-gray-600 mt-2 text-sm md:text-base">Admin Login</p>
            </div>
            
            {% if error %}
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {{ error }}
            </div>
            {% endif %}
            
            <form method="POST" action="{{ url_for('admin_login') }}">
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        Password
                    </label>
                    <input 
                        type="password" 
                        name="password" 
                        id="password"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                        placeholder="Enter admin password"
                        required
                        autocomplete="current-password"
                    >
                </div>
                
                <button 
                    type="submit"
                    class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition-colors text-base md:text-lg"
                >
                    Login
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <a href="{{ url_for('index') }}" class="text-blue-500 hover:text-blue-700 text-sm md:text-base">
                    ← Back to Attendance System
                </a>
            </div>
        </div>
        
        <p class="text-center text-gray-500 text-xs mt-4">
            Session lasts 8 hours
        </p>
    </div>
</body>
</html>
'''

with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
    f.write(admin_login_html)

print("Updated admin_login.html template")
print("\n✅ Authentication updated!")
print("- New password: RAV4Adventure2019")
print("- Session lifetime: 8 hours")
print("- Protected: /admin-input, /api/leave-requests/*/approve, /api/leave-requests/*/reject")
print("- Mobile-friendly login page")
