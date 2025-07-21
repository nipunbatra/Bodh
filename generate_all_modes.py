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
                # Use LaTeX backend through the main bodh.py converter
                success = converter.convert_to_pdf(str(md_file), str(pdf_output))
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
    <title>Bodh - Multi-Mode Generation Comparison</title>
    <style>
        body { font-family: Inter, sans-serif; margin: 2rem; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 3rem; }
        .performance-summary { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; }
        .examples-section { margin: 2rem 0; }
        .example-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }
        .example-card { 
            padding: 1.5rem; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .example-title { 
            font-weight: 600; 
            font-size: 1.1em; 
            margin-bottom: 1rem; 
            color: #2563eb;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }
        .mode-versions { margin-bottom: 1rem; }
        .mode-version { 
            margin: 0.5rem 0; 
            padding: 0.5rem 0; 
            border-bottom: 1px dotted #e5e7eb;
        }
        .mode-version:last-child { border-bottom: none; }
        .mode-name { 
            font-weight: 500; 
            color: #374151; 
            margin-bottom: 0.3rem;
        }
        .version-links { margin-bottom: 0.3rem; }
        .version-links a { 
            margin-right: 0.8rem; 
            text-decoration: none; 
            padding: 0.3rem 0.6rem; 
            border-radius: 4px; 
            font-size: 0.9em;
        }
        .html-link { background: #e7f3ff; color: #0066cc; }
        .pdf-link { background: #ffe7e7; color: #cc0000; }
        .unavailable { color: #999; font-style: italic; }
        .performance-info { 
            font-size: 0.85em; 
            color: #6b7280; 
        }
        .performance-badge { 
            font-size: 0.8em; 
            padding: 0.2rem 0.4rem; 
            border-radius: 3px; 
            margin-left: 0.5rem; 
        }
        .fast { background: #e7ffe7; color: #006600; }
        .medium { background: #fff3cd; color: #856404; }
        .slow { background: #ffe7e7; color: #cc0000; }
        .mode-legend { margin: 1rem 0; font-size: 0.9em; color: #6b7280; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Bodh Multi-Mode Generation</h1>
            <p>Each example generated with all available modes for performance comparison</p>
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
        
        # Show performance comparison
        for mode_key, mode_info in self.modes.items():
            if mode_key in mode_perf:
                avg_time = sum(mode_perf[mode_key]) / len(mode_perf[mode_key])
                badge_class = 'fast' if avg_time < 2 else 'medium' if avg_time < 5 else 'slow'
                
                index_content += f"""
                <p><strong>{mode_info['name']}:</strong> {avg_time:.2f}s average 
                <span class="performance-badge {badge_class}">{len(mode_perf[mode_key])} files</span></p>
                """
        
        # Add speedup analysis
        if 'latex_direct' in mode_perf and 'html_mathjax' in mode_perf:
            latex_avg = sum(mode_perf['latex_direct']) / len(mode_perf['latex_direct'])
            mathjax_avg = sum(mode_perf['html_mathjax']) / len(mode_perf['html_mathjax'])
            speedup = mathjax_avg / latex_avg
            index_content += f"""
            <p><strong>⚡ LaTeX is {speedup:.1f}x faster than MathJax CDN</strong></p>
            """
        
        index_content += """
            </div>
            <div class="mode-legend">
                🟢 Fast (&lt;2s) | 🟡 Medium (2-5s) | 🔴 Slow (&gt;5s)
            </div>
        </div>
        
        <div class="examples-section">
            <h2>📄 Examples with All Modes</h2>
            <div class="example-grid">
"""
        
        # Generate example cards - one per example with all modes
        all_files = set()
        for filename in self.results.keys():
            all_files.add(filename)
        
        for filename in sorted(all_files):
            stem = Path(filename).stem
            file_results = self.results.get(filename, {})
            
            index_content += f"""
                <div class="example-card">
                    <div class="example-title">{stem}</div>
                    <div class="mode-versions">
"""
            
            # Show each mode for this example
            for mode_key, mode_info in self.modes.items():
                if mode_key in file_results:
                    result = file_results[mode_key]
                    
                    index_content += f"""
                        <div class="mode-version">
                            <div class="mode-name">{mode_info['name']}</div>
                            <div class="version-links">
"""
                    
                    if result['success']:
                        if result.get('html_generated'):
                            index_content += f'<a href="{mode_key}/{stem}.html" class="html-link">HTML</a>'
                        
                        if result.get('pdf_generated'):
                            index_content += f'<a href="{mode_key}/{stem}.pdf" class="pdf-link">PDF</a>'
                        
                        perf_class = 'fast' if result['duration'] < 2 else 'medium' if result['duration'] < 5 else 'slow'
                        
                        index_content += f"""
                            </div>
                            <div class="performance-info">
                                Generated in {result['duration']:.2f}s
                                <span class="performance-badge {perf_class}">
                                    {result['pdf_size']:,} bytes
                                </span>
                            </div>
"""
                    else:
                        index_content += """
                                <span class="unavailable">Failed to generate</span>
                            </div>
                            <div class="performance-info">
                                <span class="unavailable">Generation failed</span>
                            </div>
"""
                    
                    index_content += """
                        </div>
"""
            
            index_content += """
                    </div>
                </div>
"""
        
        index_content += """
            </div>
        </div>
        
        <div style="margin-top: 3rem; text-align: center; color: #666;">
            <p>Generated with Bodh - Beautiful Markdown Presentations</p>
            <p><small>Each example shows all available generation modes for direct comparison</small></p>
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