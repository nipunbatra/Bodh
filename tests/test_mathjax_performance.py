#!/usr/bin/env python3
"""
Comprehensive MathJax Performance and Reliability Tests
Tests different MathJax loading strategies and measures performance
"""

import os
import time
import tempfile
import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bodh import MarkdownToPDF


class TestMathJaxPerformance:
    """Test MathJax performance and reliability across different scenarios"""
    
    @pytest.fixture
    def sample_math_content(self):
        """Sample content with various math complexities"""
        return {
            'simple': """# Simple Math Test

Inline math: $E = mc^2$ and $\pi \approx 3.14159$

Display math:
$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
""",
            'complex': """# Complex Math Test

## Advanced Equations

Matrix multiplication:
$$\begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} ax + by \\ cx + dy \end{bmatrix}$$

Calculus:
$$\frac{\partial}{\partial x} \int_0^x f(t) dt = f(x)$$

Statistics:
$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

Greek letters: $\alpha, \beta, \gamma, \delta, \epsilon, \zeta, \eta, \theta$
""",
            'heavy': """# Heavy Math Test

## Multiple Complex Equations

$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$

$$\oint_C \mathbf{F} \cdot d\mathbf{r} = \iint_S (\nabla \times \mathbf{F}) \cdot d\mathbf{S}$$

$$\int_{-\infty}^{\infty} \frac{\sin(x)}{x} dx = \pi$$

$$\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = e$$

$$\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}$$

$$\psi(x,t) = \sum_{n=1}^{\infty} c_n \phi_n(x) e^{-iE_n t/\hbar}$$
""",
            'mixed': """# Mixed Content with Math

## Introduction
This presentation combines text, lists, and mathematics.

- Point 1: $f(x) = ax^2 + bx + c$
- Point 2: The derivative is $f'(x) = 2ax + b$  
- Point 3: Integration gives us $\int f(x) dx = \frac{a}{3}x^3 + \frac{b}{2}x^2 + cx + C$

## Detailed Analysis

The quadratic formula:
$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$

Where:
- $a \neq 0$ (coefficient of $x^2$)
- $b$ = coefficient of $x$
- $c$ = constant term
"""
        }
    
    def test_mathjax_timeout_scenarios(self, sample_math_content):
        """Test MathJax loading under different timeout scenarios"""
        results = {}
        
        for complexity, content in sample_math_content.items():
            print(f"\nTesting {complexity} math content...")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                # Test with current timeout (8s)
                start_time = time.time()
                converter = MarkdownToPDF()
                converter.config['math']['enabled'] = True
                
                # Generate PDF and measure time
                output_file = temp_file.replace('.md', '.pdf')
                converter.convert_file(temp_file, output_file)
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[complexity] = {
                    'duration': duration,
                    'success': os.path.exists(output_file),
                    'file_size': os.path.getsize(output_file) if os.path.exists(output_file) else 0
                }
                
                print(f"  {complexity}: {duration:.2f}s, success: {results[complexity]['success']}")
                
                # Cleanup
                if os.path.exists(output_file):
                    os.unlink(output_file)
                    
            except Exception as e:
                results[complexity] = {
                    'duration': None,
                    'success': False,
                    'error': str(e)
                }
                print(f"  {complexity}: FAILED - {e}")
            
            finally:
                os.unlink(temp_file)
        
        # Analyze results
        successful_tests = sum(1 for r in results.values() if r['success'])
        total_tests = len(results)
        avg_duration = sum(r['duration'] for r in results.values() if r['duration']) / successful_tests if successful_tests > 0 else 0
        
        print(f"\nMathJax Performance Summary:")
        print(f"  Success rate: {successful_tests}/{total_tests} ({100*successful_tests/total_tests:.1f}%)")
        print(f"  Average duration: {avg_duration:.2f}s")
        
        # Assert reasonable performance
        assert successful_tests >= total_tests * 0.8, f"Too many MathJax failures: {successful_tests}/{total_tests}"
        assert avg_duration < 15.0, f"MathJax too slow: {avg_duration:.2f}s average"
    
    def test_mathjax_reliability_stress(self):
        """Stress test MathJax reliability with rapid generation"""
        print("\nRunning MathJax reliability stress test...")
        
        math_content = """# Stress Test

$$\\sum_{i=1}^{n} x_i = x_1 + x_2 + \\cdots + x_n$$

Inline: $\\alpha + \\beta = \\gamma$
"""
        
        successes = 0
        failures = 0
        total_time = 0
        
        for i in range(5):  # Reduced for faster testing
            print(f"  Iteration {i+1}/5...")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(math_content)
                temp_file = f.name
            
            try:
                start_time = time.time()
                converter = MarkdownToPDF()
                converter.config['math']['enabled'] = True
                
                output_file = temp_file.replace('.md', f'_stress_{i}.pdf')
                converter.convert_file(temp_file, output_file)
                
                duration = time.time() - start_time
                total_time += duration
                
                if os.path.exists(output_file):
                    successes += 1
                    os.unlink(output_file)
                else:
                    failures += 1
                    
            except Exception as e:
                failures += 1
                print(f"    Failed: {e}")
            
            finally:
                os.unlink(temp_file)
        
        success_rate = successes / (successes + failures) * 100
        avg_time = total_time / (successes + failures)
        
        print(f"  Stress test results: {successes} successes, {failures} failures")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Average time: {avg_time:.2f}s")
        
        assert success_rate >= 80, f"Stress test reliability too low: {success_rate:.1f}%"
    
    def test_mathjax_greek_symbols_rendering(self):
        """Test specific Greek symbol rendering that was failing"""
        print("\nTesting Greek symbol rendering...")
        
        greek_content = """# Greek Symbol Test

## Basic Greek Letters
- Alpha: $\\alpha$
- Beta: $\\beta$ 
- Gamma: $\\gamma$
- Delta: $\\delta$
- Epsilon: $\\epsilon$

## In Equations
$$\\alpha + \\beta = \\gamma$$
$$\\Delta x = x_2 - x_1$$
$$\\sum_{i=1}^{n} \\alpha_i x_i$$

## Mixed with Text
The angle $\\theta$ varies from $0$ to $2\\pi$.
The coefficient $\\lambda$ determines the eigenvalue.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(greek_content)
            temp_file = f.name
        
        try:
            start_time = time.time()
            converter = MarkdownToPDF()
            converter.config['math']['enabled'] = True
            
            output_file = temp_file.replace('.md', '_greek.pdf')
            converter.convert_file(temp_file, output_file)
            
            duration = time.time() - start_time
            success = os.path.exists(output_file)
            
            print(f"  Greek symbols test: {duration:.2f}s, success: {success}")
            
            if success:
                os.unlink(output_file)
            
            assert success, "Greek symbol rendering failed"
            
        finally:
            os.unlink(temp_file)
    
    def test_mathjax_vs_no_mathjax_performance(self):
        """Compare performance with and without MathJax"""
        print("\nComparing MathJax vs no-MathJax performance...")
        
        content_with_math = """# Math Content
$$E = mc^2$$
$\\pi \\approx 3.14159$
"""
        
        content_without_math = """# Regular Content
E = mc^2 (no math rendering)
π ≈ 3.14159 (Unicode symbols)
"""
        
        results = {}
        
        for test_name, content, math_enabled in [
            ('with_math', content_with_math, True),
            ('without_math', content_without_math, False),
            ('math_disabled', content_with_math, False)
        ]:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                start_time = time.time()
                converter = MarkdownToPDF()
                converter.config['math']['enabled'] = math_enabled
                
                output_file = temp_file.replace('.md', f'_{test_name}.pdf')
                converter.convert_file(temp_file, output_file)
                
                duration = time.time() - start_time
                success = os.path.exists(output_file)
                
                results[test_name] = {
                    'duration': duration,
                    'success': success
                }
                
                print(f"  {test_name}: {duration:.2f}s, success: {success}")
                
                if success:
                    os.unlink(output_file)
                    
            finally:
                os.unlink(temp_file)
        
        # Analyze performance difference
        if results['with_math']['success'] and results['without_math']['success']:
            overhead = results['with_math']['duration'] - results['without_math']['duration']
            print(f"  MathJax overhead: {overhead:.2f}s")
            
            # MathJax should not add more than 10 seconds overhead
            assert overhead < 10.0, f"MathJax overhead too high: {overhead:.2f}s"


def main():
    """Run MathJax performance tests directly"""
    print("Running MathJax Performance Tests...")
    
    test_instance = TestMathJaxPerformance()
    
    try:
        # Create sample content
        sample_content = {
            'simple': """# Simple Math
$$E = mc^2$$
$\\alpha + \\beta$
""",
            'complex': """# Complex Math
$$\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$$
$\\sum_{i=1}^{n} x_i$
"""
        }
        
        print("1. Testing MathJax timeout scenarios...")
        test_instance.test_mathjax_timeout_scenarios(sample_content)
        
        print("\n2. Testing MathJax reliability...")
        test_instance.test_mathjax_reliability_stress()
        
        print("\n3. Testing Greek symbols...")
        test_instance.test_mathjax_greek_symbols_rendering()
        
        print("\n4. Testing performance comparison...")
        test_instance.test_mathjax_vs_no_mathjax_performance()
        
        print("\nAll MathJax performance tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        raise


if __name__ == '__main__':
    main()