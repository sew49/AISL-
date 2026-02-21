# Script to update fiscal year summary to show Days Present
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change total_hours_worked to days_present
old = "'total_hours_worked': round(total_hours, 2),"
new = "'days_present': len(set(a.WorkDate for a in emp_attendance if a.ClockIn)),"

content = content.replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated fiscal year summary to show Days Present")
