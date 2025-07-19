#!/usr/bin/env python3
"""
Test and fix logo and slide numbering issues found in production PDFs
"""

import os
import tempfile
import shutil
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig, load_config


class TestLogoSlideNumberIssues:
    """Test specific issues with logo display and slide numbering"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_logo_not_showing_issue(self):
        """Test the exact issue where logo is not showing in PDF"""
        # Create the exact same setup as logo-demo
        test_md = os.path.join(self.temp_dir, "logo_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Logo Test

This slide should show a logo in the top-right corner.

---

# Second Slide

The logo should appear on every slide.

---

# Third Slide

Final slide with logo.
""")
        
        # Create a simple SVG logo (copy of sample-logo.svg)
        logo_file = os.path.join(self.temp_dir, "test-logo.svg")
        with open(logo_file, 'w') as f:
            f.write("""<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="100" height="60" rx="8" fill="url(#grad1)"/>
  <text x="50" y="20" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="white">बोध</text>
  <text x="50" y="40" font-family="Arial, sans-serif" font-size="8" text-anchor="middle" fill="white">KNOWLEDGE</text>
</svg>""")
        
        # Create configuration exactly like logo-demo.yml
        config = PresentationConfig()
        config.set('theme', 'modern')
        config.set('font.family', 'Inter')
        config.set('font.size', 20)
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        config.set('slide_number.position', 'bottom-right')
        config.set('logo.source', logo_file)
        config.set('logo.location', 'top-right')
        config.set('logo.size', 100)
        
        converter = MarkdownToPDF(config=config)
        
        # Generate both HTML and PDF to compare
        html_file = os.path.join(self.temp_dir, "logo_test.html")
        pdf_file = os.path.join(self.temp_dir, "logo_test.pdf")
        
        converter.convert_to_html(test_md, html_file)
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Check HTML for logo presence
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Debug: Print key parts of HTML
        print("=== LOGO DEBUG ===")
        print(f"Logo file exists: {os.path.exists(logo_file)}")
        print(f"Logo in HTML: {'logo' in html_content}")
        print(f"Base64 in HTML: {'data:image' in html_content}")
        print(f"Logo position class: {'logo-top-right' in html_content}")
        
        # Verify logo is in HTML
        assert 'logo' in html_content, "Logo element not found in HTML"
        assert 'data:image' in html_content, "Logo image data not embedded in HTML"
        
        # Check files exist
        assert os.path.exists(pdf_file), "PDF not created"
        assert os.path.exists(html_file), "HTML not created"
        
        print("✅ Logo test completed")
    
    def test_slide_numbers_overlapping_issue(self):
        """Test the slide numbers overlapping/messy issue"""
        test_md = os.path.join(self.temp_dir, "slidenum_test.md")
        
        # Create multiple slides to test slide numbering
        slides = []
        for i in range(1, 8):  # 7 slides like in the demo
            slide = f"""# Slide {i}

This is slide number {i} of 7.

## Content Section
- Point 1 for slide {i}
- Point 2 for slide {i}
- Point 3 for slide {i}

### More Content
Some additional content to make the slide substantial.
"""
            slides.append(slide)
        
        with open(test_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        # Test with slide numbering enabled
        config = PresentationConfig()
        config.set('slide_number.enabled', True)
        config.set('slide_number.format', 'current/total')
        config.set('slide_number.position', 'bottom-right')
        
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(self.temp_dir, "slidenum_test.html")
        pdf_file = os.path.join(self.temp_dir, "slidenum_test.pdf")
        
        converter.convert_to_html(test_md, html_file)
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Check HTML for slide numbering
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        print("=== SLIDE NUMBER DEBUG ===")
        print(f"Slide counter in HTML: {'slide-counter' in html_content}")
        print(f"Individual slide numbers: {html_content.count('slide-display')}")
        print(f"Total slides: {html_content.count('class=\"slide\"')}")
        
        # Look for overlapping slide number indicators
        slide_display_count = html_content.count('slide-display')
        slide_count = html_content.count('class="slide"')
        
        print(f"Expected: {slide_count} slide displays, Found: {slide_display_count}")
        
        # In PDF mode, each slide should have its own slide number
        # NOT a single global slide number that gets overwritten
        assert slide_display_count >= slide_count, "Not enough slide number displays for PDF"
        
        assert os.path.exists(pdf_file), "PDF not created"
        print("✅ Slide numbering test completed")
    
    def test_svg_logo_encoding_issue(self):
        """Test if SVG logos are properly encoded for PDF"""
        test_md = os.path.join(self.temp_dir, "svg_test.md")
        with open(test_md, 'w') as f:
            f.write("# SVG Logo Test\n\nThis tests SVG logo encoding.")
        
        # Create SVG logo
        svg_logo = os.path.join(self.temp_dir, "test.svg")
        with open(svg_logo, 'w') as f:
            f.write('<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="60" fill="red"/></svg>')
        
        config = PresentationConfig()
        config.set('logo.source', svg_logo)
        config.set('logo.location', 'top-right')
        
        converter = MarkdownToPDF(config=config)
        
        # Test the image encoding function directly
        encoded = converter._encode_image(svg_logo)
        
        print("=== SVG ENCODING DEBUG ===")
        print(f"SVG file exists: {os.path.exists(svg_logo)}")
        print(f"Encoded result: {encoded}")
        
        assert encoded is not None, "SVG logo not encoded"
        assert 'data' in encoded, "SVG encoding missing data"
        assert 'mime_type' in encoded, "SVG encoding missing MIME type"
        assert encoded['mime_type'] == 'image/svg+xml', "Wrong MIME type for SVG"
        assert len(encoded['data']) > 100, "SVG encoding too short"
        
        print("✅ SVG encoding test completed")


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