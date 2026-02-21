# Script to update admin_input.html
import re

with open('templates/admin_input.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add auto_approve to sick leave request
old_sick = "leave_type: 'Sick',"
new_sick = "leave_type: 'Sick Leave',"
content = content.replace(old_sick, new_sick)

# Add auto_approve after reason in sick section
old_sick2 = "reason: notes || 'Sick leave'\n                    })"
new_sick2 = "reason: notes || 'Manual Entry',\n                            auto_approve: true\n                        })"
content = content.replace(old_sick2, new_sick2)

# Fix 2: Add auto_approve to annual leave request - find and replace
old_annual = "leave_type: 'Annual',"
new_annual = "leave_type: 'Annual Leave',"
content = content.replace(old_annual, new_annual)

old_annual2 = "reason: notes || 'Annual leave'\n                    })"
new_annual2 = "reason: notes || 'Manual Entry',\n                            auto_approve: true\n                        })"
content = content.replace(old_annual2, new_annual2)

# Fix 3: Add min date to allow backdating
old_date = '<input type="date" id="workDate" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" required>'
new_date = '<input type="date" id="workDate" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" required min="2025-01-01">'
content = content.replace(old_date, new_date)

with open('templates/admin_input.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated admin_input.html successfully!")
