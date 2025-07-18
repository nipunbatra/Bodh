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
    
    # Check if showcase file exists
    if not os.path.exists('examples/showcase.md'):
        print("Error: examples/showcase.md not found")
        return
    
    # Read showcase content
    with open('examples/showcase.md', 'r') as f:
        content = f.read()
    
    # Themes to generate
    themes = ['modern', 'minimal', 'gradient', 'dark', 'default', 'sky', 'solarized', 'moon']
    
    html_generated = 0
    pdf_generated = 0
    
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
            html_generated += 1
            
            # Generate PDF (only for main themes to avoid timeout, and only if Playwright is available)
            if theme in ['modern', 'minimal', 'gradient', 'dark']:
                try:
                    pdf_path = f'docs/pdfs/showcase-{theme}.pdf'
                    converter.convert_to_pdf('examples/showcase.md', pdf_path)
                    print(f"Generated PDF: {pdf_path}")
                    pdf_generated += 1
                except Exception as pdf_error:
                    print(f"Warning: Could not generate PDF for {theme}: {pdf_error}")
                    # Continue without PDF generation
                
        except Exception as e:
            print(f"Error generating {theme}: {e}")
            continue
    
    print(f"Example generation completed! HTML: {html_generated}, PDF: {pdf_generated}")
    
    # Ensure index.html exists
    if not os.path.exists('docs/index.html'):
        print("Creating fallback index.html")
        create_fallback_index()

def create_fallback_index():
    """Create a fallback index.html if it doesn't exist"""
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bodh - Example Presentations</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
        h1 { color: #2563eb; }
        .example { margin: 1rem 0; padding: 1rem; border: 1px solid #ccc; border-radius: 8px; }
        a { color: #2563eb; text-decoration: none; margin-right: 1rem; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🚀 Bodh Examples</h1>
    <p><strong>Bodh</strong> (बोध) means "knowledge" in Hindi - Beautiful Markdown to PDF Presentations</p>
    
    <div class="example">
        <h3>Modern Theme</h3>
        <a href="examples/showcase-modern.html">View HTML</a>
        <a href="pdfs/showcase-modern.pdf">Download PDF</a>
    </div>
    
    <div class="example">
        <h3>Minimal Theme</h3>
        <a href="examples/showcase-minimal.html">View HTML</a>
        <a href="pdfs/showcase-minimal.pdf">Download PDF</a>
    </div>
    
    <div class="example">
        <h3>Gradient Theme</h3>
        <a href="examples/showcase-gradient.html">View HTML</a>
        <a href="pdfs/showcase-gradient.pdf">Download PDF</a>
    </div>
    
    <div class="example">
        <h3>Dark Theme</h3>
        <a href="examples/showcase-dark.html">View HTML</a>
        <a href="pdfs/showcase-dark.pdf">Download PDF</a>
    </div>
    
    <p><a href="https://github.com/nipunbatra/Bodh">View on GitHub</a></p>
</body>
</html>"""
    
    with open('docs/index.html', 'w') as f:
        f.write(index_content)
    print("Created fallback index.html")

if __name__ == "__main__":
    generate_examples()