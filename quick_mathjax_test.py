#!/usr/bin/env python3
"""
Quick MathJax Performance Test
Simple test to compare different approaches and provide recommendations
"""

import os
import time
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bodh import MarkdownToPDF


def test_math_performance():
    """Quick test of MathJax performance with different modes"""
    
    # Test content with various math complexities
    test_cases = {
        'simple': """# Simple Math
Inline: $E = mc^2$ and $\\pi \\approx 3.14$
Display: $$\\sum_{i=1}^n x_i$$
Greek: $\\alpha + \\beta = \\gamma$
""",
        'medium': """# Medium Math
$$\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$$
$$\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$$
$$P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}$$
""",
        'heavy': """# Heavy Math
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$
$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$
$$\\nabla \\times \\mathbf{B} = \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}$$
"""
    }
    
    print("⚡ Quick MathJax Performance Test")
    print("=" * 50)
    
    results = {}
    
    for case_name, content in test_cases.items():
        print(f"\n🧪 Testing {case_name} math content...")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Test with default settings
            start_time = time.time()
            
            converter = MarkdownToPDF()
            output_file = temp_file.replace('.md', '.pdf')
            
            # Generate PDF
            converter.convert_to_pdf(temp_file, output_file)
            
            duration = time.time() - start_time
            success = os.path.exists(output_file)
            file_size = os.path.getsize(output_file) if success else 0
            
            results[case_name] = {
                'duration': duration,
                'success': success,
                'file_size': file_size
            }
            
            if success:
                print(f"  ✅ Success in {duration:.2f}s ({file_size} bytes)")
                os.unlink(output_file)
            else:
                print(f"  ❌ Failed after {duration:.2f}s")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[case_name] = {
                'duration': None,
                'success': False,
                'file_size': 0,
                'error': str(e)
            }
        
        finally:
            os.unlink(temp_file)
    
    # Summary and recommendations
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results.values() if r['success']]
    total_tests = len(results)
    success_rate = len(successful_tests) / total_tests * 100
    
    print(f"Success rate: {len(successful_tests)}/{total_tests} ({success_rate:.1f}%)")
    
    if successful_tests:
        durations = [r['duration'] for r in successful_tests]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"Average time: {avg_duration:.2f}s")
        print(f"Range: {min_duration:.2f}s - {max_duration:.2f}s")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 30)
        
        if max_duration > 15:
            print("⚠️  SLOW: Consider switching to local MathJax mode")
            print("   Add to config: math.mode = 'local'")
            
        elif max_duration > 8:
            print("🔶 MODERATE: Current performance acceptable")
            print("   Consider local mode for production use")
            
        else:
            print("✅ FAST: Current settings work well")
        
        if success_rate < 90:
            print("⚠️  RELIABILITY: Consider adding fallback")
            print("   Add to config: math.fallback = 'local'")
        else:
            print("✅ RELIABLE: Good success rate")
        
        # Network dependency warning
        if any(r['duration'] and r['duration'] > 5 for r in successful_tests):
            print("\n🌐 NETWORK DEPENDENCY DETECTED")
            print("   Current setup depends on MathJax CDN")
            print("   For offline use, switch to local mode")
            print("   Or implement caching for better performance")
    
    else:
        print("❌ All tests failed - check your setup")
        
        # Show errors
        errors = [r.get('error') for r in results.values() if r.get('error')]
        if errors:
            print("\nErrors encountered:")
            for error in set(errors):  # Remove duplicates
                print(f"  - {error}")
    
    return results


def test_no_math_baseline():
    """Test baseline performance without math"""
    print(f"\n🔧 Testing baseline (no math)...")
    
    content = """# No Math Test
Regular text content without mathematical formulas.
Just plain markdown with lists and formatting.

- Point 1
- Point 2  
- Point 3

**Bold text** and *italic text*.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_file = f.name
    
    try:
        start_time = time.time()
        
        converter = MarkdownToPDF()
        # Disable math for baseline
        converter.config.config['math']['enabled'] = False
        
        output_file = temp_file.replace('.md', '.pdf')
        converter.convert_to_pdf(temp_file, output_file)
        
        duration = time.time() - start_time
        success = os.path.exists(output_file)
        
        if success:
            print(f"  ✅ Baseline: {duration:.2f}s (no math)")
            os.unlink(output_file)
            return duration
        else:
            print(f"  ❌ Baseline failed")
            return None
            
    except Exception as e:
        print(f"  ❌ Baseline error: {e}")
        return None
    
    finally:
        os.unlink(temp_file)


def main():
    """Run quick performance test"""
    print("🚀 Starting Quick MathJax Performance Analysis...\n")
    
    # Test baseline performance
    baseline_duration = test_no_math_baseline()
    
    # Test math performance
    math_results = test_math_performance()
    
    # Calculate overhead
    if baseline_duration and math_results:
        successful_math = [r for r in math_results.values() if r['success']]
        if successful_math:
            avg_math_duration = sum(r['duration'] for r in successful_math) / len(successful_math)
            overhead = avg_math_duration - baseline_duration
            
            print(f"\n⚡ PERFORMANCE ANALYSIS")
            print("-" * 30)
            print(f"Baseline (no math): {baseline_duration:.2f}s")
            print(f"Average with math:  {avg_math_duration:.2f}s")
            print(f"MathJax overhead:   {overhead:.2f}s")
            
            if overhead > 8:
                print("🔴 HIGH OVERHEAD - Strongly recommend local MathJax")
            elif overhead > 3:
                print("🟡 MODERATE OVERHEAD - Consider local MathJax")
            else:
                print("🟢 LOW OVERHEAD - Current setup OK")
    
    print(f"\n✅ Quick test completed!")


if __name__ == '__main__':
    main()