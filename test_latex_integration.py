#!/usr/bin/env python3
"""
Test LaTeX integration directly
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bodh import MarkdownToPDF


def test_latex_direct():
    """Test LaTeX direct mode"""
    
    print("🧪 Testing LaTeX Direct Integration")
    print("=" * 40)
    
    # Create converter
    converter = MarkdownToPDF()
    
    # Check LaTeX availability
    print(f"LaTeX available: {converter.latex_available}")
    
    if not converter.latex_available:
        print("❌ LaTeX not available - please install LaTeX")
        return False
    
    # Manually set PDF engine to LaTeX
    converter.config.config['pdf'] = {
        'engine': 'latex',
        'latex_engine': 'pdflatex',
        'latex_passes': 2
    }
    
    # Test with simple content
    test_file = "examples/math-demo.md"
    output_file = "test_latex_output.pdf"
    
    print(f"Converting {test_file} to {output_file}")
    
    try:
        print(f"Using PDF engine: {converter.config.config.get('pdf', {}).get('engine', 'default')}")
        result = converter.convert_to_pdf(test_file, output_file)
        
        print(f"Conversion result: {result}")
        
        if result:
            print(f"✅ Success! Generated: {output_file}")
            
            # Check file size
            output_path = Path(output_file)
            if output_path.exists():
                size = output_path.stat().st_size
                print(f"📄 File size: {size} bytes")
                return True
            else:
                print("❌ PDF file not found after generation")
                return False
        else:
            print("❌ LaTeX generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_comparison():
    """Quick performance comparison"""
    import time
    
    print("\n⚡ Performance Comparison")
    print("-" * 30)
    
    converter = MarkdownToPDF()
    test_file = "examples/math-demo.md"
    
    if converter.latex_available:
        # Test LaTeX mode
        converter.config.config['pdf'] = {'engine': 'latex'}
        start_time = time.time()
        result = converter.convert_to_pdf(test_file, "perf_test_latex.pdf")
        latex_time = time.time() - start_time
        
        if result:
            print(f"LaTeX mode: {latex_time:.2f}s")
        else:
            print("LaTeX mode: FAILED")
    
    # Test MathJax mode
    converter.config.config['pdf'] = {'engine': 'playwright'}
    converter.config.config['math'] = {'mode': 'local', 'timeout': 2000}
    start_time = time.time()
    result = converter.convert_to_pdf(test_file, "perf_test_mathjax.pdf")
    mathjax_time = time.time() - start_time
    
    if result:
        print(f"MathJax mode: {mathjax_time:.2f}s")
        
        if converter.latex_available and latex_time:
            speedup = mathjax_time / latex_time
            print(f"Speedup: {speedup:.1f}x faster with LaTeX")
    else:
        print("MathJax mode: FAILED")


if __name__ == '__main__':
    success = test_latex_direct()
    
    if success:
        test_performance_comparison()
        print("\n🎉 LaTeX integration test completed!")
    else:
        print("\n❌ LaTeX integration test failed!")