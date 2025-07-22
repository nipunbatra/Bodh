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
import tempfile
import subprocess
import shutil
from config import PresentationConfig, load_config, create_sample_config
from font_manager import FontManager
from playwright.sync_api import sync_playwright

PDF_BACKEND = 'playwright' # Default to playwright
from playwright.sync_api import sync_playwright



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
        
        # Calculate font sizes based on config
        base_size = font_size or 20
        
        # Get custom font sizes from config or calculate defaults
        if config:
            title_size = config.get('font.title_size')
            text_size = config.get('font.text_size')
        else:
            title_size = None
            text_size = None
        
        # Calculate relative font sizes (em values)
        font_sizes = {
            'h1': title_size / base_size if title_size else 2.8,
            'h2': title_size / base_size * 0.8 if title_size else 2.2,
            'text': text_size / base_size if text_size else 1.2
        }
        
        template = Template(css_content)
        return template.render(
            theme=theme_data,
            font_family=font_family,
            font_size=font_size,
            font_sizes=font_sizes,
            config=config or {}
        )


class MarkdownToPDF:
    def __init__(self, theme='default', font_family='Inter', font_size=20, 
                 logo_path=None, logo_position='top-right', config=None):
        # Use config if provided, otherwise use individual parameters
        if config:
            self.config = config
            theme_config = config.get('theme', 'default')
            if isinstance(theme_config, dict):
                self.theme_name = theme_config.get('name', 'default')
            else:
                self.theme_name = theme_config
            self.font_family = config.get('font.family', 'Inter')
            self.font_size = config.get('font.size', 20)
            self.logo_path = config.get('logo.path') or config.get('logo.source')
            self.logo_position = config.get('logo.position') or config.get('logo.location', 'top-right')
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
        self.font_manager = FontManager()
        
        # Load theme
        self.theme_data = self.theme_loader.load_theme(self.theme_name)
        
        # Generate styles
        self.css = self.style_generator.generate_css(
            self.theme_data, self.font_family, self.font_size, self.config
        )
        
        # Get optimized font CSS
        self.font_css = self.font_manager.get_optimized_font_css(self.font_family)
        
        self.template = self._get_html_template()
        self.mock_mathjax_js = self._get_mock_mathjax_js()
        self.local_mathjax_js = self._get_local_mathjax_js()
        
        # Check LaTeX availability
        self.latex_available = self._check_latex_availability()

    def _get_mock_mathjax_js(self):
        """Reads the mock MathJax JS file for testing"""
        mock_js_path = Path(__file__).parent / "static/js/mock_mathjax.js"
        if mock_js_path.exists():
            with open(mock_js_path, 'r') as f:
                return f.read()
        return ""
    
    def _get_local_mathjax_js(self):
        """Reads the local MathJax JS file for offline use"""
        local_js_path = Path(__file__).parent / "static/mathjax/mathjax-local.js"
        if local_js_path.exists():
            with open(local_js_path, 'r') as f:
                return f.read()
        return ""
    
    def _check_latex_availability(self) -> bool:
        """Check if LaTeX is available on the system"""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _encode_image(self, image_path, base_dir=None):
        """Encode image to base64 for embedding"""
        try:
            # Try absolute path first
            if os.path.isabs(image_path):
                full_path = image_path
            else:
                # CRITICAL FIX: Resolve relative to markdown file directory, not CWD
                if base_dir:
                    full_path = os.path.join(base_dir, image_path)
                else:
                    # Fallback to current working directory for backward compatibility
                    full_path = os.path.abspath(image_path)
                
            print(f"Loading image from: {full_path}")
            
            if not os.path.exists(full_path):
                print(f"Warning: Image file not found at {full_path}")
                return None
            
            # Determine MIME type based on file extension
            file_ext = os.path.splitext(full_path)[1].lower()
            if file_ext == '.svg':
                mime_type = 'image/svg+xml'
            elif file_ext == '.png':
                mime_type = 'image/png'
            elif file_ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_ext == '.gif':
                mime_type = 'image/gif'
            elif file_ext == '.webp':
                mime_type = 'image/webp'
            elif file_ext == '.pdf':
                # Convert PDF to PNG for embedding
                return self._convert_pdf_to_image(full_path)
            else:
                mime_type = 'image/png'  # Default fallback
                
            with open(full_path, 'rb') as img_file:
                data = base64.b64encode(img_file.read()).decode('utf-8')
                print(f"Successfully encoded image: {len(data)} characters, MIME: {mime_type}")
                return {'data': data, 'mime_type': mime_type}
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            return None
    
    def _convert_pdf_to_image(self, pdf_path):
        """Convert PDF to PNG for embedding in presentations"""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF
            pdf_doc = fitz.open(pdf_path)
            page = pdf_doc[0]  # Get first page
            
            # Render page to image (high DPI for quality)
            mat = fitz.Matrix(2.0, 2.0)  # 2x scale for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Encode to base64
            data = base64.b64encode(img_data).decode('utf-8')
            pdf_doc.close()
            
            print(f"Successfully converted PDF to PNG: {len(data)} characters")
            return {'data': data, 'mime_type': 'image/png'}
            
        except ImportError:
            print("Warning: PyMuPDF not installed, cannot convert PDF figures")
            print("Install with: pip install PyMuPDF")
            return None
        except Exception as e:
            print(f"Warning: Could not convert PDF {pdf_path}: {e}")
            return None
    
    def parse_markdown_slides(self, md_content, base_dir=None):
        """Parse markdown content into individual slides with advanced features"""
        slides = []
        slide_parts = md_content.split(f"\n{self.slide_separator}\n")
        
        for i, slide_content in enumerate(slide_parts):
            if slide_content.strip():
                # Validate content before processing
                self._validate_slide_content(slide_content, i + 1)
                
                # CRITICAL FIX: Process images first, before other processing
                slide_content = self._process_images(slide_content, base_dir)
                
                # Process overlays (pause markers)
                if self.config.get('overlays.enabled', False):
                    slide_content = self._process_overlays(slide_content)
                
                # Process multi-column layouts (always check for column syntax)
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
    
    def _validate_slide_content(self, content, slide_number):
        """Validate slide content and warn about potential issues"""
        warnings = []
        
        # Check for very long lines that might cause horizontal overflow
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Remove markdown formatting for length check
            clean_line = line.replace('*', '').replace('_', '').replace('`', '')
            if len(clean_line) > 120:  # Threshold for potential overflow
                warnings.append(f"Slide {slide_number}, line {line_num}: Very long line ({len(clean_line)} chars) may cause text cutoff")
        
        # Check for excessive content that might not fit on one slide
        total_lines = len([l for l in lines if l.strip()])
        if total_lines > 25:  # Threshold for too much content
            warnings.append(f"Slide {slide_number}: High content density ({total_lines} lines) may cause text cutoff")
        
        # Check for very long code blocks
        in_code_block = False
        code_lines = 0
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    if code_lines > 15:  # Too many lines in code block
                        warnings.append(f"Slide {slide_number}: Long code block ({code_lines} lines) may not fit properly")
                    in_code_block = False
                    code_lines = 0
                else:
                    in_code_block = True
            elif in_code_block:
                code_lines += 1
                if len(line) > 100:  # Very long code line
                    warnings.append(f"Slide {slide_number}: Long code line may cause horizontal overflow")
        
        # Print warnings
        for warning in warnings:
            print(f"Warning: {warning}")
            print("   Consider: breaking content across multiple slides, using shorter lines, or adjusting font size")
    
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
                        # CRITICAL FIX: Process column content as markdown!
                        column_html = markdown.markdown(
                            match.strip(), 
                            extensions=['fenced_code', 'tables', 'codehilite', 'extra']
                        )
                        column_content.append(f'<div class="column">{column_html}</div>')
                
                if column_content:
                    # CRITICAL FIX: Use actual column count, not config!
                    actual_columns = len(column_content)
                    # Replace the original content with processed columns
                    processed_content = re.sub(column_pattern, '', content, flags=re.DOTALL).strip()
                    return f'<div class="columns-layout columns-{actual_columns}">{" ".join(column_content)}</div>'
            else:
                # Fall back to simple ::: separator format
                parts = content.split(':::')
                if len(parts) >= 3:  # Should have opening, content, and closing
                    column_content = []
                    for i in range(1, len(parts), 2):  # Take every second part (content)
                        if parts[i].strip():
                            # CRITICAL FIX: Process column content as markdown!
                            column_html = markdown.markdown(
                                parts[i].strip(), 
                                extensions=['fenced_code', 'tables', 'codehilite', 'extra']
                            )
                            column_content.append(f'<div class="column">{column_html}</div>')
                    
                    if column_content:
                        # CRITICAL FIX: Use actual column count, not config!
                        actual_columns = len(column_content)
                        return f'<div class="columns-layout columns-{actual_columns}">{" ".join(column_content)}</div>'
        
        return content
    
    def _process_images(self, content, base_dir=None):
        """Process images in markdown content, converting to base64 data URLs"""
        import re
        
        # Pattern to match markdown images: ![alt text](image_path)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # Skip if already a data URL
            if image_path.startswith('data:'):
                return match.group(0)
            
            # Skip if it's a web URL
            if image_path.startswith(('http://', 'https://')):
                return match.group(0)
            
            # Try to encode the image
            encoded_result = self._encode_image(image_path, base_dir)
            if encoded_result:
                data_url = f"data:{encoded_result['mime_type']};base64,{encoded_result['data']}"
                return f"![{alt_text}]({data_url})"
            else:
                # Keep original if encoding failed
                print(f"Warning: Could not process image {image_path}, keeping original reference")
                return match.group(0)
        
        return re.sub(image_pattern, replace_image, content)
    
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
    {% if font_css %}
    <style>
        {{ font_css }}
    </style>
    {% else %}
    <link href="https://fonts.googleapis.com/css2?family={{ font_family.replace(' ', '+') }}:wght@300;400;600;700&display=swap" rel="stylesheet">
    {% endif %}
    {% if config.get('math.enabled', True) %}
    {% set math_mode = config.get('math.mode', 'cdn') %}
    {% if math_mode == 'local' or use_local_mathjax %}
    <script>
        {{ local_mathjax_js | safe }}
    </script>
    {% elif math_mode == 'fast' %}
    <script>
        {{ mock_mathjax_js | safe }}
    </script>
    {% else %}
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    {% endif %}
    <script>
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
                    MathJax.startup.defaultReady();
                    console.log('MathJax is ready');
                },
                pageReady() {
                    return MathJax.startup.document.render();
                }
            },
            loader: {
                load: ['[tex]/noerrors']
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
            <img src="data:{{ logo_mime_type }};base64,{{ logo_data }}" alt="Logo">
        </div>
        {% endif %}
        {% if show_slide_numbers and not enable_navigation %}
        <!-- Individual slide numbers for PDF -->
        <div class="slide-nav">
            <div class="slide-counter">
                <span class="slide-display">{{ loop.index }}/{{ slides|length }}</span>
            </div>
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
        <button class="nav-btn" id="prev-btn" onclick="previousSlide()"><</button>
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
        <button class="nav-btn" id="next-btn" onclick="nextSlide()">></button>
        {% endif %}
    </div>
    {% endif %}
    
    {% if config.get('overlays.enabled') %}
    <div class="overlay-controls" style="display: none;">
        Overlay 0/0
    </div>
    {% endif %}

    {% if enable_navigation %}
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
    
    def convert_to_pdf(self, markdown_file, output_file=None, _test_mode=False):
        """Convert markdown file to PDF presentation"""
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        # Check if LaTeX mode is enabled and available
        pdf_engine = self.config.get('pdf.engine', 'playwright')
        if pdf_engine == 'latex' and self.latex_available:
            return self._convert_to_pdf_latex(markdown_file, output_file)
        elif pdf_engine == 'latex' and not self.latex_available:
            print("Warning: LaTeX mode requested but LaTeX not available, falling back to Playwright")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # CRITICAL FIX: Get base directory for image resolution
        base_dir = os.path.dirname(os.path.abspath(markdown_file))
        
        # Parse slides
        slides = self.parse_markdown_slides(md_content, base_dir)
        
        if not slides:
            raise ValueError("No slides found in markdown file")
        
        # Encode logo if provided
        logo_data = None
        logo_mime_type = 'image/png'  # Default
        if self.logo_path and os.path.exists(self.logo_path):
            logo_result = self._encode_image(self.logo_path)
            if logo_result:
                logo_data = logo_result['data']
                logo_mime_type = logo_result['mime_type']
        
        # Calculate initial slide number display (for PDF we don't need it, but template expects it)
        initial_slide_number = '1'
        
        # Generate HTML
        title = Path(markdown_file).stem
        html_content = self.template.render(
            title=title,
            slides=slides,
            css=self.css,
            font_family=self.font_family,
            font_css=self.font_css,
            logo_data=logo_data,
            logo_mime_type=logo_mime_type,
            logo_position=self.logo_position,
            enable_navigation=False,
            show_arrows=False,
            show_dots=False,
            show_slide_numbers=True,
            slide_number_format='{current}/{total}',
            initial_slide_number=initial_slide_number,
            config=self.config,
            use_local_mathjax=_test_mode,
            mock_mathjax_js=self.mock_mathjax_js,
            local_mathjax_js=self.local_mathjax_js
        )
        
        # Generate PDF
        if output_file is None:
            output_file = f"{title}.pdf"
        
        # Determine PDF backend to use
        current_pdf_backend = os.environ.get('BODH_PDF_BACKEND', 'playwright') # Default to playwright

        if current_pdf_backend == 'playwright':
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
                
                # Load content - since fonts are embedded, we can load much faster
                page.set_content(html_content, wait_until='domcontentloaded')
                
                # Much shorter wait since fonts are embedded and don't need network loading
                page.wait_for_timeout(1000)  # Reduced timeout since fonts are embedded
                
                # Wait for MathJax if enabled, with configurable timeout and fallback handling
                if self.config.get('math.enabled', True) and not _test_mode:
                    math_mode = self.config.get('math.mode', 'cdn')
                    math_timeout = self.config.get('math.timeout', 8000)
                    
                    if math_mode in ['local', 'fast']:
                        # Local/fast mode - minimal wait
                        page.wait_for_timeout(500)
                        print(f"Using {math_mode} MathJax mode - fast rendering")
                    else:
                        # CDN mode - wait for full loading
                        try:
                            print(f"Waiting for MathJax CDN (timeout: {math_timeout}ms)...")
                            page.wait_for_function("""
                                () => {
                                    return window.MathJax && window.MathJax.startup && window.MathJax.startup.document.state() >= 6;
                                }
                            """, timeout=math_timeout)
                            print("MathJax loaded successfully")
                        except Exception as e:
                            fallback = self.config.get('math.fallback', 'local')
                            print(f"Warning: MathJax CDN timeout ({e})")
                            if fallback != 'disabled':
                                print(f"Continuing with {fallback} fallback...")
                            else:
                                print("No fallback enabled, continuing without math rendering")
                
                # PDF options for presentation format - let CSS handle margins
                page.pdf(
                    path=output_file,
                    format='A4',
                    landscape=True,
                    margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
                    print_background=True,
                    prefer_css_page_size=True,
                    display_header_footer=False,
                    width='11.7in',  # A4 landscape width
                    height='8.3in'   # A4 landscape height
                )
                browser.close()
        elif current_pdf_backend == 'weasyprint':
            # Use WeasyPrint for better CSS support and quality
            try:
                from weasyprint import HTML, CSS
                html_doc = HTML(string=html_content, base_url='.')
                html_doc.write_pdf(output_file, optimize_size=('fonts', 'images'))
            except (ImportError, OSError) as e:
                raise Exception(f"WeasyPrint backend selected but not available or misconfigured: {e}")
        elif current_pdf_backend == 'xhtml2pdf':
            try:
                from xhtml2pdf import pisa
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
            except ImportError as e:
                raise Exception(f"xhtml2pdf backend selected but not available: {e}")
        
        return output_file
    
    def _convert_to_pdf_latex(self, markdown_file, output_file=None):
        """Convert markdown to PDF using LaTeX backend"""
        # Read markdown content with error handling
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
        except UnicodeDecodeError:
            # Fallback to reading with error handling
            with open(markdown_file, 'r', encoding='utf-8', errors='replace') as f:
                md_content = f.read()
        
        # Convert markdown to LaTeX
        latex_content = self._markdown_to_latex(md_content)
        
        # Compile with LaTeX
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "presentation.tex"
            
            # Write LaTeX file with error handling
            try:
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
            except UnicodeEncodeError:
                # Fallback with error handling
                with open(tex_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(latex_content)
            
            try:
                # Run pdflatex
                latex_engine = self.config.get('pdf.latex_engine', 'pdflatex')
                passes = self.config.get('pdf.latex_passes', 2)
                
                for pass_num in range(passes):
                    result = subprocess.run([
                        latex_engine,
                        '-interaction=nonstopmode',
                        '-output-directory', str(temp_path),
                        str(tex_file)
                    ], capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
                    
                    print(f"LaTeX pass {pass_num + 1} returncode: {result.returncode}")
                    
                    # Check if LaTeX actually failed (no PDF output) vs just warnings
                    if result.returncode != 0:
                        # LaTeX can return non-zero but still generate PDF with warnings
                        # Check if "Output written" appears in stdout indicating successful PDF generation
                        if "Output written" not in result.stdout:
                            print(f"LaTeX compilation failed on pass {pass_num + 1}")
                            print("STDOUT:", result.stdout[-500:])
                            print("STDERR:", result.stderr[-500:])
                            return False
                        else:
                            print(f"LaTeX pass {pass_num + 1} completed with warnings (return code {result.returncode})")
                    else:
                        print(f"LaTeX pass {pass_num + 1} completed successfully")
                
                # Copy output PDF
                generated_pdf = temp_path / "presentation.pdf"
                if generated_pdf.exists():
                    if output_file is None:
                        output_file = Path(markdown_file).stem + ".pdf"
                    
                    shutil.copy2(generated_pdf, output_file)
                    print(f"Generated: {output_file} (using {latex_engine})")
                    return True
                else:
                    print("LaTeX compilation succeeded but no PDF generated")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("LaTeX compilation timed out")
                return False
            except Exception as e:
                print(f"LaTeX compilation error: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def _markdown_to_latex(self, md_content: str) -> str:
        """Convert markdown content to LaTeX document"""
        # Get theme colors
        theme = self.theme_data
        colors = theme.get('colors', {})
        
        # Convert hex colors to LaTeX RGB (integer values 0-255)
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                return "0,0,0"
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return f"{r},{g},{b}"
            except ValueError:
                return "0,0,0"
        
        bg_color = hex_to_rgb(colors.get('background', '#ffffff'))
        text_color = hex_to_rgb(colors.get('text', '#000000'))
        accent_color = hex_to_rgb(colors.get('accent', '#2563eb'))
        
        # Split into slides - but only on standalone slide separators, not table separators
        import re
        # Split on '---' that are on their own line (slide separators)
        # but not on '---' inside table rows like |---------|
        slides = re.split(r'\n---\n', md_content)
        slides = [slide.strip() for slide in slides if slide.strip()]
        
        # Generate LaTeX document
        latex_doc = f"""\\documentclass[11pt]{{article}}

% Packages
\\usepackage[landscape,margin=0.5in]{{geometry}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{xcolor}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{enumitem}}
\\usepackage{{listings}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage{{multicol}}

% Colors
\\definecolor{{bgcolor}}{{RGB}}{{{bg_color}}}
\\definecolor{{textcolor}}{{RGB}}{{{text_color}}}
\\definecolor{{accentcolor}}{{RGB}}{{{accent_color}}}

% Page setup
\\pagecolor{{bgcolor}}
\\color{{textcolor}}
\\pagestyle{{empty}}

% Commands
\\newcommand{{\\slidetitle}}[1]{{%
  \\begin{{center}}
  \\textcolor{{accentcolor}}{{\\huge\\textbf{{#1}}}}
  \\end{{center}}
  \\vspace{{0.5cm}}
}}

% Math setup
\\everymath{{\\displaystyle}}

% List styling
\\setlist[itemize]{{leftmargin=1cm,itemsep=0.3cm}}
\\renewcommand{{\\labelitemi}}{{\\textcolor{{accentcolor}}{{\\textbullet}}}}

\\begin{{document}}

"""
        
        for i, slide in enumerate(slides):
            # Extract title and content
            lines = slide.split('\n')
            title = None
            content_lines = []
            
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                elif line.strip():
                    content_lines.append(line)
            
            # Add slide
            if title:
                latex_doc += f"\\slidetitle{{{title}}}\n\n"
            
            # Process content
            content = '\n'.join(content_lines)
            content = self._convert_markdown_content_to_latex(content)
            latex_doc += content + "\n\n"
            
            # Add slide number
            latex_doc += f"\\vfill\n\\begin{{flushright}}\n\\textcolor{{gray}}{{\\small {i+1}/{len(slides)}}}\n\\end{{flushright}}\n\n"
            
            # Page break (except for last slide)
            if i < len(slides) - 1:
                latex_doc += "\\newpage\n\n"
        
        latex_doc += "\\end{document}"
        return latex_doc
    
    def _convert_columns_to_latex(self, content: str) -> str:
        """Convert multi-column layout syntax to LaTeX"""
        import re
        
        # Handle the multi-column container
        content = re.sub(r':::: columns\s*\n', r'\\begin{multicols}{2}\n', content)
        content = re.sub(r'\n::::\s*\n', r'\n\\end{multicols}\n', content)
        content = re.sub(r'\n::::\s*$', r'\n\\end{multicols}', content)
        
        # Handle column divisions
        content = re.sub(r'::: left\s*\n', r'', content)  # Remove left marker
        content = re.sub(r'\n:::\s*\n', r'\n\\columnbreak\n', content)  # Column break
        content = re.sub(r'::: right\s*\n', r'', content)  # Remove right marker
        content = re.sub(r'\n:::\s*$', r'', content)  # Remove final column marker
        
        return content
    
    def _convert_markdown_content_to_latex(self, content: str) -> str:
        """Convert markdown content to LaTeX"""
        import re
        
        # Handle Unicode characters first
        content = self._handle_unicode_for_latex(content)
        
        # Handle multi-column layouts FIRST
        content = self._convert_columns_to_latex(content)
        
        # Handle math (already in LaTeX format, just fix display math)
        content = re.sub(r'\$\$(.+?)\$\$', r'\\\\[\\1\\\\]', content, flags=re.DOTALL)
        
        # Headers
        content = re.sub(r'^### (.+)$', r'\\textbf{\\Large \1}\\\\[0.3cm]', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'\\textbf{\\huge \1}\\\\[0.5cm]', content, flags=re.MULTILINE)
        
        # Bold and italic - fix escaping
        content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
        content = re.sub(r'\*([^*]+?)\*', r'\\textit{\1}', content)
        
        # Tables BEFORE list processing to avoid interference
        content = self._convert_tables_to_latex(content)
        
        # Lists
        content = re.sub(r'^- (.+)$', r'\\item \1', content, flags=re.MULTILINE)
        
        # Wrap lists in itemize environment
        lines = content.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('\\item'):
                if not in_list:
                    result_lines.append('\\begin{itemize}')
                    in_list = True
                result_lines.append(line)
            else:
                if in_list:
                    result_lines.append('\\end{itemize}')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('\\end{itemize}')
        
        content = '\n'.join(result_lines)
        
        # Code blocks
        content = re.sub(r'```(\w+)?\n(.+?)\n```', 
                        r'\\begin{lstlisting}\n\\2\n\\end{lstlisting}', 
                        content, flags=re.DOTALL)
        
        # Inline code
        content = re.sub(r'`(.+?)`', r'\\texttt{\\1}', content)
        
        # Paragraphs
        content = re.sub(r'\n\n', r'\\\\\n', content)
        
        return content
    
    def _convert_tables_to_latex(self, content: str) -> str:
        """Convert markdown tables to LaTeX tables"""
        import re
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line looks like a table header (contains |)
            if '|' in line and line.strip():
                # Look ahead to see if next line is separator
                if i + 1 < len(lines) and '---' in lines[i + 1] and '|' in lines[i + 1]:
                    # This is a table
                    table_lines = [line]
                    i += 1  # Skip separator line
                    i += 1  # Move to first data row
                    
                    # Collect all table data rows
                    while i < len(lines) and '|' in lines[i]:
                        table_lines.append(lines[i].strip())
                        i += 1
                    
                    # Convert table to LaTeX
                    latex_table = self._markdown_table_to_latex(table_lines)
                    result_lines.append(latex_table)
                    continue
            
            result_lines.append(lines[i])
            i += 1
        
        return '\n'.join(result_lines)
    
    def _markdown_table_to_latex(self, table_lines):
        """Convert a markdown table to LaTeX table"""
        if not table_lines:
            return ""
        
        # Parse the first row to get column count
        header_row = table_lines[0]
        columns = [col.strip() for col in header_row.split('|') if col.strip()]
        col_count = len(columns)
        
        # Create LaTeX table
        latex = "\\begin{center}\n"
        latex += "\\begin{tabular}{" + "l" * col_count + "}\n"
        latex += "\\hline\n"
        
        # Add header row
        header_cells = []
        for col in columns:
            # Remove markdown formatting from headers
            col = col.replace('**', '').replace('*', '')
            header_cells.append(f"\\textbf{{{col}}}")
        latex += " & ".join(header_cells) + " \\\\\n"
        latex += "\\hline\n"
        
        # Add data rows
        for row_line in table_lines[1:]:
            cells = [cell.strip() for cell in row_line.split('|') if cell.strip()]
            if len(cells) == col_count:
                # Clean cells of markdown formatting
                clean_cells = []
                for cell in cells:
                    cell = cell.replace('**', '').replace('*', '')
                    clean_cells.append(cell)
                latex += " & ".join(clean_cells) + " \\\\\n"
        
        latex += "\\hline\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{center}\n"
        
        return latex
    
    def _handle_unicode_for_latex(self, content: str) -> str:
        """Handle Unicode characters for LaTeX compatibility"""
        # Common emoji replacements
        emoji_replacements = {
            '🚀': '\\textbf{[Rocket]}',
            '🎨': '\\textbf{[Art]}',
            '📝': '\\textbf{[Note]}',
            '🌟': '\\textbf{[Star]}',
            '⚡': '\\textbf{[Lightning]}',
            '🔧': '\\textbf{[Tool]}',
            '📊': '\\textbf{[Chart]}',
            '💾': '\\textbf{[Save]}',
            '🔍': '\\textbf{[Search]}',
            '📄': '\\textbf{[Document]}',
            '✅': '\\checkmark',
            '❌': '\\times',
            '🟢': '\\textcolor{green}{\\bullet}',
            '🟡': '\\textcolor{yellow}{\\bullet}',
            '🔴': '\\textcolor{red}{\\bullet}',
            '💻': '\\textbf{[Computer]}',
            '🌐': '\\textbf{[Web]}',
            '📱': '\\textbf{[Mobile]}',
            '🎯': '\\textbf{[Target]}',
            '🏆': '\\textbf{[Trophy]}',
            '📈': '\\textbf{[Growth]}',
            '🎉': '\\textbf{[Celebration]}',
        }
        
        # Replace emojis
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Handle Hindi text (बोध) and other special characters
        content = content.replace('बोध', 'Bodh')
        
        # Handle other problematic Unicode characters
        # Replace smart quotes
        content = content.replace('"', '"')
        content = content.replace('"', '"')
        content = content.replace(''', "'")
        content = content.replace(''', "'")
        
        # Handle em dashes and en dashes
        content = content.replace('—', '---')
        content = content.replace('–', '--')
        
        # Remove or replace other problematic Unicode characters
        # This is a fallback for any remaining Unicode issues
        try:
            content.encode('ascii')
        except UnicodeEncodeError:
            # If there are still Unicode characters, replace them with safe equivalents
            import unicodedata
            content = unicodedata.normalize('NFKD', content).encode('ascii', 'ignore').decode('ascii')
        
        return content
    
    def convert_to_html(self, markdown_file, output_file=None, _test_mode=False):
        """Convert markdown file to HTML presentation"""
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # CRITICAL FIX: Get base directory for image resolution
        base_dir = os.path.dirname(os.path.abspath(markdown_file))
        
        # Parse slides
        slides = self.parse_markdown_slides(md_content, base_dir)
        
        if not slides:
            raise ValueError("No slides found in markdown file")
        
        # Encode logo if provided
        logo_data = None
        logo_mime_type = 'image/png'  # Default
        if self.logo_path and os.path.exists(self.logo_path):
            logo_result = self._encode_image(self.logo_path)
            if logo_result:
                logo_data = logo_result['data']
                logo_mime_type = logo_result['mime_type']
        
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
            font_css=self.font_css,
            logo_data=logo_data,
            logo_mime_type=logo_mime_type,
            logo_position=self.logo_position,
            enable_navigation=self.config.get('navigation.enabled', True),
            show_arrows=self.config.get('navigation.show_arrows', True),
            show_dots=self.config.get('navigation.show_dots', True),
            show_slide_numbers=self.config.get('slide_number.enabled', True),
            slide_number_format=self.config.get_slide_number_format(),
            initial_slide_number=initial_slide_number,
            config=self.config,
            use_local_mathjax=_test_mode,
            mock_mathjax_js=self.mock_mathjax_js,
            local_mathjax_js=self.local_mathjax_js
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
            # Set PDF_BACKEND for the CLI tool based on environment variable or default
            if 'BODH_PDF_BACKEND' not in os.environ:
                os.environ['BODH_PDF_BACKEND'] = 'playwright' # Default to playwright for CLI
            output_file = converter.convert_to_pdf(args.input, args.output)
        
        if args.verbose:
            print(f"Successfully converted {args.input} to {output_file}")
            print(f"PDF Backend: {os.environ.get('BODH_PDF_BACKEND')}")
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