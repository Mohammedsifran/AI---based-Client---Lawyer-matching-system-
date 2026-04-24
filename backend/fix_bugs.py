import os
import re

pages_dir = r'c:\Users\asus\Desktop\final year project\frontend\pages'
css_path = r'c:\Users\asus\Desktop\final year project\frontend\css\style.css'

# 1. Add helper classes to CSS
with open(css_path, 'a', encoding='utf-8') as f:
    f.write('\n/* IDE Bug Fixes */\n.text-red { color: red !important; }\n.text-green { color: green !important; }\n.bg-gray { background-color: #f5f5f5 !important; }\n.bg-white { background-color: #fff !important; }\n')

# 2. Iterate through all HTML files and fix Jinja in styles
for filename in os.listdir(pages_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(pages_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the alerts globally
    # Looking for: style="color: {{ 'red' if category == 'error' else 'green' }}; text-align: center; margin-bottom: 10px;"
    # Actually, we can use a more robust regex to catch variations
    content = re.sub(
        r'style="color:\s*\{\{\s*\'red\'\s*if\s*category\s*==\s*\'error\'\s*else\s*\'green\'\s*\}\}\s*;([^"]*)"',
        r'style="\1" class="alert alert-{{ category }} {% if category == \'error\' %}text-red{% else %}text-green{% endif %}"',
        content
    )
    
    # We also need to remove the first redundant class if it existed just before the style
    # E.g. <div class="alert alert-{{ category }}"\n            style="..." class="...">
    # Let's clean it up:
    content = re.sub(
        r'class="alert alert-\{\{\s*category\s*\}\}"\s*style="([^"]*)"\s*class="([^"]*)"',
        r'class="\2" style="\1"',
        content
    )

    # Specific fix for lawyer-profile.html (lines 147, 155)
    if filename == 'lawyer-profile.html':
        content = content.replace(
            'class="{% if lawyer.description %}textarea-readonly{% else %}textarea-editable{% endif %}"',
            'class="{% if lawyer.description %}textarea-readonly bg-gray{% else %}textarea-editable bg-white{% endif %}"'
        )
        content = re.sub(
            r'background-color:\s*\{%\s*if\s*lawyer\.description\s*%\}\#f5f5f5\{%\s*else\s*%\}\#fff\{%\s*endif\s*%\}\s*;',
            '',
            content
        )
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Bug squashing complete!")
