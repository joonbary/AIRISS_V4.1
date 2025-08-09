#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('D:/AIRISS_project_clean/app/templates/airiss_v5.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for template literal errors...")

# Simple backtick counter
backtick_count = 0
current_template_start = 0

for i, line in enumerate(lines, 1):
    if i < 1640 or i > 4680:
        continue
    
    line_backticks = line.count('`')
    
    if line_backticks > 0:
        if backtick_count == 0 and line_backticks % 2 == 1:
            # Starting a template literal
            backtick_count = 1
            current_template_start = i
            print(f"Template literal starts at line {i}")
        elif backtick_count == 1 and line_backticks % 2 == 1:
            # Closing a template literal
            backtick_count = 0
            print(f"Template literal closes at line {i} (started at {current_template_start})")
        elif line_backticks % 2 == 0:
            # Even number, no change in state
            pass
        
if backtick_count > 0:
    print(f"\n⚠️ ERROR: Unclosed template literal starting at line {current_template_start}")
    print(f"Line content: {lines[current_template_start-1][:100]}")

# Also look for the specific error pattern
print("\nChecking for specific syntax patterns...")

for i in range(1640, min(4680, len(lines))):
    line = lines[i]
    
    # Check for incomplete template literals
    if '${' in line:
        # Count opening and closing braces
        open_count = line.count('${')
        close_count = line.count('}')
        if open_count > close_count:
            print(f"Line {i+1}: Possibly unclosed template expression: {line.strip()[:80]}")