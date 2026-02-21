content = open('templates/admin_input.html', 'r', encoding='utf-8').read()

# Fix duplicate 'const now = new Date()' declarations
old = """// Set default month/year
        const now = new Date();
        document.getElementById('summaryMonth').value = now.getMonth() + 1;
        document.getElementById('summaryYear').value = now.getFullYear();
        
        // Set default date range for PDF export (current month)
        const now = new Date();
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);"""

new = """// Set default month/year and date range for PDF export
        const now = new Date();
        document.getElementById('summaryMonth').value = now.getMonth() + 1;
        document.getElementById('summaryYear').value = now.getFullYear();
        
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);"""

content = content.replace(old, new)
open('templates/admin_input.html', 'w', encoding='utf-8').write(content)
print('Fixed duplicate variable declaration')
