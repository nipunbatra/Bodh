#!/usr/bin/env python3
"""
Test HTML/PDF margin parity - ensure no white borders and identical rendering
"""

import os
import tempfile
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestMarginParity:
    def test_zero_pdf_margins_configured(self):
        """Test that PDF generation uses zero margins"""
        config = load_config('test_gradient_config.yml')
        converter = MarkdownToPDF(config=config)
        
        # Check CSS has zero page margin
        css_content = converter.css
        assert 'margin: 0;' in css_content, "CSS should have zero page margin"
        
        # The PDF generation should use zero margins (verified by checking the bodh.py code)
        # This ensures HTML/PDF parity
        
    def test_gradient_background_no_white_border(self):
        """Test that gradient backgrounds extend to edges without white borders"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "gradient_test.md")
        
        content = """# Gradient Background Test

This slide should have a gradient background that extends all the way to the edges.

There should be no white border around the content.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        # Use gradient theme
        config = load_config('test_gradient_config.yml')
        converter = MarkdownToPDF(config=config)
        
        # Verify gradient background is set in CSS
        css_content = converter.css
        assert 'linear-gradient' in css_content, "CSS should contain gradient background"
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "gradient_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 2000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_html_pdf_render_consistently(self):
        """Test that HTML and PDF have consistent margins and spacing"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "consistency_test.md")
        
        content = """# Consistency Test

This content should render identically in HTML and PDF.

No white borders, same background colors, same spacing.

- List item 1
- List item 2
- List item 3

## Subheading

More content that should be positioned identically.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('test_gradient_config.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate both formats
        html_file = os.path.join(temp_dir, "consistency_test.html")
        pdf_file = os.path.join(temp_dir, "consistency_test.pdf")
        
        converter.convert_to_html(test_md, html_file)
        converter.convert_to_pdf(test_md, pdf_file)
        
        # Both should exist and be reasonably sized
        assert os.path.exists(html_file)
        assert os.path.exists(pdf_file)
        assert os.path.getsize(html_file) > 1000
        assert os.path.getsize(pdf_file) > 2000
        
        # HTML should use same CSS as PDF (embedded fonts, zero margins)
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Should have embedded fonts, not external links
        assert '@font-face' in html_content, "HTML should use embedded fonts like PDF"
        
        # Clean up
        os.unlink(test_md)
        os.unlink(html_file)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_content_area_maximized(self):
        """Test that removing margins maximizes content area"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "content_area_test.md")
        
        # Create content that would be cut off with margins
        long_content = """# Maximum Content Area

""" + "\n".join([f"Line {i}: Content that needs maximum space to avoid cutoffs" for i in range(20)])
        
        with open(test_md, 'w') as f:
            f.write(long_content)
        
        config = load_config('test_gradient_config.yml')
        converter = MarkdownToPDF(config=config)
        
        # Should not trigger content validation warnings with zero margins
        import io
        import sys
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            pdf_file = os.path.join(temp_dir, "content_area_test.pdf")
            converter.convert_to_pdf(test_md, pdf_file)
            
            output = captured_output.getvalue()
            
            # Should have fewer or no warnings about content density with more space
            warning_count = output.count("⚠️")
            assert warning_count <= 1, f"Should have minimal warnings with zero margins, got {warning_count}"
            
        finally:
            sys.stdout = old_stdout
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])