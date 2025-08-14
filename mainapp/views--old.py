import os
import json
import requests
import logging
from urllib.parse import quote
from django.shortcuts import render
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

print(f"DEBUG: Perplexity API Key loaded: {'Yes' if PERPLEXITY_API_KEY else 'No'}")

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
    """Generate images using Pollinations AI"""
    if not description.strip():
        return ""
    
    print(f"DEBUG: Generating image for: {description[:50]}...")
    
    try:
        encoded_desc = quote(description)
        seed = abs(hash(description)) % 1000
        image_url = f"https://image.pollinations.ai/prompt/{encoded_desc}?width=512&height=512&seed={seed}"
        print(f"DEBUG: Generated image URL: {image_url[:100]}...")
        return image_url
        
    except Exception as e:
        print(f"DEBUG: Error generating image: {e}")
        seed = abs(hash(description)) % 1000
        return f"https://picsum.photos/512/512?random={seed}"

def home(request):
    """Home view"""
    print("DEBUG: Home view called")
    return render(request, 'mainapp/home.html')

def generate_story(request):
    """Generate story using Perplexity API"""
    print(f"DEBUG: Generate story view called with method: {request.method}")
    
    if request.method == 'POST':
        try:
            user_prompt = request.POST.get('prompt', '').strip()
            print(f"DEBUG: User prompt: {user_prompt[:100]}...")
            
            if not user_prompt:
                return render(request, 'mainapp/home.html', {'error': 'Please provide a prompt'})
            
            if not PERPLEXITY_API_KEY:
                print("DEBUG: No API key found")
                return render(request, 'mainapp/result.html', {
                    'prompt': user_prompt,
                    'story': 'Error: PERPLEXITY_API_KEY not found in environment variables. Please check your .env file.',
                    'character': '',
                    'background': '',
                    'character_image_url': '',
                    'background_image_url': '',
                    'combined_image_url': '',
                })

            print("DEBUG: Building Perplexity API request...")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates creative stories. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": f"""Based on this prompt: {user_prompt}

Generate and output a JSON object with exactly three fields:
- "story": A compelling 2-3 paragraph creative story
- "character": A detailed character description for image generation (include appearance, clothing, pose)
- "background": A detailed background/scene description for image generation (include setting, lighting, atmosphere)

Output only valid JSON, no additional text or explanation."""
                }
            ]

            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.8
            }
            
            print(f"DEBUG: Sending request to: {PERPLEXITY_BASE_URL}/chat/completions")
            
            response = requests.post(
                f"{PERPLEXITY_BASE_URL}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            print(f"DEBUG: Response status code: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                print(f"DEBUG: API Error Response: {error_text}")
                return render(request, 'mainapp/result.html', {
                    'prompt': user_prompt,
                    'story': f'API Error ({response.status_code}): {error_text}',
                    'character': '',
                    'background': '',
                    'character_image_url': '',
                    'background_image_url': '',
                    'combined_image_url': '',
                })
            
            response.raise_for_status()
            data = response.json()
            
            print(f"DEBUG: API Response received: {json.dumps(data, indent=2)}")

            # Extract content from response
            ai_text = ""
            
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices']
                print(f"DEBUG: First choice: {choice}")
                
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
                print("DEBUG: Could not extract content from response")
                return render(request, 'mainapp/result.html', {
                    'prompt': user_prompt,
                    'story': f'Error: Could not extract content from API response: {data}',
                    'character': '',
                    'background': '',
                    'character_image_url': '',
                    'background_image_url': '',
                    'combined_image_url': '',
                })

            print(f"DEBUG: Extracted AI text: {ai_text}")

            # Clean and parse JSON
            clean_text = strip_markdown_fences(ai_text)
            print(f"DEBUG: Clean text: {clean_text}")

            try:
                result_json = json.loads(clean_text)
                story_text = result_json.get('story', '')
                character_desc = result_json.get('character', '')
                background_desc = result_json.get('background', '')
                print("DEBUG: JSON parsing successful")
            except json.JSONDecodeError as json_error:
                print(f"DEBUG: JSON parsing failed: {json_error}")
                story_text = clean_text
                character_desc = ""
                background_desc = ""

            print("DEBUG: Starting image generation...")
            
            # Generate images
            character_image_url = get_image_url(character_desc) if character_desc else ""
            background_image_url = get_image_url(background_desc) if background_desc else ""
            
            # For now, use background as combined image (simple approach)
            combined_image_url = background_image_url

            print(f"DEBUG: Character image URL: {character_image_url[:100] if character_image_url else 'None'}")
            print(f"DEBUG: Background image URL: {background_image_url[:100] if background_image_url else 'None'}")
            print(f"DEBUG: Combined image URL: {combined_image_url[:100] if combined_image_url else 'None'}")

            print("DEBUG: Rendering result template...")
            
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt,
                'story': story_text,
                'character': character_desc,
                'background': background_desc,
                'character_image_url': character_image_url,
                'background_image_url': background_image_url,
                'combined_image_url': combined_image_url,
            })

        except requests.exceptions.Timeout:
            print("DEBUG: Request timed out")
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt,
                'story': 'Error: The API request timed out. Please try again.',
                'character': '',
                'background': '',
                'character_image_url': '',
                'background_image_url': '',
                'combined_image_url': '',
            })
        
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Request error: {e}")
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt,
                'story': f'Network Error: {str(e)}',
                'character': '',
                'background': '',
                'character_image_url': '',
                'background_image_url': '',
                'combined_image_url': '',
            })
        
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt if 'user_prompt' in locals() else 'Unknown',
                'story': f'Unexpected Error: {str(e)}',
                'character': '',
                'background': '',
                'character_image_url': '',
                'background_image_url': '',
                'combined_image_url': '',
            })

    print("DEBUG: GET request - redirecting to home")
    return render(request, 'mainapp/home.html')