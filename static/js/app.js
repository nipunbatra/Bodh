class PresentationApp {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.loadExample();
    }

    initializeElements() {
        this.editor = document.getElementById('markdown-editor');
        this.configSelect = document.getElementById('config-select');
        this.themeSelect = document.getElementById('theme-select');
        this.fontSelect = document.getElementById('font-select');
        this.fontSizeSlider = document.getElementById('font-size');
        this.fontSizeValue = document.getElementById('font-size-value');
        this.previewBtn = document.getElementById('preview-btn');
        this.generateBtn = document.getElementById('generate-btn');
        this.previewPdfBtn = document.getElementById('preview-pdf-btn');
        this.uploadBtn = document.getElementById('upload-btn');
        this.exampleBtn = document.getElementById('example-btn');
        this.fileInput = document.getElementById('file-input');
        this.previewSection = document.getElementById('preview-section');
        this.previewIframe = document.getElementById('preview-iframe');
        this.closePreview = document.getElementById('close-preview');
        this.slideCount = document.getElementById('slide-count');
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        // Load available configs
        this.loadConfigs();
    }

    setupEventListeners() {
        this.fontSizeSlider.addEventListener('input', (e) => {
            this.fontSizeValue.textContent = e.target.value + 'px';
        });

        this.configSelect.addEventListener('change', () => this.loadConfigPreset());
        this.previewBtn.addEventListener('click', () => this.generatePreview());
        this.generateBtn.addEventListener('click', () => this.generatePDF());
        this.previewPdfBtn.addEventListener('click', () => this.previewPDF());
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.exampleBtn.addEventListener('click', () => this.loadExample());
        this.closePreview.addEventListener('click', () => this.closePreviewSection());

        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        // Auto-preview on changes (debounced)
        let previewTimeout;
        this.editor.addEventListener('input', () => {
            clearTimeout(previewTimeout);
            previewTimeout = setTimeout(() => {
                if (this.previewSection.classList.contains('active')) {
                    this.generatePreview();
                }
            }, 1000);
        });

        this.themeSelect.addEventListener('change', () => {
            if (this.previewSection.classList.contains('active')) {
                this.generatePreview();
            }
        });

        this.fontSelect.addEventListener('change', () => {
            if (this.previewSection.classList.contains('active')) {
                this.generatePreview();
            }
        });

        this.fontSizeSlider.addEventListener('input', () => {
            if (this.previewSection.classList.contains('active')) {
                this.generatePreview();
            }
        });
    }

    async loadExample() {
        const exampleContent = `# 🚀 Welcome to Bodh!
## Beautiful Presentations Made Easy

Transform your markdown into stunning PDFs

---

## 🎨 Features

- **Multiple Themes**: Choose from modern, minimal, gradient, and more
- **Custom Fonts**: Use any Google Font
- **Live Preview**: See changes instantly
- **Easy Export**: One-click PDF generation

---

## 📝 How to Use

### 1. Write Your Content
Use standard markdown syntax with \`---\` to separate slides

### 2. Choose Your Style
- Pick a theme that matches your presentation
- Adjust font family and size
- Preview your changes live

### 3. Generate PDF
Click the generate button to download your presentation

---

## 💡 Markdown Tips

### Lists Work Great
- Use bullet points for key information
- **Bold** and *italic* text for emphasis
- \`Code snippets\` for technical content

### Tables Are Supported

| Feature | Status | Notes |
|---------|--------|-------|
| Themes | ✅ | 8 beautiful options |
| Fonts | ✅ | Google Fonts support |
| Export | ✅ | High-quality PDF |

---

## 🌟 Pro Tips

> "The best presentations tell a story"
> 
> Keep your slides simple and focused

### Code Blocks
\`\`\`python
def create_presentation():
    return "Beautiful slides with Bodh!"
\`\`\`

---

# 🎉 Ready to Start?

**Edit this content** and click Preview to see your presentation come to life!

*Happy presenting with Bodh!*`;

        this.editor.value = exampleContent;
    }

    async loadConfigs() {
        try {
            const response = await fetch('/api/configs');
            if (response.ok) {
                const configs = await response.json();
                
                // Clear existing options (except default)
                this.configSelect.innerHTML = '<option value="">Custom (Manual Settings)</option>';
                
                // Add config options
                configs.forEach(config => {
                    const option = document.createElement('option');
                    option.value = config.id;
                    option.textContent = `${config.name} - ${config.description}`;
                    this.configSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load configs:', error);
        }
    }

    async loadConfigPreset() {
        const configId = this.configSelect.value;
        
        if (!configId) {
            // Reset to default values for custom mode
            this.themeSelect.value = 'modern';
            this.fontSelect.value = 'Inter';
            this.fontSizeSlider.value = '20';
            this.fontSizeValue.textContent = '20px';
            return;
        }

        try {
            const response = await fetch(`/api/configs/${configId}`);
            if (response.ok) {
                const config = await response.json();
                
                // Apply config to UI controls
                this.themeSelect.value = config.theme || 'modern';
                this.fontSelect.value = config.font.family || 'Inter';
                this.fontSizeSlider.value = config.font.size || 20;
                this.fontSizeValue.textContent = `${config.font.size || 20}px`;
                
                // Auto-preview if preview is active
                if (this.previewSection.classList.contains('active')) {
                    this.generatePreview();
                }
                
                this.showNotification(`Applied ${this.configSelect.options[this.configSelect.selectedIndex].text.split(' - ')[0]} configuration`, 'success');
            } else {
                this.showNotification('Failed to load configuration', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to load configuration: ' + error.message, 'error');
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.editor.value = data.content;
                this.showNotification('File uploaded successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Upload failed', 'error');
            }
        } catch (error) {
            this.showNotification('Upload failed: ' + error.message, 'error');
        }
    }

    async generatePreview() {
        const markdown = this.editor.value;
        const theme = this.themeSelect.value;
        const fontFamily = this.fontSelect.value;
        const fontSize = parseInt(this.fontSizeSlider.value);

        if (!markdown.trim()) {
            this.showNotification('Please enter some markdown content', 'error');
            return;
        }

        try {
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    markdown,
                    theme,
                    font_family: fontFamily,
                    font_size: fontSize
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.previewIframe.srcdoc = data.html;
                this.slideCount.textContent = `${data.slide_count} slides`;
                this.previewSection.classList.add('active');
                this.showNotification('Preview generated!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Preview failed', 'error');
            }
        } catch (error) {
            this.showNotification('Preview failed: ' + error.message, 'error');
        }
    }

    async generatePDF() {
        const markdown = this.editor.value;
        const theme = this.themeSelect.value;
        const fontFamily = this.fontSelect.value;
        const fontSize = parseInt(this.fontSizeSlider.value);

        if (!markdown.trim()) {
            this.showNotification('Please enter some markdown content', 'error');
            return;
        }

        this.loadingOverlay.classList.add('active');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    markdown,
                    theme,
                    font_family: fontFamily,
                    font_size: fontSize
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `presentation_${theme}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                this.showNotification('PDF generated successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'PDF generation failed', 'error');
            }
        } catch (error) {
            this.showNotification('PDF generation failed: ' + error.message, 'error');
        } finally {
            this.loadingOverlay.classList.remove('active');
        }
    }

    async previewPDF() {
        const markdown = this.editor.value;
        const theme = this.themeSelect.value;
        const fontFamily = this.fontSelect.value;
        const fontSize = parseInt(this.fontSizeSlider.value);

        if (!markdown.trim()) {
            this.showNotification('Please enter some markdown content', 'error');
            return;
        }

        this.loadingOverlay.classList.add('active');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    markdown,
                    theme,
                    font_family: fontFamily,
                    font_size: fontSize
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                
                // Show PDF in iframe
                this.previewIframe.src = url;
                this.slideCount.textContent = 'PDF Preview';
                this.previewSection.classList.add('active');
                this.showNotification('PDF preview generated!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'PDF preview failed', 'error');
            }
        } catch (error) {
            this.showNotification('PDF preview failed: ' + error.message, 'error');
        } finally {
            this.loadingOverlay.classList.remove('active');
        }
    }

    closePreviewSection() {
        this.previewSection.classList.remove('active');
        // Clean up PDF blob URL if it exists
        if (this.previewIframe.src.startsWith('blob:')) {
            window.URL.revokeObjectURL(this.previewIframe.src);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '6px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1001',
            maxWidth: '300px'
        });

        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            info: '#667eea'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to page
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PresentationApp();
});