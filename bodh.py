#!/usr/bin/env python3
"""
Bodh - Modular Markdown to PDF Presentation Tool
"""

import argparse
import os
import sys
from pathlib import Path
import markdown
from jinja2 import Template
import json
import base64
import yaml
from config import PresentationConfig, load_config, create_sample_config
try:
    from playwright.sync_api import sync_playwright
    PDF_BACKEND = 'playwright'
except ImportError:
    try:
        from weasyprint import HTML, CSS
        PDF_BACKEND = 'weasyprint'
    except ImportError:
        from xhtml2pdf import pisa
        PDF_BACKEND = 'xhtml2pdf'


class ThemeLoader:
    def __init__(self, themes_dir="themes"):
        self.themes_dir = Path(themes_dir)
        self._themes_cache = {}
    
    def load_theme(self, theme_name):
        """Load theme configuration from JSON file"""
        if theme_name in self._themes_cache:
            return self._themes_cache[theme_name]
        
        theme_file = self.themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            raise FileNotFoundError(f"Theme '{theme_name}' not found at {theme_file}")
        
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
        
        self._themes_cache[theme_name] = theme_data
        return theme_data
    
    def list_themes(self):
        """List all available themes"""
        themes = []
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem
            try:
                theme_data = self.load_theme(theme_name)
                themes.append({
                    'name': theme_name,
                    'display_name': theme_data.get('name', theme_name),
                    'description': theme_data.get('description', 'No description')
                })
            except Exception as e:
                print(f"Warning: Could not load theme {theme_name}: {e}")
        return themes


class StyleGenerator:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = Path(templates_dir)
    
    def generate_css(self, theme_data, font_family, font_size, config=None):
        """Generate CSS from template and theme data"""
        css_template_path = self.templates_dir / "base.css"
        
        if not css_template_path.exists():
            raise FileNotFoundError(f"CSS template not found at {css_template_path}")
        
        with open(css_template_path, 'r') as f:
            css_content = f.read()
        
        template = Template(css_content)
        return template.render(
            theme=theme_data,
            font_family=font_family,
            font_size=font_size,
            config=config or {}
        )


class MarkdownToPDF:
    def __init__(self, theme='default', font_family='Inter', font_size=20, 
                 logo_path=None, logo_position='top-right', config=None):
        # Use config if provided, otherwise use individual parameters
        if config:
            self.config = config
            self.theme_name = config.get('theme', 'default')
            self.font_family = config.get('font.family', 'Inter')
            self.font_size = config.get('font.size', 20)
            self.logo_path = config.get('logo.source')
            self.logo_position = config.get('logo.location', 'top-right')
            self.slide_separator = config.get('content.slide_separator', '---')
        else:
            self.config = PresentationConfig()
            self.theme_name = theme
            self.font_family = font_family
            self.font_size = font_size
            self.logo_path = logo_path
            self.logo_position = logo_position
            self.slide_separator = "---"
        
        # Initialize components
        self.theme_loader = ThemeLoader()
        self.style_generator = StyleGenerator()
        
        # Load theme
        self.theme_data = self.theme_loader.load_theme(self.theme_name)
        
        # Generate styles
        self.css = self.style_generator.generate_css(
            self.theme_data, self.font_family, self.font_size, self.config
        )
        
        self.template = self._get_html_template()
    
    def _encode_image(self, image_path):
        """Encode image to base64 for embedding"""
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            return None
    
    def parse_markdown_slides(self, md_content):
        """Parse markdown content into individual slides with advanced features"""
        slides = []
        slide_parts = md_content.split(f"\n{self.slide_separator}\n")
        
        for slide_content in slide_parts:
            if slide_content.strip():
                # Process overlays (pause markers)
                if self.config.get('overlays.enabled', False):
                    slide_content = self._process_overlays(slide_content)
                
                # Process multi-column layouts
                if self.config.get('layout.columns', 1) > 1:
                    slide_content = self._process_columns(slide_content)
                
                # Process hrules for titles
                if self.config.get('style.hrule.enabled', False) or \
                   self.theme_data.get('special_features', {}).get('title_hrule', False):
                    slide_content = self._process_hrules(slide_content)
                
                html_content = markdown.markdown(
                    slide_content.strip(), 
                    extensions=['fenced_code', 'tables', 'codehilite', 'extra']
                )
                slides.append(html_content)
        
        return slides
    
    def _process_overlays(self, content):
        """Process overlay/pause markers in markdown"""
        # Replace pause markers with HTML overlay divs
        parts = content.split('<!--pause-->')
        if len(parts) <= 1:
            parts = content.split('\\pause')
        
        if len(parts) > 1:
            processed_content = parts[0]
            for i, part in enumerate(parts[1:], 1):
                processed_content += f'<div class="overlay" data-overlay="{i}">{part}</div>'
            return processed_content
        return content
    
    def _process_columns(self, content):
        """Process multi-column layouts"""
        columns = self.config.get('layout.columns', 1)
        if columns <= 1:
            return content
        
        # Look for column separators with various formats
        if ':::' in content:
            # Handle both `::: {.column}` and `:::` formats
            import re
            
            # Pattern to match ::: {.column} content :::
            column_pattern = r'::: \{\.column\}(.*?):::'
            matches = re.findall(column_pattern, content, re.DOTALL)
            
            if matches:
                # Found {.column} format
                column_content = []
                for match in matches:
                    if match.strip():
                        column_content.append(f'<div class="column">{match.strip()}</div>')
                
                if column_content:
                    # Replace the original content with processed columns
                    processed_content = re.sub(column_pattern, '', content, flags=re.DOTALL).strip()
                    return f'<div class="columns-layout columns-{columns}">{"".join(column_content)}</div>'
            else:
                # Fall back to simple ::: separator format
                parts = content.split(':::')
                if len(parts) >= 3:  # Should have opening, content, and closing
                    column_content = []
                    for i in range(1, len(parts), 2):  # Take every second part (content)
                        if parts[i].strip():
                            column_content.append(f'<div class="column">{parts[i].strip()}</div>')
                    
                    if column_content:
                        return f'<div class="columns-layout columns-{columns}">{"".join(column_content)}</div>'
        
        return content
    
    def _process_hrules(self, content):
        """Add horizontal rules under titles"""
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_lines.append(line)
            # Add hrule after headings
            if line.startswith('# ') or line.startswith('## '):
                hrule_width = self.config.get('style.hrule.width', '80%')
                hrule_style = self.config.get('style.hrule.style', 'solid')
                hrule_thickness = self.config.get('style.hrule.thickness', '2px')
                processed_lines.append(f'<hr class="title-hrule" style="width: {hrule_width}; border-style: {hrule_style}; border-width: {hrule_thickness};">')
        
        return '\n'.join(processed_lines)
    
    def _get_html_template(self):
        """HTML template for the presentation"""
        return Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link href="https://fonts.googleapis.com/css2?family={{ font_family.replace(' ', '+') }}:wght@300;400;600;700&display=swap" rel="stylesheet">
    {% if config.get('math.enabled', True) %}
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }
        };
    </script>
    {% endif %}
    <style>
        {{ css }}
    </style>
</head>
<body{% if enable_navigation %} class="has-navigation"{% endif %}>
    {% if enable_navigation %}
    <div class="keyboard-hint">
        Use ← → keys or navigation buttons
    </div>
    {% endif %}
    
    {% for slide in slides %}
    <div class="slide{% if enable_navigation and loop.first %} active{% endif %}">
        {% if logo_data %}
        <div class="logo logo-{{ logo_position }}">
            <img src="data:image/png;base64,{{ logo_data }}" alt="Logo">
        </div>
        {% endif %}
        <div class="slide-content">
            {{ slide | safe }}
        </div>
    </div>
    {% if not loop.last %}<div class="page-break"></div>{% endif %}
    {% endfor %}
    
    {% if enable_navigation %}
    <div class="slide-nav">
        {% if show_arrows %}
        <button class="nav-btn" id="prev-btn" onclick="previousSlide()">←</button>
        {% endif %}
        
        {% if show_slide_numbers %}
        <div class="slide-counter">
            <span id="slide-display">{{ initial_slide_number }}</span>
        </div>
        {% endif %}
        
        {% if show_dots %}
        <div class="slide-dots" id="slide-dots">
            {% for slide in slides %}
            <div class="dot{% if loop.first %} active{% endif %}" onclick="goToSlide({{ loop.index0 }})"></div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if show_arrows %}
        <button class="nav-btn" id="next-btn" onclick="nextSlide()">→</button>
        {% endif %}
    </div>
    
    {% if config.get('overlays.enabled') %}
    <div class="overlay-controls" style="display: none;">
        Overlay 0/0
    </div>
    {% endif %}

    <script>
        let currentSlide = 0;
        const totalSlides = {{ slides|length }};
        
        function showSlide(n) {
            const slides = document.querySelectorAll('.slide');
            const dots = document.querySelectorAll('.dot');
            
            if (n >= totalSlides) currentSlide = 0;
            if (n < 0) currentSlide = totalSlides - 1;
            
            slides.forEach(slide => slide.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));
            
            slides[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
            
            // Update slide number display
            const slideDisplay = document.getElementById('slide-display');
            if (slideDisplay) {
                const current = currentSlide + 1;
                const total = totalSlides;
                const percent = Math.round((current / total) * 100);
                
                const format = '{{ slide_number_format }}';
                const displayText = format
                    .replace('{current}', current)
                    .replace('{total}', total)
                    .replace('{percent}', percent);
                
                slideDisplay.textContent = displayText;
            }
            
            // Update navigation buttons
            const prevBtn = document.getElementById('prev-btn');
            const nextBtn = document.getElementById('next-btn');
            
            if (prevBtn) prevBtn.disabled = currentSlide === 0;
            if (nextBtn) nextBtn.disabled = currentSlide === totalSlides - 1;
        }
        
        function nextSlide() {
            if (currentSlide < totalSlides - 1) {
                currentSlide++;
                showSlide(currentSlide);
            }
        }
        
        function previousSlide() {
            if (currentSlide > 0) {
                currentSlide--;
                showSlide(currentSlide);
            }
        }
        
        function goToSlide(n) {
            currentSlide = n;
            showSlide(currentSlide);
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                e.preventDefault();
                nextSlide();
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                previousSlide();
            } else if (e.key === 'Home') {
                e.preventDefault();
                goToSlide(0);
            } else if (e.key === 'End') {
                e.preventDefault();
                goToSlide(totalSlides - 1);
            }
        });
        
        {% if config.get('overlays.enabled') %}
        // Overlay system for pause functionality
        let currentOverlay = 0;
        let maxOverlays = 0;
        
        function updateOverlays() {
            const currentSlideElement = document.querySelectorAll('.slide')[currentSlide];
            const overlays = currentSlideElement.querySelectorAll('.overlay');
            maxOverlays = overlays.length;
            
            overlays.forEach((overlay, index) => {
                if (index < currentOverlay) {
                    overlay.classList.add('visible');
                } else {
                    overlay.classList.remove('visible');
                }
            });
            
            // Update overlay controls
            const overlayControls = document.querySelector('.overlay-controls');
            if (overlayControls && maxOverlays > 0) {
                overlayControls.textContent = `Overlay ${currentOverlay}/${maxOverlays}`;
                overlayControls.style.display = 'block';
            } else if (overlayControls) {
                overlayControls.style.display = 'none';
            }
        }
        
        function nextOverlay() {
            if (currentOverlay < maxOverlays) {
                currentOverlay++;
                updateOverlays();
                return true;
            }
            return false;
        }
        
        function previousOverlay() {
            if (currentOverlay > 0) {
                currentOverlay--;
                updateOverlays();
                return true;
            }
            return false;
        }
        
        // Override navigation to handle overlays
        const originalNextSlide = nextSlide;
        const originalPreviousSlide = previousSlide;
        
        nextSlide = function() {
            if (!nextOverlay()) {
                currentOverlay = 0;
                originalNextSlide();
                updateOverlays();
            }
        };
        
        previousSlide = function() {
            if (!previousOverlay()) {
                if (currentSlide > 0) {
                    originalPreviousSlide();
                    // Go to last overlay of previous slide
                    const prevSlideElement = document.querySelectorAll('.slide')[currentSlide];
                    const prevOverlays = prevSlideElement.querySelectorAll('.overlay');
                    currentOverlay = prevOverlays.length;
                    updateOverlays();
                }
            }
        };
        
        // Override showSlide to reset overlays
        const originalShowSlide = showSlide;
        showSlide = function(n) {
            currentOverlay = 0;
            originalShowSlide(n);
            updateOverlays();
        };
        {% endif %}
        
        // Initialize
        showSlide(0);
        {% if config.get('overlays.enabled') %}
        updateOverlays();
        {% endif %}
    </script>
    {% endif %}
</body>
</html>
        """)
    
    def convert_to_pdf(self, markdown_file, output_file=None):
        """Convert markdown file to PDF presentation"""
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Parse slides
        slides = self.parse_markdown_slides(md_content)
        
        if not slides:
            raise ValueError("No slides found in markdown file")
        
        # Encode logo if provided
        logo_data = None
        if self.logo_path and os.path.exists(self.logo_path):
            logo_data = self._encode_image(self.logo_path)
        
        # Calculate initial slide number display (for PDF we don't need it, but template expects it)
        initial_slide_number = '1'
        
        # Generate HTML
        title = Path(markdown_file).stem
        html_content = self.template.render(
            title=title,
            slides=slides,
            css=self.css,
            font_family=self.font_family,
            logo_data=logo_data,
            logo_position=self.logo_position,
            enable_navigation=False,
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=False,
            slide_number_format='{current}/{total}',
            initial_slide_number=initial_slide_number,
            config=self.config
        )
        
        # Generate PDF
        if output_file is None:
            output_file = f"{title}.pdf"
        
        if PDF_BACKEND == 'playwright':
            # Use Playwright (Chrome) for best PDF quality - identical to HTML preview
            with sync_playwright() as p:
                # Launch browser with CI-friendly options
                browser_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-default-apps',
                        '--disable-translate',
                        '--disable-extensions',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--disable-ipc-flooding-protection'
                    ]
                }
                browser = p.chromium.launch(**browser_options)
                page = browser.new_page()
                
                # Set viewport to match A4 landscape dimensions for consistent rendering
                page.set_viewport_size({"width": 1123, "height": 794})  # A4 landscape at 96 DPI
                
                # Load content and wait for fonts/images
                page.set_content(html_content, wait_until='networkidle')
                
                # Wait for fonts and images to load properly
                page.wait_for_timeout(3000)  # Increase timeout for CI and font loading
                
                # Wait for any Google Fonts to load
                page.wait_for_function("""
                    () => {
                        const fonts = document.fonts;
                        return fonts.status === 'loaded' || fonts.size === 0;
                    }
                """, timeout=10000)
                
                # PDF options for presentation format
                page.pdf(
                    path=output_file,
                    format='A4',
                    landscape=True,
                    margin={'top': '0.5cm', 'bottom': '0.5cm', 'left': '0.5cm', 'right': '0.5cm'},
                    print_background=True,
                    prefer_css_page_size=True,
                    display_header_footer=False,
                    width='11.7in',  # A4 landscape width
                    height='8.3in'   # A4 landscape height
                )
                browser.close()
        elif PDF_BACKEND == 'weasyprint':
            # Use WeasyPrint for better CSS support and quality
            html_doc = HTML(string=html_content, base_url='.')
            html_doc.write_pdf(output_file, optimize_size=('fonts', 'images'))
        else:
            # Fallback to xhtml2pdf
            with open(output_file, 'wb') as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_content, 
                    dest=pdf_file,
                    encoding='utf-8',
                    show_error_as_pdf=True,
                    default_css_media_type='print'
                )
                
            if pisa_status.err:
                raise Exception("PDF generation failed")
        
        return output_file
    
    def convert_to_html(self, markdown_file, output_file=None):
        """Convert markdown file to HTML presentation"""
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Parse slides
        slides = self.parse_markdown_slides(md_content)
        
        if not slides:
            raise ValueError("No slides found in markdown file")
        
        # Encode logo if provided
        logo_data = None
        if self.logo_path and os.path.exists(self.logo_path):
            logo_data = self._encode_image(self.logo_path)
        
        # Calculate initial slide number display
        slide_format = self.config.get_slide_number_format()
        initial_slide_number = slide_format.replace('{current}', '1').replace('{total}', str(len(slides)))
        if '{percent}' in initial_slide_number:
            initial_percent = round((1 / len(slides)) * 100)
            initial_slide_number = initial_slide_number.replace('{percent}', str(initial_percent))
        
        # Generate HTML
        title = Path(markdown_file).stem
        html_content = self.template.render(
            title=title,
            slides=slides,
            css=self.css,
            font_family=self.font_family,
            logo_data=logo_data,
            logo_position=self.logo_position,
            enable_navigation=self.config.get('navigation.enabled', True),
            show_arrows=self.config.get('navigation.show_arrows', True),
            show_dots=self.config.get('navigation.show_dots', True),
            show_slide_numbers=self.config.get('slide_number.enabled', True),
            slide_number_format=self.config.get_slide_number_format(),
            initial_slide_number=initial_slide_number,
            config=self.config
        )
        
        # Save HTML
        if output_file is None:
            output_file = f"{title}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Converted {markdown_file} to {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to beautiful PDF presentations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.md                    # Basic usage with default config
  %(prog)s slides.md -c config.yml           # Using configuration file
  %(prog)s demo.md --html                    # Generate HTML instead of PDF
  %(prog)s slides.md --preview               # Generate and open in browser
  %(prog)s --create-config                   # Create sample config
  %(prog)s --list-themes                     # Show available themes
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input markdown file')
    parser.add_argument('-c', '--config', help='Configuration file (YAML)')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    parser.add_argument('--html', action='store_true', help='Generate HTML instead of PDF')
    parser.add_argument('--preview', action='store_true', help='Open preview in browser')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--list-themes', action='store_true', help='List available themes')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    
    args = parser.parse_args()
    
    if args.create_config:
        config_file = args.config or 'bodh.yml'
        create_sample_config(config_file)
        return
    
    if args.list_themes:
        theme_loader = ThemeLoader()
        themes = theme_loader.list_themes()
        print("Available themes:")
        print("-" * 50)
        for theme in themes:
            print(f"  {theme['name']:12} - {theme['description']}")
        print("\nUsage: python bodh.py input.md -t THEME_NAME")
        return
    
    if not args.input:
        parser.error("Input markdown file is required (unless using --list-themes or --create-config)")
    
    try:
        # Load configuration
        config = None
        
        # Check for default config files
        default_configs = [
            'bodh.yml',
            'bodh.yaml',
            '.bodh.yml',
            '.bodh.yaml'
        ]
        
        config_file = args.config
        if not config_file:
            # Look for default config files
            for default_file in default_configs:
                if os.path.exists(default_file):
                    config_file = default_file
                    break
        
        if config_file:
            config = load_config(config_file)
            converter = MarkdownToPDF(config=config)
        else:
            # Use default configuration
            converter = MarkdownToPDF()
        
        if args.html or args.preview:
            # Generate HTML
            output_file = converter.convert_to_html(args.input, args.output)
            if args.preview:
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(output_file)}')
        else:
            # Generate PDF
            output_file = converter.convert_to_pdf(args.input, args.output)
        
        if args.verbose:
            print(f"Successfully converted {args.input} to {output_file}")
            print(f"PDF Backend: {PDF_BACKEND}")
            print(f"Theme: {converter.theme_name} ({converter.theme_data['name']})")
            print(f"Font: {converter.font_family} ({converter.font_size}px)")
            if converter.logo_path:
                print(f"Logo: {converter.logo_path} ({converter.logo_position})")
            if config_file:
                print(f"Configuration: {config_file}")
            if config:
                slide_format = config.get('slide_number.format', 'current/total')
                print(f"Slide numbering: {slide_format}")
        else:
            print(f"Generated: {output_file} (using {PDF_BACKEND})")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()