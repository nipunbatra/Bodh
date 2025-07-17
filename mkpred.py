#!/usr/bin/env python3
"""
mkpred - Convert Markdown to beautiful PDF presentations
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
        self.css = self._get_css_styles()
        self.themes = self._get_themes()
    
    def parse_markdown_slides(self, md_content):
        """Parse markdown content into individual slides"""
        slides = []
        slide_parts = md_content.split(f"\n{self.slide_separator}\n")
        
        for slide_content in slide_parts:
            if slide_content.strip():
                html_content = markdown.markdown(slide_content.strip())
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
    <style>
        {{ css }}
    </style>
</head>
<body>
    {% for slide in slides %}
    <div class="slide">
        {{ slide | safe }}
    </div>
    {% if not loop.last %}<div class="page-break"></div>{% endif %}
    {% endfor %}
</body>
</html>
        """)
    
    def _get_css_styles(self):
        """CSS styles for beautiful presentations"""
        return """
        @page {
            size: A4 landscape;
            margin: 2cm;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .slide {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 2rem;
            box-sizing: border-box;
        }
        
        .page-break {
            page-break-after: always;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 1rem;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
        }
        
        h2 {
            color: #34495e;
            font-size: 2em;
            margin-bottom: 1rem;
            border-left: 5px solid #3498db;
            padding-left: 1rem;
        }
        
        h3 {
            color: #7f8c8d;
            font-size: 1.5em;
            margin-bottom: 0.8rem;
        }
        
        p {
            font-size: 1.2em;
            margin-bottom: 1rem;
            text-align: justify;
        }
        
        ul, ol {
            font-size: 1.1em;
            margin-bottom: 1rem;
            padding-left: 2rem;
        }
        
        li {
            margin-bottom: 0.5rem;
        }
        
        blockquote {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            margin: 1rem 0;
            padding: 1rem;
            font-style: italic;
        }
        
        code {
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
        }
        
        pre code {
            background: none;
            padding: 0;
            color: inherit;
        }
        
        strong {
            color: #e74c3c;
        }
        
        em {
            color: #9b59b6;
        }
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
        
        # Generate HTML
        title = Path(markdown_file).stem
        html_content = self.template.render(
            title=title,
            slides=slides,
            css=self.css
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
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        converter = MarkdownToPDF()
        output_file = converter.convert_to_pdf(args.input, args.output)
        
        if args.verbose:
            print(f"Successfully converted {args.input} to {output_file}")
        else:
            print(f"Generated: {output_file}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()