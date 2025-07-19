#!/usr/bin/env python3
"""
Debug PDF template generation
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

config = PresentationConfig()
config.set('slide_number.enabled', True)
config.set('slide_number.format', 'current/total')

converter = MarkdownToPDF(config=config)

# Read markdown content
with open(test_md, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Parse slides
slides = converter.parse_markdown_slides(md_content)
print(f"Number of slides parsed: {len(slides)}")

# Generate PDF template HTML (like PDF generation does)
html_content = converter.template.render(
    title="test",
    slides=slides,
    css=converter.css,
    font_family=converter.font_family,
    logo_data=None,
    logo_mime_type='image/png',
    logo_position=converter.logo_position,
    enable_navigation=False,  # This is what PDF uses
    show_arrows=False,
    show_dots=False,
    show_slide_numbers=True,
    slide_number_format='{current}/{total}',
    initial_slide_number='1',
    config=converter.config
)

print("=== PDF TEMPLATE ANALYSIS ===")
print(f"Total slides: {html_content.count('class=\"slide\"')}")
print(f"slide-display count: {html_content.count('slide-display')}")
print(f"slide-counter count: {html_content.count('slide-counter')}")

# Find slide-display occurrences
lines = html_content.split('\n')
for i, line in enumerate(lines):
    if 'slide-display' in line:
        print(f"Line {i+1}: {line.strip()}")

print(f"\nNavigation enabled: {'has-navigation' in html_content}")
print(f"Individual slide numbers: {'Individual slide numbers for PDF' in html_content}")

# Check each slide for numbers
for i, slide in enumerate(slides):
    slide_html = f'<div class="slide'
    start_idx = html_content.find(slide_html, html_content.find(slide_html) + 1 if i > 0 else 0)
    if start_idx >= 0:
        end_idx = html_content.find('<div class="slide', start_idx + 1)
        if end_idx == -1:
            end_idx = html_content.find('</body>', start_idx)
        slide_section = html_content[start_idx:end_idx]
        has_number = 'slide-display' in slide_section
        print(f"Slide {i+1} has number: {has_number}")

# Save for inspection
with open(os.path.join(temp_dir, "pdf_template.html"), 'w') as f:
    f.write(html_content)

print(f"\nPDF template saved to: {temp_dir}/pdf_template.html")

# Cleanup
# shutil.rmtree(temp_dir)