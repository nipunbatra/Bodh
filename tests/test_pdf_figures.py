#!/usr/bin/env python3
"""
Test PDF figure conversion functionality
"""

import os
import tempfile
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestPDFFigures:
    def test_pdf_figure_conversion_works(self):
        """Test that PDF figures can be converted and embedded"""
        converter = MarkdownToPDF()
        
        # Test with one of the gradient descent PDF figures
        pdf_figure_path = "/Users/nipun/git/mkpred/gradient-descent/gd-lr-0.1.pdf"
        
        if os.path.exists(pdf_figure_path):
            result = converter._encode_image(pdf_figure_path)
            
            assert result is not None, "PDF conversion should work"
            assert 'data' in result, "Should have data field"
            assert 'mime_type' in result, "Should have mime_type field"
            assert result['mime_type'] == 'image/png', "Should convert PDF to PNG"
            assert len(result['data']) > 1000, "Should have substantial image data"
        else:
            pytest.skip("PDF figure not available for testing")

    def test_gradient_descent_presentation_generation(self):
        """Test that the full gradient descent presentation generates successfully"""
        gradient_md = "/Users/nipun/git/mkpred/gradient-descent/gradient-descent.md"
        gradient_config = "/Users/nipun/git/mkpred/gradient-descent/gradient-descent-config.yml"
        
        if os.path.exists(gradient_md) and os.path.exists(gradient_config):
            config = load_config(gradient_config)
            converter = MarkdownToPDF(config=config)
            
            temp_dir = tempfile.mkdtemp()
            pdf_output = os.path.join(temp_dir, "test_gradient.pdf")
            
            # Should generate without errors
            result = converter.convert_to_pdf(gradient_md, pdf_output)
            
            assert os.path.exists(result), "PDF should be generated"
            assert os.path.getsize(result) > 50000, "PDF should be substantial (contains figures)"
            
            # Clean up
            os.unlink(pdf_output)
            os.rmdir(temp_dir)
        else:
            pytest.skip("Gradient descent files not available for testing")

    def test_hindi_font_rendering(self):
        """Test that Hindi/Devanagari fonts render correctly"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "hindi_test.md")
        
        content = """# बोध Test

Mixed content:
- English: Knowledge
- हिंदी: ज्ञान
- Math: $\\alpha + \\beta$
"""
        
        with open(test_md, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Test with Devanagari font
        config_data = {
            'theme': 'minimal',
            'font': {'family': 'Noto Sans Devanagari', 'size': 20}
        }
        
        from config import PresentationConfig
        config = PresentationConfig()
        for key, value in config_data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        
        # Should have Devanagari font support
        assert 'Noto Sans Devanagari' in converter.font_manager.google_fonts
        
        pdf_file = os.path.join(temp_dir, "hindi_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 2000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_improved_typography_spacing(self):
        """Test that improved typography provides better spacing"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "typography_test.md")
        
        content = """# Main Title

## Section Header

### Subsection

Regular paragraph text that should have good spacing.

- List item 1
- List item 2

More content after the list.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('gradient-descent/gradient-descent-config.yml')
        converter = MarkdownToPDF(config=config)
        
        # Check that CSS has improved typography
        css_content = converter.css
        
        # Should have smaller title fonts
        assert 'font-size: 2.8em' in css_content, "H1 should use improved font size"
        assert 'font-size: 2.2em' in css_content, "H2 should use improved font size"
        
        # Should have reduced top padding
        assert 'padding-top: 1rem' in css_content, "Should have reduced padding"
        
        pdf_file = os.path.join(temp_dir, "typography_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])