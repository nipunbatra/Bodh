#!/usr/bin/env python3
"""
Simple LaTeX Test - Direct Performance Comparison
Test if LaTeX can provide faster PDF generation than MathJax
"""

import os
import time
import tempfile
import subprocess
from pathlib import Path


def test_simple_latex():
    """Test simple LaTeX compilation"""
    
    # Simple LaTeX document
    latex_content = r"""
\documentclass[11pt]{article}
\usepackage[landscape,margin=0.5in]{geometry}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}

\pagestyle{empty}

\begin{document}

\begin{center}
\huge\textbf{LaTeX Test}
\end{center}

\vspace{1cm}

This is a simple test of LaTeX compilation speed.

Mathematics work perfectly:
$$E = mc^2$$

Inline math: $\pi \approx 3.14159$ and $\alpha + \beta = \gamma$

Complex equations:
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

Lists work:
\begin{itemize}
\item First item
\item Second item with math: $f(x) = ax^2 + bx + c$
\item Third item
\end{itemize}

\newpage

\begin{center}
\huge\textbf{Second Slide}
\end{center}

\vspace{1cm}

More content here.

$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$

Matrix example:
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix}$$

\end{document}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Write LaTeX file
        tex_file = temp_dir_path / "simple_test.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print("Testing LaTeX compilation speed...")
        start_time = time.time()
        
        try:
            # Try pdflatex first (most common)
            result = subprocess.run([
                'pdflatex', 
                '-interaction=nonstopmode',
                '-output-directory', str(temp_dir_path),
                str(tex_file)
            ], capture_output=True, text=True, timeout=30)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                pdf_file = temp_dir_path / "simple_test.pdf"
                if pdf_file.exists():
                    file_size = pdf_file.stat().st_size
                    print(f"✅ LaTeX Success: {duration:.2f}s ({file_size} bytes)")
                    
                    # Copy to current directory for inspection
                    import shutil
                    shutil.copy2(pdf_file, "latex_speed_test.pdf")
                    print("📄 PDF saved as: latex_speed_test.pdf")
                    return duration
                else:
                    print("❌ LaTeX compilation succeeded but no PDF found")
            else:
                print(f"❌ LaTeX compilation failed:")
                print(result.stdout[-500:])  # Last 500 chars
                print(result.stderr[-500:])
        
        except subprocess.TimeoutExpired:
            print("❌ LaTeX compilation timed out")
        except Exception as e:
            print(f"❌ LaTeX error: {e}")
    
    return None


def test_pandoc_alternative():
    """Test pandoc as an alternative"""
    
    markdown_content = """# LaTeX Test

This is a simple test of pandoc speed.

Mathematics work perfectly:
$$E = mc^2$$

Inline math: $\pi \approx 3.14159$ and $\alpha + \beta = \gamma$

Complex equations:
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

Lists work:
- First item
- Second item with math: $f(x) = ax^2 + bx + c$
- Third item

---

# Second Slide

More content here.

$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$

Matrix example:
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix}$$
"""
    
    # Check if pandoc is available
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, timeout=5)
    except:
        print("⚠️  Pandoc not available - skipping test")
        return None
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        md_file = f.name
    
    try:
        print("\nTesting Pandoc compilation speed...")
        start_time = time.time()
        
        output_pdf = "pandoc_speed_test.pdf"
        result = subprocess.run([
            'pandoc', md_file,
            '--pdf-engine=pdflatex',
            '-o', output_pdf
        ], capture_output=True, text=True, timeout=30)
        
        duration = time.time() - start_time
        
        if result.returncode == 0 and os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✅ Pandoc Success: {duration:.2f}s ({file_size} bytes)")
            print("📄 PDF saved as: pandoc_speed_test.pdf")
            return duration
        else:
            print(f"❌ Pandoc failed:")
            print(result.stderr[-300:])
    
    except subprocess.TimeoutExpired:
        print("❌ Pandoc timed out")
    except Exception as e:
        print(f"❌ Pandoc error: {e}")
    
    finally:
        os.unlink(md_file)
    
    return None


def main():
    """Compare LaTeX approaches with MathJax baseline"""
    
    print("🚀 LaTeX vs MathJax Performance Comparison")
    print("=" * 50)
    
    # Test LaTeX approaches
    latex_time = test_simple_latex()
    pandoc_time = test_pandoc_alternative()
    
    # Show comparison with MathJax baseline
    print(f"\n📊 PERFORMANCE COMPARISON")
    print("-" * 30)
    
    # From our previous test, MathJax takes ~9.5s
    mathjax_baseline = 9.5
    print(f"MathJax (current): {mathjax_baseline:.1f}s")
    
    if latex_time:
        speedup = mathjax_baseline / latex_time
        print(f"LaTeX direct:       {latex_time:.1f}s ({speedup:.1f}x faster)")
    
    if pandoc_time:
        speedup = mathjax_baseline / pandoc_time
        print(f"Pandoc:             {pandoc_time:.1f}s ({speedup:.1f}x faster)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if latex_time and latex_time < 3:
        print("🚀 LaTeX is MUCH faster than MathJax!")
        print("   Consider implementing LaTeX backend for PDF generation")
    elif pandoc_time and pandoc_time < 3:
        print("🚀 Pandoc is MUCH faster than MathJax!")
        print("   Consider using Pandoc for PDF generation")
    else:
        print("🔍 LaTeX speeds need investigation")
        print("   Check LaTeX installation and packages")
    
    if latex_time or pandoc_time:
        print(f"\n🎯 IMPLEMENTATION STRATEGY:")
        print("1. Add LaTeX backend option to config")
        print("2. Implement markdown → LaTeX conversion")
        print("3. Use LaTeX for PDF, keep MathJax for HTML")
        print("4. Benefits: Faster, offline, better math quality")


if __name__ == '__main__':
    main()