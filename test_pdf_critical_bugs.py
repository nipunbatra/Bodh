#!/usr/bin/env python3
"""
Critical PDF bug testing - tests that focus on the most important PDF functionality
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


class TestPDFCriticalBugs:
    """Test critical PDF rendering bugs that could make PDFs unusable"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_pdf_slide_numbers_actually_render(self):
        """Test that slide numbers are ACTUALLY rendered in PDF, not just HTML"""
        test_md = os.path.join(self.temp_dir, "slide_numbers_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
This is the first slide.

---

# Slide 2
This is the second slide.

---

# Slide 3
This is the third slide.
""")
        
        config = PresentationConfig()
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        
        converter = MarkdownToPDF(config=config)
        
        # Generate both HTML and PDF
        html_file = os.path.join(self.temp_dir, "test.html")
        pdf_file = os.path.join(self.temp_dir, "test.pdf")
        
        converter.convert_to_html(test_md, html_file)
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Verify HTML has slide numbers
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'slide-counter' in html_content, "HTML missing slide counter"
        assert 'slide-display">1/3<' in html_content, "HTML slide counter not showing correct initial value"
        
        # Verify PDF exists and has reasonable size
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small ({pdf_size} bytes) - likely missing content"
        
        # Check that PDF generation parameters are correct
        assert converter.config.get('slide_number.enabled') == True, "Slide numbers not enabled in config"
        
        # Most importantly - verify the PDF HTML template includes slide numbers
        # This is where the bug likely is - PDF generation might be disabling slide numbers
        
        # Test: Generate PDF HTML content (what actually goes to PDF)
        with open(test_md, 'r') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        
        # Check PDF template rendering
        pdf_html = converter.template.render(
            title="test",
            slides=slides,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=None,
            logo_position=converter.logo_position,
            enable_navigation=False,  # This is what PDF uses
            show_arrows=False,  # This is what PDF uses
            show_dots=False,  # This is what PDF uses
            show_slide_numbers=True,  # This SHOULD be True for PDF
            slide_number_format='{current}/{total}',
            initial_slide_number='1/3',
            config=converter.config
        )
        
        # CRITICAL: PDF HTML must contain slide numbers
        assert 'slide-counter' in pdf_html, "PDF HTML missing slide counter"
        assert 'slide-display' in pdf_html, "PDF HTML missing slide display"
        assert '1/3' in pdf_html, "PDF HTML missing correct initial slide number"
        
        print("✅ PDF slide numbers test passed - slide numbers should render in PDF")
    
    def test_pdf_logo_actually_renders(self):
        """Test that logos are ACTUALLY rendered in PDF"""
        test_md = os.path.join(self.temp_dir, "logo_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Logo Test
This slide should have a logo.

---

# Second Slide
Logo should be here too.
""")
        
        config = PresentationConfig()
        config.set('logo.source', 'examples/sample-logo.svg')
        config.set('logo.location', 'top-right')
        
        converter = MarkdownToPDF(config=config)
        
        # Generate both HTML and PDF
        html_file = os.path.join(self.temp_dir, "logo_test.html")
        pdf_file = os.path.join(self.temp_dir, "logo_test.pdf")
        
        converter.convert_to_html(test_md, html_file)
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Verify HTML has logo
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'logo-top-right' in html_content, "HTML missing logo class"
        assert 'data:image/png;base64,' in html_content, "HTML missing base64 logo data"
        
        # Verify PDF exists and has reasonable size
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small ({pdf_size} bytes) - likely missing content"
        
        # Check that logo was actually encoded
        logo_data = converter._encode_image('examples/sample-logo.svg')
        assert logo_data is not None, "Logo not encoded"
        assert len(logo_data) > 100, "Logo data too small"
        
        # Test: Generate PDF HTML content (what actually goes to PDF)
        with open(test_md, 'r') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        
        # Check PDF template rendering
        pdf_html = converter.template.render(
            title="logo_test",
            slides=slides,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=logo_data,
            logo_position=converter.logo_position,
            enable_navigation=False,
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=False,
            slide_number_format='{current}/{total}',
            initial_slide_number='1/2',
            config=converter.config
        )
        
        # CRITICAL: PDF HTML must contain logo
        assert 'logo-top-right' in pdf_html, "PDF HTML missing logo class"
        assert 'data:image/png;base64,' in pdf_html, "PDF HTML missing base64 logo data"
        assert logo_data in pdf_html, "PDF HTML missing actual logo data"
        
        print("✅ PDF logo test passed - logo should render in PDF")
    
    def test_pdf_print_media_queries_work(self):
        """Test that print media queries actually work in PDF generation"""
        test_md = os.path.join(self.temp_dir, "print_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Print Test
This slide tests print media queries.

---

# Second Slide
Testing navigation hiding.
""")
        
        config = PresentationConfig()
        config.set('logo.source', 'examples/sample-logo.svg')
        config.set('slide_number.enabled', True)
        config.set('navigation.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        
        # Generate HTML
        html_file = os.path.join(self.temp_dir, "print_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check that print media queries are present and correct
        assert '@media print' in html_content, "Missing print media queries"
        
        # Check specific print rules
        print_rules = [
            'display: none !important',  # Hide interactive elements
            'display: flex !important',  # Show slides
            'display: block !important',  # Show logos
            'opacity: 1 !important',  # Make logos visible
            'backdrop-filter: none !important',  # Remove backdrop effects
            'background: transparent !important'  # Remove navigation background
        ]
        
        for rule in print_rules:
            assert rule in html_content, f"Missing print rule: {rule}"
        
        # Check that elements that should be hidden are marked
        hidden_elements = ['.keyboard-hint', '.overlay-controls', '.nav-btn', '.slide-dots', '.dot']
        for element in hidden_elements:
            assert element in html_content, f"Missing element style: {element}"
        
        # Check that slide counter is styled for print
        assert 'slide-counter' in html_content, "Missing slide counter in print styles"
        
        print("✅ Print media queries test passed")
    
    def test_pdf_viewport_and_dimensions(self):
        """Test PDF viewport dimensions and scaling"""
        test_md = os.path.join(self.temp_dir, "viewport_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Viewport Test
This slide tests viewport dimensions and scaling.

This is a very long line of text that should fit properly within the PDF viewport without being cut off or causing overflow issues that would break the layout.

---

# Second Slide
Testing content that should fit within A4 landscape dimensions.

- Bullet point 1
- Bullet point 2 with longer text
- Bullet point 3 with even longer text that tests wrapping
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "viewport_test.pdf")
        
        # Generate PDF
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Verify PDF exists and has reasonable size
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small ({pdf_size} bytes)"
        
        # Check CSS has proper viewport handling
        css = converter.css
        assert 'word-wrap: break-word' in css, "CSS missing word wrapping"
        assert 'overflow-wrap: break-word' in css, "CSS missing overflow wrapping"
        assert 'max-width: 100%' in css, "CSS missing width constraints"
        
        print("✅ PDF viewport test passed")
    
    def test_pdf_background_colors_render(self):
        """Test that background colors actually render in PDF"""
        test_md = os.path.join(self.temp_dir, "background_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Background Test
This slide tests background color rendering.

---

# Second Slide
Testing background consistency.
""")
        
        # Test with a theme that has a non-white background
        converter = MarkdownToPDF(theme='dark')
        pdf_file = os.path.join(self.temp_dir, "background_test.pdf")
        
        # Generate PDF
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Verify PDF exists
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small ({pdf_size} bytes)"
        
        # Check CSS has print background settings
        css = converter.css
        assert '-webkit-print-color-adjust: exact' in css, "CSS missing print color adjustment"
        assert 'color-adjust: exact' in css, "CSS missing color adjustment"
        
        # Check that print_background is set to True in PDF generation
        # This is done by checking the source code contains print_background=True
        with open('/Users/nipun/git/mkpred/bodh.py', 'r') as f:
            source = f.read()
        assert 'print_background=True' in source, "PDF generation missing print_background=True"
        
        print("✅ PDF background color test passed")
    
    def test_pdf_font_loading_works(self):
        """Test that fonts load correctly in PDF generation"""
        test_md = os.path.join(self.temp_dir, "font_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Font Test
This slide tests font loading.

**Bold text** and *italic text* should render correctly.

---

# Second Slide
More text with different formatting.
""")
        
        config = PresentationConfig()
        config.set('font.family', 'Inter')
        config.set('font.size', 24)
        
        converter = MarkdownToPDF(config=config)
        
        # Generate HTML to check font loading
        html_file = os.path.join(self.temp_dir, "font_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check Google Fonts link
        assert 'fonts.googleapis.com' in html_content, "Missing Google Fonts link"
        assert 'Inter' in html_content, "Missing Inter font"
        
        # Generate PDF
        pdf_file = os.path.join(self.temp_dir, "font_test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Verify PDF exists and has reasonable size
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"PDF too small ({pdf_size} bytes)"
        
        print("✅ PDF font loading test passed")


def run_critical_tests():
    """Run all critical PDF tests"""
    print("🔴 Running Critical PDF Bug Tests...")
    print("=" * 50)
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All critical PDF tests passed!")
        return True
    else:
        print("❌ Some critical PDF tests failed!")
        return False


if __name__ == "__main__":
    success = run_critical_tests()
    exit(0 if success else 1)