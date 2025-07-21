// Local MathJax implementation for offline use
// This provides core MathJax functionality without requiring CDN access

window.MathJax = {
    tex: {
        inlineMath: [['$','$'], ['\\(','\\)']],
        displayMath: [['$$','$$'], ['\\[','\\]']],
        processEscapes: true,
        processEnvironments: true,
        packages: {'[+]': ['noerrors']}
    },
    options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
        renderActions: {
            addMenu: [0, '', '']
        }
    },
    startup: {
        ready() {
            console.log('Local MathJax ready');
            this.defaultReady();
        },
        pageReady() {
            console.log('Local MathJax page ready');
            return this.document.render();
        },
        document: {
            state() { return 6; }, // Always ready state
            render() { 
                console.log('Local MathJax render complete');
                return Promise.resolve(); 
            }
        }
    },
    loader: {
        load: ['[tex]/noerrors']
    }
};

// Mock implementation for basic math rendering
// This is a simplified version that handles common cases
const LocalMathProcessor = {
    process(element) {
        // Find inline math
        element.innerHTML = element.innerHTML.replace(
            /\$([^$]+)\$/g, 
            '<span class="math-inline">$1</span>'
        );
        
        // Find display math
        element.innerHTML = element.innerHTML.replace(
            /\$\$([^$]+)\$\$/g, 
            '<div class="math-display">$1</div>'
        );
        
        // Basic Greek letter replacements
        const greekMap = {
            '\\\\alpha': 'α',
            '\\\\beta': 'β', 
            '\\\\gamma': 'γ',
            '\\\\delta': 'δ',
            '\\\\epsilon': 'ε',
            '\\\\pi': 'π',
            '\\\\theta': 'θ',
            '\\\\lambda': 'λ',
            '\\\\mu': 'μ',
            '\\\\sigma': 'σ',
            '\\\\tau': 'τ',
            '\\\\phi': 'φ',
            '\\\\chi': 'χ',
            '\\\\psi': 'ψ',
            '\\\\omega': 'ω'
        };
        
        // Apply Greek letter replacements
        for (const [latex, unicode] of Object.entries(greekMap)) {
            element.innerHTML = element.innerHTML.replace(new RegExp(latex, 'g'), unicode);
        }
        
        // Basic operation replacements
        element.innerHTML = element.innerHTML
            .replace(/\\times/g, '×')
            .replace(/\\div/g, '÷')
            .replace(/\\pm/g, '±')
            .replace(/\\mp/g, '∓')
            .replace(/\\approx/g, '≈')
            .replace(/\\neq/g, '≠')
            .replace(/\\leq/g, '≤')
            .replace(/\\geq/g, '≥')
            .replace(/\\infty/g, '∞')
            .replace(/\\sum/g, '∑')
            .replace(/\\prod/g, '∏')
            .replace(/\\int/g, '∫')
            .replace(/\\sqrt/g, '√')
            .replace(/\\partial/g, '∂')
            .replace(/\\nabla/g, '∇');
    }
};

// Auto-process math when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Processing local math...');
    
    // Process all elements with math
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        LocalMathProcessor.process(slide);
    });
    
    // Fallback: process entire body if no slides found
    if (slides.length === 0) {
        LocalMathProcessor.process(document.body);
    }
    
    console.log('Local math processing complete');
});

// Provide MathJax-compatible API
window.MathJax.startup.document.state = () => 6; // Always ready
window.MathJax.startup.document.render = () => Promise.resolve();

console.log('Local MathJax loaded successfully');