# Overlay System Demo

Welcome to the Bodh overlay demonstration!

<!--pause-->

This content appears after the first pause.

<!--pause-->

And this appears after the second pause.

---

## Progressive Reveals

First, let's talk about the concept.

<!--pause-->

Then we show the implementation:

```python
def reveal_content():
    return "Step by step!"
```

<!--pause-->

Finally, we show the results:
- ✅ Better audience engagement
- ✅ Controlled information flow  
- ✅ Dramatic presentation effect

---

## Benefits Overview

**Why use overlays?**

<!--pause-->

🎯 **Focus Attention**
- Reveals content progressively
- Keeps audience engaged
- Prevents information overload

<!--pause-->

📊 **Better Storytelling**
- Build suspense and narrative
- Control the pace of information
- Create dramatic moments

<!--pause-->

🎨 **Professional Appearance**
- Mimics PowerPoint animations
- Beamer-like pause functionality
- Smooth transitions

---

## Technical Details

The overlay system works by:

<!--pause-->

1. **Parsing pause markers** in markdown
2. **Creating overlay divs** with visibility control
3. **JavaScript navigation** handles reveals

<!--pause-->

**HTML Output Structure:**
```html
<div class="overlay" data-overlay="1">
  Hidden content initially
</div>
```

<!--pause-->

**CSS Transitions:**
```css
.overlay { 
  opacity: 0; 
  transition: opacity 0.5s; 
}
.overlay.visible { 
  opacity: 1; 
}
```

---

## Thank You!

Overlays make presentations more dynamic and engaging.

<!--pause-->

**Try it yourself:**
- Add `<!--pause-->` markers in your markdown
- Enable overlays in your config
- Use arrow keys to navigate

<!--pause-->

✨ **Happy presenting!**