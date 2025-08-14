# AI Story + Image Generator (Django)

**Features**
- **AI-powered Storytelling** — Generates a 2–3 paragraph creative story from your prompt using the **Perplexity API**.
- **Character & Background Descriptions** — Extracts rich details for image generation.
- **Image Generation** — Uses **Pollinations AI** to generate relevant character and background visuals.
- **Two UI Options** — Switch between a high-end polished UI and a lightweight basic layout.
- **Fast & Responsive** — Works well across desktop and mobile.
- **Error Handling** — Graceful fallbacks in case of API or image generation issues.

---

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


 Tip: Use High-Level UI for production and demos, and Low-Level UI for quick development and debugging.

 Optional Upgrade: UI mode switching can also be made to work via a URL parameter (e.g., ?ui=high) so you don’t have to restart the server or change settings — perfect for demos.


---

Do you want me to now **add that optional URL-based UI switching code** into this README so it’s ready for demos without editing `settings.py`? That would make it even smoother.

