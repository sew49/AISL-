with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find @app.route('/api/employees'
for i, line in enumerate(lines):
    if "/api/employees" in line and "methods" in line and "GET" in line:
        print(f'Line {i+1}: {line}', end='')
        # Print next 35 lines
        for j in range(i+1, min(i+40, len(lines))):
            print(f'{j+1}: {lines[j]}', end='')
        break
