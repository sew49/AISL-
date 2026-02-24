import re

with open('templates/staff/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix colspan in the loading row
content = content.replace('colspan="5"', 'colspan="6"')

with open('templates/staff/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed colspan!')
