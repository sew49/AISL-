# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and add the new route after the index route
old_code = """@app.route('/')
def index():
    \"\"\"Render the main dashboard\"\"\"
    return render_template('index.html')"""

new_code = """@app.route('/')
def index():
    \"\"\"Render the main dashboard\"\"\"
    return render_template('index.html')


@app.route('/admin-input')
def admin_input():
    \"\"\"Render the admin input form for manual attendance entry\"\"\"
    return render_template('admin_input.html')"""

# Replace
fixed_content = content.replace(old_code, new_code)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('Added /admin-input route!')
