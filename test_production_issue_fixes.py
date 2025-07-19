#!/usr/bin/env python3
"""
Test the exact production issues that were reported
"""

import os
import tempfile
import shutil
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestProductionIssueFixes:
    """Test the exact issues reported from production"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_logo_demo_configuration_works(self):
        """Test the exact logo-demo.yml configuration that was failing"""
        # Test with the exact files from the repository
        if not os.path.exists('configs/logo-demo.yml'):
            pytest.skip("logo-demo.yml not found")
        if not os.path.exists('examples/sample-logo.svg'):
            pytest.skip("sample-logo.svg not found")
        
        # Load the exact configuration
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Create test markdown
        test_md = os.path.join(self.temp_dir, "logo_demo_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Logo Demo Test

This slide should show the Bodh logo in the top-right corner.

---

# Slide 2

The logo should appear on every slide.

---

# Slide 3

This is slide 3 of 3. Check the slide numbering.

---

# Slide 4

This is slide 4 of 4.

---

# Slide 5  

This is slide 5 of 5.

---

# Slide 6

This is slide 6 of 6.

---

# Slide 7

Final slide with logo and correct numbering.
""")
        
        # Generate PDF
        pdf_file = os.path.join(self.temp_dir, "logo_demo_test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Generate HTML for verification
        html_file = os.path.join(self.temp_dir, "logo_demo_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Verify logo is embedded correctly
        assert 'data:image/svg+xml;base64,' in html_content, "SVG logo not embedded with correct MIME type"
        
        # Count logo occurrences (should be once per slide)
        logo_count = html_content.count('data:image/svg+xml;base64,')
        slide_count = html_content.count('class="slide"')
        print(f"Logo appears {logo_count} times for {slide_count} slides")
        
        # Logo should appear (may be multiple times due to HTML vs PDF rendering)
        assert logo_count >= slide_count, f"Logo should appear at least once per slide: {logo_count} vs {slide_count}"
        
        # Verify PDF was created
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 50000, f"PDF too small: {pdf_size} bytes"
        
        print("✅ Logo-demo configuration works correctly")
    
    def test_slide_numbers_not_overlapping_7_slides(self):
        """Test that 7 slides don't have overlapping slide numbers (like in the reported issue)"""
        # Create exactly 7 slides like in the production issue
        slides_content = []
        for i in range(1, 8):
            slides_content.append(f"""# Slide {i}

This is slide {i} of 7 slides total.

## Content Section {i}
- Point 1 for slide {i}
- Point 2 for slide {i}  
- Point 3 for slide {i}

### Additional Content
More content to make slide {i} substantial.
""")
        
        test_md = os.path.join(self.temp_dir, "seven_slides_test.md")
        with open(test_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides_content))
        
        # Use the same config as logo-demo
        if os.path.exists('configs/logo-demo.yml'):
            config = load_config('configs/logo-demo.yml')
        else:
            # Fallback config
            from config import PresentationConfig
            config = PresentationConfig()
            config.set('slide_number.enabled', True)
            config.set('slide_number.format', 'current/total')
        
        converter = MarkdownToPDF(config=config)
        
        # Generate the PDF template to check slide numbers
        with open(test_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        
        # Generate PDF template (what gets sent to browser for PDF)
        pdf_html = converter.template.render(
            title="seven_slides_test",
            slides=slides,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=None,
            logo_mime_type='image/png',
            logo_position=converter.logo_position,
            enable_navigation=False,  # PDF mode
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=True,
            slide_number_format='{current}/{total}',
            initial_slide_number='1',
            config=converter.config
        )
        
        # Verify each slide has its own number
        slide_numbers = [
            '>1/7<', '>2/7<', '>3/7<', '>4/7<', 
            '>5/7<', '>6/7<', '>7/7<'
        ]
        
        for i, slide_num in enumerate(slide_numbers, 1):
            assert slide_num in pdf_html, f"Slide {i} number '{slide_num}' not found in PDF"
        
        # Count total slide displays
        slide_display_count = pdf_html.count('slide-display')
        assert slide_display_count == 7, f"Expected 7 individual slide numbers, got {slide_display_count}"
        
        # Generate actual PDF to ensure it works
        pdf_file = os.path.join(self.temp_dir, "seven_slides_test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF not created"
        
        print("✅ 7 slides have individual slide numbers, no overlapping")
    
    def test_logo_and_slide_numbers_together(self):
        """Test that both logo and slide numbers work together without conflicts"""
        test_md = os.path.join(self.temp_dir, "combined_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Combined Test

Testing logo AND slide numbers together.

---

# Slide 2

Both logo and slide number should be visible.

---

# Slide 3

Final test slide.
""")
        
        # Create a test logo
        logo_file = os.path.join(self.temp_dir, "test_logo.svg")
        with open(logo_file, 'w') as f:
            f.write("""<svg width="80" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect width="80" height="50" fill="#4CAF50"/>
  <text x="40" y="30" text-anchor="middle" fill="white" font-size="12">TEST</text>
</svg>""")
        
        from config import PresentationConfig
        config = PresentationConfig()
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        config.set('slide_number.position', 'bottom-right')
        config.set('logo.source', logo_file)
        config.set('logo.location', 'top-right')
        config.set('logo.size', 80)
        
        converter = MarkdownToPDF(config=config)
        
        # Generate PDF
        pdf_file = os.path.join(self.temp_dir, "combined_test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Generate HTML for verification
        html_file = os.path.join(self.temp_dir, "combined_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Verify both logo and slide numbers are present
        assert 'data:image/svg+xml;base64,' in html_content, "Logo not found"
        assert 'slide-counter' in html_content, "Slide numbers not found"
        
        # Verify PDF was created successfully
        assert os.path.exists(pdf_file), "PDF not created"
        
        print("✅ Logo and slide numbers work together correctly")


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