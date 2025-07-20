#!/usr/bin/env python3
"""
Test theme rendering and visual consistency
"""

import os
import sys
import tempfile
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bodh import MarkdownToPDF
from config import load_config, PresentationConfig


class TestThemeRendering:
    def test_minimal_theme_no_double_boxes(self):
        """Test that minimal theme doesn't create weird double boxes"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "box_test.md")
        
        content = """# Test Boxes
        
Normal text.

```python
def test():
    return "code"
```

Inline `code` test.

> Quote block test
        
More content."""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config_data = {
            'theme': 'minimal',
            'font': {'family': 'Inter', 'size': 24}
        }
        
        config = PresentationConfig()
        for key, value in config_data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        
        # Check that CSS has proper code background handling
        css_content = converter.css
        
        # Should have code background
        assert 'background: #f5f5f5' in css_content, "Should have code background"
        
        # Should have rule to remove background from code inside pre
        assert 'pre code' in css_content and 'background: none' in css_content, "Should remove background from pre code"
        
        html_file = os.path.join(temp_dir, "box_test.html")
        result = converter.convert_to_html(test_md, html_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(html_file)
        os.rmdir(temp_dir)

    def test_sky_theme_consistency(self):
        """Test sky theme visual consistency"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "sky_test.md")
        
        content = """# Sky Theme Test
        
Normal content.

```javascript
console.log("test");
```

Inline `code` here.

> Quote to test styling
        """
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config_data = {
            'theme': 'sky',
            'font': {'family': 'Inter', 'size': 24}
        }
        
        config = PresentationConfig()
        for key, value in config_data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        
        html_file = os.path.join(temp_dir, "sky_test.html")
        result = converter.convert_to_html(test_md, html_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(html_file)
        os.rmdir(temp_dir)

    def test_all_themes_have_consistent_typography(self):
        """Test that all themes have consistent typography settings"""
        themes = ['minimal', 'modern', 'dark', 'sky', 'default']
        
        for theme_name in themes:
            config_data = {'theme': theme_name}
            config = PresentationConfig()
            config.set('theme', theme_name)
            
            converter = MarkdownToPDF(config=config)
            css_content = converter.css
            
            # Check for consistent font size structure
            assert 'font-size: 2.8em' in css_content, f"Theme {theme_name} should have consistent H1 size"
            assert 'font-size: 2.2em' in css_content, f"Theme {theme_name} should have consistent H2 size"
            
            # Check for proper code styling
            assert 'pre code' in css_content, f"Theme {theme_name} should handle pre code styling"


    def test_custom_font_sizes(self):
        """Test that custom font sizes are applied correctly"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "font_size_test.md")
        
        content = """# Main Title

## Subtitle

Regular paragraph text.

- List item text
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        # Test with custom font sizes
        config_data = {
            'theme': 'minimal',
            'font': {
                'family': 'Inter', 
                'size': 20,
                'title_size': 40,  # Should be 2.0em (40/20)
                'text_size': 16    # Should be 0.8em (16/20)
            }
        }
        
        config = PresentationConfig()
        for key, value in config_data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        
        # Check that CSS uses custom font sizes
        css_content = converter.css
        
        # H1 should be 2.0em (title_size / base_size = 40/20)
        assert 'font-size: 2.0em' in css_content, "H1 should use custom title size"
        
        # H2 should be 1.6em (title_size * 0.8 / base_size = 40*0.8/20)
        assert 'font-size: 1.6em' in css_content, "H2 should use scaled title size"
        
        # Text should be 0.8em (text_size / base_size = 16/20)
        assert 'font-size: 0.8em' in css_content, "Text should use custom text size"
        
        html_file = os.path.join(temp_dir, "font_size_test.html")
        result = converter.convert_to_html(test_md, html_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(html_file)
        os.rmdir(temp_dir)

    def test_default_font_sizes_when_none_specified(self):
        """Test that default font sizes are used when custom sizes are not specified"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "default_font_test.md")
        
        content = """# Title

## Subtitle

Text content."""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        # Test with no custom font sizes (should use defaults)
        config_data = {
            'theme': 'minimal',
            'font': {'family': 'Inter', 'size': 20}
        }
        
        config = PresentationConfig()
        for key, value in config_data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        css_content = converter.css
        
        # Should use default relative sizes
        assert 'font-size: 2.8em' in css_content, "Should use default H1 size"
        assert 'font-size: 2.2em' in css_content, "Should use default H2 size"
        assert 'font-size: 1.2em' in css_content, "Should use default text size"
        
        html_file = os.path.join(temp_dir, "default_font_test.html")
        result = converter.convert_to_html(test_md, html_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(html_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])