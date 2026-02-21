# Add admin authentication to app.py

# 1. Update imports to include session and redirect/url_for
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add secret key after app = Flask(__name__)
old_app = "app = Flask(__name__)"
new_app = """app = Flask(__name__)
app.secret_key = 'aero_secret_key_2026'"""

content = content.replace(old_app, new_app)

# Update imports
old_imports = "from flask import Flask, request, jsonify, render_template"
new_imports = "from flask import Flask, request, jsonify, render_template, redirect, url_for, session"

content = content.replace(old_imports, new_imports)

# 2. Find the admin_input route and add protection
# First, let's add the login and logout routes before admin_input

# Find where to insert the auth routes (before @app.route('/admin-input'))
auth_routes = '''

# =====================================================
# ADMIN AUTHENTICATION
# =====================================================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == 'Aero2026':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_input'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

'''

# Insert auth routes before admin-input route
content = content.replace(
    "@app.route('/admin-input')",
    auth_routes + "@app.route('/admin-input')"
)

# 3. Add protection to admin_input route
old_admin = """@app.route('/admin-input')
def admin_input():
    return render_template('admin_input.html')"""

new_admin = """@app.route('/admin-input')
def admin_input():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_input.html')"""

content = content.replace(old_admin, new_admin)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py with admin authentication")

# 4. Create admin_login.html template
admin_login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Aero Instrument</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full mx-4">
        <div class="bg-white rounded-xl shadow-lg p-8">
            <div class="text-center mb-8">
                <h1 class="text-2xl font-bold text-gray-800">Aero Instrument</h1>
                <p class="text-gray-600 mt-2">Admin Login</p>
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
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Enter admin password"
                        required
                    >
                </div>
                
                <button 
                    type="submit"
                    class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition-colors"
                >
                    Login
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <a href="{{ url_for('index') }}" class="text-blue-500 hover:text-blue-700 text-sm">
                    ← Back to Attendance System
                </a>
            </div>
        </div>
    </div>
</body>
</html>
'''

with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
    f.write(admin_login_html)

print("Created admin_login.html template")
print("\nAdmin authentication has been added!")
print("- Secret key: aero_secret_key_2026")
print("- Password: Aero2026")
print("- Login URL: http://192.168.8.74:5000/admin-login")
