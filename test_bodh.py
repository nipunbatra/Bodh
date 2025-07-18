#!/usr/bin/env python3
"""
Comprehensive test suite for Bodh presentation generator
Tests all major functionality to prevent regressions
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path
from bodh import MarkdownToPDF
from config import PresentationConfig


class TestBodhCore:
    """Test core functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_md = os.path.join(self.temp_dir, "test.md")
        
        # Create a simple test markdown file
        with open(self.test_md, 'w') as f:
            f.write("""# Test Presentation

## Slide 1
This is a test slide.

---

## Slide 2
This is another slide with:
- Bullet points
- **Bold text**
- *Italic text*

---

# Thank You
""")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_basic_markdown_parsing(self):
        """Test basic markdown to slides parsing"""
        converter = MarkdownToPDF()
        with open(self.test_md, 'r') as f:
            content = f.read()
        
        slides = converter.parse_markdown_slides(content)
        assert len(slides) == 3, f"Expected 3 slides, got {len(slides)}"
        assert "Test Presentation" in slides[0]
        assert "Slide 1" in slides[0]
        assert "Slide 2" in slides[1]
        assert "Thank You" in slides[2]
    
    def test_html_generation(self):
        """Test HTML output generation"""
        converter = MarkdownToPDF()
        output_file = os.path.join(self.temp_dir, "test.html")
        
        converter.convert_to_html(self.test_md, output_file)
        
        assert os.path.exists(output_file), "HTML file should be created"
        
        with open(output_file, 'r') as f:
            html_content = f.read()
        
        # Check for essential HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "Test Presentation" in html_content
        assert "slide-content" in html_content
        assert "justify-content: flex-start" in html_content  # Fixed layout
    
    def test_pdf_generation(self):
        """Test PDF output generation"""
        converter = MarkdownToPDF()
        output_file = os.path.join(self.temp_dir, "test.pdf")
        
        converter.convert_to_pdf(self.test_md, output_file)
        
        assert os.path.exists(output_file), "PDF file should be created"
        assert os.path.getsize(output_file) > 1000, "PDF should have content"


class TestConfiguration:
    """Test configuration system"""
    
    def test_default_config_loading(self):
        """Test loading default configuration"""
        config = PresentationConfig()
        
        assert config.get('theme') == 'modern'
        assert config.get('font.family') == 'Inter'
        assert config.get('font.size') == 20
        assert config.get('slide_number.enabled') == True
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = PresentationConfig()
        
        # Test valid config
        issues = config.validate()
        assert len(issues) == 0, f"Default config should be valid, got issues: {issues}"
        
        # Test invalid theme
        config.set('theme', 'invalid_theme')
        issues = config.validate()
        assert len(issues) > 0, "Invalid theme should cause validation error"
    
    def test_slide_number_formats(self):
        """Test different slide number formats"""
        config = PresentationConfig()
        
        # Test current/total format
        config.set('slide_number.format', 'current/total')
        format_str = config.get_slide_number_format()
        assert format_str == '{current}/{total}'
        
        # Test percent format
        config.set('slide_number.format', 'percent')
        format_str = config.get_slide_number_format()
        assert format_str == '{percent}%'
        
        # Test current only format
        config.set('slide_number.format', 'current')
        format_str = config.get_slide_number_format()
        assert format_str == '{current}'


class TestAdvancedFeatures:
    """Test advanced features like columns, overlays, etc."""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_multi_column_processing(self):
        """Test multi-column layout processing"""
        config = PresentationConfig()
        config.set('layout.columns', 2)
        
        converter = MarkdownToPDF(config=config)
        
        # Test new ::: {.column} format
        content = """# Multi-Column Test

::: {.column}
### Left Column
Content for left side
:::

::: {.column}
### Right Column
Content for right side
:::
"""
        
        processed = converter._process_columns(content)
        assert 'columns-layout columns-2' in processed
        assert '<div class="column">' in processed
        assert 'Left Column' in processed
        assert 'Right Column' in processed
    
    def test_hrule_processing(self):
        """Test horizontal rule processing"""
        config = PresentationConfig()
        config.set('style.hrule.enabled', True)
        config.set('style.hrule.width', '80%')
        
        converter = MarkdownToPDF(config=config)
        
        content = """# Main Title

## Subtitle

Some content here."""
        
        processed = converter._process_hrules(content)
        assert '<hr class="title-hrule"' in processed
        assert 'width: 80%' in processed
    
    def test_overlay_processing(self):
        """Test overlay/pause processing"""
        config = PresentationConfig()
        config.set('overlays.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        
        content = """# Overlay Demo

First content

<!--pause-->

Second content after pause

<!--pause-->

Third content
"""
        
        processed = converter._process_overlays(content)
        assert '<div class="overlay"' in processed
        assert 'data-overlay=' in processed


class TestSlideNumberCalculation:
    """Test slide number calculation and display"""
    
    def test_initial_slide_number_calculation(self):
        """Test that initial slide numbers are calculated correctly"""
        config = PresentationConfig()
        
        # Test percent format
        config.set('slide_number.format', 'percent')
        converter = MarkdownToPDF(config=config)
        
        slides = ['slide1', 'slide2', 'slide3', 'slide4', 'slide5']  # 5 slides
        
        slide_format = config.get_slide_number_format()
        initial_slide_number = slide_format.replace('{current}', '1').replace('{total}', str(len(slides)))
        if '{percent}' in initial_slide_number:
            initial_percent = round((1 / len(slides)) * 100)
            initial_slide_number = initial_slide_number.replace('{percent}', str(initial_percent))
        
        assert initial_slide_number == '20%', f"Expected '20%', got '{initial_slide_number}'"
        
        # Test current/total format
        config.set('slide_number.format', 'current/total')
        slide_format = config.get_slide_number_format()
        initial_slide_number = slide_format.replace('{current}', '1').replace('{total}', str(len(slides)))
        
        assert initial_slide_number == '1/5', f"Expected '1/5', got '{initial_slide_number}'"


class TestThemes:
    """Test different themes"""
    
    def test_all_themes_loadable(self):
        """Test that all themes can be loaded without errors"""
        themes = ['default', 'modern', 'minimal', 'gradient', 'dark', 'sky', 'solarized', 'moon', 'metropolis']
        
        for theme in themes:
            converter = MarkdownToPDF(theme=theme)
            # Check that CSS was generated (theme was loaded successfully)
            assert converter.css is not None
            assert len(converter.css) > 100  # Should have substantial CSS content
            assert f"Theme: {theme}" not in converter.css or theme in ['modern', 'default']  # Basic smoke test


class TestCSSGeneration:
    """Test CSS generation and template rendering"""
    
    def test_css_contains_fixed_layout(self):
        """Test that generated CSS has fixed layout (not centered)"""
        converter = MarkdownToPDF()
        css = converter.css
        
        # Should have flex-start for fixed positioning
        assert 'justify-content: flex-start' in css
        assert 'padding-top: 2rem' in css
    
    def test_mathjax_overflow_handling(self):
        """Test that MathJax-enabled configs have proper overflow handling"""
        config = PresentationConfig()
        config.set('math.enabled', True)
        
        converter = MarkdownToPDF(config=config)
        css = converter.css
        
        # Should have overflow: visible for MathJax
        assert 'overflow: visible' in css


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_markdown_file(self):
        """Test handling of missing markdown files"""
        converter = MarkdownToPDF()
        
        with pytest.raises(FileNotFoundError):
            converter.convert_to_html("nonexistent.md", "output.html")
    
    def test_empty_markdown_content(self):
        """Test handling of empty markdown"""
        temp_dir = tempfile.mkdtemp()
        try:
            empty_md = os.path.join(temp_dir, "empty.md")
            with open(empty_md, 'w') as f:
                f.write("")
            
            converter = MarkdownToPDF()
            
            with pytest.raises(ValueError, match="No slides found"):
                converter.convert_to_html(empty_md, "output.html")
        finally:
            shutil.rmtree(temp_dir)


def run_comprehensive_test():
    """Run all tests and return results"""
    import subprocess
    import sys
    
    print("🧪 Running Bodh Test Suite...")
    print("=" * 50)
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    # Install pytest if not available
    try:
        import pytest
    except ImportError:
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        import pytest
    
    success = run_comprehensive_test()
    exit(0 if success else 1)