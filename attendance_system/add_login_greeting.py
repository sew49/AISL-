# Update admin_login.html with time-based greeting

with open('templates/admin_login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the h1 to add id for greeting
content = content.replace(
    '<h1 class="text-xl md:text-2xl font-bold text-gray-800">Aero Instrument Management</h1>',
    '<h1 id="greeting" class="text-xl md:text-2xl font-bold text-gray-800">Loading...</h1>'
)

# 2. Add the JavaScript for greeting before the closing </body> tag
script = '''
    <script>
        function setGreeting() {
            const now = new Date();
            const hour = now.getHours();
            let greeting = '';
            
            if (hour >= 5 && hour < 12) {
                greeting = 'Good morning! Welcome to AISL attendance web. Please login to continue.';
            } else if (hour >= 12 && hour < 18) {
                greeting = 'Good afternoon! Welcome to AISL attendance web. Please login to continue.';
            } else {
                greeting = 'Good evening! Welcome to AISL attendance web. Please login to continue.';
            }
            
            document.getElementById('greeting').textContent = greeting;
        }
        
        // Set greeting on page load
        setGreeting();
    </script>
</body>'''

content = content.replace('</body>', script)

with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added time-based greeting to admin_login.html")
