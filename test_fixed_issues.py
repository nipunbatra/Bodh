#!/usr/bin/env python3
"""
Test the fixed logo and slide numbering issues
"""

import os
import tempfile
import shutil
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig


class TestFixedIssues:
    """Test that the issues are actually fixed"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_svg_logo_displays_correctly(self):
        """Test that SVG logos display with correct MIME type"""
        test_md = os.path.join(self.temp_dir, "logo_test.md")
        with open(test_md, 'w') as f:
            f.write("# Logo Test\n\nThis slide should show an SVG logo.")
        
        # Create SVG logo
        svg_logo = os.path.join(self.temp_dir, "test.svg")
        with open(svg_logo, 'w') as f:
            f.write("""<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="60" fill="blue"/>
  <text x="50" y="35" text-anchor="middle" fill="white" font-size="14">LOGO</text>
</svg>""")
        
        config = PresentationConfig()
        config.set('logo.source', svg_logo)
        config.set('logo.location', 'top-right')
        
        converter = MarkdownToPDF(config=config)
        
        # Test PDF generation
        pdf_file = os.path.join(self.temp_dir, "logo_test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Test HTML generation to verify MIME type
        html_file = os.path.join(self.temp_dir, "logo_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Verify SVG is embedded with correct MIME type
        assert 'data:image/svg+xml;base64,' in html_content, "SVG logo not embedded with correct MIME type"
        assert os.path.exists(pdf_file), "PDF not created"
        
        print("✅ SVG logo displays correctly with proper MIME type")
    
    def test_png_logo_displays_correctly(self):
        """Test that PNG logos still work correctly"""
        test_md = os.path.join(self.temp_dir, "png_test.md")
        with open(test_md, 'w') as f:
            f.write("# PNG Logo Test\n\nThis slide should show a PNG logo.")
        
        # Create minimal PNG (1x1 pixel)
        png_logo = os.path.join(self.temp_dir, "test.png")
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(png_logo, 'wb') as f:
            f.write(png_data)
        
        config = PresentationConfig()
        config.set('logo.source', png_logo)
        config.set('logo.location', 'top-left')
        
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(self.temp_dir, "png_test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Verify PNG is embedded with correct MIME type
        assert 'data:image/png;base64,' in html_content, "PNG logo not embedded with correct MIME type"
        
        print("✅ PNG logo displays correctly")
    
    def test_pdf_slide_numbers_individual(self):
        """Test that PDF has individual slide numbers, not overlapping"""
        test_md = os.path.join(self.temp_dir, "slidenum_test.md")
        
        # Create 5 slides
        slides = []
        for i in range(1, 6):
            slides.append(f"# Slide {i}\n\nContent for slide {i}")
        
        with open(test_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        config = PresentationConfig()
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        
        converter = MarkdownToPDF(config=config)
        
        # Generate the PDF template HTML (this is what gets converted to PDF)
        with open(test_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        slides_parsed = converter.parse_markdown_slides(md_content)
        
        # Generate PDF template (navigation disabled for PDF)
        pdf_html = converter.template.render(
            title="slidenum_test",
            slides=slides_parsed,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=None,
            logo_mime_type='image/png',
            logo_position=converter.logo_position,
            enable_navigation=False,  # Key: PDF disables navigation
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=True,
            slide_number_format='{current}/{total}',
            initial_slide_number='1',
            config=converter.config
        )
        
        # Verify individual slide numbers
        slide_count = pdf_html.count('class="slide"')
        slide_display_count = pdf_html.count('slide-display')
        
        print(f"Slides: {slide_count}, Slide displays: {slide_display_count}")
        
        # Each slide should have its own slide number
        assert slide_count == 5, f"Expected 5 slides, got {slide_count}"
        assert slide_display_count == 5, f"Expected 5 slide displays, got {slide_display_count}"
        
        # Verify specific slide numbers
        assert '>1/5<' in pdf_html, "First slide number not found"
        assert '>2/5<' in pdf_html, "Second slide number not found" 
        assert '>3/5<' in pdf_html, "Third slide number not found"
        assert '>4/5<' in pdf_html, "Fourth slide number not found"
        assert '>5/5<' in pdf_html, "Fifth slide number not found"
        
        print("✅ PDF slide numbers are individual, not overlapping")
    
    def test_html_vs_pdf_slide_numbering(self):
        """Test that HTML and PDF have different slide numbering approaches"""
        test_md = os.path.join(self.temp_dir, "comparison_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
Content 1

---

# Slide 2
Content 2

---

# Slide 3
Content 3""")
        
        config = PresentationConfig()
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        
        converter = MarkdownToPDF(config=config)
        
        # Generate HTML (with navigation)
        html_file = os.path.join(self.temp_dir, "test.html")
        converter.convert_to_html(test_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Generate PDF
        pdf_file = os.path.join(self.temp_dir, "test.pdf")
        converter.convert_to_pdf(test_md, pdf_file)
        
        # HTML should have navigation (single dynamic slide number)
        html_slide_displays = html_content.count('slide-display')
        html_has_navigation = 'has-navigation' in html_content
        
        print(f"HTML: {html_slide_displays} slide displays, navigation: {html_has_navigation}")
        
        # HTML should have 1 dynamic slide display + navigation
        assert html_has_navigation, "HTML should have navigation"
        assert html_slide_displays <= 2, "HTML should have minimal slide displays (dynamic)"
        
        # PDF file should exist (indicating PDF generation worked)
        assert os.path.exists(pdf_file), "PDF not created"
        
        print("✅ HTML and PDF have different slide numbering approaches")


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