#!/usr/bin/env python3
"""
LaTeX-based PDF Generation Engine
Alternative to MathJax/browser-based PDF generation using native LaTeX
"""

import os
import re
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import markdown
from markdown.extensions import codehilite, tables, toc


class LaTeXPDFEngine:
    """LaTeX-based PDF generation engine for presentations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.latex_available = self._check_latex_availability()
        
    def _check_latex_availability(self) -> bool:
        """Check if LaTeX is available on the system"""
        # Try different LaTeX engines in order of preference
        engines = ['lualatex', 'xelatex', 'pdflatex']
        
        for engine in engines:
            try:
                result = subprocess.run([engine, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.latex_engine = engine
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return False
    
    def is_available(self) -> bool:
        """Check if LaTeX engine can be used"""
        return self.latex_available
    
    def convert_markdown_to_pdf(self, markdown_file: str, output_file: str) -> bool:
        """Convert markdown file to PDF using LaTeX"""
        if not self.latex_available:
            raise RuntimeError("LaTeX not available on system. Install texlive or similar.")
        
        try:
            # Read markdown content
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Parse slides
            slides = self._parse_slides(md_content)
            
            # Generate LaTeX
            latex_content = self._generate_latex(slides)
            
            # Compile to PDF
            return self._compile_latex_to_pdf(latex_content, output_file)
            
        except Exception as e:
            print(f"LaTeX conversion failed: {e}")
            return False
    
    def _parse_slides(self, md_content: str) -> List[Dict[str, str]]:
        """Parse markdown content into slides"""
        # Split by slide separators
        slide_contents = re.split(r'^---\s*$', md_content, flags=re.MULTILINE)
        
        slides = []
        for i, content in enumerate(slide_contents):
            content = content.strip()
            if not content:
                continue
                
            # Extract title (first heading)
            title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else f"Slide {i+1}"
            
            # Remove title from content for body
            if title_match:
                body = re.sub(r'^#\s+.+$', '', content, count=1, flags=re.MULTILINE).strip()
            else:
                body = content
            
            slides.append({
                'title': title,
                'content': body,
                'number': i + 1
            })
        
        return slides
    
    def _generate_latex(self, slides: List[Dict[str, str]]) -> str:
        """Generate LaTeX document from slides"""
        
        # Get theme colors and settings
        theme = self.config.get('theme', {})
        colors = theme.get('colors', {})
        font_family = self.config.get('font', {}).get('family', 'sans')
        
        # LaTeX preamble
        latex_content = self._get_latex_preamble()
        
        # Document start
        latex_content += "\\begin{document}\n\n"
        
        # Generate slides
        for slide in slides:
            latex_content += self._generate_slide_latex(slide)
            latex_content += "\n\\newpage\n\n"
        
        # Remove last newpage
        latex_content = latex_content.rstrip("\\newpage\n\n")
        
        # Document end
        latex_content += "\n\\end{document}"
        
        return latex_content
    
    def _get_latex_preamble(self) -> str:
        """Generate LaTeX preamble with packages and settings"""
        theme = self.config.get('theme', {})
        colors = theme.get('colors', {})
        
        # Convert hex colors to LaTeX format
        bg_color = self._hex_to_latex_color(colors.get('background', '#ffffff'))
        text_color = self._hex_to_latex_color(colors.get('text', '#000000'))
        accent_color = self._hex_to_latex_color(colors.get('accent', '#2563eb'))
        
        # Use simplified preamble that works with pdflatex
        preamble = f"""\\documentclass[11pt]{{article}}

% Packages
\\usepackage[landscape,margin=0.5in]{{geometry}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{xcolor}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{enumitem}}
\\usepackage{{listings}}
\\usepackage{{graphicx}}

% Colors
\\definecolor{{bgcolor}}{{{bg_color}}}
\\definecolor{{textcolor}}{{{text_color}}}
\\definecolor{{accentcolor}}{{{accent_color}}}

% Page setup
\\pagecolor{{bgcolor}}
\\color{{textcolor}}
\\pagestyle{{empty}}

% Custom commands
\\newcommand{{\\slidetitle}}[1]{{%
  \\begin{{center}}
  \\textcolor{{accentcolor}}{{\\huge\\textbf{{#1}}}}
  \\end{{center}}
  \\vspace{{0.5cm}}
}}

% Math setup
\\everymath{{\\displaystyle}}

% List styling
\\setlist[itemize]{{leftmargin=1cm,itemsep=0.3cm}}
\\renewcommand{{\\labelitemi}}{{\\textcolor{{accentcolor}}{{\\textbullet}}}}

% Code styling
\\lstset{{
  backgroundcolor=\\color{{gray!10}},
  basicstyle=\\ttfamily\\small,
  keywordstyle=\\color{{accentcolor}}\\bfseries,
  stringstyle=\\color{{green!60!black}},
  commentstyle=\\color{{gray}},
  showstringspaces=false,
  breaklines=true,
  frame=single,
  rulecolor=\\color{{gray!30}}
}}

"""
        return preamble
    
    def _hex_to_latex_color(self, hex_color: str) -> str:
        """Convert hex color to LaTeX RGB format"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return "RGB{0,0,0}"  # Default to black
        
        try:
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255  
            b = int(hex_color[4:6], 16) / 255
            return f"RGB{{{r:.3f},{g:.3f},{b:.3f}}}"
        except ValueError:
            return "RGB{0,0,0}"
    
    def _generate_slide_latex(self, slide: Dict[str, str]) -> str:
        """Generate LaTeX for a single slide"""
        title = slide['title']
        content = slide['content']
        
        # Convert markdown to LaTeX
        latex_content = self._markdown_to_latex(content)
        
        slide_latex = f"""
\\slidetitle{{{title}}}

{latex_content}

\\vfill
\\begin{{flushright}}
\\textcolor{{gray}}{{\\small {slide['number']}}}
\\end{{flushright}}
"""
        
        return slide_latex
    
    def _markdown_to_latex(self, md_content: str) -> str:
        """Convert markdown content to LaTeX"""
        
        # Handle math equations (already in LaTeX format)
        # Inline math: $...$ stays as $...$
        # Display math: $$...$$ becomes \\[...\\]
        content = re.sub(r'\\$\\$(.+?)\\$\\$', r'\\\\[\\1\\\\]', md_content, flags=re.DOTALL)
        
        # Headers
        content = re.sub(r'^### (.+)$', r'\\textbf{\\Large \\1}\\\\[0.3cm]', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'\\textbf{\\huge \\1}\\\\[0.5cm]', content, flags=re.MULTILINE)
        
        # Bold and italic
        content = re.sub(r'\\*\\*(.+?)\\*\\*', r'\\textbf{\\1}', content)
        content = re.sub(r'\\*(.+?)\\*', r'\\textit{\\1}', content)
        
        # Lists
        content = re.sub(r'^- (.+)$', r'\\item \\1', content, flags=re.MULTILINE)
        
        # Wrap lists in itemize environment
        lines = content.split('\\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('\\item'):
                if not in_list:
                    result_lines.append('\\begin{itemize}')
                    in_list = True
                result_lines.append(line)
            else:
                if in_list:
                    result_lines.append('\\end{itemize}')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('\\end{itemize}')
        
        content = '\\n'.join(result_lines)
        
        # Code blocks
        content = re.sub(r'```(\\w+)?\\n(.+?)\\n```', 
                        r'\\begin{lstlisting}\\n\\2\\n\\end{lstlisting}', 
                        content, flags=re.DOTALL)
        
        # Inline code
        content = re.sub(r'`(.+?)`', r'\\texttt{\\1}', content)
        
        # Paragraphs (double newlines)
        content = re.sub(r'\\n\\n', r'\\\\[0.3cm]\\n', content)
        
        return content
    
    def _compile_latex_to_pdf(self, latex_content: str, output_file: str) -> bool:
        """Compile LaTeX content to PDF"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Write LaTeX file
            tex_file = temp_dir_path / "presentation.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # Run LaTeX with detected engine
                latex_cmd = getattr(self, 'latex_engine', 'pdflatex')
                result = subprocess.run([
                    latex_cmd, 
                    '-interaction=nonstopmode',
                    '-output-directory', str(temp_dir_path),
                    str(tex_file)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    print(f"LaTeX compilation failed:")
                    print(result.stdout)
                    print(result.stderr)
                    return False
                
                # Copy output PDF
                pdf_file = temp_dir_path / "presentation.pdf"
                if pdf_file.exists():
                    shutil.copy2(pdf_file, output_file)
                    return True
                else:
                    print("LaTeX compilation succeeded but no PDF generated")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("LaTeX compilation timed out")
                return False
            except Exception as e:
                print(f"LaTeX compilation error: {e}")
                return False


def test_latex_engine():
    """Test the LaTeX engine"""
    
    # Sample configuration
    config = {
        'theme': {
            'colors': {
                'background': '#ffffff',
                'text': '#1a1a1a', 
                'accent': '#2563eb'
            }
        },
        'font': {
            'family': 'Inter'
        }
    }
    
    # Create test markdown
    test_md = '''# LaTeX Engine Test

This is a test of the LaTeX PDF generation engine.

---

# Mathematics Support

Inline math: $E = mc^2$ and $\\pi \\approx 3.14159$

Display math:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

Greek letters: $\\alpha + \\beta = \\gamma$

---

# Lists and Formatting

- **Bold text** and *italic text*
- Mathematical expressions: $f(x) = ax^2 + bx + c$
- Code: `print("Hello World")`

## Subsection

More content here.

---

# Code Example

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

The Fibonacci sequence is mathematically defined as:
$$F(n) = F(n-1) + F(n-2)$$
'''
    
    # Test the engine
    engine = LaTeXPDFEngine(config)
    
    print(f"LaTeX available: {engine.is_available()}")
    
    if engine.is_available():
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_md)
            temp_md = f.name
        
        try:
            output_pdf = "latex_test.pdf"
            success = engine.convert_markdown_to_pdf(temp_md, output_pdf)
            
            if success:
                print(f"✅ LaTeX PDF generated: {output_pdf}")
            else:
                print("❌ LaTeX PDF generation failed")
                
        finally:
            os.unlink(temp_md)
    else:
        print("⚠️  LaTeX not available - install texlive or similar")


if __name__ == '__main__':
    test_latex_engine()