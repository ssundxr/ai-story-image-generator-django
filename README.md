# AI Story + Image Generator (Django)

This project generates AI-powered **stories** and **images** based on text prompts, character descriptions, and background details.  
It comes with **two UI modes**:

| Mode                | Files Used                                                          | Description                                                                 |
|---------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **High-Level UI/UX** | `homeUIUX.html`, `resultUIUX.html`, `baseUIUX.html`, `style.css`     | Modern design with animations, gradients, and advanced CSS styling.        |
| **Low-Level UI**     | `home.html`, `result.html`, `base.html`                             | Minimal, fast-loading templates for quick testing and debugging.           |

---

## 🖥 Switching UI Modes

You can easily toggle between UI modes without rewriting code.  
In `settings.py`, add:

```python
# settings.py
UI_MODE = "high"  # Options: "high" or "low"
