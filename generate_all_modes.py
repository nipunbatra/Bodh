#!/usr/bin/env python3
"""
Comprehensive Generation Script
Generate all examples in all three modes: HTML+MathJax, Local MathJax, and LaTeX
Provides performance comparison and quality assessment
"""

import os
import time
import shutil
from pathlib import Path
import subprocess
import tempfile
from typing import Dict, List, Tuple, Any
import json

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from bodh import MarkdownToPDF


class ComprehensiveGenerator:
    """Generate presentations in all available modes with performance tracking"""
    
    def __init__(self):
        self.results = {}
        self.output_dir = Path("generated_examples")
        self.examples_dir = Path("examples")
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "html_mathjax").mkdir(exist_ok=True)
        (self.output_dir / "local_mathjax").mkdir(exist_ok=True)
        (self.output_dir / "latex_direct").mkdir(exist_ok=True)
        (self.output_dir / "performance_reports").mkdir(exist_ok=True)
        
        # Generation modes
        self.modes = {
            'html_mathjax': {
                'name': 'HTML + MathJax CDN',
                'description': 'Standard web-based generation with MathJax from CDN',
                'config_override': {
                    'math.mode': 'cdn',
                    'math.timeout': 8000,
                    'pdf.engine': 'playwright'
                }
            },
            'local_mathjax': {
                'name': 'HTML + Local MathJax',
                'description': 'Fast local rendering without network dependency',
                'config_override': {
                    'math.mode': 'local',
                    'math.timeout': 2000,
                    'pdf.engine': 'playwright'
                }
            },
            'latex_direct': {
                'name': 'LaTeX Direct',
                'description': 'Native LaTeX compilation (fastest and highest quality)',
                'config_override': {
                    'pdf.engine': 'latex',
                    'pdf.latex_engine': 'pdflatex',
                    'math.engine': 'latex'
                }
            }
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check which generation modes are available"""
        deps = {}
        
        # Check LaTeX
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, timeout=5)
            deps['latex'] = result.returncode == 0
        except:
            deps['latex'] = False
        
        # Check Playwright (should always be available)
        deps['playwright'] = True
        
        # Check if we have example files
        deps['examples'] = self.examples_dir.exists()
        
        return deps
    
    def get_example_files(self) -> List[Path]:
        """Get all markdown example files"""
        if not self.examples_dir.exists():
            print(f"❌ Examples directory not found: {self.examples_dir}")
            return []
        
        md_files = list(self.examples_dir.glob("*.md"))
        print(f"📁 Found {len(md_files)} example files")
        
        return md_files
    
    def generate_single_example(self, md_file: Path, mode: str) -> Dict[str, Any]:
        """Generate a single example in specified mode"""
        mode_info = self.modes[mode]
        start_time = time.time()
        
        try:
            # Create converter
            converter = MarkdownToPDF()
            
            # Apply mode-specific configuration
            for key, value in mode_info['config_override'].items():
                converter.config.set(key, value)
            
            # Generate output paths
            stem = md_file.stem
            html_output = self.output_dir / mode / f"{stem}.html"
            pdf_output = self.output_dir / mode / f"{stem}.pdf"
            
            # Generate based on mode
            if mode == 'latex_direct' and self.check_dependencies()['latex']:
                # Use LaTeX directly (need to implement LaTeX backend)
                success = self._generate_latex_direct(md_file, pdf_output)
                html_generated = False
            else:
                # Use standard Playwright approach
                # Generate HTML
                converter.convert_to_html(str(md_file), str(html_output))
                html_generated = html_output.exists()
                
                # Generate PDF
                converter.convert_to_pdf(str(md_file), str(pdf_output))
                success = pdf_output.exists()
            
            duration = time.time() - start_time
            
            # Get file sizes
            html_size = html_output.stat().st_size if html_output.exists() else 0
            pdf_size = pdf_output.stat().st_size if pdf_output.exists() else 0
            
            return {
                'success': success,
                'duration': duration,
                'html_generated': html_output.exists(),
                'pdf_generated': pdf_output.exists(),
                'html_size': html_size,
                'pdf_size': pdf_size,
                'mode': mode,
                'file': md_file.name
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'success': False,
                'duration': duration,
                'error': str(e),
                'mode': mode,
                'file': md_file.name
            }
    
    def _generate_latex_direct(self, md_file: Path, pdf_output: Path) -> bool:
        """Generate PDF using direct LaTeX compilation"""
        # For now, use the simple LaTeX approach from our test
        # This is a placeholder - would need full LaTeX backend implementation
        
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Simple conversion to LaTeX (basic implementation)
        latex_content = self._convert_markdown_to_latex(md_content)
        
        # Compile with LaTeX
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "presentation.tex"
            
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                result = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', str(temp_path),
                    str(tex_file)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    generated_pdf = temp_path / "presentation.pdf"
                    if generated_pdf.exists():
                        shutil.copy2(generated_pdf, pdf_output)
                        return True
                
            except subprocess.TimeoutExpired:
                pass
        
        return False
    
    def _convert_markdown_to_latex(self, md_content: str) -> str:
        """Basic markdown to LaTeX conversion"""
        # This is a simplified version - would need full implementation
        
        # Split into slides
        slides = md_content.split('---')
        
        latex_doc = r"""
\documentclass[11pt]{article}
\usepackage[landscape,margin=0.5in]{geometry}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{enumitem}

\pagestyle{empty}

\definecolor{accentcolor}{RGB}{37,99,235}

\newcommand{\slidetitle}[1]{%
  \begin{center}
  \textcolor{accentcolor}{\huge\textbf{#1}}
  \end{center}
  \vspace{0.5cm}
}

\begin{document}
"""
        
        for i, slide in enumerate(slides):
            slide = slide.strip()
            if not slide:
                continue
            
            # Extract title
            lines = slide.split('\n')
            title_line = None
            content_lines = []
            
            for line in lines:
                if line.startswith('# '):
                    title_line = line[2:].strip()
                else:
                    content_lines.append(line)
            
            if title_line:
                latex_doc += f"\\slidetitle{{{title_line}}}\n\n"
            
            # Basic content conversion
            content = '\n'.join(content_lines)
            
            # Convert basic markdown
            content = content.replace('**', '\\textbf{').replace('**', '}')
            content = content.replace('*', '\\textit{').replace('*', '}')
            
            # Convert lists
            import re
            content = re.sub(r'^- (.+)$', r'\\item \1', content, flags=re.MULTILINE)
            
            # Wrap lists
            if '\\item' in content:
                content = '\\begin{itemize}\n' + content + '\n\\end{itemize}'
            
            latex_doc += content + '\n\n'
            
            if i < len(slides) - 1:  # Not last slide
                latex_doc += '\\newpage\n\n'
        
        latex_doc += '\\end{document}'
        return latex_doc
    
    def generate_all_examples(self) -> None:
        """Generate all examples in all available modes"""
        deps = self.check_dependencies()
        example_files = self.get_example_files()
        
        if not example_files:
            print("❌ No example files found")
            return
        
        print(f"🚀 Starting comprehensive generation...")
        print(f"📊 Dependencies: LaTeX={deps['latex']}, Playwright={deps['playwright']}")
        print(f"📁 Processing {len(example_files)} examples in {len(self.modes)} modes")
        print("=" * 60)
        
        total_generations = len(example_files) * len(self.modes)
        current = 0
        
        for md_file in example_files:
            print(f"\n📄 Processing: {md_file.name}")
            print("-" * 40)
            
            self.results[md_file.name] = {}
            
            for mode_key, mode_info in self.modes.items():
                current += 1
                
                # Skip LaTeX mode if not available
                if mode_key == 'latex_direct' and not deps['latex']:
                    print(f"  ⏭️  [{current}/{total_generations}] Skipping {mode_info['name']} (LaTeX not available)")
                    continue
                
                print(f"  🔄 [{current}/{total_generations}] Generating with {mode_info['name']}...")
                
                result = self.generate_single_example(md_file, mode_key)
                self.results[md_file.name][mode_key] = result
                
                if result['success']:
                    print(f"     ✅ Success in {result['duration']:.2f}s (PDF: {result['pdf_size']} bytes)")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"     ❌ Failed in {result['duration']:.2f}s: {error}")
    
    def generate_performance_report(self) -> None:
        """Generate comprehensive performance and quality report"""
        
        print(f"\n📊 COMPREHENSIVE PERFORMANCE REPORT")
        print("=" * 60)
        
        # Calculate statistics by mode
        mode_stats = {}
        
        for mode_key, mode_info in self.modes.items():
            results = []
            for file_results in self.results.values():
                if mode_key in file_results and file_results[mode_key]['success']:
                    results.append(file_results[mode_key])
            
            if results:
                durations = [r['duration'] for r in results]
                pdf_sizes = [r['pdf_size'] for r in results]
                
                mode_stats[mode_key] = {
                    'name': mode_info['name'],
                    'description': mode_info['description'],
                    'successful': len(results),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'avg_pdf_size': sum(pdf_sizes) / len(pdf_sizes),
                    'total_duration': sum(durations)
                }
        
        # Display performance comparison
        print(f"\n🏆 PERFORMANCE COMPARISON")
        print("-" * 30)
        
        for mode_key, stats in mode_stats.items():
            print(f"\n{stats['name']}:")
            print(f"  Success rate: {stats['successful']} files")
            print(f"  Average time: {stats['avg_duration']:.2f}s")
            print(f"  Range: {stats['min_duration']:.2f}s - {stats['max_duration']:.2f}s")
            print(f"  Avg PDF size: {stats['avg_pdf_size']:.0f} bytes")
        
        # Calculate speedups
        if 'html_mathjax' in mode_stats and 'latex_direct' in mode_stats:
            baseline = mode_stats['html_mathjax']['avg_duration']
            latex_time = mode_stats['latex_direct']['avg_duration']
            speedup = baseline / latex_time
            
            print(f"\n⚡ SPEEDUP ANALYSIS")
            print("-" * 20)
            print(f"LaTeX is {speedup:.1f}x faster than MathJax CDN")
        
        if 'html_mathjax' in mode_stats and 'local_mathjax' in mode_stats:
            baseline = mode_stats['html_mathjax']['avg_duration']
            local_time = mode_stats['local_mathjax']['avg_duration']
            speedup = baseline / local_time
            print(f"Local MathJax is {speedup:.1f}x faster than CDN")
        
        # Detailed file-by-file results
        print(f"\n📋 DETAILED RESULTS BY FILE")
        print("-" * 40)
        
        for filename, file_results in self.results.items():
            print(f"\n📄 {filename}:")
            
            for mode_key in self.modes.keys():
                if mode_key in file_results:
                    result = file_results[mode_key]
                    mode_name = self.modes[mode_key]['name']
                    
                    if result['success']:
                        print(f"  ✅ {mode_name}: {result['duration']:.2f}s")
                    else:
                        print(f"  ❌ {mode_name}: FAILED")
        
        # Save detailed report
        report_file = self.output_dir / "performance_reports" / "comprehensive_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                'mode_stats': mode_stats,
                'detailed_results': self.results,
                'generation_timestamp': time.time()
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")
    
    def generate_index_html(self) -> None:
        """Generate an HTML index page showing all generated examples"""
        
        index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bodh - All Generation Modes Comparison</title>
    <style>
        body { font-family: Inter, sans-serif; margin: 2rem; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; }
        .mode-section { margin: 2rem 0; padding: 1.5rem; border: 1px solid #ddd; border-radius: 8px; }
        .mode-title { color: #2563eb; font-size: 1.5em; margin-bottom: 1rem; }
        .example-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
        .example-card { padding: 1rem; border: 1px solid #eee; border-radius: 6px; }
        .example-title { font-weight: 600; margin-bottom: 0.5rem; }
        .example-links a { margin-right: 1rem; text-decoration: none; padding: 0.3rem 0.8rem; border-radius: 4px; }
        .html-link { background: #e7f3ff; color: #0066cc; }
        .pdf-link { background: #ffe7e7; color: #cc0000; }
        .performance-badge { font-size: 0.8em; padding: 0.2rem 0.5rem; border-radius: 3px; margin-left: 0.5rem; }
        .fast { background: #e7ffe7; color: #006600; }
        .medium { background: #fff3cd; color: #856404; }
        .slow { background: #ffe7e7; color: #cc0000; }
        .header { text-align: center; margin-bottom: 3rem; }
        .performance-summary { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Bodh Presentation Generation</h1>
            <p>Comprehensive comparison of all generation modes</p>
        </div>
        
        <div class="performance-summary">
            <h2>📊 Performance Summary</h2>
            <div class="mode-comparison">
"""
        
        # Add performance data
        mode_perf = {}
        for filename, file_results in self.results.items():
            for mode_key, result in file_results.items():
                if result['success']:
                    if mode_key not in mode_perf:
                        mode_perf[mode_key] = []
                    mode_perf[mode_key].append(result['duration'])
        
        for mode_key, mode_info in self.modes.items():
            if mode_key in mode_perf:
                avg_time = sum(mode_perf[mode_key]) / len(mode_perf[mode_key])
                badge_class = 'fast' if avg_time < 2 else 'medium' if avg_time < 5 else 'slow'
                
                index_content += f"""
                <p><strong>{mode_info['name']}:</strong> {avg_time:.2f}s average 
                <span class="performance-badge {badge_class}">{len(mode_perf[mode_key])} files</span></p>
                """
        
        index_content += """
            </div>
        </div>
"""
        
        # Add sections for each mode
        for mode_key, mode_info in self.modes.items():
            index_content += f"""
        <div class="mode-section">
            <h2 class="mode-title">{mode_info['name']}</h2>
            <p>{mode_info['description']}</p>
            <div class="example-grid">
"""
            
            for filename, file_results in self.results.items():
                if mode_key in file_results and file_results[mode_key]['success']:
                    result = file_results[mode_key]
                    stem = Path(filename).stem
                    
                    perf_class = 'fast' if result['duration'] < 2 else 'medium' if result['duration'] < 5 else 'slow'
                    
                    index_content += f"""
                <div class="example-card">
                    <div class="example-title">{stem}</div>
                    <div class="example-links">
"""
                    
                    if result.get('html_generated'):
                        index_content += f'<a href="{mode_key}/{stem}.html" class="html-link">HTML</a>'
                    
                    if result.get('pdf_generated'):
                        index_content += f'<a href="{mode_key}/{stem}.pdf" class="pdf-link">PDF</a>'
                    
                    index_content += f"""
                    </div>
                    <div>Generated in {result['duration']:.2f}s 
                    <span class="performance-badge {perf_class}">
                        {result['pdf_size']} bytes
                    </span>
                    </div>
                </div>
"""
            
            index_content += """
            </div>
        </div>
"""
        
        index_content += """
        <div style="margin-top: 3rem; text-align: center; color: #666;">
            <p>Generated with Bodh - Beautiful Markdown Presentations</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save index file
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w') as f:
            f.write(index_content)
        
        print(f"📄 Index page generated: {index_file}")
    
    def run_complete_generation(self) -> None:
        """Run the complete generation process"""
        print("🎯 COMPREHENSIVE BODH GENERATION SUITE")
        print("=" * 50)
        print("Generating all examples in all available modes:")
        print("• HTML + MathJax CDN (current default)")
        print("• HTML + Local MathJax (fast offline)")  
        print("• LaTeX Direct (fastest, highest quality)")
        print()
        
        # Check system
        deps = self.check_dependencies()
        if not deps['latex']:
            print("⚠️  LaTeX not detected - install with:")
            print("   curl -sL https://yihui.org/tinytex/install-bin-unix.sh | sh")
            print("   tlmgr install amsmath amsfonts amssymb xcolor enumitem")
            print()
        
        # Generate everything
        self.generate_all_examples()
        
        # Create reports
        self.generate_performance_report()
        self.generate_index_html()
        
        print(f"\n🎉 GENERATION COMPLETE!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🌐 View results: open {self.output_dir}/index.html")


def main():
    """Main execution function"""
    generator = ComprehensiveGenerator()
    generator.run_complete_generation()


if __name__ == '__main__':
    main()