import requests
import json

response = requests.get('http://127.0.0.1:5000/api/employees')
data = response.json()

emp6 = [e for e in data['employees'] if e['employee_code'] == 'EMP006'][0]
print(f"EMP006 {emp6['first_name']} {emp6['last_name']}: leave_balance={emp6['leave_balance']}")
