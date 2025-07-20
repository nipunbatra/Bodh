#!/usr/bin/env python3
"""
Playwright timeout robustness testing
Testing edge cases that could cause timeout issues in PDF generation
"""

import os
import tempfile
import shutil
import subprocess
import sys
import time
from pathlib import Path
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig


class TestPlaywrightTimeoutRobustness:
    """Test edge cases that could cause Playwright timeouts"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_many_missing_images_different_types(self):
        """Test with many missing images of different types and URLs"""
        missing_md = os.path.join(self.temp_dir, "missing_images.md")
        
        # Create various types of missing image references
        missing_images = [
            "![Local missing](missing.jpg)",
            "![Local missing PNG](missing.png)",
            "![Local missing SVG](missing.svg)",
            "![Local missing GIF](missing.gif)",
            "![Local missing WebP](missing.webp)",
            "![HTTP URL](http://example.com/missing.jpg)",
            "![HTTPS URL](https://example.com/missing.png)",
            "![Invalid URL](not-a-url)",
            "![Empty URL]()",
            "![Relative up](../missing.jpg)",
            "![Relative down](./missing.png)",
            "![Absolute path](/nonexistent/image.jpg)",
            "![Home path](~/missing.svg)",
            "![Very long path](very/long/path/that/does/not/exist/and/goes/deep/into/directories/image.jpg)",
            "![Special chars](missing-with-special-chars!@#$%^&*().jpg)",
            "![Spaces in name](missing with spaces.jpg)",
            "![Unicode name](missing-ñáéíóú.jpg)",
            "![Query string](http://example.com/image.jpg?param=value)",
            "![Fragment](http://example.com/image.jpg#fragment)",
            "![Port](http://example.com:8080/image.jpg)",
            "![Slow domain](http://httpbin.org/delay/10)",  # This will timeout
        ]
        
        # Create 5 slides with different combinations
        slides = []
        for i in range(5):
            slide_images = missing_images[i*4:(i+1)*4]  # 4 images per slide
            slide_content = f"""# Slide {i+1} - Missing Images Test
            
This slide tests missing images of various types.

{chr(10).join(slide_images)}

## More content
This ensures the slide has substantial content beyond just images.

- Point 1
- Point 2
- Point 3
"""
            slides.append(slide_content)
        
        with open(missing_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        # Time the conversion
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "missing_images.pdf")
        
        # Should not timeout or hang
        converter.convert_to_pdf(missing_md, pdf_file, _test_mode=True)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete in reasonable time (under 30 seconds)
        assert conversion_time < 30, f"Conversion took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✅ Multiple missing images handled in {conversion_time:.2f} seconds")
    
    def test_external_font_loading_timeout(self):
        """Test with external fonts that might timeout"""
        font_md = os.path.join(self.temp_dir, "font_test.md")
        
        with open(font_md, 'w') as f:
            f.write("""# Font Loading Test

This tests font loading timeout scenarios.

## Different Font Weights
**Bold text** and *italic text* and ***bold italic***.

## Lists
- Item 1
- Item 2
- Item 3

## Code Blocks
```python
def test_font_loading():
    return "Testing font loading"
```

## Tables
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| More 1   | More 2   | More 3   |
""")
        
        # Test with different font configurations
        test_fonts = [
            "Inter",  # Standard font
            "Roboto", # Another Google Font
            "Arial",  # System font
            "InvalidFont123",  # Invalid font (should fallback)
        ]
        
        for font in test_fonts:
            config = PresentationConfig()
            config.set('font.family', font)
            
            converter = MarkdownToPDF(config=config)
            pdf_file = os.path.join(self.temp_dir, f"font_{font}.pdf")
            
            start_time = time.time()
            converter.convert_to_pdf(font_md, pdf_file, _test_mode=True)
            end_time = time.time()
            
            conversion_time = end_time - start_time
            
            # Should complete in reasonable time
            assert conversion_time < 20, f"Font {font} conversion took too long: {conversion_time:.2f} seconds"
            assert os.path.exists(pdf_file), f"PDF not created for font {font}"
            
            print(f"✅ Font {font} handled in {conversion_time:.2f} seconds")
    
    def test_large_content_with_missing_resources(self):
        """Test large content with missing images and fonts"""
        large_md = os.path.join(self.temp_dir, "large_with_missing.md")
        
        # Create large content with missing resources
        slides = []
        for i in range(10):
            slide_content = f"""# Slide {i+1} - Large Content Test

![Missing image {i}](missing_{i}.jpg)

## Large text section
{'This is a large text section that repeats many times to test rendering performance. ' * 50}

## Code section
```python
def large_function_{i}():
    '''This is a large function with lots of content'''
    data = [{{'item': j, 'value': f'data_{{j}}_{{i}}'}} for j in range(50)]
    return data
```

## Another missing image
![Another missing {i}](https://nonexistent-domain-{i}.com/image.jpg)

## More content
{' '.join([f'Additional content line {j}. ' for j in range(20)])}

## Table with missing image
| Column | Data | Image |
|--------|------|-------|
| Row 1  | Data | ![Missing table image](table_{i}.jpg) |
| Row 2  | Data | ![Another missing](table2_{i}.jpg) |
"""
            slides.append(slide_content)
        
        with open(large_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "large_with_missing.pdf")
        
        converter.convert_to_pdf(large_md, pdf_file, _test_mode=True)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete in reasonable time (under 45 seconds for 10 slides)
        assert conversion_time < 45, f"Large content conversion took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 50000, f"PDF too small for large content: {pdf_size} bytes"
        
        print(f"✅ Large content with missing resources handled in {conversion_time:.2f} seconds")
    
    def test_mixed_valid_invalid_images(self):
        """Test with mix of valid and invalid images"""
        mixed_md = os.path.join(self.temp_dir, "mixed_images.md")
        
        # Create a simple valid image (1x1 PNG)
        valid_image = os.path.join(self.temp_dir, "valid.png")
        # Create a minimal valid PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(valid_image, 'wb') as f:
            f.write(png_data)
        
        with open(mixed_md, 'w') as f:
            f.write(f"""# Mixed Images Test

## Valid Image
![Valid image](valid.png)

## Missing Image
![Missing image](missing.jpg)

## Another Valid Image
![Another valid](valid.png)

## Invalid URL
![Invalid URL](http://nonexistent.com/image.jpg)

## More Content
This slide mixes valid and invalid images to test timeout handling.

- Valid images should load
- Invalid images should be skipped
- PDF generation should not hang

## Code Block
```python
def test_mixed_images():
    return "Testing mixed valid/invalid images"
```

## Final Missing Image
![Final missing](final_missing.png)
""")
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "mixed_images.pdf")
        
        converter.convert_to_pdf(mixed_md, pdf_file, _test_mode=True)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete quickly since we're not waiting for network idle
        assert conversion_time < 15, f"Mixed images conversion took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 5000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✅ Mixed valid/invalid images handled in {conversion_time:.2f} seconds")
    
    def test_rapid_fire_with_missing_resources(self):
        """Test rapid generation of PDFs with missing resources"""
        test_md = os.path.join(self.temp_dir, "rapid_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Rapid Fire Test

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](https://nonexistent.com/image.jpg)

## Content
This is a test slide with missing resources.

## More Content
- Point 1
- Point 2
- Point 3
""")
        
        converter = MarkdownToPDF()
        
        start_time = time.time()
        
        # Generate 5 PDFs rapidly
        for i in range(5):
            pdf_file = os.path.join(self.temp_dir, f"rapid_{i}.pdf")
            converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
            assert os.path.exists(pdf_file), f"PDF {i} not created"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time (under 25 seconds for 5 PDFs)
        assert total_time < 25, f"Rapid fire with missing resources took too long: {total_time:.2f} seconds"
        
        print(f"✅ Rapid fire with missing resources: 5 PDFs in {total_time:.2f} seconds")
    
    def test_timeout_scenarios_stress(self):
        """Test various timeout scenarios that could cause issues"""
        timeout_md = os.path.join(self.temp_dir, "timeout_test.md")
        
        # Create content that could potentially cause timeouts
        timeout_content = """# Timeout Scenarios Test

## Scenario 1: Many missing images
![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](missing3.gif)
![Missing 4](missing4.svg)
![Missing 5](missing5.webp)

## Scenario 2: External URLs (these will timeout)
![External 1](http://httpbin.org/delay/10)
![External 2](https://httpbin.org/delay/5)
![External 3](http://example.com/nonexistent.jpg)

## Scenario 3: Large content blocks
""" + ("This is a very long line of text that repeats many times. " * 100) + """

## Scenario 4: Complex markdown
```python
# Large code block
""" + '\n'.join([f"line_{i} = 'This is line {i}'" for i in range(100)]) + """
```

## Scenario 5: Large table
| Col1 | Col2 | Col3 | Col4 |
|------|------|------|------|
""" + '\n'.join([f"| Row{i} | Data{i} | More{i} | Extra{i} |" for i in range(50)]) + """

## Scenario 6: Mixed content with missing resources
![Final missing](final.jpg)
![Another missing](another.png)
![Last missing](last.svg)
"""
        
        with open(timeout_md, 'w') as f:
            f.write(timeout_content)
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "timeout_test.pdf")
        
        # This should not hang or timeout
        converter.convert_to_pdf(timeout_md, pdf_file, _test_mode=True)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete in reasonable time despite timeout scenarios
        assert conversion_time < 30, f"Timeout scenarios took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 20000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✅ Timeout scenarios handled in {conversion_time:.2f} seconds")


def run_playwright_timeout_tests():
    """Run all Playwright timeout tests"""
    print("⏱️  Running Playwright Timeout Robustness Tests...")
    print("=" * 60)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short", "--timeout=60"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All Playwright timeout tests passed!")
        return True
    else:
        print("❌ Some Playwright timeout tests failed!")
        return False


if __name__ == "__main__":
    success = run_playwright_timeout_tests()
    exit(0 if success else 1)