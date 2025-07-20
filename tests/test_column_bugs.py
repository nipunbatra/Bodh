#!/usr/bin/env python3
"""
Column functionality bug testing
"""

import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
from bodh import MarkdownToPDF
from config import PresentationConfig


class TestColumnBugs:
    """Test column functionality edge cases"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_column_markdown_processing(self):
        """Test that column content is properly processed as markdown"""
        column_md = os.path.join(self.temp_dir, "column_test.md")
        with open(column_md, 'w') as f:
            f.write("""# Column Markdown Test

::: {.column}
### Left Column
This is **bold** and *italic* text.

- List item 1
- List item 2
- List item 3

```python
def test():
    return "code"
```
:::

::: {.column}
### Right Column
This is a [link](http://example.com).

| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |

> This is a blockquote
:::
""")
        
        converter = MarkdownToPDF()
        html_file = os.path.join(self.temp_dir, "column_test.html")
        pdf_file = os.path.join(self.temp_dir, "column_test.pdf")
        
        converter.convert_to_html(column_md, html_file)
        converter.convert_to_pdf(column_md, pdf_file)
        
        # Check HTML content
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Verify markdown elements are properly processed
        assert '<strong>bold</strong>' in html_content, "Bold text not processed"
        assert '<em>italic</em>' in html_content, "Italic text not processed"
        assert '<ul>' in html_content, "Lists not processed"
        assert '<li>List item 1</li>' in html_content, "List items not processed"
        assert '<table>' in html_content, "Tables not processed"
        assert '<blockquote>' in html_content, "Blockquotes not processed"
        assert 'codehilite' in html_content, "Code blocks not processed"
        assert '<a href="http://example.com">' in html_content, "Links not processed"
        
        assert os.path.exists(pdf_file), "PDF not created"
        print("✅ Column markdown processing works correctly")
    
    def test_dynamic_column_count(self):
        """Test that column count is dynamic based on content"""
        test_cases = [
            ("2 columns", 2, """
::: {.column}
Column 1
:::

::: {.column}
Column 2
:::
"""),
            ("3 columns", 3, """
::: {.column}
Column 1
:::

::: {.column}
Column 2
:::

::: {.column}
Column 3
:::
"""),
            ("4 columns", 4, """
::: {.column}
Column 1
:::

::: {.column}
Column 2
:::

::: {.column}
Column 3
:::

::: {.column}
Column 4
:::
"""),
        ]
        
        for name, expected_count, content in test_cases:
            test_md = os.path.join(self.temp_dir, f"columns_{expected_count}.md")
            with open(test_md, 'w') as f:
                f.write(f"# {name}\n{content}")
            
            converter = MarkdownToPDF()
            html_file = os.path.join(self.temp_dir, f"columns_{expected_count}.html")
            
            converter.convert_to_html(test_md, html_file)
            
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            # Check that correct column class is used
            assert f'columns-{expected_count}' in html_content, f"Expected columns-{expected_count} class for {name}"
            
            # Check that column count in CSS matches
            assert f'grid-template-columns: {" ".join(["1fr"] * expected_count)}' in html_content, f"CSS grid not correct for {name}"
            
            print(f"✅ {name} handled correctly")
    
    def test_mixed_column_content(self):
        """Test columns with different types of content"""
        mixed_md = os.path.join(self.temp_dir, "mixed_columns.md")
        with open(mixed_md, 'w') as f:
            f.write("""# Mixed Column Content

::: {.column}
### Text Column
This is a regular text column with paragraphs.

Multiple paragraphs should work fine.
:::

::: {.column}
### Code Column
```python
def hello():
    print("Hello from code column")
    return True
```

More code:
```bash
echo "Command line"
ls -la
```
:::

::: {.column}
### List Column
- First item
- Second item
  - Nested item
  - Another nested
- Third item

Numbered list:

1. Numbered list
2. Second number
3. Third number
:::

::: {.column}
### Table Column
| Feature | Status |
|---------|--------|
| Columns | ✅ |
| Tables  | ✅ |
| Lists   | ✅ |
| Code    | ✅ |
:::
""")
        
        converter = MarkdownToPDF()
        html_file = os.path.join(self.temp_dir, "mixed_columns.html")
        pdf_file = os.path.join(self.temp_dir, "mixed_columns.pdf")
        
        converter.convert_to_html(mixed_md, html_file)
        converter.convert_to_pdf(mixed_md, pdf_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check that all content types are properly processed
        assert 'columns-4' in html_content, "Should have 4 columns"
        assert 'codehilite' in html_content, "Code blocks should be highlighted"
        assert '<table>' in html_content, "Tables should be processed"
        assert '<ul>' in html_content, "Unordered lists should be processed"
        assert '<ol>' in html_content, "Ordered lists should be processed"
        assert '<p>' in html_content, "Paragraphs should be processed"
        
        assert os.path.exists(pdf_file), "PDF not created"
        pdf_size = os.path.getsize(pdf_file)
        assert pdf_size > 20000, f"PDF too small: {pdf_size} bytes"
        
        print("✅ Mixed column content handled correctly")
    
    def test_column_edge_cases(self):
        """Test edge cases in column processing"""
        edge_cases = [
            ("Empty columns", """
::: {.column}
:::

::: {.column}
Content
:::
"""),
            ("Whitespace only", """
::: {.column}
   
   
:::

::: {.column}
Content
:::
"""),
            ("Nested markdown", """
::: {.column}
### Nested

> Blockquote with **bold** and *italic*

- List with `code`
- More items
:::

::: {.column}
### More Nested

```python
# Code with comment
def func():
    '''Docstring'''
    return [1, 2, 3]
```
:::
"""),
            ("Special characters", """
::: {.column}
### Special chars: ñáéíóú

Unicode: 🚀 🎨 📝

Math: α β γ δ ε
:::

::: {.column}
### More Special

Currency: $ € £ ¥

Symbols: © ™ ® ℠
:::
"""),
        ]
        
        for name, content in edge_cases:
            test_md = os.path.join(self.temp_dir, f"edge_{name.replace(' ', '_')}.md")
            with open(test_md, 'w') as f:
                f.write(f"# {name}\n{content}")
            
            converter = MarkdownToPDF()
            html_file = os.path.join(self.temp_dir, f"edge_{name.replace(' ', '_')}.html")
            
            # Should not crash with edge cases
            converter.convert_to_html(test_md, html_file)
            
            assert os.path.exists(html_file), f"HTML not created for {name}"
            
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            # Should have column layout
            assert 'columns-layout' in html_content, f"Column layout missing for {name}"
            
            print(f"✅ Edge case '{name}' handled correctly")
    
    def test_column_css_generation(self):
        """Test that column CSS is properly generated"""
        column_md = os.path.join(self.temp_dir, "css_test.md")
        with open(column_md, 'w') as f:
            f.write("""# CSS Test

::: {.column}
Column 1
:::

::: {.column}
Column 2
:::
""")
        
        converter = MarkdownToPDF()
        html_file = os.path.join(self.temp_dir, "css_test.html")
        
        converter.convert_to_html(column_md, html_file)
        
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check CSS rules are present
        assert '.columns-layout' in html_content, "Column layout CSS missing"
        assert '.columns-2' in html_content, "2-column CSS missing"
        assert '.columns-3' in html_content, "3-column CSS missing"
        assert '.columns-4' in html_content, "4-column CSS missing"
        assert '.columns-5' in html_content, "5-column CSS missing"
        assert '.column' in html_content, "Column CSS missing"
        assert 'display: grid' in html_content, "Grid display CSS missing"
        assert 'grid-template-columns' in html_content, "Grid template CSS missing"
        assert 'flex-direction: column' in html_content, "Flex direction CSS missing"
        
        print("✅ Column CSS generation works correctly")


def run_column_tests():
    """Run all column tests"""
    print("🏛️ Running Column Bug Tests...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ All column tests passed!")
        return True
    else:
        print("❌ Some column tests failed!")
        return False


if __name__ == "__main__":
    success = run_column_tests()
    exit(0 if success else 1)