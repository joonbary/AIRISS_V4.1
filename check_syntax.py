import re

with open('D:/AIRISS_project_clean/app/templates/airiss_v5.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find script tags
script_pattern = r'<script[^>]*>(.*?)</script>'
scripts = re.findall(script_pattern, content, re.DOTALL)

print(f"Found {len(scripts)} script blocks")

# Look for potential syntax errors
for i, script in enumerate(scripts):
    lines = script.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Look for potential HTML tags in JavaScript (outside template literals)
        if not line.strip().startswith('//'):
            # Count backticks to check if we're in a template literal
            backtick_count = line.count('`')
            
            # Simple check for < that might be HTML
            if '<' in line and '`' not in line:
                # Skip comparison operators
                if not any(op in line for op in ['<=', '<<', '< ', ' <']):
                    print(f'Script {i+1}, Line {line_num}: {line.strip()[:100]}')
                    
# Also check for unclosed braces
open_braces = content.count('{')
close_braces = content.count('}')
print(f"\nBrace count: {{ = {open_braces}, }} = {close_braces}, diff = {open_braces - close_braces}")