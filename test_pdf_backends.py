#!/usr/bin/env python3
"""
Test different PDF generation backends
Compare Playwright vs WeasyPrint vs xhtml2pdf
"""

import os
import tempfile
import shutil
import time
import pytest
from bodh import MarkdownToPDF


class TestPDFBackends:
    """Test different PDF generation backends"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_weasyprint_backend(self):
        """Test WeasyPrint backend performance and quality"""
        test_md = os.path.join(self.temp_dir, "weasyprint_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# WeasyPrint Backend Test

Testing WeasyPrint as PDF backend.

![Missing image](missing.jpg)

## Performance Test
This tests WeasyPrint performance with missing images.

- Point 1
- Point 2
- Point 3

## Code Block
```python
def test_weasyprint():
    return "WeasyPrint backend test"
```

## Table
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
""")
        
        # Test with missing images (should be fast)
        start_time = time.time()
        
        # Force WeasyPrint backend by monkey-patching
        import bodh
        original_backend = bodh.PDF_BACKEND
        bodh.PDF_BACKEND = 'weasyprint'
        
        try:
            converter = MarkdownToPDF()
            pdf_file = os.path.join(self.temp_dir, "weasyprint_test.pdf")
            
            converter.convert_to_pdf(test_md, pdf_file)
            
            end_time = time.time()
            conversion_time = end_time - start_time
            
            assert os.path.exists(pdf_file), "WeasyPrint PDF not created"
            pdf_size = os.path.getsize(pdf_file)
            
            print(f"✅ WeasyPrint: {conversion_time:.2f} seconds, {pdf_size} bytes")
            
            # WeasyPrint should be fast with missing images
            assert conversion_time < 5, f"WeasyPrint took too long: {conversion_time:.2f} seconds"
            
            return conversion_time, pdf_size
            
        finally:
            bodh.PDF_BACKEND = original_backend
    
    def test_playwright_backend(self):
        """Test Playwright backend performance"""
        test_md = os.path.join(self.temp_dir, "playwright_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Playwright Backend Test

Testing Playwright as PDF backend.

![Missing image](missing.jpg)

## Performance Test
This tests Playwright performance with missing images.

- Point 1
- Point 2
- Point 3

## Code Block
```python
def test_playwright():
    return "Playwright backend test"
```

## Table
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
""")
        
        start_time = time.time()
        
        # Force Playwright backend
        import bodh
        original_backend = bodh.PDF_BACKEND
        bodh.PDF_BACKEND = 'playwright'
        
        try:
            converter = MarkdownToPDF()
            pdf_file = os.path.join(self.temp_dir, "playwright_test.pdf")
            
            converter.convert_to_pdf(test_md, pdf_file)
            
            end_time = time.time()
            conversion_time = end_time - start_time
            
            assert os.path.exists(pdf_file), "Playwright PDF not created"
            pdf_size = os.path.getsize(pdf_file)
            
            print(f"✅ Playwright: {conversion_time:.2f} seconds, {pdf_size} bytes")
            
            return conversion_time, pdf_size
            
        finally:
            bodh.PDF_BACKEND = original_backend
    
    def test_backend_comparison(self):
        """Compare different backends on same content"""
        test_md = os.path.join(self.temp_dir, "comparison_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Backend Comparison Test

Testing different PDF backends on identical content.

![Missing 1](missing1.jpg)
![Missing 2](missing2.png)
![Missing 3](http://nonexistent.com/image.jpg)

## Content
This is standard content for comparison.

**Bold text** and *italic text*.

## List
- Item 1
- Item 2
- Item 3

## Code
```python
def backend_comparison():
    return "Comparing PDF backends"
```

## Table
| Backend | Speed | Quality |
|---------|-------|---------|
| Playwright | Medium | High |
| WeasyPrint | Fast | Medium |
| xhtml2pdf | Fast | Low |
""")
        
        results = {}
        
        # Test each backend
        backends = ['playwright', 'weasyprint']
        
        for backend in backends:
            import bodh
            original_backend = bodh.PDF_BACKEND
            bodh.PDF_BACKEND = backend
            
            try:
                start_time = time.time()
                
                converter = MarkdownToPDF()
                pdf_file = os.path.join(self.temp_dir, f"comparison_{backend}.pdf")
                
                converter.convert_to_pdf(test_md, pdf_file)
                
                end_time = time.time()
                conversion_time = end_time - start_time
                
                assert os.path.exists(pdf_file), f"{backend} PDF not created"
                pdf_size = os.path.getsize(pdf_file)
                
                results[backend] = {
                    'time': conversion_time,
                    'size': pdf_size,
                    'exists': True
                }
                
                print(f"✅ {backend}: {conversion_time:.2f}s, {pdf_size} bytes")
                
            except Exception as e:
                results[backend] = {
                    'time': None,
                    'size': None,
                    'exists': False,
                    'error': str(e)
                }
                print(f"❌ {backend}: {e}")
                
            finally:
                bodh.PDF_BACKEND = original_backend
        
        return results
    
    def test_missing_images_backend_comparison(self):
        """Compare backend performance with many missing images"""
        missing_md = os.path.join(self.temp_dir, "missing_comparison.md")
        
        # Create content with many missing images
        missing_images = [f"![Missing {i}](missing_{i}.jpg)" for i in range(20)]
        
        with open(missing_md, 'w') as f:
            f.write(f"""# Missing Images Backend Comparison

{chr(10).join(missing_images)}

## Content
This tests backend performance with many missing images.
""")
        
        results = {}
        backends = ['playwright', 'weasyprint']
        
        for backend in backends:
            import bodh
            original_backend = bodh.PDF_BACKEND
            bodh.PDF_BACKEND = backend
            
            try:
                start_time = time.time()
                
                converter = MarkdownToPDF()
                pdf_file = os.path.join(self.temp_dir, f"missing_{backend}.pdf")
                
                converter.convert_to_pdf(missing_md, pdf_file)
                
                end_time = time.time()
                conversion_time = end_time - start_time
                
                results[backend] = conversion_time
                
                print(f"✅ {backend} with missing images: {conversion_time:.2f}s")
                
            except Exception as e:
                print(f"❌ {backend} failed: {e}")
                results[backend] = None
                
            finally:
                bodh.PDF_BACKEND = original_backend
        
        return results


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