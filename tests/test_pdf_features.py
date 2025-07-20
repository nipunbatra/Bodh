#!/usr/bin/env python3
"""
Comprehensive PDF feature testing for Bodh
Test PDF-specific functionality and accuracy
"""

import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig, load_config
import json


class TestPDFSlideNumbers:
    """Test PDF slide number rendering"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_slide_numbers_all_themes(self):
        """Test that slide numbers appear in PDF for all themes"""
        themes = ['default', 'modern', 'minimal', 'gradient', 'dark', 'sky', 'solarized', 'moon', 'metropolis']
        
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
First slide content

---

# Slide 2  
Second slide content

---

# Slide 3
Third slide content
""")
        
        for theme in themes:
            config_file = os.path.join(self.temp_dir, f"{theme}_config.yml")
            with open(config_file, 'w') as f:
                f.write(f"""theme: {theme}
slide_number:
  enabled: true
  format: current/total
""")
            
            config = load_config(config_file)
            converter = MarkdownToPDF(config=config)
            pdf_file = os.path.join(self.temp_dir, f"{theme}_test.pdf")
            html_file = os.path.join(self.temp_dir, f"{theme}_test.html")
            
            # Generate both HTML and PDF
            converter.convert_to_html(test_md, html_file, _test_mode=True)
            converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
            
            # Verify HTML has slide numbers
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            assert 'slide-counter' in html_content, f"Theme {theme}: HTML missing slide counter"
            assert 'slide-display' in html_content, f"Theme {theme}: HTML missing slide display"
            
            # Verify PDF was created and has content
            assert os.path.exists(pdf_file), f"Theme {theme}: PDF not created"
            assert os.path.getsize(pdf_file) > 5000, f"Theme {theme}: PDF too small, likely missing content"
    
    def test_pdf_slide_number_formats(self):
        """Test different slide number formats in PDF"""
        formats = ['current', 'current/total', 'percent']
        
        test_md = os.path.join(self.temp_dir, "format_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
First slide

---

# Slide 2
Second slide

---

# Slide 3
Third slide
""")
        
        for format_type in formats:
            config = PresentationConfig()
            config.set('slide_number.format', format_type)
            config.set('slide_number.enabled', True)
            
            converter = MarkdownToPDF(config=config)
            safe_format = format_type.replace('/', '_')
            pdf_file = os.path.join(self.temp_dir, f"format_{safe_format}.pdf")
            html_file = os.path.join(self.temp_dir, f"format_{safe_format}.html")
            
            converter.convert_to_html(test_md, html_file, _test_mode=True)
            converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
            
            # Verify HTML has correct format
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            if format_type == 'current':
                assert 'slide-display">1<' in html_content, f"Format {format_type}: Wrong initial display"
            elif format_type == 'current/total':
                assert 'slide-display">1/3<' in html_content, f"Format {format_type}: Wrong initial display"
            elif format_type == 'percent':
                assert 'slide-display">33%<' in html_content, f"Format {format_type}: Wrong initial display"
            
            # Verify PDF was created
            assert os.path.exists(pdf_file), f"Format {format_type}: PDF not created"
            assert os.path.getsize(pdf_file) > 5000, f"Format {format_type}: PDF too small"


class TestPDFLogoRendering:
    """Test PDF logo rendering"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_logo_all_positions(self):
        """Test logo rendering in all positions for PDF"""
        positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        
        test_md = os.path.join(self.temp_dir, "logo_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Logo Test
This slide should have a logo in the specified position.

---

# Second Slide
Logo should be on this slide too.
""")
        
        for position in positions:
            config = PresentationConfig()
            config.set('logo.source', 'examples/sample-logo.svg')
            config.set('logo.location', position)
            config.set('slide_number.enabled', True)
            
            converter = MarkdownToPDF(config=config)
            pdf_file = os.path.join(self.temp_dir, f"logo_{position}.pdf")
            html_file = os.path.join(self.temp_dir, f"logo_{position}.html")
            
            converter.convert_to_html(test_md, html_file, _test_mode=True)
            converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
            
            # Verify HTML has logo
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            assert f'logo-{position}' in html_content, f"Position {position}: HTML missing logo class"
            assert 'data:image/svg+xml;base64,' in html_content, f"Position {position}: HTML missing logo data"
            
            # Verify PDF was created
            assert os.path.exists(pdf_file), f"Position {position}: PDF not created"
            assert os.path.getsize(pdf_file) > 5000, f"Position {position}: PDF too small"


class TestPDFComplexContent:
    """Test PDF rendering with complex content"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_code_highlighting(self):
        """Test PDF code syntax highlighting"""
        code_md = os.path.join(self.temp_dir, "code_test.md")
        with open(code_md, 'w') as f:
            f.write("""# Code Test

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

---

# JavaScript Code

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "code_test.pdf")
        html_file = os.path.join(self.temp_dir, "code_test.html")
        
        converter.convert_to_html(code_md, html_file, _test_mode=True)
        converter.convert_to_pdf(code_md, pdf_file, _test_mode=True)
        
        # Verify HTML has syntax highlighting
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'codehilite' in html_content, "HTML missing syntax highlighting"
        assert '<span class="k">def</span>' in html_content, "HTML missing keyword highlighting"
        assert '<span class="nb">print</span>' in html_content, "HTML missing builtin highlighting"
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "Code test PDF not created"
        assert os.path.getsize(pdf_file) > 10000, "Code test PDF too small"
    
    def test_pdf_tables(self):
        """Test PDF table rendering"""
        table_md = os.path.join(self.temp_dir, "table_test.md")
        with open(table_md, 'w') as f:
            f.write("""# Table Test

| Feature | Status | Quality |
|---------|--------|---------|
| PDF Gen | ✅ | Excellent |
| HTML Gen | ✅ | Perfect |
| Themes | ✅ | Multiple |
| Fonts | ✅ | Google Fonts |

---

# Complex Table

| Column 1 | Column 2 | Column 3 | Column 4 |
|----------|----------|----------|----------|
| A very long piece of text that should wrap | B | C | D |
| E | F very long text | G | H |
| I | J | K very long text that tests wrapping | L |
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "table_test.pdf")
        html_file = os.path.join(self.temp_dir, "table_test.html")
        
        converter.convert_to_html(table_md, html_file, _test_mode=True)
        converter.convert_to_pdf(table_md, pdf_file, _test_mode=True)
        
        # Verify HTML has tables
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert '<table>' in html_content, "HTML missing table"
        assert '<thead>' in html_content, "HTML missing table header"
        assert '<tbody>' in html_content, "HTML missing table body"
        assert 'PDF Gen' in html_content, "HTML missing table content"
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "Table test PDF not created"
        assert os.path.getsize(pdf_file) > 10000, "Table test PDF too small"
    
    def test_pdf_math_rendering(self):
        """Test PDF math rendering"""
        math_md = os.path.join(self.temp_dir, "math_test.md")
        with open(math_md, 'w') as f:
            f.write("""# Math Test

## Display Math
$$E = mc^2$$

$$\\sum_{i=1}^{n} x_i = x_1 + x_2 + \\cdots + x_n$$

---

# Inline Math
The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$.

Einstein's famous equation $E = mc^2$ relates energy and mass.
""")
        
        config = PresentationConfig()
        config.set('math.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        pdf_file = os.path.join(self.temp_dir, "math_test.pdf")
        html_file = os.path.join(self.temp_dir, "math_test.html")
        
        converter.convert_to_html(math_md, html_file, _test_mode=True)
        converter.convert_to_pdf(math_md, pdf_file, _test_mode=True)
        
        # Verify HTML has MathJax
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'MathJax' in html_content, "MathJax not included for math rendering"
        assert 'state: () => 6' in html_content, "Mock MathJax content not loaded"
        assert '$E = mc^2$' in html_content, "HTML missing math content"
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "Math test PDF not created"
        assert os.path.getsize(pdf_file) > 10000, "Math test PDF too small"
    
    def test_pdf_images(self):
        """Test PDF image rendering"""
        image_md = os.path.join(self.temp_dir, "image_test.md")
        with open(image_md, 'w') as f:
            f.write("""# Image Test

![Sample Image](examples/sample-image.png)

---

# Multiple Images

![Small Image](examples/sample-image-small.png)

![JPG Image](examples/sample-image.jpg)
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "image_test.pdf")
        html_file = os.path.join(self.temp_dir, "image_test.html")
        
        converter.convert_to_html(image_md, html_file, _test_mode=True)
        converter.convert_to_pdf(image_md, pdf_file, _test_mode=True)
        
        # Verify HTML has images
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert '<img' in html_content, "HTML missing images"
        assert 'sample-image.png' in html_content, "HTML missing PNG image"
        assert 'sample-image.jpg' in html_content, "HTML missing JPG image"
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "Image test PDF not created"
        assert os.path.getsize(pdf_file) > 15000, "Image test PDF too small"


class TestPDFPrintMediaQueries:
    """Test PDF print media query handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_print_queries_present(self):
        """Test that print media queries are present in HTML"""
        test_md = os.path.join(self.temp_dir, "print_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Print Test
Testing print media queries.

---

# Second Slide
More content.
""")
        
        config = PresentationConfig()
        config.set('logo.source', 'examples/sample-logo.svg')
        config.set('slide_number.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        html_file = os.path.join(self.temp_dir, "print_test.html")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check that print media queries are present
        assert '@media print' in html_content, "Missing print media queries"
        assert 'display: none !important' in html_content, "Print queries not hiding interactive elements"
        assert 'display: flex !important' in html_content, "Print queries not showing slides"
        assert 'slide-counter' in html_content, "Print queries missing slide counter styles"
        
        # Check CSS rules for print
        assert '.nav-btn' in html_content, "Missing nav button styles"
        assert '.keyboard-hint' in html_content, "Missing keyboard hint styles"
        assert '.slide-dots' in html_content, "Missing slide dots styles"
        assert '.logo' in html_content, "Missing logo styles"


class TestPDFContentAccuracy:
    """Test PDF content accuracy"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_slide_count_accuracy(self):
        """Test that PDF processes correct number of slides"""
        test_md = os.path.join(self.temp_dir, "slide_count.md")
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
Content 1

---

# Slide 2
Content 2

---

# Slide 3
Content 3

---

# Slide 4
Content 4

---

# Slide 5
Content 5
""")
        
        converter = MarkdownToPDF()
        
        # Test slide parsing directly
        with open(test_md, 'r') as f:
            content = f.read()
        
        slides = converter.parse_markdown_slides(content)
        
        # Should have exactly 5 slides
        assert len(slides) == 5, f"Expected 5 slides, got {len(slides)}"
        
        # Check slide content
        assert 'Slide 1' in slides[0], "First slide missing expected content"
        assert 'Slide 2' in slides[1], "Second slide missing expected content"
        assert 'Slide 5' in slides[4], "Fifth slide missing expected content"
        
        # Generate files
        html_file = os.path.join(self.temp_dir, "slide_count.html")
        pdf_file = os.path.join(self.temp_dir, "slide_count.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "PDF not created"
        assert os.path.getsize(pdf_file) > 10000, "PDF too small for 5 slides"
    
    def test_pdf_content_completeness(self):
        """Test that PDF preserves all content types"""
        content_md = os.path.join(self.temp_dir, "content_test.md")
        with open(content_md, 'w') as f:
            f.write("""# Main Title
This is the main title slide.

## Subtitle
With a subtitle.

---

# Second Slide
- Bullet point 1
- Bullet point 2
- Bullet point 3

**Bold text** and *italic text*.

---

# Code Slide
```python
def hello():
    print("Hello, World!")
```

---

# Table Slide
| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |
| 1    | 2    | 3    |
""")
        
        converter = MarkdownToPDF()
        
        # Test content parsing
        with open(content_md, 'r') as f:
            content = f.read()
        
        slides = converter.parse_markdown_slides(content)
        
        # Should have 4 slides
        assert len(slides) == 4, f"Expected 4 slides, got {len(slides)}"
        
        # Check content preservation
        all_content = ''.join(slides)
        assert 'Main Title' in all_content, "Missing main title"
        assert 'Subtitle' in all_content, "Missing subtitle"
        assert 'Second Slide' in all_content, "Missing second slide"
        assert 'Bullet point 1' in all_content, "Missing bullet points"
        assert 'def' in all_content and 'hello' in all_content, "Missing code content"
        assert '<table>' in all_content, "Missing table"
        assert 'Col1' in all_content, "Missing table headers"
        
        # Generate files
        html_file = os.path.join(self.temp_dir, "content_test.html")
        pdf_file = os.path.join(self.temp_dir, "content_test.pdf")
        
        converter.convert_to_html(content_md, html_file, _test_mode=True)
        converter.convert_to_pdf(content_md, pdf_file, _test_mode=True)
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "PDF not created"
        assert os.path.getsize(pdf_file) > 15000, "PDF too small for complex content"


class TestPDFErrorHandling:
    """Test PDF error handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_missing_images(self):
        """Test PDF generation with missing images"""
        bad_image_md = os.path.join(self.temp_dir, "bad_image.md")
        with open(bad_image_md, 'w') as f:
            f.write("""# Bad Image Test
![Missing Image](nonexistent-image.png)

This should not crash PDF generation.

---

# Another Slide
More content after missing image.
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "bad_image.pdf")
        
        # Should not crash
        converter.convert_to_pdf(bad_image_md, pdf_file, _test_mode=True)
        
        assert os.path.exists(pdf_file), "PDF not created with missing image"
        assert os.path.getsize(pdf_file) > 5000, "PDF too small with missing image"
    
    def test_pdf_missing_logo(self):
        """Test PDF generation with missing logo"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("""# Logo Test
This should work even with missing logo.

---

# Second Slide
More content.
""")
        
        config = PresentationConfig()
        config.set('logo.source', 'nonexistent-logo.png')
        config.set('slide_number.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        pdf_file = os.path.join(self.temp_dir, "bad_logo.pdf")
        
        # Should not crash
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        assert os.path.exists(pdf_file), "PDF not created with missing logo"
        assert os.path.getsize(pdf_file) > 5000, "PDF too small with missing logo"


def run_pdf_tests():
    """Run all PDF tests"""
    print("🧪 Running PDF Feature Tests...")
    print("=" * 50)
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All PDF tests passed!")
        return True
    else:
        print("❌ Some PDF tests failed!")
        return False


if __name__ == "__main__":
    success = run_pdf_tests()
    exit(0 if success else 1)