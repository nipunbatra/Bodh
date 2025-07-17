#!/usr/bin/env python3
"""
Bodh Web UI - Beautiful web interface for markdown to PDF presentations
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
import shutil
from pathlib import Path
import json
import argparse
from werkzeug.utils import secure_filename
from bodh import MarkdownToPDF, ThemeLoader
import traceback

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize theme loader
theme_loader = ThemeLoader()

@app.route('/')
def index():
    """Main page with editor"""
    themes = theme_loader.list_themes()
    return render_template('index.html', themes=themes)

@app.route('/api/themes')
def get_themes():
    """Get available themes"""
    themes = theme_loader.list_themes()
    return jsonify(themes)

@app.route('/api/preview', methods=['POST'])
def preview_slides():
    """Generate HTML preview of slides"""
    try:
        data = request.json
        markdown_content = data.get('markdown', '')
        theme = data.get('theme', 'default')
        font_family = data.get('font_family', 'Inter')
        font_size = data.get('font_size', 20)
        
        if not markdown_content.strip():
            return jsonify({'error': 'No markdown content provided'}), 400
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            tmp.write(markdown_content)
            tmp_path = tmp.name
        
        try:
            # Create converter
            converter = MarkdownToPDF(
                theme=theme,
                font_family=font_family,
                font_size=font_size
            )
            
            # Parse slides
            slides = converter.parse_markdown_slides(markdown_content)
            
            # Generate HTML preview with navigation
            html_content = converter.template.render(
                title="Preview",
                slides=slides,
                css=converter.css,
                font_family=font_family,
                logo_data=None,
                logo_position='top-right',
                enable_navigation=True,
                show_arrows=True,
                show_dots=True,
                show_slide_numbers=True,
                slide_number_format='{current}/{total}'
            )
            
            return jsonify({
                'html': html_content,
                'slide_count': len(slides)
            })
            
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_pdf():
    """Generate PDF from markdown"""
    try:
        data = request.json
        markdown_content = data.get('markdown', '')
        theme = data.get('theme', 'default')
        font_family = data.get('font_family', 'Inter')
        font_size = data.get('font_size', 20)
        
        if not markdown_content.strip():
            return jsonify({'error': 'No markdown content provided'}), 400
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_md:
            tmp_md.write(markdown_content)
            tmp_md_path = tmp_md.name
        
        tmp_pdf_path = tmp_md_path.replace('.md', '.pdf')
        
        try:
            # Create converter
            converter = MarkdownToPDF(
                theme=theme,
                font_family=font_family,
                font_size=font_size
            )
            
            # Generate PDF
            output_path = converter.convert_to_pdf(tmp_md_path, tmp_pdf_path)
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'presentation_{theme}.pdf',
                mimetype='application/pdf'
            )
            
        finally:
            # Cleanup
            if os.path.exists(tmp_md_path):
                os.unlink(tmp_md_path)
            # PDF cleanup happens after send_file
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload markdown file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.md'):
            content = file.read().decode('utf-8')
            return jsonify({'content': content})
        
        return jsonify({'error': 'Please upload a .md file'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    parser = argparse.ArgumentParser(description='Bodh Web UI - Beautiful presentation generator')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload in debug mode')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Bodh Web UI...")
    print(f"📍 Server: http://localhost:{args.port}")
    print(f"🎨 Themes: {len(theme_loader.list_themes())} available")
    print(f"📝 Ready to create beautiful presentations!")
    print(f"⚡ Press Ctrl+C to stop")
    
    try:
        app.run(
            debug=args.debug,
            host=args.host,
            port=args.port,
            use_reloader=not args.no_reload if args.debug else False
        )
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Bodh!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


if __name__ == '__main__':
    main()