#!/usr/bin/env python3
"""
Test actual production PDF issues:
1. Slide numbers overlapping in same position
2. Text getting cut off / not fully loaded
"""

import os
import tempfile
import shutil
import time
from bodh import MarkdownToPDF
from config import load_config


class TestProductionPDFIssues:
    """Test the specific issues found in production PDFs"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_logo_demo_exact_reproduction(self):
        """Test the exact logo-demo scenario to reproduce issues"""
        # Use the exact logo-demo configuration
        if not os.path.exists('configs/logo-demo.yml'):
            print("Skipping test - logo-demo.yml not found")
            return
            
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Create content similar to feature-showcase.md
        test_md = os.path.join(self.temp_dir, "logo_demo_reproduction.md")
        with open(test_md, 'w') as f:
            f.write("""# 🚀 Bodh Feature Showcase
## Complete Configuration Demonstration

This presentation demonstrates **logos**, **slide numbering**, **navigation**, and **styling** options.

---

## 📊 Slide Numbering Formats

Bodh supports multiple slide numbering formats:

### Current Only
- Format: `current` → Shows: **1**, **2**, **3**
- Perfect for minimal presentations

### Current/Total
- Format: `current/total` → Shows: **1/8**, **2/8**, **3/8**
- Great for showing progress

### Percentage
- Format: `percent` → Shows: **12%**, **25%**, **37%**
- Ideal for long presentations

---

## 🖼️ Logo Positioning

Logos can be placed in **four corners**:

| Position | Best For |
|----------|----------|
| `top-left` | Company branding |
| `top-right` | Event logos |
| `bottom-left` | University marks |
| `bottom-right` | Certification badges |

**Note:** Logo size is configurable from 50-200px

---

## 🎨 Navigation Options

### Arrow Navigation
- **Enabled**: Previous/Next buttons
- **Disabled**: Keyboard-only navigation

### Dot Navigation  
- **Small dots**: Minimal distraction
- **Hidden**: Clean presentation mode

### Progress Bar
- **Visible**: Shows completion percentage
- **Hidden**: Focus on content

---

## 🎭 Theme Variations

### Modern Themes
- **Modern**: Clean, professional
- **Minimal**: Ultra-clean, lots of whitespace
- **Gradient**: Colorful backgrounds

### Traditional Themes
- **Dark**: Perfect for tech talks
- **Solarized**: Easy on the eyes
- **Default**: Classic presentation style

---

## 💼 Corporate Features

### Professional Setup
```yaml
theme: dark
slide_number: { format: current, position: top-right }
logo: { location: top-left, size: 120 }
navigation: { show_arrows: false, show_dots: true }
style: { animations: false, rounded_corners: false }
```

### Academic Setup
```yaml
theme: solarized
slide_number: { format: current/total, position: bottom-center }
logo: { location: bottom-left, size: 80 }
navigation: { show_progress: true }
```

---

## 🔧 Configuration Power

### YAML Configuration
- **Flexible**: Override any setting
- **Reusable**: Save configurations for different events
- **Portable**: Share configs across teams

### CLI Overrides
```bash
# Use config but override theme
bodh slides.md -c corporate.yml -t gradient

# Override slide numbering
bodh slides.md -c config.yml --slide-format percent
```

---

# 🎉 Ready to Create?

**Bodh** makes beautiful presentations effortless!

1. **Write** in Markdown
2. **Configure** with YAML  
3. **Generate** stunning PDFs

*Experience the power of knowledge sharing!*
""")
        
        # Generate the exact PDF template that gets sent to Playwright
        with open(test_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        print(f"Parsed {len(slides)} slides")
        
        # Get logo data
        logo_data = None
        logo_mime_type = 'image/png'
        if converter.logo_path and os.path.exists(converter.logo_path):
            logo_result = converter._encode_image(converter.logo_path)
            if logo_result:
                logo_data = logo_result['data']
                logo_mime_type = logo_result['mime_type']
        
        # Generate the EXACT HTML that goes to PDF
        pdf_html = converter.template.render(
            title="logo_demo_reproduction",
            slides=slides,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=logo_data,
            logo_mime_type=logo_mime_type,
            logo_position=converter.logo_position,
            enable_navigation=False,  # PDF mode
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=True,
            slide_number_format='{current}/{total}',
            initial_slide_number='1',
            config=converter.config
        )
        
        # Save the HTML for inspection
        debug_html = os.path.join(self.temp_dir, "pdf_debug.html")
        with open(debug_html, 'w') as f:
            f.write(pdf_html)
        
        print(f"PDF HTML template saved to: {debug_html}")
        
        # Analyze slide numbering
        slide_displays = pdf_html.count('slide-display')
        slides_count = len(slides)
        
        print(f"Slides: {slides_count}, Slide displays: {slide_displays}")
        
        # Check for specific slide numbers
        slide_numbers_found = []
        for i in range(1, slides_count + 1):
            slide_num = f'{i}/{slides_count}'
            if f'>{slide_num}<' in pdf_html:
                slide_numbers_found.append(slide_num)
        
        print(f"Slide numbers found: {slide_numbers_found}")
        
        # Look for overlapping slide number positioning
        lines = pdf_html.split('\n')
        slide_nav_lines = []
        for i, line in enumerate(lines):
            if 'slide-nav' in line or 'slide-display' in line:
                slide_nav_lines.append(f"Line {i+1}: {line.strip()}")
        
        print("Slide navigation HTML:")
        for line in slide_nav_lines:
            print(f"  {line}")
        
        # Generate actual PDF
        pdf_file = os.path.join(self.temp_dir, "logo_demo_reproduction.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        print(f"Generated PDF: {pdf_size} bytes")
        
        # SPECIFIC CHECKS FOR REPORTED ISSUES:
        
        # 1. Slide numbers should be individual, not overlapping
        assert slide_displays == slides_count, f"Expected {slides_count} individual slide numbers, got {slide_displays}"
        
        # 2. Each slide should have its own number
        assert len(slide_numbers_found) == slides_count, f"Not all slide numbers found: {slide_numbers_found}"
        
        print("✅ Logo demo reproduction test completed")
    
    def test_text_content_loading_issues(self):
        """Test for text getting cut off or not fully loaded"""
        test_md = os.path.join(self.temp_dir, "text_loading_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Text Loading Test

This slide tests whether all text content loads properly in the PDF.

## Long Content Section
This is a long paragraph that should be fully visible in the PDF output. Sometimes text can get cut off if the rendering process doesn't wait long enough for all content to load properly. This paragraph specifically tests that scenario.

### Subsection with More Text
More content here that should be fully visible. The issue might be related to:

1. Playwright timing issues
2. Font loading delays  
3. CSS rendering delays
4. Content not fully processed

## Code Block Test
```python
def test_text_loading():
    # This code block should be fully visible
    long_variable_name = "This is a long string that tests text loading"
    another_long_variable = "More text content for testing"
    return f"{long_variable_name} {another_long_variable}"
```

## Table Test
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Content that should be fully visible | More content | Even more |
| Test data for loading verification | Additional data | Final data |

## Final Paragraph
This final paragraph should be completely visible in the PDF. If any text is cut off or missing, it indicates a content loading or rendering issue that needs to be fixed.

---

# Second Slide

This second slide tests multi-slide text loading.

## More Content
All of this content should be fully loaded and visible in the final PDF output.

### Testing Different Content Types
- **Bold text** should render completely
- *Italic text* should render completely  
- `Code text` should render completely
- [Link text](http://example.com) should render completely

## Mathematical Content
The equation $E = mc^2$ should render properly.

Display equation:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

## Final Content
This is the final content on the second slide that should be fully visible.
""")
        
        converter = MarkdownToPDF()
        
        # Add extra wait time to ensure content loads
        # Let's check the current Playwright timeout settings
        pdf_file = os.path.join(self.temp_dir, "text_loading_test.pdf")
        
        start_time = time.time()
        converter.convert_to_pdf(test_md, pdf_file)
        end_time = time.time()
        
        conversion_time = end_time - start_time
        print(f"PDF conversion took: {conversion_time:.2f} seconds")
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        print(f"PDF size: {pdf_size} bytes")
        
        # PDF should be substantial if all content loaded
        assert pdf_size > 30000, f"PDF too small, content may be cut off: {pdf_size} bytes"
        
        print("✅ Text content loading test completed")
    
    def test_playwright_timing_investigation(self):
        """Investigate Playwright timing issues that might cause content to be cut off"""
        test_md = os.path.join(self.temp_dir, "timing_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Playwright Timing Test

This tests whether Playwright is waiting long enough for content to load.

## Content that might load slowly:
- Mathematical equations: $\\alpha + \\beta = \\gamma$
- Code blocks with syntax highlighting
- Tables with formatting
- Long paragraphs with complex styling

```python
# This code block tests syntax highlighting loading
def complex_function_with_long_name():
    result = "Testing whether this content loads completely"
    return result
```

## Large Table
| Very Long Header 1 | Very Long Header 2 | Very Long Header 3 |
|--------------------|--------------------|--------------------|
| Long content here | More long content | Even more content |
| Additional row | More data | Final column |

## Final Test Content
This content should be fully loaded and visible in the PDF.
""")
        
        # Test current PDF generation with timing analysis
        converter = MarkdownToPDF()
        
        # Generate PDF and measure timing
        pdf_file = os.path.join(self.temp_dir, "timing_test.pdf")
        
        start_time = time.time()
        converter.convert_to_pdf(test_md, pdf_file)
        end_time = time.time()
        
        print(f"PDF generation took: {end_time - start_time:.2f} seconds")
        
        # Check if PDF was created and has reasonable size
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        print(f"PDF size: {pdf_size} bytes")
        
        # Also generate HTML for comparison
        html_file = os.path.join(self.temp_dir, "timing_test.html")
        converter.convert_to_html(test_md, html_file)
        
        html_size = os.path.getsize(html_file)
        print(f"HTML size: {html_size} bytes")
        
        # PDF should be reasonably sized relative to HTML
        assert pdf_size > 10000, f"PDF suspiciously small: {pdf_size} bytes"
        
        print("✅ Playwright timing investigation completed")


if __name__ == "__main__":
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "-s", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    exit(result.returncode)