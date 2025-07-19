#!/usr/bin/env python3
"""
Font Manager - Download and embed fonts to avoid loading issues
"""

import os
import requests
import base64
import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse


class FontManager:
    def __init__(self, cache_dir=".bodh_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Google Fonts API for font families
        self.google_fonts = {
            'Inter': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
            'Roboto': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
            'Open Sans': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap',
            'Lato': 'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap',
            'Montserrat': 'https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap',
            'Source Sans Pro': 'https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap',
            'Fira Code': 'https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap',
            'JetBrains Mono': 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap',
        }
    
    def get_font_cache_key(self, font_family):
        """Generate cache key for font family"""
        return hashlib.md5(font_family.encode()).hexdigest()
    
    def download_font_css(self, font_family):
        """Download and parse Google Fonts CSS"""
        if font_family not in self.google_fonts:
            print(f"Warning: Font '{font_family}' not in supported Google Fonts list")
            return None
            
        cache_key = self.get_font_cache_key(font_family)
        css_cache_file = self.cache_dir / f"{cache_key}.css"
        
        # Check if cached
        if css_cache_file.exists():
            with open(css_cache_file, 'r') as f:
                return f.read()
        
        try:
            # Download CSS
            print(f"Downloading font CSS for {font_family}...")
            response = requests.get(self.google_fonts[font_family], timeout=10)
            response.raise_for_status()
            
            css_content = response.text
            
            # Cache CSS
            with open(css_cache_file, 'w') as f:
                f.write(css_content)
            
            return css_content
        except Exception as e:
            print(f"Warning: Failed to download font CSS for {font_family}: {e}")
            return None
    
    def download_font_files(self, css_content, font_family):
        """Download actual font files from CSS"""
        if not css_content:
            return {}
            
        cache_key = self.get_font_cache_key(font_family)
        
        # Extract font URLs from CSS
        font_urls = re.findall(r'url\((https://[^)]+)\)', css_content)
        
        embedded_fonts = {}
        
        for url in font_urls:
            try:
                # Generate filename from URL
                parsed_url = urlparse(url)
                filename = f"{cache_key}_{hashlib.md5(url.encode()).hexdigest()[:8]}.woff2"
                font_cache_file = self.cache_dir / filename
                
                # Check if cached
                if font_cache_file.exists():
                    with open(font_cache_file, 'rb') as f:
                        font_data = f.read()
                else:
                    # Download font
                    print(f"Downloading font file: {url}")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    font_data = response.content
                    
                    # Cache font
                    with open(font_cache_file, 'wb') as f:
                        f.write(font_data)
                
                # Encode to base64
                font_base64 = base64.b64encode(font_data).decode('utf-8')
                embedded_fonts[url] = f"data:font/woff2;base64,{font_base64}"
                
            except Exception as e:
                print(f"Warning: Failed to download font file {url}: {e}")
                continue
        
        return embedded_fonts
    
    def generate_embedded_css(self, font_family):
        """Generate CSS with embedded font data"""
        css_content = self.download_font_css(font_family)
        if not css_content:
            return None
        
        embedded_fonts = self.download_font_files(css_content, font_family)
        
        # Replace URLs with embedded data
        embedded_css = css_content
        for original_url, data_url in embedded_fonts.items():
            embedded_css = embedded_css.replace(original_url, data_url)
        
        return embedded_css
    
    def get_fallback_css(self, font_family):
        """Generate fallback CSS for system fonts"""
        system_fonts = {
            'Inter': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'Roboto': 'Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'Open Sans': '"Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'Lato': 'Lato, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'Montserrat': 'Montserrat, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'Source Sans Pro': '"Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'Fira Code': '"Fira Code", "SF Mono", Monaco, monospace',
            'JetBrains Mono': '"JetBrains Mono", "SF Mono", Monaco, monospace',
        }
        
        fallback = system_fonts.get(font_family, f'"{font_family}", sans-serif')
        
        return f"""
/* Fallback font stack for {font_family} */
@font-face {{
    font-family: '{font_family}';
    font-style: normal;
    font-weight: 400;
    src: local('{font_family}'), local('{font_family.replace(' ', '-')}');
}}

body, h1, h2, h3, h4, h5, h6 {{
    font-family: {fallback};
}}
"""

    def get_optimized_font_css(self, font_family, use_embedded=True):
        """Get optimized font CSS (embedded or fallback)"""
        if use_embedded:
            embedded_css = self.generate_embedded_css(font_family)
            if embedded_css:
                print(f"Using embedded fonts for {font_family}")
                return embedded_css
        
        print(f"Using fallback fonts for {font_family}")
        return self.get_fallback_css(font_family)


if __name__ == "__main__":
    # Test font manager
    fm = FontManager()
    css = fm.get_optimized_font_css('Inter')
    print("Generated CSS length:", len(css) if css else 0)