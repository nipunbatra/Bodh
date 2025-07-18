#!/usr/bin/env python3
"""
Generate HTML and PDF examples for GitHub Pages
"""

import os
from pathlib import Path
from bodh import MarkdownToPDF

def _get_slide_number_format(format_type):
    """Convert config format to template format"""
    format_map = {
        'current': '{current}',
        'current/total': '{current}/{total}',
        'total': '{total}',
        'percent': '{percent}%'
    }
    return format_map.get(format_type, '{current}/{total}')

def generate_examples():
    """Generate HTML and PDF examples for all themes"""
    
    print("🚀 Starting Bodh example generation...")
    print(f"📁 Current working directory: {os.getcwd()}")
    
    # Create output directories
    print("📂 Creating output directories...")
    os.makedirs('docs/examples', exist_ok=True)
    os.makedirs('docs/pdfs', exist_ok=True)
    print("✅ Output directories created: docs/examples/ and docs/pdfs/")
    
    # Check if showcase file exists
    if not os.path.exists('examples/showcase.md'):
        print("❌ Error: examples/showcase.md not found")
        print("📁 Current directory contents:")
        for item in os.listdir('.'):
            print(f"  - {item}")
        return
    
    # Read showcase content
    print("📖 Reading showcase.md content...")
    with open('examples/showcase.md', 'r') as f:
        content = f.read()
    print(f"✅ Read {len(content)} characters from showcase.md")
    
    # Basic theme examples
    themes = ['modern', 'minimal', 'gradient', 'dark', 'default', 'sky', 'solarized', 'moon']
    print(f"🎨 Will generate examples for {len(themes)} themes: {', '.join(themes)}")
    
    # Configuration-based examples
    config_examples = [
        ('logo-demo', 'configs/logo-demo.yml'),
        ('slide-numbers-demo', 'configs/slide-numbers-demo.yml'), 
        ('corporate-branding', 'configs/corporate-branding.yml')
    ]
    print(f"⚙️ Will generate {len(config_examples)} configuration examples")
    
    html_generated = 0
    pdf_generated = 0
    
    for i, theme in enumerate(themes, 1):
        print(f"\n🎨 [{i}/{len(themes)}] Generating examples for theme: {theme}")
        
        try:
            print(f"  🔧 Creating MarkdownToPDF converter for {theme}...")
            # Create converter
            converter = MarkdownToPDF(theme=theme, font_family='Inter', font_size=20)
            print(f"  ✅ Converter created successfully")
            
            print(f"  📝 Parsing slides from markdown...")
            # Parse slides
            slides = converter.parse_markdown_slides(content)
            print(f"  ✅ Found {len(slides)} slides")
            
            print(f"  🌐 Generating HTML content...")
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
            print(f"  ✅ Generated {len(html_content)} characters of HTML")
            
            # Write HTML file
            html_path = f'docs/examples/showcase-{theme}.html'
            print(f"  💾 Writing HTML to {html_path}...")
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"  ✅ HTML saved: {html_path}")
            html_generated += 1
            
            # Generate PDF (only for main themes to avoid timeout, and only if Playwright is available)
            if theme in ['modern', 'minimal', 'gradient', 'dark']:
                try:
                    pdf_path = f'docs/pdfs/showcase-{theme}.pdf'
                    print(f"  📄 Generating PDF: {pdf_path}...")
                    converter.convert_to_pdf('examples/showcase.md', pdf_path)
                    print(f"  ✅ PDF generated: {pdf_path}")
                    pdf_generated += 1
                except Exception as pdf_error:
                    print(f"  ⚠️  Warning: Could not generate PDF for {theme}: {pdf_error}")
                    # Continue without PDF generation
            else:
                print(f"  ⏭️  Skipping PDF generation for {theme} (not in main themes)")
                
        except Exception as e:
            print(f"  ❌ Error generating {theme}: {e}")
            import traceback
            print(f"  📋 Full error trace: {traceback.format_exc()}")
            continue
    
    # Generate configuration-based examples
    print(f"\n⚙️ Generating configuration-based examples...")
    for i, (example_name, config_path) in enumerate(config_examples, 1):
        print(f"\n🔧 [{i}/{len(config_examples)}] Generating {example_name} with {config_path}")
        
        try:
            # Check if config file exists
            if not os.path.exists(config_path):
                print(f"  ❌ Config file not found: {config_path}")
                continue
                
            print(f"  📖 Loading configuration from {config_path}")
            from config import load_config
            config = load_config(config_path)
            print(f"  ✅ Configuration loaded successfully")
            
            # Create converter with configuration
            print(f"  🔧 Creating converter with configuration...")
            converter = MarkdownToPDF(config=config)
            print(f"  ✅ Converter created successfully")
            
            # Use feature showcase content for config examples
            showcase_content = content
            if example_name == 'feature-showcase' and os.path.exists('examples/feature-showcase.md'):
                with open('examples/feature-showcase.md', 'r') as f:
                    showcase_content = f.read()
                print(f"  📖 Using feature-showcase.md content")
            
            # Parse slides
            print(f"  📝 Parsing slides...")
            slides = converter.parse_markdown_slides(showcase_content)
            print(f"  ✅ Found {len(slides)} slides")
            
            # Generate HTML
            print(f"  🌐 Generating HTML...")
            html_content = converter.template.render(
                title=f'Bodh {example_name.replace("-", " ").title()} Demo',
                slides=slides,
                css=converter.css,
                font_family=config.get('font.family', 'Inter'),
                logo_data=None,  # Logo will be handled by config
                logo_position=config.get('logo.location', 'top-right'),
                enable_navigation=config.get('navigation.enabled', True),
                show_arrows=config.get('navigation.show_arrows', True),
                show_dots=config.get('navigation.show_dots', True),
                show_slide_numbers=config.get('slide_number.enabled', True),
                slide_number_format=_get_slide_number_format(config.get('slide_number.format', 'current/total'))
            )
            
            # Write HTML file
            html_path = f'docs/examples/{example_name}.html'
            print(f"  💾 Writing HTML to {html_path}...")
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"  ✅ HTML saved: {html_path}")
            html_generated += 1
            
            # Generate PDF for configuration examples
            try:
                pdf_path = f'docs/pdfs/{example_name}.pdf'
                print(f"  📄 Generating PDF: {pdf_path}...")
                
                # Use showcase content for PDF generation
                temp_md_file = f'temp_{example_name}.md'
                with open(temp_md_file, 'w') as f:
                    f.write(showcase_content)
                
                converter.convert_to_pdf(temp_md_file, pdf_path)
                os.remove(temp_md_file)  # Clean up temp file
                
                print(f"  ✅ PDF generated: {pdf_path}")
                pdf_generated += 1
            except Exception as pdf_error:
                print(f"  ⚠️  Warning: Could not generate PDF for {example_name}: {pdf_error}")
                
        except Exception as e:
            print(f"  ❌ Error generating {example_name}: {e}")
            import traceback
            print(f"  📋 Full error trace: {traceback.format_exc()}")
            continue
    
    print(f"\n🎉 Example generation completed!")
    print(f"📊 Summary: {html_generated} HTML files, {pdf_generated} PDF files generated")
    
    # Ensure index.html exists
    if not os.path.exists('docs/index.html'):
        print("🔧 Creating fallback index.html...")
        create_fallback_index()
        print("✅ Fallback index.html created")
    else:
        print("✅ Index.html already exists")
    
    # Final verification
    print(f"\n📁 Final verification of docs/ directory:")
    if os.path.exists('docs'):
        for root, dirs, files in os.walk('docs'):
            level = root.replace('docs', '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({size} bytes)")
    else:
        print("❌ No docs directory found!")

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