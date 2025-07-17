#!/usr/bin/env python3
"""
Configuration management for MarkPresent
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class PresentationConfig:
    """Configuration handler for MarkPresent presentations"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_default_config()
        if config_file:
            self.load_config(config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            'theme': 'modern',
            'font': {
                'family': 'Inter',
                'size': 20
            },
            'logo': {
                'source': None,
                'location': 'top-right',
                'size': 100
            },
            'slide_number': {
                'enabled': True,
                'format': 'current/total',  # Options: 'current', 'current/total', 'total'
                'position': 'bottom-right'
            },
            'navigation': {
                'enabled': True,
                'show_arrows': True,
                'show_dots': True,
                'show_progress': True,
                'keyboard_shortcuts': True
            },
            'output': {
                'format': 'pdf',  # Options: 'pdf', 'html'
                'filename': None,  # Auto-generate if None
                'page_size': 'A4',
                'orientation': 'landscape'
            },
            'content': {
                'slide_separator': '---',
                'title_slide': True,
                'thank_you_slide': False
            },
            'style': {
                'slide_padding': '3rem',
                'element_margin': '1.5rem',
                'shadows': False,
                'rounded_corners': False,
                'animations': True
            }
        }
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from YAML file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            user_config = yaml.safe_load(f)
        
        # Merge user config with defaults
        self.config = self._merge_configs(self.config, user_config)
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config_file: str) -> None:
        """Save current configuration to YAML file"""
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'font.size')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_slide_number_format(self) -> str:
        """Get the slide number format string"""
        format_type = self.get('slide_number.format', 'current/total')
        
        formats = {
            'current': '{current}',
            'current/total': '{current}/{total}',
            'total': '{total}',
            'percent': '{percent}%'
        }
        
        return formats.get(format_type, '{current}/{total}')
    
    def get_logo_config(self) -> Dict[str, Any]:
        """Get logo configuration"""
        return {
            'source': self.get('logo.source'),
            'location': self.get('logo.location', 'top-right'),
            'size': self.get('logo.size', 100)
        }
    
    def get_theme_config(self) -> Dict[str, Any]:
        """Get theme and styling configuration"""
        return {
            'theme': self.get('theme', 'modern'),
            'font_family': self.get('font.family', 'Inter'),
            'font_size': self.get('font.size', 20),
            'shadows': self.get('style.shadows', False),
            'rounded_corners': self.get('style.rounded_corners', False),
            'animations': self.get('style.animations', True)
        }
    
    def get_navigation_config(self) -> Dict[str, Any]:
        """Get navigation configuration"""
        return {
            'enabled': self.get('navigation.enabled', True),
            'show_arrows': self.get('navigation.show_arrows', True),
            'show_dots': self.get('navigation.show_dots', True),
            'show_progress': self.get('navigation.show_progress', True),
            'keyboard_shortcuts': self.get('navigation.keyboard_shortcuts', True)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.config.copy()
    
    def validate(self) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate theme
        if self.get('theme') not in ['default', 'modern', 'minimal', 'gradient', 'dark', 'sky', 'solarized', 'moon']:
            issues.append("Invalid theme. Must be one of: default, modern, minimal, gradient, dark, sky, solarized, moon")
        
        # Validate font size
        font_size = self.get('font.size')
        if not isinstance(font_size, int) or font_size < 8 or font_size > 72:
            issues.append("Font size must be between 8 and 72")
        
        # Validate logo location
        logo_location = self.get('logo.location')
        if logo_location not in ['top-left', 'top-right', 'bottom-left', 'bottom-right']:
            issues.append("Logo location must be one of: top-left, top-right, bottom-left, bottom-right")
        
        # Validate slide number format
        slide_format = self.get('slide_number.format')
        if slide_format not in ['current', 'current/total', 'total', 'percent']:
            issues.append("Slide number format must be one of: current, current/total, total, percent")
        
        return issues


def load_config(config_file: Optional[str] = None) -> PresentationConfig:
    """Helper function to load configuration"""
    return PresentationConfig(config_file)


def create_sample_config(output_file: str = 'markpresent.yml') -> None:
    """Create a sample configuration file"""
    config = PresentationConfig()
    
    # Add comments to the sample config
    sample_config = {
        '# MarkPresent Configuration File': None,
        '# Theme selection': None,
        'theme': 'modern',  # Options: default, modern, minimal, gradient, dark, sky, solarized, moon
        
        '# Font configuration': None,
        'font': {
            'family': 'Inter',  # Any Google Font name
            'size': 20  # Font size in pixels
        },
        
        '# Logo configuration': None,
        'logo': {
            'source': None,  # Path to logo image file
            'location': 'top-right',  # Options: top-left, top-right, bottom-left, bottom-right
            'size': 100  # Maximum logo size in pixels
        },
        
        '# Slide numbering': None,
        'slide_number': {
            'enabled': True,
            'format': 'current/total',  # Options: current, current/total, total, percent
            'position': 'bottom-right'  # Position of slide numbers
        },
        
        '# Navigation controls': None,
        'navigation': {
            'enabled': True,
            'show_arrows': True,  # Show prev/next buttons
            'show_dots': True,    # Show slide dots
            'show_progress': True, # Show progress bar
            'keyboard_shortcuts': True  # Enable keyboard navigation
        },
        
        '# Output settings': None,
        'output': {
            'format': 'pdf',  # Options: pdf, html
            'filename': None,  # Auto-generate if None
            'page_size': 'A4',
            'orientation': 'landscape'
        },
        
        '# Content settings': None,
        'content': {
            'slide_separator': '---',
            'title_slide': True,
            'thank_you_slide': False
        },
        
        '# Style settings': None,
        'style': {
            'slide_padding': '3rem',
            'element_margin': '1.5rem',
            'shadows': False,
            'rounded_corners': False,
            'animations': True
        }
    }
    
    # Remove comment keys before saving
    clean_config = {k: v for k, v in sample_config.items() if not k.startswith('#')}
    
    with open(output_file, 'w') as f:
        f.write("# MarkPresent Configuration File\n")
        f.write("# https://github.com/nipunbatra/MarkPresent\n\n")
        yaml.dump(clean_config, f, default_flow_style=False, indent=2)
    
    print(f"Sample configuration created: {output_file}")


if __name__ == "__main__":
    # Create sample config if run directly
    create_sample_config()