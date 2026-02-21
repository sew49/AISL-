# Update main index.html to show Clock In and Clock Out columns
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update table header
old_header = '''<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>'''

new_header = '''<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock In</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock Out</th>'''

content = content.replace(old_header, new_header)

# Update the JavaScript to show clock_in and clock_out
old_js = '''const rows = data.employees.map(emp => {
                        let statusBadge = '';
                        let timeDisplay = '-';
                        
                        if (emp.status === 'Present') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Present</span>';
                            timeDisplay = emp.clock_in || '-';
                        } else if (emp.status === 'On Leave') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">On Leave</span>';
                            timeDisplay = emp.clock_in || '-';
                        } else {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Not Clocked In</span>';
                        }
                        
                        return \`
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">\${emp.employee_name}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">\${emp.employee_code}</td>
                                <td class="px-3 py-2">\${statusBadge}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">\${timeDisplay}</td>
                            </tr>
                        \`;
                    }).join('');'''

new_js = '''const rows = data.employees.map(emp => {
                        let statusBadge = '';
                        let clockInDisplay = '-';
                        let clockOutDisplay = '-';
                        
                        if (emp.status === 'Present') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Present</span>';
                            clockInDisplay = emp.clock_in || '-';
                        } else if (emp.status === 'Clocked Out') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Clocked Out</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = emp.clock_out || '-';
                        } else if (emp.status === 'On Leave') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">On Leave</span>';
                        } else {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Not Clocked In</span>';
                        }
                        
                        return \`
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">\${emp.employee_name}</td>
                                <td class="px-3 py-2">\${statusBadge}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">\${clockInDisplay}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">\${clockOutDisplay}</td>
                            </tr>
                        \`;
                    }).join('');'''

content = content.replace(old_js, new_js)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html with Clock In and Clock Out columns")
