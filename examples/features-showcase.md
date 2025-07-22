# Bodh Features Showcase
*Beautiful presentations from markdown*

---

## Multi-Column Layouts

::: {.columns}

::: {.column width="50%"}
### Left Column
- Feature demonstrations
- Easy to implement
- Professional layouts
- Responsive design
:::

::: {.column width="50%"}
### Right Column
- Code examples
- Mathematical equations
- Visual elements
- Interactive content
:::

:::

---

## Mathematics: Inline vs Display

### Inline Mathematics
We can include math like $f(x) = ax^2 + bx + c$ directly in text, or more complex expressions like $\sum_{i=1}^{n} x_i^2$.

### Display Mathematics
For more prominent equations, use display mode:

$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

$$\nabla f(x,y) = \begin{bmatrix}
\frac{\partial f}{\partial x} \\
\frac{\partial f}{\partial y}
\end{bmatrix}$$

---

## Lists and Formatting

### Bullet Points
- **Bold text** for emphasis
- *Italic text* for style  
- `Code snippets` inline
- [Links](https://github.com) for references

### Numbered Lists
1. First important point
2. Second key concept
3. Third essential element
4. Final summary point

### Mixed Lists
- Main category
  1. Sub-item one
  2. Sub-item two
- Another category
  - Nested bullet
  - Another nested item

---

## Code Highlighting

### Python Example
```python
def gradient_descent(f, grad_f, x0, alpha=0.01):
    """Gradient descent optimization"""
    x = x0
    for i in range(1000):
        x = x - alpha * grad_f(x)
        if abs(grad_f(x)) < 1e-6:
            break
    return x
```

### JavaScript Example  
```javascript
function createChart(data) {
    return {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            animation: true
        }
    };
}
```

---

## Tables and Data

### Simple Table
| Method | Speed | Accuracy |
|--------|-------|----------|
| SGD | Fast | 85% |
| Adam | Medium | 92% |
| L-BFGS | Slow | 96% |

### Complex Table
| Algorithm | Time Complexity | Space | Best Use Case |
|-----------|----------------|-------|---------------|
| **Gradient Descent** | O(n×d×k) | O(d) | Convex problems |
| **Stochastic GD** | O(d×k) | O(d) | Large datasets |
| **Newton's Method** | O(n×d²×k) | O(d²) | Small scale |

---

## Figures and Images

### Simple Figure
![Sample visualization](sample-image.jpg)

### Figure with Caption
![Beautiful landscape with mountains and trees creating a serene natural scene](sample-image.jpg "Nature's beauty")

### Sized Image
<img src="sample-logo.svg" width="200" alt="Bodh Logo">

---

## Blockquotes and Callouts

> **Important Note:** Gradient descent is a fundamental optimization algorithm used across machine learning, from linear regression to deep neural networks.

> *"The best way to learn is by doing."*  
> — Anonymous

### Multiple Quote Levels
> This is a first-level quote
>> This is a nested quote
>>> This is deeply nested

---

## Advanced Typography

### Text Styles
- **Bold emphasis**
- *Italic style*
- ~~Strikethrough text~~
- `Monospace code`
- Small caps: <span style="font-variant: small-caps">Small Caps Text</span>

### Special Characters
- Mathematical: α, β, γ, Δ, Σ, π, ∞
- Arrows: → ← ↑ ↓ ⟨ ⟩
- Symbols: ★ ✓ ✗ ⚠ ℹ

---

## Interactive Elements

### Progress Indicators
- [x] Feature implementation complete
- [x] Testing and validation done  
- [ ] Documentation in progress
- [ ] Final review pending

### Keyboard Shortcuts
Press <kbd>Ctrl</kbd> + <kbd>C</kbd> to copy  
Press <kbd>→</kbd> for next slide  
Press <kbd>←</kbd> for previous slide

---

## Mathematical Showcases

### Matrix Operations
$$A = \begin{bmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{bmatrix}$$

### Complex Equations
$$\mathcal{L}(\theta) = \frac{1}{N}\sum_{i=1}^{N} \ell(f(x_i; \theta), y_i) + \lambda R(\theta)$$

### Multi-line Equations
$$\begin{align}
\nabla_\theta \mathcal{L} &= \frac{1}{N}\sum_{i=1}^{N} \nabla_\theta \ell(f(x_i; \theta), y_i) + \lambda \nabla_\theta R(\theta) \\
&= \mathbb{E}_{(x,y) \sim \mathcal{D}}[\nabla_\theta \ell(f(x; \theta), y)] + \lambda \nabla_\theta R(\theta)
\end{align}$$

---

## Summary

### What You've Seen
✓ **Multi-column layouts** for organized content  
✓ **Inline and display mathematics** with LaTeX  
✓ **Various list types** and formatting options  
✓ **Code highlighting** for multiple languages  
✓ **Tables** for data presentation  
✓ **Images and figures** with flexible sizing  
✓ **Typography** and special characters  

### Ready for Real Content
Now let's see these features in action with a complete example: **Gradient Descent Tutorial**

*Bodh makes beautiful presentations effortless!*