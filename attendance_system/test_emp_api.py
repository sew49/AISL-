import requests
import json

# Test the API directly with fresh request
resp = requests.get('http://127.0.0.1:5000/api/employees', headers={'Cache-Control': 'no-cache'})
data = resp.json()

print('Total employees returned:', len(data['employees']))

# Show the full list
for emp in data['employees']:
    print(f"  {emp['employee_code']}: {emp['first_name']} {emp['last_name']} - active={emp.get('is_active', 'N/A')}")

# Check if EMP023 is missing
codes = [e['employee_code'] for e in data['employees']]
if 'EMP023' in codes:
    print('\nEMP023 is present')
else:
    print('\nEMP023 is MISSING')
