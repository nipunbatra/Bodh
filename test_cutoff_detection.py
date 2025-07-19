#!/usr/bin/env python3
"""
Test content cutoff detection and warnings
"""

import os
import tempfile
import pytest
from bodh import MarkdownToPDF
from config import load_config


class TestCutoffDetection:
    def test_very_long_lines_trigger_warning(self):
        """Test that very long lines trigger warnings about potential cutoffs"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "long_lines.md")
        
        # Create content with extremely long lines
        long_line = "This is an extremely long line that might cause horizontal overflow issues in PDF generation and should trigger a warning to the user about potential content cutoffs " * 10
        
        content = f"""# Long Line Test

{long_line}

## Code with Long Lines

```python
def extremely_long_function_name_that_might_cause_issues(very_long_parameter_name_one, very_long_parameter_name_two, very_long_parameter_name_three, very_long_parameter_name_four):
    return "This function name and line is so long that it will definitely cause overflow issues and should be detected and warned about"
```

More text after the long content.
"""
        
        with open(test_md, 'w') as f:
            f.write(content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        # This should generate warnings about long content
        pdf_file = os.path.join(temp_dir, "long_lines.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)

    def test_oversized_content_detection(self):
        """Test detection of content that exceeds slide boundaries"""
        temp_dir = tempfile.mkdtemp()
        test_md = os.path.join(temp_dir, "oversized.md")
        
        # Create content that's very likely to overflow
        massive_content = """# Massive Content Test

""" + "\n".join([f"Line {i}: " + ("Very long content that keeps going and going " * 20) for i in range(50)])

        with open(test_md, 'w') as f:
            f.write(massive_content)
        
        config = load_config('configs/logo-demo.yml')
        converter = MarkdownToPDF(config=config)
        
        pdf_file = os.path.join(temp_dir, "oversized.pdf")
        result = converter.convert_to_pdf(test_md, pdf_file)
        
        assert os.path.exists(result)
        
        # Clean up
        os.unlink(test_md)
        os.unlink(pdf_file)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])