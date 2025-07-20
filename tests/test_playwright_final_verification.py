#!/usr/bin/env python3
"""
Final verification of Playwright timeout fix
Test the most extreme scenarios to ensure no regressions
"""

import os
import tempfile
import shutil
import time
import pytest
from bodh import MarkdownToPDF


class TestPlaywrightFinalVerification:
    """Final verification of timeout fix robustness"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_extreme_missing_image_scenario(self):
        """Test the most extreme missing image scenario"""
        extreme_md = os.path.join(self.temp_dir, "extreme_missing.md")
        
        # Create 50 missing images of various types
        missing_images = []
        for i in range(50):
            missing_images.extend([
                f"![Missing JPG {i}](missing_{i}.jpg)",
                f"![Missing PNG {i}](missing_{i}.png)",
                f"![Missing GIF {i}](missing_{i}.gif)",
                f"![Missing SVG {i}](missing_{i}.svg)",
                f"![Missing WebP {i}](missing_{i}.webp)",
                f"![HTTP URL {i}](http://nonexistent-{i}.com/image.jpg)",
                f"![HTTPS URL {i}](https://nonexistent-{i}.com/image.png)",
                f"![Invalid URL {i}](not-a-url-{i})",
                f"![Relative {i}](../missing_{i}.jpg)",
                f"![Absolute {i}](/nonexistent/missing_{i}.png)",
            ])
        
        with open(extreme_md, 'w') as f:
            f.write(f"""# Extreme Missing Images Test

This slide contains 500 missing images to test the absolute worst-case scenario.

{chr(10).join(missing_images)}

## Content After Images
This content should still render correctly despite the massive number of missing images above.

### Subsection
More content to ensure the slide is substantial.

## List
- Point 1
- Point 2
- Point 3

## Code
```python
def test_extreme_scenario():
    return "This should work despite missing images"
```

## Final Missing Images
![Final 1](final1.jpg)
![Final 2](final2.png)
![Final 3](final3.gif)
""")
        
        # This is the ultimate stress test
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "extreme_missing.pdf")
        
        converter.convert_to_pdf(extreme_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete quickly despite 500+ missing images
        assert conversion_time < 15, f"Extreme scenario took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 15000, f"PDF too small: {pdf_size} bytes"
        
        print(f"✅ Extreme scenario (500+ missing images): {conversion_time:.2f} seconds")
    
    def test_timeout_boundary_conditions(self):
        """Test boundary conditions around timeout values"""
        boundary_md = os.path.join(self.temp_dir, "boundary_test.md")
        
        with open(boundary_md, 'w') as f:
            f.write("""# Timeout Boundary Test

Testing boundary conditions for timeout handling.

## Missing Images
![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](missing3.gif)

## Large Content
""" + "This is a large content block that repeats many times to test memory and timeout boundaries. " * 200 + """

## Code Block
```python
# Large code block to test rendering boundaries
""" + '\n'.join([f"def function_{i}(): return 'test_{i}'" for i in range(100)]) + """
```

## More Missing Images
![Missing 4](missing4.svg)
![Missing 5](missing5.webp)
![Missing 6](http://nonexistent.com/image.jpg)
""")
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "boundary_test.pdf")
        
        converter.convert_to_pdf(boundary_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should complete within reasonable time
        assert conversion_time < 10, f"Boundary test took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        print(f"✅ Boundary conditions handled in {conversion_time:.2f} seconds")
    
    def test_concurrent_pdf_generation(self):
        """Test that multiple PDFs can be generated without interference"""
        test_md = os.path.join(self.temp_dir, "concurrent_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Concurrent Test

Testing concurrent PDF generation.

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)

## Content
This is a test slide for concurrent generation.
""")
        
        # Test sequential generation (simulating concurrent usage)
        start_time = time.time()
        
        for i in range(3):
            converter = MarkdownToPDF()  # New instance each time
            pdf_file = os.path.join(self.temp_dir, f"concurrent_{i}.pdf")
            
            converter.convert_to_pdf(test_md, pdf_file)
            
            assert os.path.exists(pdf_file), f"PDF {i} not created"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete all 3 PDFs quickly
        assert total_time < 15, f"Concurrent generation took too long: {total_time:.2f} seconds"
        
        print(f"✅ Concurrent generation: 3 PDFs in {total_time:.2f} seconds")
    
    def test_memory_and_timeout_interaction(self):
        """Test interaction between memory usage and timeout handling"""
        memory_md = os.path.join(self.temp_dir, "memory_timeout.md")
        
        # Create memory-intensive content with missing images
        slides = []
        for i in range(5):
            slide_content = f"""# Memory + Timeout Test Slide {i+1}

![Missing {i}](missing_{i}.jpg)

## Large Content Block {i+1}
{("This is a large content block that should consume memory while also testing timeout scenarios. " * 100)}

## Code Block {i+1}
```python
# Large code block for slide {i+1}
{chr(10).join([f"data_{i}_{j} = 'large_string_content_' * 100" for j in range(50)])}
```

## More Missing Images {i+1}
![Missing HTTP {i}](http://nonexistent-{i}.com/image.jpg)
![Missing HTTPS {i}](https://nonexistent-{i}.com/image.png)
![Missing Local {i}](missing_local_{i}.gif)

## Table {i+1}
| Column A | Column B | Column C | Column D |
|----------|----------|----------|----------|
{chr(10).join([f"| Data {i}_{j} | Value {i}_{j} | More {i}_{j} | Extra {i}_{j} |" for j in range(20)])}
"""
            slides.append(slide_content)
        
        with open(memory_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "memory_timeout.pdf")
        
        converter.convert_to_pdf(memory_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # Should handle memory + timeout scenarios
        assert conversion_time < 20, f"Memory+timeout test took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 50000, f"PDF too small for memory test: {pdf_size} bytes"
        
        print(f"✅ Memory + timeout interaction: {conversion_time:.2f} seconds, {pdf_size} bytes")
    
    def test_regression_prevention(self):
        """Test to prevent regression to original timeout issues"""
        regression_md = os.path.join(self.temp_dir, "regression_test.md")
        
        # This is the exact pattern that was causing 30+ second timeouts
        with open(regression_md, 'w') as f:
            f.write("""# Regression Prevention Test

This tests the exact scenario that was causing timeouts before the fix.

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](missing3.gif)
![Missing 4](missing4.svg)
![Missing 5](missing5.webp)
![Missing 6](http://nonexistent.com/image.jpg)
![Missing 7](../missing7.png)
![Missing 8](./missing8.jpg)
![Missing 9](/absolute/missing9.png)
![Missing 10](~/missing10.jpg)

---

# More Missing Images

![Missing 11](missing11.jpg)
![Missing 12](missing12.png)
![Missing 13](missing13.gif)
![Missing 14](missing14.svg)
![Missing 15](missing15.webp)
![Missing 16](http://nonexistent2.com/image.jpg)
![Missing 17](../missing17.png)
![Missing 18](./missing18.jpg)
![Missing 19](/absolute/missing19.png)
![Missing 20](~/missing20.jpg)

---

# Even More Missing Images

![Missing 21](missing21.jpg)
![Missing 22](missing22.png)
![Missing 23](missing23.gif)
![Missing 24](missing24.svg)
![Missing 25](missing25.webp)
![Missing 26](http://nonexistent3.com/image.jpg)
![Missing 27](../missing27.png)
![Missing 28](./missing28.jpg)
![Missing 29](/absolute/missing29.png)
![Missing 30](~/missing30.jpg)
""")
        
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "regression_test.pdf")
        
        converter.convert_to_pdf(regression_md, pdf_file)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        # This MUST complete quickly (was taking 30+ seconds before)
        assert conversion_time < 8, f"REGRESSION! Conversion took too long: {conversion_time:.2f} seconds"
        
        assert os.path.exists(pdf_file), "PDF not created"
        
        print(f"✅ Regression prevention: {conversion_time:.2f} seconds (was 30+ seconds before)")


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