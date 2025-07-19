#!/usr/bin/env python3
"""
Test that slide positioning bug is fixed - slide numbers should not overlap
"""

import os
import tempfile
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestSlidePositioningFix:
    def test_slide_nav_positioning_in_print_css(self):
        """Test that slide-nav has correct positioning in print CSS"""
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Check that print CSS has absolute positioning
        css_content = converter.css
        
        # Should have print media query with absolute positioning
        assert '@media print' in css_content
        assert 'position: absolute !important' in css_content
        assert 'top: 1rem !important' in css_content
        
        # Ensure it's within the print media query
        print_css_start = css_content.find('@media print')
        print_css_end = css_content.find('}', css_content.rfind('position: absolute !important'))
        
        print_css_section = css_content[print_css_start:print_css_end]
        assert 'position: absolute !important' in print_css_section
        assert 'top: 1rem !important' in print_css_section
    
    def test_slide_numbers_have_unique_positions_in_html(self):
        """Test that each slide number appears in its own slide container"""
        # Create test markdown
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "positioning_test.md")
        
        with open(test_md, 'w') as f:
            f.write("""# Slide 1
Content 1

---

# Slide 2  
Content 2

---

# Slide 3
Content 3
""")
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate HTML for PDF (not interactive)
        with open(test_md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        slides = converter.parse_markdown_slides(md_content)
        
        # Get logo data  
        logo_data = None
        logo_mime_type = 'image/png'
        if converter.logo_path and os.path.exists(converter.logo_path):
            logo_result = converter._encode_image(converter.logo_path)
            if logo_result:
                logo_data = logo_result['data']
                logo_mime_type = logo_result['mime_type']
        
        html_content = converter.template.render(
            title="positioning_test",
            slides=slides,
            css=converter.css,
            font_family=converter.font_family,
            logo_data=logo_data,
            logo_mime_type=logo_mime_type,
            logo_position=converter.logo_position,
            enable_navigation=False,  # PDF mode
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=True,
            slide_number_format='{current}/{total}',
            initial_slide_number='1',
            config=converter.config
        )
        
        # Verify each slide has its own slide-nav container
        assert html_content.count('<div class="slide-nav">') == 3
        assert html_content.count('1/3') == 1
        assert html_content.count('2/3') == 1
        assert html_content.count('3/3') == 1
        
        # Verify each slide number is within its own slide container
        slide_divs = html_content.split('<div class="slide">')
        
        # First element before any slide div is just the header
        assert len(slide_divs) == 4  # header + 3 slides
        
        # Check each slide has its expected number
        assert '1/3' in slide_divs[1]  # First slide
        assert '2/3' in slide_divs[2]  # Second slide  
        assert '3/3' in slide_divs[3]  # Third slide
        
        # Ensure numbers don't bleed between slides
        assert '2/3' not in slide_divs[1]
        assert '3/3' not in slide_divs[1]
        assert '1/3' not in slide_divs[2]
        assert '3/3' not in slide_divs[2]
        assert '1/3' not in slide_divs[3]
        assert '2/3' not in slide_divs[3]
        
        # Clean up
        os.unlink(test_md)
        os.rmdir(temp_dir)

    def test_slide_nav_css_properties_in_print_mode(self):
        """Test that slide-nav CSS has correct properties for PDF rendering"""
        config = load_config('configs/logo-demo.yml') 
        converter = MarkdownToPDF(config=config)
        
        css_content = converter.css
        
        # Find the print media query section
        print_start = css_content.find('@media print')
        assert print_start != -1, "Print media query not found"
        
        # Find the end of the print media query
        print_end = css_content.find('}', css_content.rfind('}', print_start, len(css_content)))
        print_section = css_content[print_start:print_end]
        
        # Verify positioning properties are in the print section
        assert 'position: absolute !important' in print_section
        assert 'top: 1rem !important' in print_section  
        assert 'right: 1rem !important' in print_section
        assert 'background: transparent !important' in print_section
        assert 'z-index: 1000 !important' in print_section


if __name__ == "__main__":
    pytest.main([__file__, "-v"])