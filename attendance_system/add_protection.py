# Add admin protection check

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the admin_input function and add protection
old = "    return render_template('admin_input.html')"
new = "    if not session.get('admin_logged_in'):\n        return redirect(url_for('admin_login'))\n    return render_template('admin_input.html')"

# Only replace in the admin_input function context
if old in content and "if not session.get('admin_logged_in')" not in content:
    content = content.replace(old, new, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added admin protection")
else:
    print("Already protected or pattern not found")
