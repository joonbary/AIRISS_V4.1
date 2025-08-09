import re

with open('D:/AIRISS_project_clean/app/templates/airiss_v5.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Checking for syntax errors in JavaScript...")

# Track template literals
in_template = False
template_start_line = 0
template_depth = 0

for i, line in enumerate(lines, 1):
    # Skip lines outside script tags (roughly)
    if i < 1640 or i > 4680:
        continue
    
    # Track template literal boundaries
    for char in line:
        if char == '`':
            if template_depth == 0:
                template_depth = 1
                template_start_line = i
            else:
                template_depth = 0
    
    # Look for suspicious < characters outside template literals
    if template_depth == 0 and '<' in line:
        # Skip if it's a comment
        if '//' in line and line.index('//') < line.index('<'):
            continue
        
        # Skip comparison operators
        if any(op in line for op in ['<=', '<<', '< ', ' <']):
            continue
            
        # Check if there's an HTML tag pattern
        html_pattern = r'<[a-zA-Z/][^>]*>'
        if re.search(html_pattern, line):
            print(f"Line {i}: Possible HTML in JavaScript: {line.strip()[:100]}")

# Check for unclosed template literals
if template_depth > 0:
    print(f"\nWarning: Unclosed template literal starting at line {template_start_line}")

print("\nChecking for other common syntax errors...")

# Check for missing commas between object properties
for i in range(1640, min(4680, len(lines))):
    line = lines[i].strip()
    next_line = lines[i+1].strip() if i+1 < len(lines) else ""
    
    # Pattern: property definition followed by another property without comma
    if re.match(r'^[a-zA-Z_]\w*\s*:', line) and line.endswith('}'):
        if re.match(r'^[a-zA-Z_]\w*\s*:', next_line):
            print(f"Line {i+1}: Possible missing comma after property")

print("\nDone checking.")