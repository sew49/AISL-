# Read the file with UTF-8 encoding
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the yearly_totals initialization
old_code = '''            # Initialize yearly totals for this employee as floats
            yearly_totals = {year: 0.0 for year in target_years}'''

new_code = '''            # Initialize separate yearly totals for Annual and Sick leave
            annual_totals = {year: 0.0 for year in target_years}
            sick_totals = {year: 0.0 for year in target_years}'''

content = content.replace(old_code, new_code)

# Replace the yearly_totals accumulation
old_code2 = '''                    if year in target_years:
                        yearly_totals[year] += float(leave.TotalDays) if leave.TotalDays else 0.0'''

new_code2 = '''                    if year in target_years:
                        days = float(leave.TotalDays) if leave.TotalDays else 0.0
                        # Separate by leave type
                        if leave.LeaveType == 'Annual':
                            annual_totals[year] += days
                        elif leave.LeaveType == 'Sick':
                            sick_totals[year] += days'''

content = content.replace(old_code2, new_code2)

# Replace the row building
old_code3 = '''            # Build the row with Employee ID, Full Name (using name_map), and yearly totals
            row = {
                'emp_id': emp_id,
                'full_name': name_map.get(emp_id, f"{emp.FirstName} {emp.LastName}"),
                'years': yearly_totals
            }'''

new_code3 = '''            # Build the row with Employee ID, Full Name (using name_map), and separate yearly totals
            row = {
                'emp_id': emp_id,
                'full_name': name_map.get(emp_id, f"{emp.FirstName} {emp.LastName}"),
                'annual': annual_totals,
                'sick': sick_totals
            }'''

content = content.replace(old_code3, new_code3)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')
