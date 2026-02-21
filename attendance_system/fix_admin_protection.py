# Fix admin_input route protection

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the admin_input function
old_code = """@app.route('/admin-input')
def admin_input():
    return render_template('admin_input.html')"""

new_code = """@app.route('/admin-input')
def admin_input():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_input.html')"""

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated admin_input route with protection")
