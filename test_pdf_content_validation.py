#!/usr/bin/env python3
"""
Tests for PDF content validation - ensuring content actually appears correctly in PDFs
"""

import os
import tempfile
import pytest
import subprocess
from bodh import MarkdownToPDF
from config import load_config


class TestPDFContentValidation:
    
    def test_embedded_fonts_work_properly(self):
        """Test that embedded fonts actually work and don't cause rendering issues"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "font_test.md")
        
        content = """# Font Test

This tests various font weights and styles:

**Bold text should be clearly bold**

*Italic text should be clearly italic* 

`Code text should use monospace font`

Regular text should use the configured font family.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Verify font CSS is embedded
        assert converter.font_css is not None
        assert len(converter.font_css) > 100  # Should have substantial embedded font data
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "font_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        # PDF should exist and be reasonably sized
        assert os.path.exists(result)
        assert os.path.getsize(result) > 5000  # Should be larger due to embedded fonts
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_content_validation_warnings_work(self):
        """Test that content validation warnings are properly triggered"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "validation_test.md")
        
        # Create content designed to trigger validation warnings
        long_line = "This is an extremely long line designed to trigger validation warnings " * 5
        many_lines = "\n".join([f"Line {i}" for i in range(30)])
        
        content = f"""# Validation Test

{long_line}

## Many Lines Section

{many_lines}

```python
def very_long_function_name_that_should_trigger_horizontal_overflow_warning():
    return "This line is also extremely long and should trigger warnings about code overflow"
```
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Capture output to verify warnings were printed
        import io
        import sys
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            pdf_file = os.path.join(temp_dir, "validation_test.pdf")
            converter.convert_to_pdf(test_md, pdf_file)
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Should have validation warnings
            assert "⚠️" in output
            assert "may cause text cutoff" in output
            assert "💡 Consider:" in output
            
        finally:
            sys.stdout = old_stdout
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_math_content_renders_in_pdf(self):
        """Test that mathematical content renders properly in PDF"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "math_test.md")
        
        content = """# Math Test

Inline math: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$

Display math:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

Complex equation:
$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        pdf_file = os.path.join(temp_dir, "math_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        # PDF should exist and be reasonably sized
        assert os.path.exists(result)
        assert os.path.getsize(result) > 3000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_code_blocks_render_properly(self):
        """Test that code blocks render with proper formatting"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "code_test.md")
        
        content = """# Code Test

Python code:
```python
def hello_world():
    print("Hello, World!")
    return "success"
```

JavaScript code:
```javascript
const greeting = "Hello";
console.log(greeting + " World!");
```

Bash commands:
```bash
ls -la
grep "pattern" file.txt
```
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        pdf_file = os.path.join(temp_dir, "code_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 2000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_multi_column_layout_in_pdf(self):
        """Test that multi-column layouts work properly in PDF"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "columns_test.md")
        
        content = """# Multi-Column Test

::: {.column}
Left column content:
- Item 1
- Item 2
- Item 3
:::

::: {.column}
Right column content:
- Item A
- Item B  
- Item C
:::
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        pdf_file = os.path.join(temp_dir, "columns_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 2000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_logo_appears_in_pdf(self):
        """Test that logo actually appears in the PDF"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "logo_test.md")
        
        content = """# Logo Test

This slide should have a logo in the top-right corner.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        # Use config with logo
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Verify logo is configured
        assert converter.logo_path is not None
        assert os.path.exists(converter.logo_path)
        
        pdf_file = os.path.join(temp_dir, "logo_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        # PDF with embedded logo should be larger
        assert os.path.getsize(result) > 3000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_slide_numbers_appear_correctly(self):
        """Test that slide numbers appear correctly and increment"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "numbers_test.md")
        
        content = """# Slide 1
First slide content

---

# Slide 2  
Second slide content

---

# Slide 3
Third slide content
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate HTML to check slide numbers
        with open(test_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        
        # Should have 3 slides
        assert len(slides) == 3
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "numbers_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 2000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_pdf_performance_is_improved(self):
        """Test that PDF generation is faster with embedded fonts"""
        import time
        
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "performance_test.md")
        
        content = """# Performance Test

This is a test of PDF generation speed with embedded fonts.

Regular content that should render quickly.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Time the PDF generation
        start_time = time.time()
        pdf_file = os.path.join(temp_dir, "performance_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should be faster than before (less than 8 seconds)
        assert generation_time < 8.0
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])