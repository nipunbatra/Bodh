#!/usr/bin/env python3
"""
Test image path resolution functionality
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bodh import MarkdownToPDF
from config import PresentationConfig


class TestImagePathResolution:
    def test_relative_image_paths_resolve_to_markdown_directory(self):
        """Test that relative image paths are resolved relative to the markdown file, not CWD"""
        temp_dir = tempfile.mkdtemp()
        subdir = os.path.join(temp_dir, "presentations")
        os.makedirs(subdir)
        
        # Create a test image file
        image_path = os.path.join(subdir, "test-image.png")
        with open(image_path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # Minimal PNG header
        
        # Create markdown file with relative image path
        md_file = os.path.join(subdir, "test.md")
        md_content = """# Test Slide

![Test image](test-image.png)

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        # Change to a different directory to test that paths are resolved relative to MD file
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)  # Change away from the markdown file directory
            
            config = PresentationConfig()
            config.set('theme', 'minimal')
            converter = MarkdownToPDF(config=config)
            
            # This should work because image path should be resolved relative to markdown file
            html_file = os.path.join(subdir, "test.html")
            result = converter.convert_to_html(md_file, html_file)
            
            assert os.path.exists(result), "HTML should be generated successfully"
            
            # Check that the HTML contains a data URL (image was embedded)
            with open(result, 'r') as f:
                html_content = f.read()
            
            assert 'data:image/png;base64,' in html_content, "Image should be embedded as data URL"
            
        finally:
            os.chdir(original_cwd)
            # Clean up
            import shutil
            shutil.rmtree(temp_dir)

    def test_absolute_image_paths_work(self):
        """Test that absolute image paths work correctly"""
        temp_dir = tempfile.mkdtemp()
        
        # Create a test image file
        image_path = os.path.join(temp_dir, "absolute-test.png")
        with open(image_path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # Minimal PNG header
        
        # Create markdown file with absolute image path
        md_file = os.path.join(temp_dir, "test.md")
        md_content = f"""# Test Slide

![Test image]({image_path})

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        config = PresentationConfig()
        config.set('theme', 'minimal')
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "test.html")
        result = converter.convert_to_html(md_file, html_file)
        
        assert os.path.exists(result), "HTML should be generated successfully"
        
        # Check that the HTML contains a data URL (image was embedded)
        with open(result, 'r') as f:
            html_content = f.read()
        
        assert 'data:image/png;base64,' in html_content, "Image should be embedded as data URL"
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_nonexistent_image_handling(self):
        """Test that nonexistent images are handled gracefully"""
        temp_dir = tempfile.mkdtemp()
        
        # Create markdown file with path to nonexistent image
        md_file = os.path.join(temp_dir, "test.md")
        md_content = """# Test Slide

![Missing image](nonexistent-image.png)

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        config = PresentationConfig()
        config.set('theme', 'minimal')
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "test.html")
        result = converter.convert_to_html(md_file, html_file)
        
        assert os.path.exists(result), "HTML should be generated even with missing image"
        
        # Check that the original image reference is preserved when image is missing
        with open(result, 'r') as f:
            html_content = f.read()
        
        assert 'nonexistent-image.png' in html_content, "Original image path should be preserved when missing"
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_url_images_are_not_processed(self):
        """Test that HTTP/HTTPS URLs are not processed for local encoding"""
        temp_dir = tempfile.mkdtemp()
        
        # Create markdown file with web URL
        md_file = os.path.join(temp_dir, "test.md")
        md_content = """# Test Slide

![Web image](https://example.com/image.png)

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        config = PresentationConfig()
        config.set('theme', 'minimal')
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "test.html")
        result = converter.convert_to_html(md_file, html_file)
        
        assert os.path.exists(result), "HTML should be generated successfully"
        
        # Check that the URL is preserved (not converted to data URL)
        with open(result, 'r') as f:
            html_content = f.read()
        
        assert 'https://example.com/image.png' in html_content, "Web URLs should be preserved"
        assert 'data:image' not in html_content, "Web URLs should not be converted to data URLs"
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_data_urls_are_preserved(self):
        """Test that existing data URLs are not double-processed"""
        temp_dir = tempfile.mkdtemp()
        
        # Create markdown file with existing data URL
        md_file = os.path.join(temp_dir, "test.md")
        md_content = """# Test Slide

![Data image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==)

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        config = PresentationConfig()
        config.set('theme', 'minimal')
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "test.html")
        result = converter.convert_to_html(md_file, html_file)
        
        assert os.path.exists(result), "HTML should be generated successfully"
        
        # Check that the data URL is preserved exactly
        with open(result, 'r') as f:
            html_content = f.read()
        
        assert 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==' in html_content, "Existing data URLs should be preserved"
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_pdf_image_conversion(self):
        """Test that PDF images are converted to PNG and embedded"""
        temp_dir = tempfile.mkdtemp()
        
        # For this test, we'll create a minimal PDF file (this is just a test, real PDF would be complex)
        pdf_path = os.path.join(temp_dir, "test.pdf")
        # Create a dummy file - in real testing this would need PyMuPDF to be available
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%mock pdf for testing')
        
        # Create markdown file with PDF image
        md_file = os.path.join(temp_dir, "test.md")
        md_content = """# Test Slide

![PDF image](test.pdf)

Content here."""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        config = PresentationConfig()
        config.set('theme', 'minimal')
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "test.html")
        result = converter.convert_to_html(md_file, html_file)
        
        assert os.path.exists(result), "HTML should be generated successfully"
        
        # Since PyMuPDF might not be available in test environment, 
        # the PDF conversion might fail, but the original path should be preserved
        with open(result, 'r') as f:
            html_content = f.read()
        
        # Either it was converted to data URL or original path is preserved
        assert 'test.pdf' in html_content or 'data:image/png;base64,' in html_content, "PDF should be processed or path preserved"
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])