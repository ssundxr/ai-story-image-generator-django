# AI Story + Image Generator (Django)

✨ **Features**
- **AI-powered Storytelling** — Generates a 2–3 paragraph creative story from your prompt using the **Perplexity API**.
- **Character & Background Descriptions** — Extracts rich details for image generation.
- **Image Generation** — Uses **Pollinations AI** to generate relevant character and background visuals.
- **Two UI Options** — Switch between a high-end polished UI and a lightweight basic layout.
- **Fast & Responsive** — Works well across desktop and mobile.
- **Error Handling** — Graceful fallbacks in case of API or image generation issues.

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-story-image-generator-django.git
cd ai-story-image-generator-django
2️⃣ Create Virtual Environment & Activate
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Create .env File
PERPLEXITY_API_KEY=your_perplexity_api_key_here

5️⃣ Run Migrations
python manage.py migrate

6️⃣ Start Server
python manage.py runserver


Visit: http://127.0.0.1:8000

💡 Usage

Open the app in your browser.

Enter a creative story prompt (e.g., "A lonely astronaut discovers a secret garden on Mars").

Wait for the results — you'll get:

2–3 paragraph AI-generated story

Character description + image

Background description + image

Switch between UI modes (see below).

🎨 UI Modes
Mode	Templates Used	Description
High-Level UI/UX	mainapp/homeUIUX.html, mainapp/resultUIUX.html, mainapp/baseUIUX.html, static/css/style.css	Modern design with animations, gradients, and advanced CSS styling.
Low-Level UI	mainapp/home.html, mainapp/result.html, mainapp/base.html	Minimal, fast-loading templates for quick testing and debugging.
