# Update index.html with time-based greeting and add Total Hours column

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the header greeting
old_header = """<div>
                    <h1 class="text-xl md:text-2xl font-bold">Welcome to Aero Instrument</h1>
                    <p class="text-blue-200 text-sm">Attendance Management System</p>
                </div>"""

new_header = """<div>
                    <h1 id="greeting" class="text-xl md:text-2xl font-bold">Loading...</h1>
                    <p class="text-blue-200 text-sm">Attendance Management System</p>
                </div>"""

content = content.replace(old_header, new_header)

# 2. Add Total Hours column to table header
old_thead = """<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock In</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock Out</th>
                        </tr>
                    </thead>"""

new_thead = """<th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock In</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Clock Out</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Hours</th>
                        </tr>
                    </thead>"""

content = content.replace(old_thead, new_thead)

# 3. Update the JavaScript to add greeting and calculate total hours
old_js_end = """// Set today's date and day type
        function setHeaderDate() {
            const now = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', options);
            
            const dayOfWeek = now.getDay();
            const dayTypeEl = document.getElementById('dayType');
            
            if (dayOfWeek === 6) {
                dayTypeEl.textContent = 'Saturday (5hrs)';
                dayTypeEl.className = 'text-sm bg-yellow-500/30 px-3 py-1 rounded-full';
            } else if (dayOfWeek === 0) {
                dayTypeEl.textContent = 'Sunday (No Work)';
                dayTypeEl.className = 'text-sm bg-red-500/30 px-3 py-1 rounded-full';
            } else {
                dayTypeEl.textContent = 'Standard Day (8hrs)';
                dayTypeEl.className = 'text-sm bg-green-500/30 px-3 py-1 rounded-full';
            }
        }"""

new_js_end = """// Set time-based greeting
        function setGreeting() {
            const now = new Date();
            const hour = now.getHours();
            let greeting = '';
            
            if (hour >= 5 && hour < 12) {
                greeting = 'Good morning, Welcome to AISL attendance web. Please login to continue.';
            } else if (hour >= 12 && hour < 18) {
                greeting = 'Good afternoon, Welcome to AISL attendance web. Please login to continue.';
            } else {
                greeting = 'Good evening, Welcome to AISL attendance web. Please login to continue.';
            }
            
            document.getElementById('greeting').textContent = greeting;
        }

        // Set today's date and day type
        function setHeaderDate() {
            const now = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', options);
            
            const dayOfWeek = now.getDay();
            const dayTypeEl = document.getElementById('dayType');
            
            if (dayOfWeek === 6) {
                dayTypeEl.textContent = 'Saturday (5hrs)';
                dayTypeEl.className = 'text-sm bg-yellow-500/30 px-3 py-1 rounded-full';
            } else if (dayOfWeek === 0) {
                dayTypeEl.textContent = 'Sunday (No Work)';
                dayTypeEl.className = 'text-sm bg-red-500/30 px-3 py-1 rounded-full';
            } else {
                dayTypeEl.textContent = 'Standard Day (8hrs)';
                dayTypeEl.className = 'text-sm bg-green-500/30 px-3 py-1 rounded-full';
            }
        }"""

content = content.replace(old_js_end, new_js_end)

# 4. Update the table row rendering to include Total Hours
old_table_render = """const rows = data.employees.map(emp => {
                        let statusBadge = '';
                        let clockInDisplay = '-';
                        let clockOutDisplay = '-';
                        
                        // Determine status and time displays
                        if (emp.status === 'Present') {
                            // Has clock_in but no clock_out
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Present</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = '-';
                        } else if (emp.status === 'Clocked Out') {
                            // Has both clock_in and clock_out
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Clocked Out</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = emp.clock_out || '-';
                        } else if (emp.status === 'On Leave') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">On Leave</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = '-';
                        } else {
                            // Not Clocked In
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Not Clocked In</span>';
                            clockInDisplay = '-';
                            clockOutDisplay = '-';
                        }
                        
                        return `
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">${emp.employee_name}</td>
                                <td class="px-3 py-2">${statusBadge}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${clockInDisplay}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${clockOutDisplay}</td>
                            </tr>
                        `;
                    }).join('');"""

new_table_render = """const rows = data.employees.map(emp => {
                        let statusBadge = '';
                        let clockInDisplay = '-';
                        let clockOutDisplay = '-';
                        let totalHours = '-';
                        
                        // Calculate total hours if both times exist
                        if (emp.clock_in && emp.clock_out) {
                            const [inH, inM] = emp.clock_in.split(':').map(Number);
                            const [outH, outM] = emp.clock_out.split(':').map(Number);
                            const totalMins = (outH * 60 + outM) - (inH * 60 + inM);
                            totalHours = (totalMins / 60).toFixed(1);
                        }
                        
                        // Determine status and time displays
                        if (emp.status === 'Present') {
                            // Has clock_in but no clock_out
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Present</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = '-';
                            totalHours = '-';
                        } else if (emp.status === 'Clocked Out') {
                            // Has both clock_in and clock_out
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Clocked Out</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = emp.clock_out || '-';
                        } else if (emp.status === 'On Leave') {
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">On Leave</span>';
                            clockInDisplay = emp.clock_in || '-';
                            clockOutDisplay = '-';
                        } else {
                            // Not Clocked In
                            statusBadge = '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Not Clocked In</span>';
                            clockInDisplay = '-';
                            clockOutDisplay = '-';
                        }
                        
                        return `
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">${emp.employee_name}</td>
                                <td class="px-3 py-2">${statusBadge}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${clockInDisplay}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${clockOutDisplay}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${totalHours}</td>
                            </tr>
                        `;
                    }).join('');"""

content = content.replace(old_table_render, new_table_render)

# 5. Update colspan in loading and error states
content = content.replace("colspan=\"4\"", 'colspan="5"')

# 6. Update initialization to call setGreeting
content = content.replace("setHeaderDate();", "setHeaderDate();\n        setGreeting();")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added time-based greeting and Total Hours column to index.html")
