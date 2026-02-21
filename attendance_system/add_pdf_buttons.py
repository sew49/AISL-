# Script to add PDF export buttons to index.html

# Read the file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add export buttons section before the closing </header> of Status section
# Find the pattern for "Today's Status" section header
old_status_header = '''<h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Today's Status
                </h2>'''

new_status_header = '''<h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Today's Status
                </h2>
                <div class="flex gap-2">
                    <input type="date" id="attStartDate" class="px-2 py-1 text-sm border rounded w-32">
                    <input type="date" id="attEndDate" class="px-2 py-1 text-sm border rounded w-32">
                    <button onclick="exportAttendancePDF()" class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded flex items-center">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Export
                    </button>
                </div>'''

content = content.replace(old_status_header, new_status_header)

# Add the JavaScript function before the closing </script>
old_js_end = '''// Initialize
        setHeaderDate();
        fetchEmployees();
        fetchTodayStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(fetchTodayStatus, 30000);
    </script>'''

new_js_end = '''// Initialize
        setHeaderDate();
        fetchEmployees();
        fetchTodayStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(fetchTodayStatus, 30000);
        
        // Set default date range for PDF export (current month)
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        document.getElementById('attStartDate').valueAsDate = startOfMonth;
        document.getElementById('attEndDate').valueAsDate = now;
        
        // Export Attendance PDF
        function exportAttendancePDF() {
            const startDate = document.getElementById('attStartDate').value;
            const endDate = document.getElementById('attEndDate').value;
            
            if (!startDate || !endDate) {
                showAlert('Please select date range', 'error');
                return;
            }
            
            window.open(`${API_BASE}/api/reports/attendance-pdf?start_date=${startDate}&end_date=${endDate}`, '_blank');
        }
    </script>'''

content = content.replace(old_js_end, new_js_end)

# Write back
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("PDF export buttons added to index.html")
