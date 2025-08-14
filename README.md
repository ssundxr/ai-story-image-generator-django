# AI Story + Image Generator (Django)

**Features**
- **AI-powered Storytelling** — Generates a 2–3 paragraph creative story from your prompt using the **Perplexity API**.
- **Character & Background Descriptions** — Extracts rich details for image generation.
- **Image Generation** — Uses **Pollinations AI** to generate relevant character and background visuals.
- **Two UI Options** — Switch between a high-end polished UI and a lightweight basic layout.
- **Fast & Responsive** — Works well across desktop.
- **Error Handling** — Graceful fallbacks in case of API or image generation issues.

---
HERE ARE SOME SAMPLE SCREEN SHOTS THAT RAN ON LOCAL HOST
<!-- Row 1 -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/a7c64617-de94-4c2a-ad13-91e3d49a7b6c" width="48%" />
  <img src="https://github.com/user-attachments/assets/90a55e1f-c5d1-4f65-819b-4fa7bfcb24c5" width="48%" />
</p>

<!-- Row 2 -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/6f1be487-11d1-4dda-ae58-b3504f582d74" width="48%" />
  <img src="https://github.com/user-attachments/assets/aafa99ba-6f80-4002-a5fe-f0ed1c25bcd1" width="48%" />
</p>


##Installation & Setup

### 1️.Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-story-image-generator-django.git
cd ai-story-image-generator-django
```
2️.Create Virtual Environment & Activate
```python -m venv venv```
# Windows
```venv\Scripts\activate```
# Mac/Linux
```source venv/bin/activate```

3️.Install Dependencies
```pip install -r requirements.txt```

4️.Create .env File
```PERPLEXITY_API_KEY=your_perplexity_api_key_here```

5️.Run Migrations
```python manage.py migrate```

6️.Start Server
```python manage.py runserver```


```Visit: http://127.0.0.1:8000```

Usage

Open the app in your browser.

Enter a creative story prompt (e.g., "A lonely astronaut discovers a secret garden on Mars").

Wait for the results — you'll get:

 """ 2–3 paragraph AI-generated story,Character description + image,Background description + image """

Switch between UI modes (see below).

| Mode                | Files Used                                                          | Description                                                                 |
|---------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **High-Level UI/UX** | `homeUIUX.html`, `resultUIUX.html`, `baseUIUX.html`, `style.css`     | Modern design with animations, gradients, and advanced CSS styling.        |
| **Low-Level UI**     | `home.html`, `result.html`, `base.html`                             | Minimal, fast-loading templates for quick testing and debugging.           |

---

Switching UI Modes

In views.py, you can load templates dynamically based on a setting:

# views.py
```
from django.conf import settings
from django.shortcuts import render

def home(request):
    if settings.UI_MODE == "high":
        return render(request, "mainapp/homeUIUX.html")
    return render(request, "mainapp/home.html")

def result(request):
    if settings.UI_MODE == "high":
        return render(request, "mainapp/resultUIUX.html")
    return render(request, "mainapp/result.html")
```
setup instructions:
## 🔑 API Key Setup

1. **Get a Perplexity API key:**
   - Sign up at [Perplexity.ai](https://www.perplexity.ai/)
   - Go to Settings → API Keys
   - Generate a new API key

2. **Create your environment file:**
 ```cp .env.example .env```

3. **Add your API key to `.env`:**
```PERPLEXITY_API_KEY=your_actual_api_key_here```

 **** Tip: Use High-Level UI for production and demos, and Low-Level UI for quick development and debugging. ****



