# 🚀 Bodh - Beautiful Markdown to PDF Presentations

**Bodh** (बोध) means "knowledge" or "understanding" in Hindi - the perfect name for a tool that helps you share your insights through beautiful presentations.

Transform your markdown into stunning professional presentations with multiple backends and comprehensive feature support.

## 🎯 **One Example, Multiple Themes & Configurations**

**Single comprehensive gradient descent tutorial demonstrating ALL features:**

- **Machine Learning Content**: Gradient descent theory, neural networks, optimization algorithms
- **Advanced Layouts**: Multi-column designs, mathematical equations, code syntax highlighting  
- **Professional Design**: Tables, performance benchmarks, typography, branding
- **Testing & Quality**: Unit tests, CI/CD examples, validation frameworks

**Same content, different themes and configurations:**

| Theme/Style | HTML Preview | PDF Download | Description |
|-------------|-------------|--------------|-------------|
| **Modern** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-modern.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-modern.pdf) | Clean professional design, blue accents |
| **Minimal** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-minimal.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-minimal.pdf) | Clean and simple, no logo, minimal styling |
| **Dark** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-dark.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-dark.pdf) | Dark background, light text, bold styling |
| **Gradient** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-gradient.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-gradient.pdf) | Colorful gradient background, stylish design |
| **Academic** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-academic.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-academic.pdf) | Traditional academic paper style, LaTeX backend |
| **Presentation** | [View HTML](https://nipunbatra.github.io/Bodh/examples/gradient-descent-presentation.html) | [Download PDF](https://nipunbatra.github.io/Bodh/pdfs/gradient-descent-presentation.pdf) | Large fonts, no slide numbers, bold colors |

*Perfect demonstration: Same comprehensive content styled with different themes, configurations, and design approaches*

## ✨ Features

### 🚀 **Multiple Generation Backends**
- **Playwright Backend**: Full-featured with MathJax, interactive elements, complex layouts
- **LaTeX Direct**: Ultra-fast native LaTeX compilation (15x faster)
- **Local MathJax**: Offline math rendering without CDN dependencies

### 📋 **Content & Layout**
- **Multi-column Layouts**: Professional side-by-side content organization
- **Mathematical Notation**: LaTeX equations with MathJax or native LaTeX
- **Code Syntax Highlighting**: Python, JavaScript, SQL, YAML with line numbers
- **Tables & Data**: Performance benchmarks, comparison tables, data visualization
- **Professional Typography**: Inter font family, optimized spacing, visual hierarchy

### 🎨 **Design & Branding**
- **Modern Themes**: Clean, professional styling for technical presentations
- **Logo Integration**: Configurable positioning (bottom-right, top-right, etc.)
- **Slide Numbers**: Customizable format and positioning
- **Responsive Design**: Adapts to different screen sizes and orientations

### 🔧 **Development & Testing**
- **Comprehensive Test Suite**: 21 unit tests covering all functionality
- **CI/CD Integration**: Automated testing and deployment
- **Performance Monitoring**: Benchmark comparison between backends
- **Error Handling**: Graceful fallbacks and detailed error reporting

## 🎨 Available Themes

| Theme | Description |
|-------|-------------|
| **modern** | Slides.com inspired clean design |
| **minimal** | Ultra-clean with generous spacing |
| **gradient** | Reveal.js inspired gradient backgrounds |
| **dark** | Professional dark theme |
| **default** | Clean white with subtle blue accents |
| **sky** | Light blue modern theme |
| **solarized** | Warm, eye-friendly colors |
| **moon** | Dark blue space-inspired |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web UI

```bash
# Default port (5000)
python app.py

# Custom port
python app.py -p 8080

# With debug mode
python app.py -p 3000 -d
```

### 3. Open in Browser

```
http://localhost:5000
```

## 📝 Command Line Usage

### Basic Usage
```bash
# Basic usage
python bodh.py presentation.md

# With custom theme and font
python bodh.py slides.md -t modern -f "Inter" -s 22

# With logo
python bodh.py slides.md -t gradient -l logo.png -p top-right
```

### Configuration Files
```bash
# Create sample configuration
python bodh.py --create-config

# Use specific configuration
python bodh.py slides.md -c configs/minimal.yml

# Override config with CLI arguments
python bodh.py slides.md -c config.yml -t dark -f "Roboto"

# Auto-detect default config (bodh.yml)
python bodh.py slides.md -v
```

### Available Options
```bash
# See all options
python bodh.py --help

# List available themes
python bodh.py --list-themes
```

## 📋 Markdown Format

Separate slides with `---`:

```markdown
# Welcome Slide
## Your presentation title

Content for first slide

---

## Second Slide

- Bullet point 1
- Bullet point 2
- Bullet point 3

---

# Thank You!

Questions?
```

## 🎯 Features in Detail

### Configuration System
- **YAML Configuration**: Full support for configuration files
- **Auto-detection**: Automatically finds `bodh.yml` in current directory
- **CLI Overrides**: Command line arguments override config values
- **Example Configs**: Minimal, presentation, and academic styles included

### Slide Navigation
- **Keyboard**: Arrow keys, Space, Home, End
- **Mouse**: Click navigation buttons or dots
- **Touch**: Swipe on mobile devices
- **Slide Numbers**: Multiple formats (1, 1/10, 10, 10%)

### Supported Markdown
- Headers (H1-H6)
- Lists (ordered and unordered)
- **Bold** and *italic* text
- `Code snippets` and code blocks
- Tables
- Blockquotes
- Images

### PDF Generation
- **High-quality PDF output** using Chrome's PDF engine (Playwright)
- **Identical quality to HTML preview** - full CSS support, gradients, shadows, animations
- Landscape A4 format
- Print-ready quality
- Consistent typography
- **Fallback support** for WeasyPrint and xhtml2pdf if Playwright unavailable

## 🛠️ Development

### Project Structure
```
Bodh/
├── app.py              # Web UI server
├── bodh.py             # Core presentation generator
├── themes/             # JSON theme configurations
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
└── examples/           # Sample presentations
```

### Adding New Themes

1. Create a new JSON file in `themes/` directory
2. Define colors, typography, spacing, and effects
3. Theme will automatically appear in the UI

## 🎨 CLI Options

### Web UI (`app.py`)
```bash
-p, --port      Port number (default: 5000)
--host          Host address (default: 0.0.0.0)
-d, --debug     Enable debug mode
--no-reload     Disable auto-reload
```

### CLI Tool (`bodh.py`)
```bash
-t, --theme     Theme name (default: default)
-f, --font      Font family (default: Inter)
-s, --size      Font size (default: 20)
-l, --logo      Logo image path
-p, --position  Logo position
-o, --output    Output PDF filename
-v, --verbose   Verbose output
```

## 📦 Requirements

- Python 3.7+
- Flask 3.0+
- Markdown
- Jinja2
- xhtml2pdf

## 🌟 Pro Tips

1. **Keep slides simple** - One main point per slide
2. **Use consistent formatting** - Stick to your chosen theme
3. **Test different themes** - Preview before generating PDF
4. **Optimize images** - Use web-optimized formats
5. **Preview first** - Always check HTML preview before PDF

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

## 📄 License

MIT License - See LICENSE file for details

---

**Happy Presenting!** 🎉