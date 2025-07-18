# 📐 Mathematics with Bodh

## LaTeX Math Support Demo

Bodh now supports beautiful mathematical equations using **MathJax**!

---

# Inline Mathematics

You can write inline math like $E = mc^2$ or $\pi \approx 3.14159$ directly in your text.

The quadratic formula $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$ is a fundamental algebraic equation.

Statistical concepts like the normal distribution $\mathcal{N}(\mu, \sigma^2)$ are easy to express.

---

# Display Mathematics

For larger equations, use display math:

$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

Complex mathematical expressions work beautifully:

$$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$$

---

# Advanced Examples

## Matrices and Linear Algebra

$$\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
\begin{bmatrix}
x \\
y
\end{bmatrix}
=
\begin{bmatrix}
ax + by \\
cx + dy
\end{bmatrix}$$

## Calculus

The fundamental theorem of calculus:

$$\int_a^b f'(x) dx = f(b) - f(a)$$

---

# Probability and Statistics

## Bayes' Theorem

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

## Normal Distribution

The probability density function:

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$

---

# Physics Examples

## Maxwell's Equations

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}$$

$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$$

$$\nabla \cdot \mathbf{B} = 0$$

$$\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}$$

---

# Mixed Content

You can mix math with code, lists, and other markdown elements:

## Machine Learning Cost Function

For linear regression, the cost function is:

$$J(\theta) = \frac{1}{2m} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)})^2$$

Where:
- $m$ = number of training examples
- $h_\theta(x) = \theta_0 + \theta_1 x$ = hypothesis function
- $\theta$ = parameters to learn

```python
def cost_function(theta, X, y):
    m = len(y)
    predictions = X @ theta
    return (1/(2*m)) * np.sum((predictions - y)**2)
```

---

# Thank You!

## Ready for Mathematical Presentations?

✨ **LaTeX math support is now available**

- Use `$...$` for inline math: $\alpha + \beta$
- Use `$$...$$` for display math
- Full MathJax support with all symbols and environments
- Works in both HTML preview and PDF export

*Perfect for academic presentations, research talks, and technical documentation!*