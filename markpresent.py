#!/usr/bin/env python3
"""
MarkPresent - Modular Markdown to PDF Presentation Tool
"""

import argparse
import os
import sys
from pathlib import Path
import markdown
from jinja2 import Template
from xhtml2pdf import pisa
import json
import base64


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
    
    def generate_css(self, theme_data, font_family, font_size):
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
            font_size=font_size
        )


class MarkdownToPDF:
    def __init__(self, theme='default', font_family='Inter', font_size=20, 
                 logo_path=None, logo_position='top-right'):
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
        self.theme_data = self.theme_loader.load_theme(theme)
        
        # Generate styles
        self.css = self.style_generator.generate_css(
            self.theme_data, font_family, font_size
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
        """Parse markdown content into individual slides"""
        slides = []
        slide_parts = md_content.split(f"\n{self.slide_separator}\n")
        
        for slide_content in slide_parts:
            if slide_content.strip():
                html_content = markdown.markdown(
                    slide_content.strip(), 
                    extensions=['fenced_code', 'tables', 'codehilite']
                )
                slides.append(html_content)
        
        return slides
    
    def _get_html_template(self):
        """HTML template for the presentation"""
        return Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link href="https://fonts.googleapis.com/css2?family={{ font_family.replace(' ', '+') }}:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        {{ css }}
    </style>
</head>
<body>
    {% for slide in slides %}
    <div class="slide">
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
        
        # Generate HTML
        title = Path(markdown_file).stem
        html_content = self.template.render(
            title=title,
            slides=slides,
            css=self.css,
            font_family=self.font_family,
            logo_data=logo_data,
            logo_position=self.logo_position
        )
        
        # Generate PDF
        if output_file is None:
            output_file = f"{title}.pdf"
        
        with open(output_file, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
            
        if pisa_status.err:
            raise Exception("PDF generation failed")
        
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to beautiful PDF presentations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.md                    # Basic usage
  %(prog)s slides.md -t dark -f "Roboto"     # Dark theme with custom font
  %(prog)s demo.md -l logo.png -p bottom-left # With logo
  %(prog)s --list-themes                      # Show available themes
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    parser.add_argument('-t', '--theme', default='default', 
                       help='Theme name (default: default)')
    parser.add_argument('-f', '--font', default='Inter', 
                       help='Font family (default: Inter)')
    parser.add_argument('-s', '--size', type=int, default=20, 
                       help='Base font size (default: 20)')
    parser.add_argument('-l', '--logo', help='Path to logo image')
    parser.add_argument('-p', '--position', 
                       choices=['top-left', 'top-right', 'bottom-left', 'bottom-right'],
                       default='top-right', help='Logo position (default: top-right)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--list-themes', action='store_true', help='List available themes')
    
    args = parser.parse_args()
    
    if args.list_themes:
        theme_loader = ThemeLoader()
        themes = theme_loader.list_themes()
        print("Available themes:")
        print("-" * 50)
        for theme in themes:
            print(f"  {theme['name']:12} - {theme['description']}")
        print("\nUsage: python markpresent.py input.md -t THEME_NAME")
        return
    
    if not args.input:
        parser.error("Input markdown file is required (unless using --list-themes)")
    
    try:
        converter = MarkdownToPDF(
            theme=args.theme,
            font_family=args.font,
            font_size=args.size,
            logo_path=args.logo,
            logo_position=args.position
        )
        
        output_file = converter.convert_to_pdf(args.input, args.output)
        
        if args.verbose:
            print(f"Successfully converted {args.input} to {output_file}")
            print(f"Theme: {args.theme} ({converter.theme_data['name']})")
            print(f"Font: {args.font} ({args.size}px)")
            if args.logo:
                print(f"Logo: {args.logo} ({args.position})")
        else:
            print(f"Generated: {output_file}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()