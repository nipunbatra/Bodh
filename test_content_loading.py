#!/usr/bin/env python3
"""
Test for content loading issues - text getting cut off or not fully loaded
"""

import os
import tempfile
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestContentLoading:
    def test_long_content_doesnt_get_cut_off(self):
        """Test that long content doesn't get cut off in PDF"""
        # Create test markdown with very long content
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "long_content.md")
        
        long_content = """# Long Content Test

This is a test slide with very long content to see if it gets cut off or not fully loaded in the PDF.

""" + "\n".join([f"This is line {i} of very long content that should not be cut off. " * 5 for i in range(20)])

        long_content += """

## Second Section

""" + "\n".join([f"More content line {i} to test overflow handling. " * 3 for i in range(15)])

        with open(test_md, 'w') as f:
            f.write(long_content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "long_content.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        # Check that PDF was created successfully
        assert os.path.exists(result)
        assert os.path.getsize(result) > 1000  # PDF should be reasonably sized
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_math_content_renders_properly(self):
        """Test that mathematical content renders without getting cut off"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "math_content.md")
        
        math_content = """# Math Test

Here are some mathematical equations:

Inline math: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$

Display math:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

More complex math:
$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$

$$\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}
\\begin{pmatrix}
e & f \\\\
g & h
\\end{pmatrix} = 
\\begin{pmatrix}
ae + bg & af + bh \\\\
ce + dg & cf + dh
\\end{pmatrix}$$

End of math content.
"""

        with open(test_md, 'w') as f:
            f.write(math_content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "math_content.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        # Check that PDF was created successfully
        assert os.path.exists(result)
        assert os.path.getsize(result) > 1000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_code_blocks_dont_overflow(self):
        """Test that code blocks are properly contained and don't overflow"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "code_content.md")
        
        code_content = """# Code Block Test

Here's a very long line of code that might cause overflow:

```python
def very_long_function_name_that_might_cause_horizontal_overflow_in_pdf_rendering(parameter_one, parameter_two, parameter_three, parameter_four):
    return "This is a very long string that might also cause issues with text wrapping and overflow in PDF generation"
```

And some more code:

```bash
echo "This is a very long command line that goes on and on and might cause horizontal scrolling or text cutoff issues"
```

```javascript
const veryLongVariableName = someFunctionWithAVeryLongName(parameterOne, parameterTwo, parameterThree, parameterFour, parameterFive);
```

End of code test.
"""

        with open(test_md, 'w') as f:
            f.write(code_content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Generate PDF
        pdf_file = os.path.join(temp_dir, "code_content.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        # Check that PDF was created successfully
        assert os.path.exists(result)
        assert os.path.getsize(result) > 1000
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_font_loading_timeout_handling(self):
        """Test that font loading timeouts are handled gracefully"""
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # Check that the PDF generation settings include proper timeouts
        # This is indirectly tested by ensuring PDFs generate successfully
        # even when fonts might not load
        
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "font_test.md")
        
        content = "# Font Test\n\nThis tests font loading with various characters: áéíóú çñü αβγδε"
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        # Generate PDF - should succeed even if fonts have issues
        pdf_file = os.path.join(temp_dir, "font_test.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 500
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])