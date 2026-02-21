"""
Script to add Fiscal Year Summary Table to admin_input.html
"""

# Read the file
with open('templates/admin_input.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the Fiscal Year Summary section before </main>
old_main_end = '''        <!-- Recent Attendance Entries -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mt-4">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Recent Attendance Entries
            </h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                        </tr>
                    </thead>
                    <tbody id="recentEntries" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="4" class="px-3 py-4 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>'''

new_main_end = '''        <!-- Recent Attendance Entries -->
        <section class="bg-white rounded-xl card-shadow p-4 md:p-6 mt-4">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Recent Attendance Entries
            </h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                        </tr>
                    </thead>
                    <tbody id="recentEntries" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="4" class="px-3 py-4 text-center text-gray-500">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Fiscal Year Summary Table -->
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

content = content.replace(old_main_end, new_main_end)

# Add the JavaScript function before the closing </script>
old_js_end = '''        // Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
        
        // Set default date range for PDF export (current month)'''

new_js_end = '''        // Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
        fetchFiscalYearSummary();
        
        // Set default date range for PDF export (current month)'''

content = content.replace(old_js_end, new_js_end)

# Add the fetchFiscalYearSummary function
old_fetch_function = '''        // Export Leave PDF
        function exportLeavePDF() {'''

new_fetch_function = '''        // Fetch Fiscal Year Summary
        async function fetchFiscalYearSummary() {
            try {
                const response = await fetch(`${API_BASE}/api/reports/fiscal-year-summary`);
                const data = await response.json();
                
                if (data.success && data.summary) {
                    const rows = data.summary.map(emp => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-3 py-2 font-medium text-gray-900 text-sm">${emp.employee_name}</td>
                            <td class="px-3 py-2 text-gray-600 text-sm">${emp.total_hours_worked}</td>
                            <td class="px-3 py-2 text-gray-600 text-sm">${emp.annual_leave_taken} (${emp.annual_leave_remaining} remaining)</td>
                            <td class="px-3 py-2 text-gray-600 text-sm">${emp.sick_days_taken}</td>
                            <td class="px-3 py-2 text-gray-600 text-sm">${emp.unpaid_absences}</td>
                        </tr>
                    `).join('');
                    
                    document.getElementById('fiscalYearSummaryTable').innerHTML = rows;
                } else {
                    document.getElementById('fiscalYearSummaryTable').innerHTML = '<tr><td colspan="5" class="px-3 py-4 text-center text-gray-500">No data found</td></tr>';
                }
            } catch (error) {
                console.error('Error fetching fiscal year summary:', error);
                document.getElementById('fiscalYearSummaryTable').innerHTML = '<tr><td colspan="5" class="px-3 py-4 text-center text-red-500">Failed to load summary</td></tr>';
            }
        }

        // Export Leave PDF
        function exportLeavePDF() {'''

content = content.replace(old_fetch_function, new_fetch_function)

# Write back
with open('templates/admin_input.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fiscal Year Summary Table added to admin_input.html")
