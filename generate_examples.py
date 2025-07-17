#!/usr/bin/env python3
"""
Generate HTML and PDF examples for GitHub Pages
"""

import os
from pathlib import Path
from bodh import MarkdownToPDF

def generate_examples():
    """Generate HTML and PDF examples for all themes"""
    
    # Create output directories
    os.makedirs('docs/examples', exist_ok=True)
    os.makedirs('docs/pdfs', exist_ok=True)
    
    # Read showcase content
    with open('examples/showcase.md', 'r') as f:
        content = f.read()
    
    # Themes to generate
    themes = ['modern', 'minimal', 'gradient', 'dark', 'default', 'sky', 'solarized', 'moon']
    
    for theme in themes:
        print(f"Generating examples for theme: {theme}")
        
        try:
            # Create converter
            converter = MarkdownToPDF(theme=theme, font_family='Inter', font_size=20)
            
            # Parse slides
            slides = converter.parse_markdown_slides(content)
            
            # Generate HTML with navigation
            html_content = converter.template.render(
                title=f'Bodh Showcase - {theme.title()} Theme',
                slides=slides,
                css=converter.css,
                font_family='Inter',
                logo_data=None,
                logo_position='top-right',
                enable_navigation=True,
                show_arrows=True,
                show_dots=True,
                show_slide_numbers=True,
                slide_number_format='{current}/{total}'
            )
            
            # Write HTML file
            html_path = f'docs/examples/showcase-{theme}.html'
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"Generated HTML: {html_path}")
            
            # Generate PDF (only for main themes to avoid timeout)
            if theme in ['modern', 'minimal', 'gradient', 'dark']:
                pdf_path = f'docs/pdfs/showcase-{theme}.pdf'
                converter.convert_to_pdf('examples/showcase.md', pdf_path)
                print(f"Generated PDF: {pdf_path}")
                
        except Exception as e:
            print(f"Error generating {theme}: {e}")
            continue
    
    print("Example generation completed!")

if __name__ == "__main__":
    generate_examples()