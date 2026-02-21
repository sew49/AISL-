"""
Script to add notification bell to main index.html
"""

index_html_path = 'templates/index.html'
with open(index_html_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Add notification bell in the header
old_header = '''<div class="text-right">
                    <p id="currentDate" class="text-lg font-semibold"></p>
                    <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                </div>'''

new_header = '''<div class="text-right flex items-center gap-3">
                    <!-- Notification Bell -->
                    <div class="relative">
                        <button id="notificationBell" class="relative p-2 text-white hover:bg-white/20 rounded-full transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                            </svg>
                            <span id="notificationBadge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">0</span>
                        </button>
                        <!-- Notification Dropdown -->
                        <div id="notificationDropdown" class="hidden absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50 border border-gray-200">
                            <div class="p-3 border-b border-gray-200">
                                <h3 class="font-semibold text-gray-800">Notifications</h3>
                            </div>
                            <div id="notificationList" class="max-h-64 overflow-y-auto">
                                <p class="p-4 text-gray-500 text-sm text-center">No notifications</p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <p id="currentDate" class="text-lg font-semibold"></p>
                        <p id="dayType" class="text-sm bg-white/20 px-3 py-1 rounded-full inline-block"></p>
                    </div>
                </div>'''

index_content = index_content.replace(old_header, new_header)

# Add notification JavaScript
old_script = '''        let employees = [];
        let selectedEmployeeId = null;'''

new_script = '''        let employees = [];
        let selectedEmployeeId = null;
        
        // Notification functions
        async function fetchNotifications() {
            if (!selectedEmployeeId) return;
            
            try {
                const response = await fetch(`${API_BASE}/api/notifications?emp_id=${selectedEmployeeId}`);
                const data = await response.json();
                
                if (data.success && data.notifications) {
                    // Update badge count
                    const unreadCount = data.notifications.filter(n => !n.is_read).length;
                    const badge = document.getElementById('notificationBadge');
                    if (unreadCount > 0) {
                        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
                        badge.classList.remove('hidden');
                    } else {
                        badge.classList.add('hidden');
                    }
                    
                    // Update notification list
                    const listEl = document.getElementById('notificationList');
                    if (data.notifications.length > 0) {
                        listEl.innerHTML = data.notifications.slice(0, 10).map(n => `
                            <div class="p-3 border-b border-gray-100 hover:bg-gray-50 ${n.is_read ? 'opacity-60' : ''}">
                                <p class="text-sm text-gray-800">${n.message}</p>
                                <p class="text-xs text-gray-500 mt-1">${new Date(n.created_at).toLocaleString()}</p>
                            </div>
                        `).join('');
                    } else {
                        listEl.innerHTML = '<p class="p-4 text-gray-500 text-sm text-center">No notifications</p>';
                    }
                }
            } catch (error) {
                console.error('Error fetching notifications:', error);
            }
        }
        
        // Toggle notification dropdown
        document.addEventListener('click', (e) => {
            const bell = document.getElementById('notificationBell');
            const dropdown = document.getElementById('notificationDropdown');
            
            if (bell && bell.contains(e.target)) {
                dropdown.classList.toggle('hidden');
                if (!dropdown.classList.contains('hidden') && selectedEmployeeId) {
                    fetchNotifications();
                }
            } else if (dropdown && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });'''

index_content = index_content.replace(old_script, new_script)

# Update employee selection to also fetch notifications
old_emp_select = '''        // Also update selectedEmployeeId when select changes
        employeeSelect.addEventListener('change', (e) => {
            selectedEmployeeId = e.target.value;
            if (selectedEmployeeId) {
                const emp = employees.find(em => em.emp_id == selectedEmployeeId);
                if (emp) {
                    employeeSearch.value = `${emp.first_name} ${emp.last_name}`;
                }
            }
        });'''

new_emp_select = '''        // Also update selectedEmployeeId when select changes
        employeeSelect.addEventListener('change', (e) => {
            selectedEmployeeId = e.target.value;
            if (selectedEmployeeId) {
                const emp = employees.find(em => em.emp_id == selectedEmployeeId);
                if (emp) {
                    employeeSearch.value = `${emp.first_name} ${emp.last_name}`;
                }
                // Fetch notifications when employee is selected
                fetchNotifications();
            }
        });
        
        // When clicking on dropdown item, also fetch notifications
        document.querySelectorAll('#employeeDropdown > div[data-id]').forEach(item => {
            item.addEventListener('click', () => {
                const empId = item.dataset.id;
                selectedEmployeeId = empId;
                const empName = item.dataset.name;
                employeeSearch.value = empName;
                employeeDropdown.classList.add('hidden');
                // Fetch notifications
                fetchNotifications();
            });
        });'''

index_content = index_content.replace(old_emp_select, new_emp_select)

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print("✅ Updated index.html with notification bell")
