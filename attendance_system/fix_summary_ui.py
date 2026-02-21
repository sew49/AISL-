# Update admin_input.html to show Days Present
with open('templates/admin_input.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the table header
old_header = '<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Hours</th>'
new_header = '<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Days Present</th>'
content = content.replace(old_header, new_header)

# Update the data row to show days_present instead of total_hours_worked
old_data = '${emp.total_hours_worked}'
new_data = '${emp.days_present}'
content = content.replace(old_data, new_data)

with open('templates/admin_input.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated admin_input.html to show Days Present")
