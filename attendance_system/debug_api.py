import requests

response = requests.get('http://127.0.0.1:5000/api/employees')
data = response.json()
print(f"Success: {data.get('success')}")
print(f"Total: {len(data.get('employees', []))}")
print("Employee codes:", [e['employee_code'] for e in data.get('employees', [])])
print("First few employees:", [(e['employee_code'], e['first_name'], e['last_name']) for e in data.get('employees', [])[:5]])
