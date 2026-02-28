import requests

response = requests.get('http://127.0.0.1:5000/api/attendance/today')
data = response.json()

print(f"Success: {data.get('success')}")
print(f"Date: {data.get('date')}")
print(f"Total employees: {len(data.get('employees', []))}")

# Show first 3
for emp in data.get('employees', [])[:3]:
    print(f"  {emp['employee_code']}: {emp['employee_name']} - {emp['status']}")
