#!/usr/bin/env python3
"""
mkpred - Convert Markdown to beautiful PDF presentations
Enhanced version with themes, fonts, logos, and images
"""

import argparse
import os
import sys
from pathlib import Path
import markdown
from jinja2 import Template
from xhtml2pdf import pisa
import re
import json
import base64


class MarkdownToPDF:
    def __init__(self, theme='default', font_family='Inter', font_size=20, logo_path=None, logo_position='top-right'):
        self.slide_separator = "---"
        self.theme = theme
        self.font_family = font_family
        self.font_size = font_size
        self.logo_path = logo_path
        self.logo_position = logo_position
        self.template = self._get_html_template()
        self.themes = self._get_themes()
    
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
                html_content = markdown.markdown(slide_content.strip(), extensions=['fenced_code'])
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
    
    def _get_themes(self):
        """Available themes inspired by reveal.js"""
        return {
            'default': {
                'bg_color': '#ffffff',
                'text_color': '#333333',
                'heading_color': '#2c3e50',
                'accent_color': '#3498db',
                'code_bg': '#f4f4f4',
                'quote_bg': '#f8f9fa'
            },
            'dark': {
                'bg_color': '#2c3e50',
                'text_color': '#ecf0f1',
                'heading_color': '#3498db',
                'accent_color': '#e74c3c',
                'code_bg': '#34495e',
                'quote_bg': '#34495e'
            },
            'sky': {
                'bg_color': '#f0f8ff',
                'text_color': '#2c3e50',
                'heading_color': '#1e3a8a',
                'accent_color': '#3b82f6',
                'code_bg': '#e0f2fe',
                'quote_bg': '#dbeafe'
            },
            'solarized': {
                'bg_color': '#fdf6e3',
                'text_color': '#657b83',
                'heading_color': '#b58900',
                'accent_color': '#d33682',
                'code_bg': '#eee8d5',
                'quote_bg': '#eee8d5'
            },
            'moon': {
                'bg_color': '#1a202c',
                'text_color': '#e2e8f0',
                'heading_color': '#63b3ed',
                'accent_color': '#ed8936',
                'code_bg': '#2d3748',
                'quote_bg': '#2d3748'
            }
        }
    
    def _get_css_styles(self):
        """CSS styles for beautiful presentations"""
        theme_colors = self.themes.get(self.theme, self.themes['default'])
        
        return f"""
        @page {{
            size: A4 landscape;
            margin: 1.5cm;
        }}
        
        body {{
            font-family: '{self.font_family}', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: {theme_colors['text_color']};
            background-color: {theme_colors['bg_color']};
            margin: 0;
            padding: 0;
            font-size: {self.font_size}px;
        }}
        
        .slide {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 3rem;
            box-sizing: border-box;
            background-color: {theme_colors['bg_color']};
            position: relative;
        }}
        
        .slide-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .logo {{
            position: absolute;
            z-index: 100;
        }}
        
        .logo img {{
            max-width: 100px;
            max-height: 60px;
            opacity: 0.8;
        }}
        
        .logo-top-left {{
            top: 2rem;
            left: 2rem;
        }}
        
        .logo-top-right {{
            top: 2rem;
            right: 2rem;
        }}
        
        .logo-bottom-left {{
            bottom: 2rem;
            left: 2rem;
        }}
        
        .logo-bottom-right {{
            bottom: 2rem;
            right: 2rem;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
        
        h1 {{
            color: {theme_colors['heading_color']};
            font-size: 2.8em;
            margin-bottom: 1.5rem;
            text-align: center;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-bottom: 4px solid {theme_colors['accent_color']};
            padding-bottom: 0.8rem;
        }}
        
        h2 {{
            color: {theme_colors['heading_color']};
            font-size: 2.2em;
            margin-bottom: 1.2rem;
            font-weight: 600;
            border-left: 6px solid {theme_colors['accent_color']};
            padding-left: 1.5rem;
        }}
        
        h3 {{
            color: {theme_colors['heading_color']};
            font-size: 1.8em;
            margin-bottom: 1rem;
            font-weight: 600;
        }}
        
        h4 {{
            color: {theme_colors['heading_color']};
            font-size: 1.4em;
            margin-bottom: 0.8rem;
            font-weight: 600;
        }}
        
        p {{
            font-size: 1.2em;
            margin-bottom: 1.5rem;
            text-align: justify;
            font-weight: 400;
        }}
        
        ul, ol {{
            font-size: 1.1em;
            margin-bottom: 1.5rem;
            padding-left: 2.5rem;
        }}
        
        li {{
            margin-bottom: 0.8rem;
            line-height: 1.8;
        }}
        
        li::marker {{
            color: {theme_colors['accent_color']};
            font-weight: 600;
        }}
        
        blockquote {{
            background: {theme_colors['quote_bg']};
            border-left: 6px solid {theme_colors['accent_color']};
            margin: 2rem 0;
            padding: 2rem;
            font-style: italic;
            font-size: 1.3em;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        blockquote p {{
            margin-bottom: 0;
            font-weight: 300;
        }}
        
        code {{
            background: {theme_colors['code_bg']};
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.9em;
            color: {theme_colors['accent_color']};
            font-weight: 600;
        }}
        
        pre {{
            background: {theme_colors['code_bg']};
            padding: 2rem;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9em;
            border: 1px solid {theme_colors['accent_color']};
            margin: 1.5rem 0;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: {theme_colors['text_color']};
            font-weight: 400;
        }}
        
        strong {{
            color: {theme_colors['accent_color']};
            font-weight: 700;
        }}
        
        em {{
            color: {theme_colors['accent_color']};
            font-style: italic;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 2rem auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
        }}
        
        th, td {{
            border: 1px solid {theme_colors['accent_color']};
            padding: 1rem;
            text-align: left;
        }}
        
        th {{
            background-color: {theme_colors['accent_color']};
            color: white;
            font-weight: 600;
        }}
        
        .center {{
            text-align: center;
        }}
        
        .large {{
            font-size: 1.5em;
        }}
        
        .highlight {{
            background-color: {theme_colors['accent_color']};
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}
        """
    
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
            css=self._get_css_styles(),
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
    parser = argparse.ArgumentParser(description='Convert Markdown to beautiful PDF presentations')
    parser.add_argument('input', nargs='?', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    parser.add_argument('-t', '--theme', choices=['default', 'dark', 'sky', 'solarized', 'moon'], 
                       default='default', help='Theme for the presentation')
    parser.add_argument('-f', '--font', default='Inter', help='Font family (default: Inter)')
    parser.add_argument('-s', '--size', type=int, default=20, help='Base font size (default: 20)')
    parser.add_argument('-l', '--logo', help='Path to logo image')
    parser.add_argument('-p', '--position', choices=['top-left', 'top-right', 'bottom-left', 'bottom-right'],
                       default='top-right', help='Logo position (default: top-right)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--list-themes', action='store_true', help='List available themes')
    
    args = parser.parse_args()
    
    if args.list_themes:
        print("Available themes:")
        themes = ['default', 'dark', 'sky', 'solarized', 'moon']
        for theme in themes:
            print(f"  - {theme}")
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
            print(f"Theme: {args.theme}")
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