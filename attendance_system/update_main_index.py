# Update main index.html to show today's status table
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New index.html content with Today's Status table
new_index = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance Management System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        }
        .card-shadow {
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white py-4 px-4 shadow-lg sticky top-0 z-50">
        <div class="max-w-5xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                <div>
                    <h1 class="text-xl md:text-2xl font-bold">Welcome to Aero Instrument</h1>
                    <p class="text-blue-200 text-sm">Attendance Management System</p>
                </div>
                <div class="text-right">
                    <p id="currentDate" class="text-lg font-semibold"></p>
                    <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-5xl mx-auto p-4 pb-20">
        <!-- Alert Messages -->
        <div id="alertMessage" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 hidden">
            <div class="bg-white rounded-lg shadow-xl p-4 max-w-md border-l-4" id="alertContent"></div>
        </div>

        <!-- Clock In/Out Section -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mb-4">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Clock In / Out
            </h2>
            
            <div class="space-y-4">
                <!-- Searchable Dropdown -->
                <div class="relative">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Select Employee</label>
                    <div class="relative">
                        <input 
                            type="text" 
                            id="employeeSearch" 
                            placeholder="Search employee..." 
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                            autocomplete="off"
                        >
                        <select id="employeeSelect" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer">
                            <option value="">-- Select Employee --</option>
                        </select>
                    </div>
                    <!-- Dropdown Options -->
                    <div id="employeeDropdown" class="hidden absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    </div>
                </div>
                
                <div class="flex flex-col sm:flex-row gap-3">
                    <button id="clockInBtn" class="flex-1 px-6 py-4 bg-green-500 hover:bg-green-600 text-white font-bold rounded-lg transition-colors flex items-center justify-center text-lg">
                        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                        </svg>
                        Clock In
                    </button>
                    
                    <button id="clockOutBtn" class="flex-1 px-6 py-4 bg-red-500 hover:bg-red-600 text-white font-bold rounded-lg transition-colors flex items-center justify-center text-lg">
                        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                        </svg>
                        Clock Out
                    </button>
                </div>
            </div>
            
            <div id="clockMessage" class="mt-4 p-3 rounded-lg hidden"></div>
        </section>

        <!-- Today's Status Table -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Today's Status
                </h2>
                <button id="refreshBtn" class="p-2 text-gray-500 hover:text-blue-600 transition-colors" title="Refresh">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                </button>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                        </tr>
                    </thead>
                    <tbody id="todayTableBody" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="4" class="px-3 py-8 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <p class="text-xs text-gray-400 mt-3 text-center">
                Auto-refreshes every 30 seconds
            </p>
        </section>
    </main>

    <script>
        const API_BASE = 'http://192.168.8.74:5000';
        
        // DOM Elements
        const employeeSearch = document.getElementById('employeeSearch');
        const employeeSelect = document.getElementById('employeeSelect');
        const employeeDropdown = document.getElementById('employeeDropdown');
        const clockInBtn = document.getElementById('clockInBtn');
        const clockOutBtn = document.getElementById('clockOutBtn');
        const clockMessage = document.getElementById('clockMessage');
        const todayTableBody = document.getElementById('todayTableBody');
        const refreshBtn = document.getElementById('refreshBtn');
        
        let employees = [];
        let selectedEmployeeId = null;

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
        }

        // Show alert message
        function showAlert(message, type = 'success') {
            const alertEl = document.getElementById('alertMessage');
            const alertContent = document.getElementById('alertContent');
            
            if (type === 'success') {
                alertContent.className = 'bg-green-100 border-green-500 text-green-800';
            } else if (type === 'warning') {
                alertContent.className = 'bg-yellow-100 border-yellow-500 text-yellow-800';
            } else {
                alertContent.className = 'bg-red-100 border-red-500 text-red-800';
            }
            
            alertContent.innerHTML = message;
            alertEl.classList.remove('hidden');
            
            setTimeout(() => {
                alertEl.classList.add('hidden');
            }, 5000);
        }

        // Fetch employees
        async function fetchEmployees() {
            try {
                const response = await fetch(`${API_BASE}/api/employees`);
                const data = await response.json();
                
                if (data.success && data.employees) {
                    employees = data.employees;
                    renderEmployeeDropdown('');
                }
            } catch (error) {
                console.error('Error fetching employees:', error);
            }
        }

        // Render employee dropdown
        function renderEmployeeDropdown(filter = '') {
            const filtered = employees.filter(emp => 
                `${emp.first_name} ${emp.last_name}`.toLowerCase().includes(filter.toLowerCase()) ||
                emp.employee_code.toLowerCase().includes(filter.toLowerCase())
            );
            
            let optionsHTML = `<option value="">-- Select Employee --</option>`;
            filtered.forEach(emp => {
                const fullName = `${emp.first_name} ${emp.last_name}`;
                optionsHTML += `<option value="${emp.emp_id}">${fullName} (${emp.employee_code})</option>`;
            });
            
            employeeSelect.innerHTML = optionsHTML;
            
            let dropdownHTML = filtered.map(emp => 
                `<div class="px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-0" data-id="${emp.emp_id}" data-name="${emp.first_name} ${emp.last_name}">
                    <div class="font-medium">${emp.first_name} ${emp.last_name}</div>
                    <div class="text-xs text-gray-500">${emp.employee_code}</div>
                </div>`
            ).join('');
            
            if (filter === '') {
                dropdownHTML = `<div class="px-4 py-2 text-gray-500 text-sm">Type to search...</div>` + dropdownHTML;
            }
            
            employeeDropdown.innerHTML = dropdownHTML || `<div class="px-4 py-2 text-gray-500">No results found</div>`;
            
            document.querySelectorAll('#employeeDropdown > div[data-id]').forEach(item => {
                item.addEventListener('click', () => {
                    const empId = item.dataset.id;
                    const empName = item.dataset.name;
                    selectedEmployeeId = empId;
                    employeeSearch.value = empName;
                    employeeDropdown.classList.add('hidden');
                });
            });
        }

        // Search input handler
        employeeSearch.addEventListener('input', (e) => {
            renderEmployeeDropdown(e.target.value);
            employeeDropdown.classList.remove('hidden');
        });

        employeeSearch.addEventListener('focus', () => {
            renderEmployeeDropdown(employeeSearch.value);
            employeeDropdown.classList.remove('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('#employeeSearch') && !e.target.closest('#employeeDropdown')) {
                employeeDropdown.classList.add('hidden');
            }
        });

        employeeSelect.addEventListener('change', (e) => {
            selectedEmployeeId = e.target.value;
            if (selectedEmployeeId) {
                const emp = employees.find(em => em.emp_id == selectedEmployeeId);
                if (emp) {
                    employeeSearch.value = `${emp.first_name} ${emp.last_name}`;
                }
            }
        });

        // Clock In
        clockInBtn.addEventListener('click', async () => {
            const empId = selectedEmployeeId || employeeSelect.value;
            if (!empId) {
                showAlert('Please select an employee', 'error');
                return;
            }

            const today = new Date().toISOString().split('T')[0];
            const now = new Date().toTimeString().slice(0, 5);

            try {
                const response = await fetch(`${API_BASE}/api/attendance`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        emp_id: parseInt(empId),
                        work_date: today,
                        clock_in: now
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    showAlert(`✅ Clocked in successfully at ${now}`, 'success');
                    fetchTodayStatus();
                } else {
                    showAlert(`❌ ${data.error || 'Failed to clock in'}`, 'error');
                }
            } catch (error) {
                console.error('Error clocking in:', error);
                showAlert('❌ Failed to connect to server', 'error');
            }
        });

        // Clock Out
        clockOutBtn.addEventListener('click', async () => {
            const empId = selectedEmployeeId || employeeSelect.value;
            if (!empId) {
                showAlert('Please select an employee', 'error');
                return;
            }

            try {
                const today = new Date().toISOString().split('T')[0];
                const response = await fetch(`${API_BASE}/api/attendance?emp_id=${empId}&start_date=${today}&end_date=${today}`);
                const data = await response.json();
                
                if (data.success && data.attendance && data.attendance.length > 0) {
                    const attendance = data.attendance[0];
                    
                    if (attendance.clock_out) {
                        showAlert('⚠️ Already clocked out today', 'warning');
                        return;
                    }

                    const now = new Date().toTimeString().slice(0, 5);
                    
                    const updateResponse = await fetch(`${API_BASE}/api/attendance/${attendance.attendance_id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ clock_out: now })
                    });

                    const updateData = await updateResponse.json();
                    
                    if (updateData.success) {
                        showAlert(`✅ Clocked out successfully at ${now}`, 'success');
                        fetchTodayStatus();
                    } else {
                        showAlert(`❌ ${updateData.error || 'Failed to clock out'}`, 'error');
                    }
                } else {
                    showAlert('❌ No clock-in record found. Please clock in first.', 'error');
                }
            } catch (error) {
                console.error('Error clocking out:', error);
                showAlert('❌ Failed to connect to server', 'error');
            }
        });

        // Fetch today's status using new API
        async function fetchTodayStatus() {
            try {
                const response = await fetch(`${API_BASE}/api/attendance/today`);
                const data = await response.json();
                
                if (data.success && data.employees) {
                    const rows = data.employees.map(emp => {
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
                        
                        return `
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">${emp.employee_name}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${emp.employee_code}</td>
                                <td class="px-3 py-2">${statusBadge}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${timeDisplay}</td>
                            </tr>
                        `;
                    }).join('');

                    todayTableBody.innerHTML = rows;
                } else {
                    todayTableBody.innerHTML = '<tr><td colspan="4" class="px-3 py-8 text-center text-gray-500">No data available</td></tr>';
                }
            } catch (error) {
                console.error('Error fetching status:', error);
                todayTableBody.innerHTML = '<tr><td colspan="4" class="px-3 py-8 text-center text-red-500 text-sm">Failed to load status</td></tr>';
            }
        }

        // Refresh button
        refreshBtn.addEventListener('click', fetchTodayStatus);

        // Initialize
        setHeaderDate();
        fetchEmployees();
        fetchTodayStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(fetchTodayStatus, 30000);
    </script>
</body>
</html>'''

# Write new content
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_index)

print("Updated main index.html with Today's Status table")
