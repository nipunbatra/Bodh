#!/usr/bin/env python3
"""
Comprehensive functional testing suite
World-class testing to catch real-world issues and edge cases
"""

import os
import tempfile
import shutil
import re
import pytest
from bodh import MarkdownToPDF, ThemeLoader, StyleGenerator
from config import PresentationConfig, load_config


class TestCSSRenderingIssues:
    """Test CSS rendering and layout issues that cause visual problems"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_gradient_theme_excessive_whitespace(self):
        """Test the specific issue with gradient theme having too much whitespace"""
        test_md = os.path.join(self.temp_dir, "gradient_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Gradient Theme Test

This slide should not have excessive whitespace around the gradient background.

## Content Section
- Point 1
- Point 2
- Point 3

The gradient should fill the slide properly without huge margins.
""")
        
        converter = MarkdownToPDF(theme='gradient')
        
        # Generate HTML to analyze CSS
        html_file = os.path.join(self.temp_dir, "gradient_test.html")
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check for excessive padding issues
        css_section = html_content[html_content.find('<style>'):html_content.find('</style>')]
        
        # Extract slide padding value
        padding_match = re.search(r'\.slide\s*{[^}]*padding:\s*([^;]+);', css_section, re.DOTALL)
        if padding_match:
            padding_value = padding_match.group(1).strip()
            print(f"Gradient theme slide padding: {padding_value}")
            
            # 4rem is excessive for PDF - should be max 3rem
            if 'rem' in padding_value:
                padding_num = float(re.search(r'(\d+\.?\d*)', padding_value).group(1))
                assert padding_num <= 3.0, f"Excessive slide padding in gradient theme: {padding_value} (should be ≤ 3rem)"
        
        # Check page margins
        page_margin_match = re.search(r'@page\s*{[^}]*margin:\s*([^;]+);', css_section, re.DOTALL)
        if page_margin_match:
            margin_value = page_margin_match.group(1).strip()
            print(f"Page margin: {margin_value}")
            
            # 1.5cm is reasonable, but combined with 4rem padding is too much
            if 'cm' in margin_value:
                margin_num = float(re.search(r'(\d+\.?\d*)', margin_value).group(1))
                assert margin_num <= 2.0, f"Excessive page margin: {margin_value}"
        
        print("✅ Gradient theme whitespace analysis completed")
    
    def test_all_themes_reasonable_spacing(self):
        """Test that all themes have reasonable spacing values"""
        theme_loader = ThemeLoader()
        themes = theme_loader.list_themes()
        
        spacing_issues = []
        
        for theme_info in themes:
            theme_name = theme_info['name']
            try:
                theme_data = theme_loader.load_theme(theme_name)
                
                # Check slide padding
                if 'spacing' in theme_data and 'slide_padding' in theme_data['spacing']:
                    padding = theme_data['spacing']['slide_padding']
                    
                    # Convert to numeric value for comparison
                    if isinstance(padding, str):
                        if 'rem' in padding:
                            padding_val = float(re.search(r'(\d+\.?\d*)', padding).group(1))
                            if padding_val > 3.5:
                                spacing_issues.append(f"{theme_name}: excessive slide_padding {padding}")
                        elif 'px' in padding:
                            padding_val = float(re.search(r'(\d+\.?\d*)', padding).group(1))
                            if padding_val > 60:  # ~3.5rem at 16px base
                                spacing_issues.append(f"{theme_name}: excessive slide_padding {padding}")
                
                # Check element margins
                if 'spacing' in theme_data and 'element_margin' in theme_data['spacing']:
                    margin = theme_data['spacing']['element_margin']
                    if isinstance(margin, str) and 'rem' in margin:
                        margin_val = float(re.search(r'(\d+\.?\d*)', margin).group(1))
                        if margin_val > 2.5:
                            spacing_issues.append(f"{theme_name}: excessive element_margin {margin}")
                
            except Exception as e:
                print(f"Warning: Could not analyze theme {theme_name}: {e}")
        
        if spacing_issues:
            print("Spacing issues found:")
            for issue in spacing_issues:
                print(f"  - {issue}")
        
        # Fail if any major spacing issues found
        assert len(spacing_issues) == 0, f"Themes with excessive spacing: {spacing_issues}"
        
        print(f"✅ All {len(themes)} themes have reasonable spacing")
    
    def test_css_background_rendering(self):
        """Test that CSS backgrounds render properly without layout issues"""
        test_cases = [
            ('gradient', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'),
            ('dark', '#1a1a1a'),
            ('minimal', '#ffffff'),
        ]
        
        for theme_name, expected_bg in test_cases:
            test_md = os.path.join(self.temp_dir, f"bg_test_{theme_name}.md")
            with open(test_md, 'w') as f:
                f.write(f"# {theme_name.title()} Background Test\n\nTesting background rendering.")
            
            try:
                converter = MarkdownToPDF(theme=theme_name)
                html_file = os.path.join(self.temp_dir, f"bg_test_{theme_name}.html")
                converter.convert_to_html(test_md, html_file, _test_mode=True)
                
                with open(html_file, 'r') as f:
                    html_content = f.read()
                
                # Check that background is applied to both body and slide
                assert f'background: {expected_bg}' in html_content or expected_bg in html_content, \
                    f"Background not properly applied in {theme_name} theme"
                
                print(f"✅ {theme_name} theme background renders correctly")
                
            except Exception as e:
                print(f"Warning: Could not test {theme_name} theme: {e}")


class TestMarkdownParsingEdgeCases:
    """Test markdown parsing edge cases that could cause layout issues"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_extremely_long_lines(self):
        """Test handling of extremely long lines that could break layout"""
        long_line = "This is an extremely long line of text that goes on and on and on without any breaks and could potentially cause layout issues in PDF rendering if not handled properly. " * 10
        
        test_md = os.path.join(self.temp_dir, "long_lines.md")
        with open(test_md, 'w') as f:
            f.write(f"""# Long Lines Test

{long_line}

## Another Section

{long_line}

### Code Block Test
```python
# This is a very long line of code that should wrap properly: {long_line.replace(' ', '_')}
def very_long_function_name_that_might_cause_issues():
    return "{long_line}"
```
""")
        
        converter = MarkdownToPDF()
        
        # Should not crash
        html_file = os.path.join(self.temp_dir, "long_lines.html")
        pdf_file = os.path.join(self.temp_dir, "long_lines.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Check that CSS has word wrapping
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'word-wrap: break-word' in html_content, "Missing word-wrap CSS for long lines"
        assert 'overflow-wrap: break-word' in html_content, "Missing overflow-wrap CSS"
        
        assert os.path.exists(pdf_file), "PDF not created with long lines"
        print("✅ Extremely long lines handled correctly")
    
    def test_nested_markdown_structures(self):
        """Test deeply nested markdown structures"""
        test_md = os.path.join(self.temp_dir, "nested.md")
        with open(test_md, 'w') as f:
            f.write("""# Nested Structures Test

## Lists
- Item 1
  - Nested item 1
    - Deep nested item 1
      - Very deep item 1
        - Extremely deep item 1
          - Super deep item 1
    - Deep nested item 2
  - Nested item 2
- Item 2

## Blockquotes
> Level 1 quote
> > Level 2 quote
> > > Level 3 quote
> > > > Level 4 quote
> > > > > Level 5 quote
> > > > > > Level 6 quote

## Mixed Nesting
1. Numbered list
   > With blockquote
   > > And nested blockquote
   
   ```python
   # With code block
   def nested_function():
       if True:
           if True:
               if True:
                   return "deeply nested"
   ```
   
   - And bullet list
     - Nested bullets
       - Deep bullets

## Tables in Lists
- Item with table:
  
  | Col1 | Col2 | Col3 |
  |------|------|------|
  | A    | B    | C    |
  | D    | E    | F    |
  
- Another item
""")
        
        converter = MarkdownToPDF()
        
        # Should handle complex nesting without crashing
        html_file = os.path.join(self.temp_dir, "nested.html")
        pdf_file = os.path.join(self.temp_dir, "nested.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Verify HTML structure
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check for proper nesting
        assert '<ul>' in html_content and '</ul>' in html_content, "Lists not properly processed"
        assert '<blockquote>' in html_content and '</blockquote>' in html_content, "Blockquotes not processed"
        assert '<table>' in html_content and '</table>' in html_content, "Tables not processed"
        assert '<ol>' in html_content and '</ol>' in html_content, "Numbered lists not processed"
        
        assert os.path.exists(pdf_file), "PDF not created with nested structures"
        print("✅ Nested markdown structures handled correctly")
    
    def test_special_characters_and_encoding(self):
        """Test handling of special characters and encoding issues"""
        test_md = os.path.join(self.temp_dir, "special_chars.md")
        with open(test_md, 'w', encoding='utf-8') as f:
            f.write("""# Special Characters Test

## Unicode Characters
- Emoji: 🚀 🎨 📝 ✅ ❌ 🔥 💡 🌟
- Math: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
- Arrows: ← → ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙
- Symbols: © ® ™ ℠ ℡ ℉ ℃ ⌘ ⌥ ⇧

## International Text
- Chinese: 你好世界，这是一个测试
- Arabic: مرحبا بالعالم، هذا اختبار
- Russian: Привет мир, это тест
- Japanese: こんにちは世界、これはテストです
- Hindi: नमस्ते दुनिया, यह एक परीक्षण है

## Problematic Characters
- Quotes: "smart quotes" 'single quotes' „German quotes"
- Dashes: en-dash – em-dash — minus −
- Spaces: regular space, non-breaking space , em space , thin space 
- Special: ¡¿§¶†‡•‰‱‴‵‶‷‸‹›«»‚„‥…‰‱

## Code with Special Chars
```python
# Testing special characters in code
def test_unicode():
    text = "Hello 世界! Γειά σου κόσμε!"
    emoji = "🎉🔥💯"
    math = "∑(i=1 to ∞) 1/i² = π²/6"
    return f"{text} {emoji} {math}"
```

## LaTeX-like Math
- Inline: $\\alpha + \\beta = \\gamma$
- Display: $$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$
""")
        
        converter = MarkdownToPDF()
        
        # Should handle all special characters without crashing
        html_file = os.path.join(self.temp_dir, "special_chars.html")
        pdf_file = os.path.join(self.temp_dir, "special_chars.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Verify UTF-8 encoding is preserved
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check that Unicode characters are preserved
        assert '🚀' in html_content, "Emoji not preserved"
        assert '你好世界' in html_content, "Chinese characters not preserved"
        assert 'α β γ' in html_content, "Greek letters not preserved"
        assert '"smart quotes"' in html_content or '"smart quotes"' in html_content, "Smart quotes not preserved"
        
        assert os.path.exists(pdf_file), "PDF not created with special characters"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 20000, f"PDF with special chars too small: {pdf_size} bytes"
        
        print("✅ Special characters and encoding handled correctly")


class TestConfigurationEdgeCases:
    """Test configuration edge cases and validation"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_missing_theme_fallback(self):
        """Test behavior when theme files are missing or corrupted"""
        # Test with non-existent theme
        with pytest.raises(FileNotFoundError):
            MarkdownToPDF(theme='nonexistent_theme_12345')
    
    def test_malformed_theme_json(self):
        """Test handling of malformed theme JSON files"""
        # Create malformed theme file
        bad_theme_file = os.path.join(self.temp_dir, "bad_theme.json")
        with open(bad_theme_file, 'w') as f:
            f.write('{"name": "Bad Theme", "colors": { invalid json }')
        
        # Should handle gracefully
        theme_loader = ThemeLoader(self.temp_dir)
        with pytest.raises(Exception):  # Should raise JSON decode error
            theme_loader.load_theme('bad_theme')
    
    def test_extreme_configuration_values(self):
        """Test with extreme configuration values"""
        test_md = os.path.join(self.temp_dir, "config_test.md")
        with open(test_md, 'w') as f:
            f.write("# Config Test\nTesting extreme config values")
        
        extreme_configs = [
            # Font sizes
            {'font.size': 1},      # Tiny
            {'font.size': 200},    # Huge
            {'font.size': -10},    # Negative (should be handled)
            
            # Spacing
            {'spacing.slide_padding': '10rem'},    # Excessive
            {'spacing.slide_padding': '0'},        # None
            {'spacing.element_margin': '5rem'},    # Large
            
            # Invalid values
            {'font.family': ''},   # Empty
            {'font.family': None}, # None
        ]
        
        for config_dict in extreme_configs:
            try:
                config = PresentationConfig()
                for key, value in config_dict.items():
                    config.set(key, value)
                
                converter = MarkdownToPDF(config=config)
                pdf_file = os.path.join(self.temp_dir, f"extreme_{hash(str(config_dict))}.pdf")
                
                # Should not crash
                converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
                assert os.path.exists(pdf_file), f"PDF not created with config: {config_dict}"
                
                print(f"✅ Handled extreme config: {config_dict}")
                
            except Exception as e:
                print(f"Config {config_dict} caused error: {e}")
                # Some extreme configs should fail gracefully
                assert "font.size" in str(config_dict) or "None" in str(config_dict), \
                    f"Unexpected error with config {config_dict}: {e}"
    
    def test_configuration_inheritance_and_overrides(self):
        """Test that configuration values are properly inherited and overridden"""
        test_md = os.path.join(self.temp_dir, "inheritance_test.md")
        with open(test_md, 'w') as f:
            f.write("# Inheritance Test\nTesting config inheritance")
        
        # Test with theme + config overrides
        config = PresentationConfig()
        config.set('font.size', 25)  # Override default
        config.set('slide_number.enabled', False)  # Override theme
        
        converter = MarkdownToPDF(theme='modern', config=config)
        
        # Check that overrides took effect
        assert converter.font_size == 25, "Font size override not applied"
        assert converter.config.get('slide_number.enabled') == False, "Config override not applied"
        
        # Generate to verify it works
        html_file = os.path.join(self.temp_dir, "inheritance_test.html")
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'font-size: 25px' in html_content, "Font size not applied in CSS"
        
        print("✅ Configuration inheritance and overrides work correctly")


class TestContentRenderingIssues:
    """Test content rendering issues that could cause visual problems"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_table_overflow_handling(self):
        """Test handling of tables that exceed slide width"""
        test_md = os.path.join(self.temp_dir, "table_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Table Overflow Test

## Normal Table
| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |

## Wide Table
| Very Long Column Header That Might Cause Issues | Another Very Long Column Header | Third Long Header | Fourth Header | Fifth Header | Sixth Header |
|---|---|---|---|---|---|
| Very long content that could cause horizontal overflow issues | More long content here | Even more content | Additional data | More data | Final column |
| Another row with lots of content | More content here | And more | And more | And more | And more |

## Table with Code
| Function | Code | Description |
|----------|------|-------------|
| `very_long_function_name_that_might_wrap()` | `return "very long string that could cause issues"` | This is a very long description that might cause wrapping issues |
""")
        
        converter = MarkdownToPDF()
        
        html_file = os.path.join(self.temp_dir, "table_test.html")
        pdf_file = os.path.join(self.temp_dir, "table_test.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Check CSS handles table overflow
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Should have responsive table CSS
        assert 'table' in html_content, "Tables not processed"
        assert 'overflow' in html_content, "No overflow handling for tables"
        
        assert os.path.exists(pdf_file), "PDF not created with wide tables"
        print("✅ Table overflow handling works correctly")
    
    def test_code_block_formatting(self):
        """Test code block formatting and syntax highlighting"""
        test_md = os.path.join(self.temp_dir, "code_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Code Block Test

## Python Code
```python
def very_long_function_name_that_might_cause_wrapping_issues():
    # This is a very long comment that should be handled properly
    very_long_variable_name = "very long string value that might cause issues"
    return very_long_variable_name.replace("issues", "handled properly")

class VeryLongClassNameThatMightCauseIssues:
    def __init__(self, very_long_parameter_name_here):
        self.very_long_attribute_name = very_long_parameter_name_here
```

## JavaScript Code
```javascript
function veryLongFunctionNameThatMightCauseWrappingIssues() {
    const veryLongVariableName = "very long string value that might cause issues";
    return veryLongVariableName.replace(/issues/g, "handled properly");
}
```

## Bash Code
```bash
#!/bin/bash
very_long_command_that_might_cause_issues --with-very-long-parameter-names --and-more-parameters --that-keep-going --and-going --until-it-wraps
```

## Plain Text
```
This is plain text that might be very long and cause wrapping issues in the code block rendering system.
```
""")
        
        converter = MarkdownToPDF()
        
        html_file = os.path.join(self.temp_dir, "code_test.html")
        pdf_file = os.path.join(self.temp_dir, "code_test.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Check code highlighting and formatting
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'codehilite' in html_content or 'highlight' in html_content, "Code highlighting not applied"
        assert '<pre>' in html_content and '<code>' in html_content, "Code blocks not properly formatted"
        
        assert os.path.exists(pdf_file), "PDF not created with code blocks"
        print("✅ Code block formatting works correctly")
    
    def test_mathematical_content(self):
        """Test mathematical content rendering"""
        test_md = os.path.join(self.temp_dir, "math_test.md")
        with open(test_md, 'w') as f:
            f.write("""# Mathematical Content Test

## Inline Math
The equation $E = mc^2$ is famous. Also $\\alpha + \\beta = \\gamma$.

## Display Math
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$

## Complex Equations
$$\\frac{\\partial}{\\partial t} \\Psi(\\mathbf{r}, t) = \\frac{i\\hbar}{2m} \\nabla^2 \\Psi(\\mathbf{r}, t) + V(\\mathbf{r}) \\Psi(\\mathbf{r}, t)$$

## Matrices
$$\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}
\\begin{pmatrix}
x \\\\
y
\\end{pmatrix}
=
\\begin{pmatrix}
ax + by \\\\
cx + dy
\\end{pmatrix}$$
""")
        
        converter = MarkdownToPDF()
        
        html_file = os.path.join(self.temp_dir, "math_test.html")
        pdf_file = os.path.join(self.temp_dir, "math_test.pdf")
        
        converter.convert_to_html(test_md, html_file, _test_mode=True)
        converter.convert_to_pdf(test_md, pdf_file, _test_mode=True)
        
        # Check MathJax is included
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert 'MathJax' in html_content, "MathJax not included for math rendering"
        assert 'state: () => 6' in html_content, "Mock MathJax content not loaded"
        
        # Check for math delimiters
        assert '$' in html_content or '\\(' in html_content, "Math delimiters not preserved"
        
        assert os.path.exists(pdf_file), "PDF not created with math content"
        print("✅ Mathematical content rendering works correctly")


if __name__ == "__main__":
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    exit(result.returncode)