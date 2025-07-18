# 🚀 Bodh Feature Showcase
## Complete Configuration Demonstration

This presentation demonstrates **logos**, **slide numbering**, **navigation**, and **styling** options.

---

## 📊 Slide Numbering Formats

Bodh supports multiple slide numbering formats:

### Current Only
- Format: `current` → Shows: **1**, **2**, **3**
- Perfect for minimal presentations

### Current/Total
- Format: `current/total` → Shows: **1/8**, **2/8**, **3/8**
- Great for showing progress

### Percentage
- Format: `percent` → Shows: **12%**, **25%**, **37%**
- Ideal for long presentations

---

## 🖼️ Logo Positioning

Logos can be placed in **four corners**:

| Position | Best For |
|----------|----------|
| `top-left` | Company branding |
| `top-right` | Event logos |
| `bottom-left` | University marks |
| `bottom-right` | Certification badges |

**Note:** Logo size is configurable from 50-200px

---

## 🎨 Navigation Options

### Arrow Navigation
- **Enabled**: Previous/Next buttons
- **Disabled**: Keyboard-only navigation

### Dot Navigation  
- **Small dots**: Minimal distraction
- **Hidden**: Clean presentation mode

### Progress Bar
- **Visible**: Shows completion percentage
- **Hidden**: Focus on content

---

## 🎭 Theme Variations

### Modern Themes
- **Modern**: Clean, professional
- **Minimal**: Ultra-clean, lots of whitespace
- **Gradient**: Colorful backgrounds

### Traditional Themes
- **Dark**: Perfect for tech talks
- **Solarized**: Easy on the eyes
- **Default**: Classic presentation style

---

## 💼 Corporate Features

### Professional Setup
```yaml
theme: dark
slide_number: { format: current, position: top-right }
logo: { location: top-left, size: 120 }
navigation: { show_arrows: false, show_dots: true }
style: { animations: false, rounded_corners: false }
```

### Academic Setup
```yaml
theme: solarized
slide_number: { format: current/total, position: bottom-center }
logo: { location: bottom-left, size: 80 }
navigation: { show_progress: true }
```

---

## 🔧 Configuration Power

### YAML Configuration
- **Flexible**: Override any setting
- **Reusable**: Save configurations for different events
- **Portable**: Share configs across teams

### CLI Overrides
```bash
# Use config but override theme
bodh slides.md -c corporate.yml -t gradient

# Override slide numbering
bodh slides.md -c config.yml --slide-format percent
```

---

# 🎉 Ready to Create?

**Bodh** makes beautiful presentations effortless!

1. **Write** in Markdown
2. **Configure** with YAML  
3. **Generate** stunning PDFs

*Experience the power of knowledge sharing!*