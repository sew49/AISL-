"""
Script to add Monthly Attendance Summary to admin-input page
"""

import os

# First, add the API endpoint to app.py
# We need to find a good place to add it

app_py_path = 'app.py'
with open(app_py_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Check if the endpoint already exists
if 'monthly-attendance-summary' not in app_content:
    # Add the monthly attendance summary endpoint before the fiscal year summary
    monthly_endpoint = '''

@app.route('/api/reports/monthly-attendance-summary')
def get_monthly_attendance_summary():
    """Get monthly attendance summary for all employees"""
    try:
        # Get current month or from query params
        year = request.args.get('year', type=int, default=datetime.now().year)
        month = request.args.get('month', type=int, default=datetime.now().month)
        
        # Calculate first and last day of month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1)
        else:
            last_day = date(year, month + 1, 1)
        
        # Get all active employees
        employees = Employee.query.filter_by(IsActive=True).all()
        
        # Get all attendance records for the month
        attendance_records = Attendance.query.filter(
            Attendance.WorkDate >= first_day,
            Attendance.WorkDate < last_day
        ).all()
        
        # Get holidays for the month
        holidays = Holiday.query.filter(
            Holiday.holiday_date >= first_day,
            Holiday.holiday_date < last_day
        ).all()
        holiday_dates = {h.holiday_date for h in holidays}
        
        # Calculate target workdays (excluding Sundays and holidays)
        target_days = 0
        current = first_day
        while current < last_day:
            if current.weekday() != 6 and current not in holiday_dates:  # Not Sunday and not holiday
                target_days += 1
            current = date.fromordinal(current.toordinal() + 1)
        
        # Build summary for each employee
        summary = []
        
        for emp in employees:
            emp_id = emp.EmpID
            
            # Count unique days with clock in
            emp_attendance = [a for a in attendance_records if a.EmpID == emp_id and a.ClockIn]
            unique_days = len(set(a.WorkDate for a in emp_attendance))
            
            summary.append({
                'employee_name': f"{emp.FirstName} {emp.LastName}",
                'employee_code': emp.EmployeeCode,
                'month': f"{first_day.strftime('%B %Y')}",
                'days_present': unique_days,
                'target_days': target_days
            })
        
        return jsonify({
            'success': True,
            'month': first_day.strftime('%B %Y'),
            'year': year,
            'month_num': month,
            'target_days': target_days,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

'''
    
    # Insert before fiscal year summary
    app_content = app_content.replace(
        "@app.route('/api/reports/fiscal-year-summary')",
        monthly_endpoint + "@app.route('/api/reports/fiscal-year-summary')"
    )
    
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    
    print("✅ Added monthly attendance summary API endpoint")
else:
    print("ℹ️ Monthly attendance summary API already exists")

# Now update the admin_input.html to add the new table
admin_html_path = 'templates/admin_input.html'
with open(admin_html_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

# Add the Monthly Attendance Summary section after Fiscal Year Summary
# First, let's find where Fiscal Year Summary ends
fiscal_section = '''        <!-- Fiscal Year Summary Table -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mt-4">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4 gap-2">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Fiscal Year Summary (Oct 2025 - Present)
                </h2>
                <button onclick="fetchFiscalYearSummary()" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded">
                    Refresh
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Hours</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Annual Leave (of 21)</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sick Days</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Unpaid Absences</th>
                        </tr>
                    </thead>
                    <tbody id="fiscalYearSummaryTable" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="5" class="px-3 py-4 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>'''

new_section = '''        <!-- Fiscal Year Summary Table -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mt-4">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4 gap-2">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Fiscal Year Summary (Oct 2025 - Present)
                </h2>
                <button onclick="fetchFiscalYearSummary()" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded">
                    Refresh
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Hours</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Annual Leave (of 21)</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sick Days</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Unpaid Absences</th>
                        </tr>
                    </thead>
                    <tbody id="fiscalYearSummaryTable" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="5" class="px-3 py-4 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Monthly Attendance Summary Table -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mt-4">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4 gap-2">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Monthly Attendance Summary
                </h2>
                <div class="flex gap-2 items-center">
                    <select id="summaryMonth" class="px-2 py-1 text-sm border rounded">
                        <option value="1">January</option>
                        <option value="2">February</option>
                        <option value="3">March</option>
                        <option value="4">April</option>
                        <option value="5">May</option>
                        <option value="6">June</option>
                        <option value="7">July</option>
                        <option value="8">August</option>
                        <option value="9">September</option>
                        <option value="10">October</option>
                        <option value="11">November</option>
                        <option value="12">December</option>
                    </select>
                    <select id="summaryYear" class="px-2 py-1 text-sm border rounded">
                        <option value="2025">2025</option>
                        <option value="2026">2026</option>
                    </select>
                    <button onclick="fetchMonthlyAttendanceSummary()" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded">
                        Load
                    </button>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Days Present</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Target Days</th>
                        </tr>
                    </thead>
                    <tbody id="monthlyAttendanceTable" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="4" class="px-3 py-4 text-center text-gray-500">Select month and click Load</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>'''

admin_content = admin_content.replace(fiscal_section, new_section)

# Add the JavaScript function
# Find a good place to add it
old_js = '''        // Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
        fetchFiscalYearSummary();'''

new_js = '''        // Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
        fetchFiscalYearSummary();
        
        // Set default month/year
        const now = new Date();
        document.getElementById('summaryMonth').value = now.getMonth() + 1;
        document.getElementById('summaryYear').value = now.getFullYear();'''

admin_content = admin_content.replace(old_js, new_js)

# Add the fetchMonthlyAttendanceSummary function
old_fetch = '''        // Fetch Fiscal Year Summary
        async function fetchFiscalYearSummary() {'''

new_fetch = '''        // Fetch Monthly Attendance Summary
        async function fetchMonthlyAttendanceSummary() {
            const year = document.getElementById('summaryYear').value;
            const month = document.getElementById('summaryMonth').value;
            
            try {
                const response = await fetch(`${API_BASE}/api/reports/monthly-attendance-summary?year=${year}&month=${month}`);
                const data = await response.json();
                
                const tableBody = document.getElementById('monthlyAttendanceTable');
                
                if (data.success && data.summary) {
                    const rows = data.summary.map(emp => {
                        const presentClass = emp.days_present >= emp.target_days ? 'text-green-600 font-semibold' : 
                                           emp.days_present >= emp.target_days * 0.5 ? 'text-yellow-600' : 'text-red-600';
                        
                        return `
                            <tr class="hover:bg-gray-50">
                                <td class="px-3 py-2 font-medium text-gray-900 text-sm">${emp.employee_name}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${emp.month}</td>
                                <td class="px-3 py-2 text-sm ${presentClass}">${emp.days_present}</td>
                                <td class="px-3 py-2 text-gray-600 text-sm">${emp.target_days}</td>
                            </tr>
                        `;
                    }).join('');
                    
                    tableBody.innerHTML = rows;
                } else {
                    tableBody.innerHTML = '<tr><td colspan="4" class="px-3 py-4 text-center text-gray-500">No data found</td></tr>';
                }
            } catch (error) {
                console.error('Error fetching monthly attendance:', error);
                document.getElementById('monthlyAttendanceTable').innerHTML = '<tr><td colspan="4" class="px-3 py-4 text-center text-red-500">Failed to load data</td></tr>';
            }
        }

        // Fetch Fiscal Year Summary
        async function fetchFiscalYearSummary() {'''

admin_content = admin_content.replace(old_fetch, new_fetch)

with open(admin_html_path, 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("✅ Added Monthly Attendance Summary table to admin page")
print("\\n✅ All updates completed!")
