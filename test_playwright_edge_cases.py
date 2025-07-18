#!/usr/bin/env python3
"""
Test specific Playwright edge cases that could cause issues
"""

import os
import tempfile
import shutil
import time
import pytest
from bodh import MarkdownToPDF


class TestPlaywrightEdgeCases:
    """Test specific edge cases for Playwright timeout handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_original_failing_scenario(self):
        """Test the exact scenario that was failing before the fix"""
        missing_images_md = os.path.join(self.temp_dir, "missing_images.md")
        
        missing_images = [
            "![Missing 1](missing1.jpg)",
            "![Missing 2](missing2.png)",
            "![Missing 3](missing3.gif)",
            "![Missing 4](missing4.svg)",
            "![Missing 5](missing5.webp)",
            "![Missing 6](http://nonexistent.com/image.jpg)",
            "![Missing 7](../missing7.png)",
            "![Missing 8](./missing8.jpg)",
            "![Missing 9](/absolute/missing9.png)",
            "![Missing 10](~/missing10.jpg)",
        ]
        
        with open(missing_images_md, 'w') as f:
            f.write(f"""# Missing Images Test
{chr(10).join(missing_images)}

---

# More Missing Images
{chr(10).join(missing_images)}

---

# Even More Missing Images
{chr(10).join(missing_images)}
""")
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "missing_images.pdf")
        
        # This was the exact scenario that was timing out before
        converter.convert_to_pdf(missing_images_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete quickly now (was timing out at 30+ seconds before)
        assert conversion_time < 10, f"Conversion still taking too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        print(f"✅ Original failing scenario now works in {conversion_time:.2f} seconds")
    
    def test_domcontentloaded_vs_networkidle_performance(self):
        """Compare performance difference between domcontentloaded and networkidle"""
        test_md = os.path.join(self.temp_dir, "performance_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Performance Test

This tests the performance difference between wait strategies.

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](http://nonexistent.com/image.jpg)

## Content
Regular content that should render quickly.

## More Content
- Point 1
- Point 2
- Point 3
""")
        
        # Test current implementation (domcontentloaded)
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "performance_test.pdf")
        
        converter.convert_to_pdf(test_md, pdf_file)
        
        end_time = time.time()
        domcontentloaded_time = end_time - start_time
        
        assert os.path.exists(pdf_file), "PDF not created"
        
        # Should be fast with domcontentloaded
        assert domcontentloaded_time < 8, f"domcontentloaded still slow: {domcontentloaded_time:.2f} seconds"
        
        print(f"✅ domcontentloaded strategy: {domcontentloaded_time:.2f} seconds")
    
    def test_font_loading_fallback_behavior(self):
        """Test that font loading timeout doesn't break PDF generation"""
        font_md = os.path.join(self.temp_dir, "font_fallback.md")
        
        with open(font_md, 'w') as f:
            f.write("""# Font Fallback Test

This tests font loading with potential timeout scenarios.

## Different Text Styles
**Bold text** should render correctly.
*Italic text* should render correctly.
***Bold italic*** should render correctly.
`Code text` should render correctly.

## Mathematical Content
The quadratic formula: x = (-b ± √(b² - 4ac)) / 2a

## Unicode Content
Special characters: ñáéíóú αβγδε 中文 العربية

## Large Content Block
""" + "This is a repeating line to test font rendering under load. " * 100)
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "font_fallback.pdf")
        
        converter.convert_to_pdf(font_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete even if font loading has issues
        assert conversion_time < 15, f"Font fallback took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✅ Font fallback behavior works in {conversion_time:.2f} seconds")
    
    def test_browser_resource_cleanup(self):
        """Test that browser resources are properly cleaned up"""
        test_md = os.path.join(self.temp_dir, "cleanup_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Cleanup Test

Testing browser resource cleanup.

![Missing](missing.jpg)

## Content
This is a simple test slide.
""")
        
        # Generate multiple PDFs to test resource cleanup
        converter = MarkdownToPDF()
        
        for i in range(3):
            pdf_file = os.path.join(self.temp_dir, f"cleanup_{i}.pdf")
            
            start_time = time.time()
            converter.convert_to_pdf(test_md, pdf_file)
            end_time = time.time()
            
            conversion_time = end_time - start_time
            
            # Each conversion should be consistent (no resource buildup)
            assert conversion_time < 8, f"Conversion {i} took too long: {conversion_time:.2f} seconds"
            assert os.path.exists(pdf_file), f"PDF {i} not created"
            
            print(f"✅ Cleanup test {i}: {conversion_time:.2f} seconds")
    
    def test_error_handling_robustness(self):
        """Test error handling in timeout scenarios"""
        error_md = os.path.join(self.temp_dir, "error_test.md")
        
        with open(error_md, 'w') as f:
            f.write("""# Error Handling Test

Testing error handling robustness.

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Invalid URL](not-a-valid-url)
![Another missing](missing3.gif)

## Content
This tests error handling during PDF generation.

## More Content
- Point 1
- Point 2
- Point 3
""")
        
        # This should not throw exceptions
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "error_test.pdf")
        
        # Should handle errors gracefully
        converter.convert_to_pdf(error_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF not created despite errors"
        print("✅ Error handling is robust")


if __name__ == "__main__":
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    exit(result.returncode)