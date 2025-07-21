#!/usr/bin/env python3
"""
Comprehensive MathJax Performance Benchmark
Tests different MathJax modes and measures performance, reliability, and quality
"""

import os
import time
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bodh import MarkdownToPDF


class MathJaxBenchmark:
    """Comprehensive MathJax performance benchmarking"""
    
    def __init__(self):
        self.results = {}
        self.test_content = {
            'simple': """# Simple Math Test

Basic inline math: $E = mc^2$ and $\\pi \\approx 3.14159$

Basic display math:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

Greek letters: $\\alpha + \\beta = \\gamma$
""",
            'medium': """# Medium Complexity Math

## Equations
$$\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}$$

$$\\frac{\\partial}{\\partial x} \\int_0^x f(t) dt = f(x)$$

## Matrices
$$\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix} \\begin{bmatrix} x \\\\ y \\end{bmatrix} = \\begin{bmatrix} ax + by \\\\ cx + dy \\end{bmatrix}$$

## Statistics  
$$P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}$$
""",
            'heavy': """# Heavy Math Test

## Multiple Complex Equations

Quantum mechanics:
$$\\psi(x,t) = \\sum_{n=1}^{\\infty} c_n \\phi_n(x) e^{-iE_n t/\\hbar}$$

Maxwell's equations:
$$\\nabla \\times \\mathbf{B} = \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}$$

Calculus:
$$\\oint_C \\mathbf{F} \\cdot d\\mathbf{r} = \\iint_S (\\nabla \\times \\mathbf{F}) \\cdot d\\mathbf{S}$$

Number theory:
$$\\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s} = \\prod_{p \\text{ prime}} \\frac{1}{1-p^{-s}}$$

Complex analysis:
$$\\oint_C f(z) dz = 2\\pi i \\sum \\text{Res}(f, z_k)$$
"""
        }
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive MathJax benchmark"""
        print("🔬 Starting MathJax Performance Benchmark...")
        print("=" * 60)
        
        # Test scenarios
        scenarios = [
            ('default', {}),  # Default CDN mode
            ('local_mode', {'use_local': True}),  # Local mode test
        ]
        
        for scenario_name, config in scenarios:
            print(f"\n📊 Testing scenario: {scenario_name}")
            print("-" * 40)
            
            self.results[scenario_name] = {}
            
            for complexity, content in self.test_content.items():
                print(f"  Testing {complexity} content...")
                
                result = self._test_scenario(content, config)
                self.results[scenario_name][complexity] = result
                
                print(f"    Duration: {result['duration']:.2f}s")
                print(f"    Success: {result['success']}")
                print(f"    File size: {result['file_size']} bytes")
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _test_scenario(self, content: str, config: Dict) -> Dict[str, Any]:
        """Test a specific scenario and return metrics"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            start_time = time.time()
            
            # Create converter
            converter = MarkdownToPDF()
            
            # Apply test config
            if config.get('use_local'):
                # Force local mode for testing
                converter.config.config['math']['mode'] = 'local'
            
            # Generate PDF
            output_file = temp_file.replace('.md', '.pdf')
            converter.convert_file(temp_file, output_file)
            
            duration = time.time() - start_time
            success = os.path.exists(output_file)
            file_size = os.path.getsize(output_file) if success else 0
            
            # Cleanup
            if success:
                os.unlink(output_file)
            
            return {
                'duration': duration,
                'success': success,
                'file_size': file_size,
                'error': None
            }
            
        except Exception as e:
            return {
                'duration': None,
                'success': False,
                'file_size': 0,
                'error': str(e)
            }
        
        finally:
            os.unlink(temp_file)
    
    def _generate_summary(self):
        """Generate benchmark summary"""
        print("\n" + "=" * 60)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 60)
        
        for scenario, results in self.results.items():
            print(f"\n🎯 Scenario: {scenario}")
            
            successful_tests = sum(1 for r in results.values() if r['success'])
            total_tests = len(results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            successful_durations = [r['duration'] for r in results.values() if r['success'] and r['duration']]
            avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
            
            print(f"  Success rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            print(f"  Average duration: {avg_duration:.2f}s")
            
            # Show individual results
            for complexity, result in results.items():
                status = "✅" if result['success'] else "❌"
                duration_str = f"{result['duration']:.2f}s" if result['duration'] else "FAILED"
                print(f"    {status} {complexity}: {duration_str}")
                
                if result['error']:
                    print(f"        Error: {result['error']}")
        
        # Performance comparison
        if len(self.results) >= 2:
            print(f"\n⚡ PERFORMANCE COMPARISON")
            print("-" * 40)
            
            scenarios = list(self.results.keys())
            if len(scenarios) >= 2:
                scenario1, scenario2 = scenarios[0], scenarios[1]
                
                # Compare average durations
                durations1 = [r['duration'] for r in self.results[scenario1].values() if r['success'] and r['duration']]
                durations2 = [r['duration'] for r in self.results[scenario2].values() if r['success'] and r['duration']]
                
                if durations1 and durations2:
                    avg1 = sum(durations1) / len(durations1)
                    avg2 = sum(durations2) / len(durations2)
                    
                    if avg1 < avg2:
                        speedup = avg2 / avg1
                        print(f"🚀 {scenario1} is {speedup:.2f}x faster than {scenario2}")
                    else:
                        speedup = avg1 / avg2
                        print(f"🚀 {scenario2} is {speedup:.2f}x faster than {scenario1}")
    
    def stress_test(self, iterations: int = 10) -> Dict[str, Any]:
        """Run stress test with repeated generations"""
        print(f"\n🔥 STRESS TEST ({iterations} iterations)")
        print("=" * 60)
        
        content = self.test_content['medium']  # Use medium complexity
        results = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...", end=" ")
            
            result = self._test_scenario(content, {})
            results.append(result)
            
            if result['success']:
                print(f"✅ {result['duration']:.2f}s")
            else:
                print(f"❌ FAILED")
        
        # Analyze stress test results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        success_rate = len(successful) / len(results) * 100
        
        if successful:
            durations = [r['duration'] for r in successful]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = min_duration = max_duration = 0
        
        stress_summary = {
            'iterations': iterations,
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'min_duration': min_duration,
            'max_duration': max_duration
        }
        
        print(f"\n📊 Stress Test Results:")
        print(f"  Success rate: {len(successful)}/{iterations} ({success_rate:.1f}%)")
        print(f"  Average time: {avg_duration:.2f}s")
        print(f"  Min/Max time: {min_duration:.2f}s / {max_duration:.2f}s")
        
        return stress_summary
    
    def save_results(self, filename: str = "mathjax_benchmark.json"):
        """Save benchmark results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


def main():
    """Run the MathJax benchmark"""
    print("🧪 MathJax Performance Benchmark Suite")
    print("Testing different MathJax modes and measuring performance\n")
    
    benchmark = MathJaxBenchmark()
    
    try:
        # Run main benchmark
        results = benchmark.run_benchmark()
        
        # Run stress test
        stress_results = benchmark.stress_test(5)  # 5 iterations for speed
        
        # Save results
        benchmark.save_results()
        
        print("\n✅ Benchmark completed successfully!")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        # Check if any scenario has poor performance
        poor_performance = False
        for scenario, results in benchmark.results.items():
            durations = [r['duration'] for r in results.values() if r['success'] and r['duration']]
            if durations and max(durations) > 10:  # Over 10 seconds
                print(f"⚠️  {scenario} has slow performance (max: {max(durations):.1f}s)")
                poor_performance = True
        
        if poor_performance:
            print("💬 Consider using local MathJax mode for better performance")
            print("💬 Or implement caching for repeated mathematical content")
        else:
            print("✅ Performance looks good across all scenarios")
        
        # Check reliability
        total_tests = sum(len(results) for results in benchmark.results.values())
        total_successes = sum(sum(1 for r in results.values() if r['success']) for results in benchmark.results.values())
        overall_success_rate = total_successes / total_tests * 100 if total_tests > 0 else 0
        
        if overall_success_rate < 90:
            print(f"⚠️  Low success rate: {overall_success_rate:.1f}%")
            print("💬 Consider implementing better fallback mechanisms")
        else:
            print(f"✅ Good reliability: {overall_success_rate:.1f}% success rate")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        raise


if __name__ == '__main__':
    main()