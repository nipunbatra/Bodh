#!/usr/bin/env python3
"""
Debug slide numbering issue
"""

import os
import tempfile
import shutil
from bodh import MarkdownToPDF
from config import PresentationConfig

# Create test
temp_dir = tempfile.mkdtemp()
test_md = os.path.join(temp_dir, "test.md")

with open(test_md, 'w') as f:
    f.write("""# Slide 1
Content 1

---

# Slide 2
Content 2

---

# Slide 3
Content 3
""")

# Test PDF generation
config = PresentationConfig()
config.set('slide_number.enabled', True)
config.set('slide_number.format', 'current/total')

converter = MarkdownToPDF(config=config)

html_file = os.path.join(temp_dir, "test.html")
pdf_file = os.path.join(temp_dir, "test.pdf")

# Generate both
converter.convert_to_html(test_md, html_file)
converter.convert_to_pdf(test_md, pdf_file)

# Read HTML output
with open(html_file, 'r') as f:
    html_content = f.read()

print("=== HTML ANALYSIS ===")
print(f"Total slides: {html_content.count('class=\"slide\"')}")
print(f"slide-display count: {html_content.count('slide-display')}")
print(f"slide-counter count: {html_content.count('slide-counter')}")

# Find slide-display occurrences
lines = html_content.split('\n')
for i, line in enumerate(lines):
    if 'slide-display' in line:
        print(f"Line {i+1}: {line.strip()}")

# Check for navigation vs non-navigation
print(f"\nNavigation enabled in HTML: {'has-navigation' in html_content}")
print(f"Individual slide numbers: {'Individual slide numbers for PDF' in html_content}")

# Cleanup
shutil.rmtree(temp_dir)