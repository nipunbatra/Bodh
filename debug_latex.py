#!/usr/bin/env python3
"""Debug LaTeX functionality"""

import subprocess
from pathlib import Path
import tempfile

def test_latex():
    # Test LaTeX availability directly
    result = subprocess.run(['pdflatex', '--version'], capture_output=True, text=True)
    print('LaTeX available:', result.returncode == 0)

    if result.returncode == 0:
        # Test simple LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_content = r'''\documentclass{article}
\begin{document}
Hello World
\end{document}'''
            
            tex_file = Path(temp_dir) / 'test.tex'
            with open(tex_file, 'w') as f:
                f.write(tex_content)
            
            result = subprocess.run([
                'pdflatex', 
                '-interaction=nonstopmode',
                '-output-directory', temp_dir,
                str(tex_file)
            ], capture_output=True, text=True)
            
            print('Return code:', result.returncode)
            print('PDF exists:', (Path(temp_dir) / 'test.pdf').exists())
            if result.returncode != 0:
                print('STDERR:', result.stderr[:500])
                print('STDOUT:', result.stdout[:500])
            else:
                print('✅ Basic LaTeX works!')

if __name__ == '__main__':
    test_latex()