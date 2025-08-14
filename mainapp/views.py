import os
import json
import requests
from urllib.parse import quote
from django.shortcuts import render
from dotenv import load_dotenv
import time

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

def strip_markdown_fences(text: str) -> str:
    """Remove triple backticks and optional ```json fences from LLM output."""
    text = text.strip()

    # Remove starting fence
    if text.startswith("```json"):
        text = text[len("```json"):].lstrip()
    elif text.startswith("```"):
        text = text[len("```"):].lstrip()

    # Remove ending fence
    if text.endswith("```"):
        text = text[:-3].rstrip()

    return text


def get_image_url(description):
    """
    Try multiple image generation APIs with fallbacks.
    """
    if not description.strip():
        return ""
    
    print(f"Generating image for: {description[:100]}...")
    
    # Try Craiyon with shorter timeout first
    try:
        print("Trying Craiyon API...")
        url = "https://api.craiyon.com/v3"
        data = {
            "prompt": description,
            "token": None,
            "model": "art",
            "negative_prompt": ""
        }
        response = requests.post(url, json=data, timeout=30)  # Reduced timeout
        response.raise_for_status()
        result = response.json()
        images = result.get("images") or []
        if images:
            print("Successfully generated image with Craiyon")
            return f"data:image/jpeg;base64,{images}"
    except Exception as e:
        print(f"Craiyon API failed: {e}")
    
    # Try alternative Craiyon endpoint
    try:
        print("Trying alternative Craiyon endpoint...")
        url = "https://backend.craiyon.com/generate"
        payload = {"prompt": description}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("images") and len(result["images"]) > 0:
            print("Successfully generated image with alternative Craiyon endpoint")
            return f"data:image/jpeg;base64,{result['images']}"
    except Exception as e:
        print(f"Alternative Craiyon endpoint failed: {e}")
    
    # Fallback to placeholder with themed images
    print("Using placeholder image fallback")
    # Create a more relevant placeholder based on description keywords
    seed = abs(hash(description)) % 1000
    
    # Try to make placeholder more relevant based on description
    if any(word in description.lower() for word in ['character', 'person', 'man', 'woman', 'hero', 'villain']):
        return f"https://picsum.photos/512/512?random={seed}&grayscale"
    elif any(word in description.lower() for word in ['landscape', 'forest', 'mountain', 'castle', 'city']):
        return f"https://picsum.photos/512/512?random={seed}"
    else:
        return f"https://picsum.photos/512/512?random={seed}&blur=2"

def home(request):
    return render(request, 'mainapp/home.html')

def generate_story(request):
    if request.method == 'POST':
        user_prompt = request.POST.get('prompt', '').strip()

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates creative stories. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": f"""Based on this prompt: {user_prompt}

Generate and output a JSON object with exactly three fields:
- "story": A 2-3 paragraph creative story
- "character": A detailed character description for image generation  
- "background": A detailed background/scene description for image generation

Output only valid JSON, no additional text or explanation."""
            }
        ]

        try:
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.8
            }
            
            response = requests.post(
                f"{PERPLEXITY_BASE_URL}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()

            # Handle different possible response structures
            ai_text = ""
            
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices']
                
                if isinstance(choice, dict):
                    if 'message' in choice and 'content' in choice['message']:
                        ai_text = choice['message']['content']
                    elif 'text' in choice:
                        ai_text = choice['text']
                    elif 'content' in choice:
                        ai_text = choice['content']
                elif isinstance(choice, str):
                    ai_text = choice
            
            if not ai_text:
                # Try to find content anywhere in the response
                def extract_content(obj):
                    if isinstance(obj, dict):
                        if 'content' in obj:
                            return obj['content']
                        for value in obj.values():
                            result = extract_content(value)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = extract_content(item)
                            if result:
                                return result
                    return None
                
                ai_text = extract_content(data) or ""
            
            if not ai_text:
                raise Exception(f"Could not extract content from response")

            # Clean markdown fences if any
            clean_text = strip_markdown_fences(ai_text)

            # Parse JSON
            try:
                result_json = json.loads(clean_text)
                story_text = result_json.get('story', '')
                character_desc = result_json.get('character', '')
                background_desc = result_json.get('background', '')
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing failed: {json_error}")
                story_text = clean_text
                character_desc = ""
                background_desc = ""

        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            story_text = f"Error generating story: {e}"
            character_desc = ""
            background_desc = ""

        # Generate images with improved error handling
        print("Starting image generation...")
        character_image_url = get_image_url(character_desc) if character_desc else ""
        background_image_url = get_image_url(background_desc) if background_desc else ""

        print(f"Character image result: {'Generated' if character_image_url else 'Failed'}")
        print(f"Background image result: {'Generated' if background_image_url else 'Failed'}")

        return render(request, 'mainapp/result.html', {
            'prompt': user_prompt,
            'story': story_text,
            'character': character_desc,
            'background': background_desc,
            'character_image_url': character_image_url,
            'background_image_url': background_image_url,
        })

    return render(request, 'mainapp/home.html')