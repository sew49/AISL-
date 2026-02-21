# Script to add PDF export buttons to admin_input.html

# Read the file
with open('templates/admin_input.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add export buttons to Leave Records section
old_leave_header = '''<h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
                Leave Records
                <button id="refreshLeaveBtn" class="ml-2 p-1 text-blue-600 hover:text-blue-800" title="Refresh">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                </button>
            </h2>'''

new_leave_header = '''<div class="flex flex-col md:flex-row md:items-center md:justify-between mb-4 gap-2">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    Leave Records
                    <button id="refreshLeaveBtn" class="ml-2 p-1 text-blue-600 hover:text-blue-800" title="Refresh">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                    </button>
                </h2>
                <div class="flex gap-2 items-center">
                    <input type="date" id="leaveStartDate" class="px-2 py-1 text-sm border rounded w-32">
                    <input type="date" id="leaveEndDate" class="px-2 py-1 text-sm border rounded w-32">
                    <button onclick="exportLeavePDF()" class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Export PDF
                    </button>
                </div>
            </div>'''

content = content.replace(old_leave_header, new_leave_header)

# Add JavaScript for PDF export
old_js_end = '''// Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
    </script>'''

new_js_end = '''// Initialize
        fetchEmployees();
        fetchLeaveRecords();
        fetchRecentEntries();
        
        // Set default date range for PDF export (current month)
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        document.getElementById('leaveStartDate').valueAsDate = startOfMonth;
        document.getElementById('leaveEndDate').valueAsDate = now;
        
        // Export Leave PDF
        function exportLeavePDF() {
            const startDate = document.getElementById('leaveStartDate').value;
            const endDate = document.getElementById('leaveEndDate').value;
            
            if (!startDate || !endDate) {
                showAlert('Please select date range', 'error');
                return;
            }
            
            window.open(`${API_BASE}/api/reports/leave-pdf?start_date=${startDate}&end_date=${endDate}`, '_blank');
        }
    </script>'''

content = content.replace(old_js_end, new_js_end)

# Write back
with open('templates/admin_input.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("PDF export buttons added to admin_input.html")
