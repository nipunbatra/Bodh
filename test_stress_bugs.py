#!/usr/bin/env python3
"""
Extreme stress testing for Bodh - hunt for edge case bugs
High-stakes testing with boundary conditions and error scenarios
"""

import os
import tempfile
import shutil
import subprocess
import sys
import time
from pathlib import Path
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig, load_config


class TestExtremeBoundaryConditions:
    """Test extreme boundary conditions that could break the system"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_massive_presentation_100_slides(self):
        """Test with 100 slides to check memory and performance"""
        massive_md = os.path.join(self.temp_dir, "massive.md")
        
        # Generate 100 slides with varying content
        slides = []
        for i in range(100):
            slide_content = f"""# Slide {i+1}
This is slide number {i+1} with some content.

## Subsection {i+1}
- Point 1 for slide {i+1}
- Point 2 for slide {i+1}
- Point 3 for slide {i+1}

### Code Example {i+1}
```python
def function_{i+1}():
    return "slide {i+1}"
```

Here's some longer text to make the slide more substantial and test text wrapping and layout with various amounts of content across different slides.
"""
            slides.append(slide_content)
        
        with open(massive_md, 'w') as f:
            f.write('\n\n---\n\n'.join(slides))
        
        # Time the operation
        start_time = time.time()
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "massive.pdf")
        
        # Should not crash or timeout
        converter.convert_to_pdf(massive_md, pdf_file)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify PDF was created and has substantial content
        assert os.path.exists(pdf_file), "Massive PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 500000, f"PDF too small for 100 slides: {pdf_size} bytes"
        
        # Performance should be reasonable (under 2 minutes)
        assert processing_time < 120, f"Processing took too long: {processing_time:.2f} seconds"
        
        print(f"✅ 100-slide presentation processed in {processing_time:.2f} seconds, {pdf_size} bytes")
    
    def test_extremely_long_single_slide(self):
        """Test with one slide containing massive amounts of text"""
        long_text = "This is a very long line of text that repeats many times to test text wrapping and layout behavior. " * 200
        
        extreme_md = os.path.join(self.temp_dir, "extreme.md")
        
        # Generate table rows
        table_rows = '| Very long cell content that should wrap properly | Another long cell | Third long cell | Fourth long cell |\n' * 20
        
        # Generate code functions
        code_functions = '\n'.join([f'def long_function_name_{i}():\n    return "very long string " * 100' for i in range(50)])
        
        with open(extreme_md, 'w') as f:
            f.write(f"""# Extreme Text Test

{long_text}

## More Content
{'Another paragraph with lots of text. ' * 100}

### Even More
{'Final section with excessive content to test boundaries. ' * 150}

#### Tables
| Column 1 | Column 2 | Column 3 | Column 4 |
|----------|----------|----------|----------|
{table_rows}

#### Code Blocks
```python
# This is a very long code block that should be handled properly
{code_functions}
```
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "extreme.pdf")
        
        # Should not crash with extreme content
        converter.convert_to_pdf(extreme_md, pdf_file)
        
        assert os.path.exists(pdf_file), "Extreme content PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 25000, f"PDF too small for extreme content: {pdf_size} bytes"
        
        print(f"✅ Extreme content processed successfully, {pdf_size} bytes")
    
    def test_unicode_stress_test(self):
        """Test with extensive Unicode and international characters"""
        unicode_md = os.path.join(self.temp_dir, "unicode.md")
        with open(unicode_md, 'w', encoding='utf-8') as f:
            f.write("""# Unicode Stress Test 🌍

## Emoji Overload
🚀🎨📝✅❌🔥💡🌟⭐🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲🎯🎪🎭🎨🎲

## Mathematical Symbols
∑∏∂∇∆∞∫∮∯∰∱∲∳∴∵∶∷∸∹∺∻∼∽∾∿≀≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≐≑≒≓≔≕≖≗≘≙≚≛≜≝≞≟≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊌⊍⊎⊏⊐⊑⊒⊓⊔⊕⊖⊗⊘⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⊲⊳⊴⊵⊶⊷⊸⊹⊺⊻⊼⊽⊾⊿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿

## Chinese Characters
你好世界这是一个测试中文字符的演示文稿包含很多中文字符来测试字体渲染和布局问题这些字符应该能够正确显示在PDF中而不会出现乱码或者布局问题希望能够正确处理所有的中文字符包括繁体字和简体字以及各种标点符号

## Arabic Text (RTL)
مرحبا بالعالم هذا اختبار للنص العربي يجب أن يتم عرضه بشكل صحيح من اليمين إلى اليسار وأن تكون الخطوط واضحة ومقروءة في ملف PDF النهائي

## Japanese Text
こんにちは世界これは日本語のテストですひらがなカタカナ漢字が正しく表示されることを確認しています

## Russian Text
Привет мир это тест русского текста кириллические символы должны отображаться корректно в PDF файле

## Mixed Script Chaos
English text مع النص العربي и русский текст 和中文字符 along with हिंदी text และภาษาไทย plus 한국어 text!

---

## Special Characters Table
| Symbol | Unicode | Description |
|--------|---------|-------------|
| ™ | U+2122 | Trademark |
| © | U+00A9 | Copyright |
| ® | U+00AE | Registered |
| ℠ | U+2120 | Service Mark |
| ℡ | U+2121 | Telephone |
| ℉ | U+2109 | Fahrenheit |
| ℃ | U+2103 | Celsius |
| ⌘ | U+2318 | Command Key |
| ⌥ | U+2325 | Option Key |
| ⇧ | U+21E7 | Shift Key |

---

## Combining Characters Test
a̋ e̋ i̋ ő ű ÿ ẍ ẅ ṽ ṵ ṱ ṟ q̈ p̈ ḧ ģ f̈ d̈ c̈ b̈ ä

## Zero-Width Characters
Zero‌Width‌Non‌Joiner‌Test
Zero​Width​Space​Test
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "unicode.pdf")
        
        # Should handle all Unicode characters without crashing
        converter.convert_to_pdf(unicode_md, pdf_file)
        
        assert os.path.exists(pdf_file), "Unicode PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 20000, f"Unicode PDF too small: {pdf_size} bytes"
        
        print(f"✅ Unicode stress test passed, {pdf_size} bytes")
    
    def test_malformed_markdown_edge_cases(self):
        """Test with malformed and edge case markdown"""
        malformed_md = os.path.join(self.temp_dir, "malformed.md")
        with open(malformed_md, 'w') as f:
            f.write("""# Malformed Markdown Test

## Unclosed Code Blocks
```python
def unclosed_function():
    return "missing closing backticks"

## Nested Code Blocks
```python
def outer():
    '''python
    def inner():
        return "nested"
    '''
    return inner()
```

## Broken Tables
| Column 1 | Column 2
|----------|
| Missing cells |
| Too many | cells | here | extra |
Column without pipes

## Malformed Lists
- Item 1
  - Nested item
    - Deep nested
- Item 2
    * Mixed list markers
    + Different markers
      1. Numbered in bullets
      2. More numbers
- Item 3

## Broken Links
[Link with no URL]()
[Link with broken URL](http://this-is-not-a-valid-url-at-all.invalid)
![Image with no path]()
![Image with broken path](broken-image.jpg)

## Excessive Nesting
# H1
## H2
### H3
#### H4
##### H5
###### H6
####### H7 (invalid)
######## H8 (invalid)

## Mixed Formatting
***Bold and italic*** with `code` and ~~strikethrough~~ and **bold with `code` inside** and *italic with **bold inside** text*.

## Broken HTML
<div>Unclosed div
<span>Unclosed span
<p>Unclosed paragraph

<script>alert('xss attempt')</script>
<iframe src="javascript:alert('xss')"></iframe>

## Special Separators
---
***
___
--------
========

## Unicode Separators
—————————————————————————————————
═══════════════════════════════════
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Empty Sections
#
##
### 
#### 
##### 
###### 

---

## Only Whitespace Content
   
	
		
            
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "malformed.pdf")
        
        # Should handle malformed markdown gracefully
        converter.convert_to_pdf(malformed_md, pdf_file)
        
        assert os.path.exists(pdf_file), "Malformed markdown PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 10000, f"Malformed markdown PDF too small: {pdf_size} bytes"
        
        print(f"✅ Malformed markdown handled gracefully, {pdf_size} bytes")


class TestConfigurationEdgeCases:
    """Test edge cases in configuration handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_invalid_theme_fallback(self):
        """Test behavior with invalid theme"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("# Test\nContent")
        
        # Test with completely invalid theme
        with pytest.raises(FileNotFoundError):
            converter = MarkdownToPDF(theme='nonexistent_theme_12345')
    
    def test_extreme_font_sizes(self):
        """Test with extreme font sizes"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("# Font Size Test\nTesting extreme font sizes")
        
        extreme_sizes = [1, 2, 5, 100, 200, 500, 1000]
        
        for size in extreme_sizes:
            config = PresentationConfig()
            config.set('font.size', size)
            
            converter = MarkdownToPDF(config=config)
            pdf_file = os.path.join(self.temp_dir, f"font_{size}.pdf")
            
            # Should not crash with extreme font sizes
            converter.convert_to_pdf(test_md, pdf_file)
            
            assert os.path.exists(pdf_file), f"PDF not created with font size {size}"
            
            print(f"✅ Font size {size} handled successfully")
    
    def test_invalid_config_values(self):
        """Test with invalid configuration values"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("# Config Test\nTesting invalid config values")
        
        config = PresentationConfig()
        
        # Test with invalid values
        invalid_configs = [
            ('font.size', -10),
            ('font.size', 'invalid'),
            ('font.family', 12345),
            ('font.family', ''),
            ('slide_number.format', 'invalid_format'),
            ('logo.location', 'invalid_position'),
            ('layout.columns', -5),
            ('layout.columns', 'invalid'),
            ('layout.columns', 100),  # Too many columns
        ]
        
        for key, value in invalid_configs:
            config.set(key, value)
        
        converter = MarkdownToPDF(config=config)
        pdf_file = os.path.join(self.temp_dir, "invalid_config.pdf")
        
        # Should handle invalid configs gracefully
        converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF not created with invalid config"
        print("✅ Invalid config values handled gracefully")
    
    def test_corrupted_config_file(self):
        """Test with corrupted YAML config file"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("# Config Test\nContent")
        
        corrupted_config = os.path.join(self.temp_dir, "corrupted.yml")
        with open(corrupted_config, 'w') as f:
            f.write("""
theme: modern
font:
  family: Inter
  size: 20
  invalid_nesting:
    - item1
    - item2
    - nested:
        - deep1
        - deep2
        - invalid: {broken: yaml: syntax}
slide_number:
  enabled: true
  format: current/total
  position: invalid_position
navigation:
  enabled: true
  show_arrows: not_a_boolean
  show_dots: "string_instead_of_boolean"
math:
  enabled: 12345
logo:
  source: 
  location: 
  size: -100
layout:
  columns: "invalid_number"
  column_gap: negative_value
""")
        
        # Should handle corrupted config gracefully
        config = load_config(corrupted_config)
        converter = MarkdownToPDF(config=config)
        pdf_file = os.path.join(self.temp_dir, "corrupted_config.pdf")
        
        converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF not created with corrupted config"
        print("✅ Corrupted config file handled gracefully")


class TestPerformanceAndMemoryEdgeCases:
    """Test performance and memory edge cases"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_rapid_fire_pdf_generation(self):
        """Test rapid generation of multiple PDFs"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("""# Rapid Fire Test
This is a test for rapid PDF generation.

---

# Slide 2
More content here.

---

# Slide 3
Final slide.
""")
        
        converter = MarkdownToPDF()
        
        # Generate 20 PDFs rapidly
        start_time = time.time()
        for i in range(20):
            pdf_file = os.path.join(self.temp_dir, f"rapid_{i}.pdf")
            converter.convert_to_pdf(test_md, pdf_file)
            assert os.path.exists(pdf_file), f"PDF {i} not created"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time
        assert total_time < 60, f"Rapid fire test took too long: {total_time:.2f} seconds"
        
        print(f"✅ Rapid fire test: 20 PDFs in {total_time:.2f} seconds")
    
    def test_memory_intensive_content(self):
        """Test with memory-intensive content"""
        memory_md = os.path.join(self.temp_dir, "memory.md")
        
        # Create content that should consume significant memory
        large_table_rows = []
        for i in range(1000):
            large_table_rows.append(f"| Cell {i}A | Cell {i}B | Cell {i}C | Cell {i}D |")
        
        with open(memory_md, 'w') as f:
            f.write(f"""# Memory Test
Large table follows:

| Column A | Column B | Column C | Column D |
|----------|----------|----------|----------|
{chr(10).join(large_table_rows)}

---

# Large Code Block
```python
# Large code block
{chr(10).join([f"line_{i} = 'This is line {i} with some content'" for i in range(1000)])}
```

---

# Large List
{''.join([f"- List item {i} with detailed content and explanations" + chr(10) for i in range(500)])}
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "memory.pdf")
        
        # Should handle memory-intensive content
        converter.convert_to_pdf(memory_md, pdf_file)
        
        assert os.path.exists(pdf_file), "Memory-intensive PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 100000, f"Memory-intensive PDF too small: {pdf_size} bytes"
        
        print(f"✅ Memory-intensive content handled, {pdf_size} bytes")


class TestImageAndMediaEdgeCases:
    """Test edge cases with images and media"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_missing_images_stress(self):
        """Test with many missing images"""
        missing_images_md = os.path.join(self.temp_dir, "missing_images.md")
        
        missing_images = [
            "![Missing 1](missing1.jpg)",
            "![Missing 2](missing2.png)",
            "![Missing 3](missing3.gif)",
            "![Missing 4](missing4.svg)",
            "![Missing 5](missing5.webp)",
            "![Missing 6](http://nonexistent.com/image.jpg)",
            "![Missing 7](../missing7.png)",
            "![Missing 8](./missing8.jpg)",
            "![Missing 9](/absolute/missing9.png)",
            "![Missing 10](~/missing10.jpg)",
        ]
        
        with open(missing_images_md, 'w') as f:
            f.write(f"""# Missing Images Test
{chr(10).join(missing_images)}

---

# More Missing Images
{chr(10).join(missing_images)}

---

# Even More Missing Images
{chr(10).join(missing_images)}
""")
        
        converter = MarkdownToPDF()
        pdf_file = os.path.join(self.temp_dir, "missing_images.pdf")
        
        # Should handle missing images gracefully
        converter.convert_to_pdf(missing_images_md, pdf_file)
        
        assert os.path.exists(pdf_file), "PDF with missing images not created"
        print("✅ Missing images handled gracefully")
    
    def test_invalid_logo_paths(self):
        """Test with various invalid logo paths"""
        test_md = os.path.join(self.temp_dir, "test.md")
        with open(test_md, 'w') as f:
            f.write("# Logo Test\nTesting invalid logo paths")
        
        invalid_logos = [
            "",  # Empty string
            "   ",  # Whitespace only
            "nonexistent.jpg",  # File doesn't exist
            "/absolute/path/to/nonexistent.png",  # Absolute path doesn't exist
            "~/nonexistent.svg",  # Home path doesn't exist
            "http://nonexistent.com/logo.png",  # URL (not supported)
            "../../../etc/passwd",  # Security test
            "logo.jpg\x00",  # Null byte injection
            "logo.jpg;rm -rf /",  # Command injection attempt
            "logo.jpg\nrm -rf /",  # Newline injection
        ]
        
        for i, logo_path in enumerate(invalid_logos):
            config = PresentationConfig()
            config.set('logo.source', logo_path)
            
            converter = MarkdownToPDF(config=config)
            pdf_file = os.path.join(self.temp_dir, f"invalid_logo_{i}.pdf")
            
            # Should handle invalid logo paths gracefully
            converter.convert_to_pdf(test_md, pdf_file)
            
            assert os.path.exists(pdf_file), f"PDF not created with invalid logo {i}"
        
        print("✅ Invalid logo paths handled gracefully")


def run_stress_tests():
    """Run all stress tests"""
    print("🔥 Running EXTREME STRESS TESTS...")
    print("=" * 60)
    
    # Run pytest with longer timeout
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short", "--timeout=300"
    ], capture_output=True, text=True, timeout=600)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("🎉 ALL STRESS TESTS PASSED!")
        return True
    else:
        print("💥 SOME STRESS TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = run_stress_tests()
    exit(0 if success else 1)