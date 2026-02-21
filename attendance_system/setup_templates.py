"""
Python script to automatically create a 'templates' folder and generate index.html
with a professional Tailwind CSS UI for the Attendance System.
"""

import os
import shutil

def setup_templates_folder():
    """Create templates folder and generate index.html"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(script_dir, 'templates')
    
    # Create templates folder if it doesn't exist
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"✅ Created 'templates' folder at: {templates_dir}")
    else:
        print(f"📁 'templates' folder already exists at: {templates_dir}")
    
    # Path for the index.html file
    index_html_path = os.path.join(templates_dir, 'index.html')
    
    # Generate the index.html content
    index_html_content = '''<!DOCTYPE html>
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
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white py-4 px-4 shadow-lg sticky top-0 z-50">
        <div class="max-w-4xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                <div>
                    <h1 class="text-xl md:text-2xl font-bold">Attendance System</h1>
                    <p class="text-blue-200 text-sm">Fiscal Year 2026</p>
                </div>
                <div class="text-right">
                    <p id="currentDate" class="text-lg font-semibold"></p>
                    <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto p-4 pb-20">
        <!-- Alert Messages -->
        <div id="alertMessage" class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 hidden">
            <div class="bg-white rounded-lg shadow-xl p-4 max-w-md border-l-4" id="alertContent"></div>
        </div>

        <!-- Attendance Section -->
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
                        <!-- Options populated by JS -->
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

        <!-- Leave Management Section -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mb-4">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                Leave Request
                <span class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Max 21 days/year</span>
            </h2>
            
            <form id="leaveForm" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Leave Type</label>
                        <select id="leaveType" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                            <option value="Annual">Annual Leave</option>
                            <option value="Sick">Sick Leave</option>
                            <option value="Absent">Absent</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
                        <input type="date" id="leaveDate" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Reason (Optional)</label>
                    <input type="text" id="leaveReason" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Reason for leave...">
                </div>
                
                <!-- Leave Balance Warning -->
                <div id="leaveBalanceWarning" class="hidden bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <p class="text-yellow-800 text-sm">
                        <svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                        <span id="balanceWarningText"></span>
                    </p>
                </div>
                
                <button type="submit" class="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors">
                    Submit Leave Request
                </button>
            </form>
            
            <div id="leaveMessage" class="mt-4 p-3 rounded-lg hidden"></div>
        </section>

        <!-- Status Dashboard -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Today's Status
                </h2>
                <button id="refreshStatus" class="p-2 text-gray-500 hover:text-blue-600 transition-colors" title="Refresh">
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
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time In</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        </tr>
                    </thead>
                    <tbody id="statusTableBody" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="3" class="px-3 py-8 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div id="emptyStatus" class="hidden text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                No employees clocked in today
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
        const leaveForm = document.getElementById('leaveForm');
        const leaveMessage = document.getElementById('leaveMessage');
        const statusTableBody = document.getElementById('statusTableBody');
        const refreshStatusBtn = document.getElementById('refreshStatus');
        const emptyStatus = document.getElementById('emptyStatus');
        const leaveBalanceWarning = document.getElementById('leaveBalanceWarning');
        const balanceWarningText = document.getElementById('balanceWarningText');
        
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

        // Show inline message
        function showMessage(element, message, isSuccess) {
            element.textContent = message;
            element.className = `mt-4 p-3 rounded-lg ${isSuccess ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`;
            element.classList.remove('hidden');
            setTimeout(() => element.classList.add('hidden'), 5000);
        }

        // Fetch employees and populate dropdowns
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
                showAlert('Failed to connect to server', 'error');
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
            
            // Update visible dropdown
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
            
            // Add click handlers to dropdown items
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

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#employeeSearch') && !e.target.closest('#employeeDropdown')) {
                employeeDropdown.classList.add('hidden');
            }
        });

        // Also update selectedEmployeeId when select changes
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

        // Check leave balance when leave type or employee changes
        async function checkLeaveBalance(empId, leaveType) {
            if (!empId || leaveType !== 'Annual') {
                leaveBalanceWarning.classList.add('hidden');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/leave-balances?emp_id=${empId}`);
                const data = await response.json();
                
                if (data.success && data.leave_balances && data.leave_balances.length > 0) {
                    const balance = data.leave_balances[0];
                    const remaining = balance.remaining_annual;
                    
                    if (remaining < 5) {
                        balanceWarningText.textContent = `Warning: Only ${remaining} annual leave days remaining!`;
                        leaveBalanceWarning.classList.remove('hidden');
                    } else if (remaining < 10) {
                        balanceWarningText.textContent = `You have ${remaining} annual leave days remaining.`;
                        leaveBalanceWarning.classList.remove('hidden');
                    } else {
                        leaveBalanceWarning.classList.add('hidden');
                    }
                } else {
                    leaveBalanceWarning.classList.add('hidden');
                }
            } catch (error) {
                console.error('Error checking balance:', error);
            }
        }

        // Listen for leave form changes
        document.getElementById('leaveType').addEventListener('change', (e) => {
            const empId = selectedEmployeeId || employeeSelect.value;
            checkLeaveBalance(empId, e.target.value);
        });

        // Submit Leave Request
        leaveForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const empId = selectedEmployeeId || employeeSelect.value;
            const leaveType = document.getElementById('leaveType').value;
            const leaveDate = document.getElementById('leaveDate').value;
            const reason = document.getElementById('leaveReason').value;

            if (!empId) {
                showAlert('Please select an employee', 'error');
                return;
            }

            if (!leaveDate) {
                showAlert('Please select a date', 'error');
                return;
            }

            // Check annual leave limit
            if (leaveType === 'Annual') {
                try {
                    const response = await fetch(`${API_BASE}/api/leave-balances?emp_id=${empId}`);
                    const data = await response.json();
                    
                    if (data.success && data.leave_balances && data.leave_balances.length > 0) {
                        const balance = data.leave_balances[0];
                        if (balance.remaining_annual <= 0) {
                            showAlert('❌ No annual leave days remaining!', 'error');
                            return;
                        }
                    }
                } catch (error) {
                    console.error('Error checking balance:', error);
                }
            }

            try {
                const response = await fetch(`${API_BASE}/api/leave-requests`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        emp_id: parseInt(empId),
                        leave_type: leaveType,
                        start_date: leaveDate,
                        end_date: leaveDate,
                        reason: reason
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ Leave request submitted successfully!', 'success');
                    leaveForm.reset();
                    leaveBalanceWarning.classList.add('hidden');
                } else {
                    showAlert(`❌ ${data.error || 'Failed to submit leave request'}`, 'error');
                }
            } catch (error) {
                console.error('Error submitting leave request:', error);
                showAlert('❌ Failed to connect to server', 'error');
            }
        });

        // Fetch today's attendance status
        async function fetchTodayStatus() {
            try {
                const today = new Date().toISOString().split('T')[0];
                const response = await fetch(`${API_BASE}/api/attendance?start_date=${today}&end_date=${today}`);
                const data = await response.json();
                
                if (data.success && data.attendance && data.attendance.length > 0) {
                    const empMap = {};
                    if (employees.length > 0) {
                        employees.forEach(emp => {
                            empMap[emp.emp_id] = `${emp.first_name} ${emp.last_name}`;
                        });
                    }

                    const rows = data.attendance.map(att => {
                        const empName = empMap[att.emp_id] || 'Unknown';
                        const status = att.clock_out ? 'Out' : 'In';
                        const statusClass = att.clock_out ? 'bg-gray-100 text-gray-800' : 'bg-green-100 text-green-800';
                        
                        return `
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">${empName}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${att.clock_in || '-'}</td>
                                <td class="px-3 py-2">
                                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${statusClass}">
                                        ${status}
                                    </span>
                                </td>
                            </tr>
                        `;
                    }).join('');

                    statusTableBody.innerHTML = rows;
                    emptyStatus.classList.add('hidden');
                } else {
                    statusTableBody.innerHTML = '';
                    emptyStatus.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error fetching status:', error);
                statusTableBody.innerHTML = '<tr><td colspan="3" class="px-3 py-8 text-center text-red-500 text-sm">Failed to load status</td></tr>';
            }
        }

        // Refresh button
        refreshStatusBtn.addEventListener('click', fetchTodayStatus);

        // Initialize
        setHeaderDate();
        fetchEmployees();
        fetchTodayStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(fetchTodayStatus, 30000);
    </script>
</body>
</html>'''
    
    # Write the index.html file
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(index_html_content)
    
    print(f"✅ Generated 'index.html' at: {index_html_path}")
    print(f"\n📋 Summary:")
    print(f"   - Templates folder: {templates_dir}")
    print(f"   - Index HTML: {index_html_path}")
    print(f"   - API Endpoint: http://192.168.8.74:5000")
    print(f"\n🚀 Run 'python app.py' and visit http://192.168.8.74:5000 to see the website!")

if __name__ == '__main__':
    setup_templates_folder()
