import os
import json
import requests
import logging
from urllib.parse import quote
from django.shortcuts import render
from django.conf import settings
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import base64
from typing import Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

class ImageMerger:
    """Advanced image merging using PIL to create coherent scenes"""
    
    @staticmethod
    def download_image(url: str) -> Optional[Image.Image]:
        """Download image from URL and return PIL Image"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert('RGBA')
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    @staticmethod
    def create_coherent_scene(character_url: str, background_url: str) -> Optional[str]:
        """
        Merge character and background into a coherent scene
        Returns base64 encoded image string
        """
        try:
            # Download images
            char_img = ImageMerger.download_image(character_url)
            bg_img = ImageMerger.download_image(background_url)
            
            if not char_img or not bg_img:
                logger.warning("Failed to download one or both images")
                return character_url or background_url
            
            # Standardize size
            scene_width, scene_height = 800, 600
            bg_img = bg_img.resize((scene_width, scene_height), Image.Resampling.LANCZOS)
            
            # Character processing
            char_img = ImageMerger._prepare_character(char_img, scene_width, scene_height)
            
            # Create the merged scene
            merged_scene = ImageMerger._compose_scene(bg_img, char_img)
            
            # Add artistic effects
            final_scene = ImageMerger._apply_scene_effects(merged_scene)
            
            # Convert to base64
            return ImageMerger._image_to_base64(final_scene)
            
        except Exception as e:
            logger.error(f"Error in scene creation: {e}")
            return None
    
    @staticmethod
    def _prepare_character(char_img: Image.Image, scene_width: int, scene_height: int) -> Image.Image:
        """Prepare character image for scene integration"""
        # Resize character to fit proportionally (max 40% of scene width)
        max_char_width = int(scene_width * 0.4)
        max_char_height = int(scene_height * 0.7)
        
        # Calculate aspect ratio preserving resize
        char_ratio = char_img.width / char_img.height
        if char_ratio > 1:  # Wider than tall
            new_width = min(max_char_width, char_img.width)
            new_height = int(new_width / char_ratio)
        else:  # Taller than wide
            new_height = min(max_char_height, char_img.height)
            new_width = int(new_height * char_ratio)
        
        char_img = char_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create soft edges for better blending
        char_img = ImageMerger._create_soft_edges(char_img)
        
        return char_img
    
    @staticmethod
    def _create_soft_edges(img: Image.Image) -> Image.Image:
        """Create soft edges around character for better blending"""
        # Create a mask with soft edges
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Create rounded rectangle mask
        margin = 10
        draw.rounded_rectangle(
            [margin, margin, img.width - margin, img.height - margin],
            radius=20,
            fill=255
        )
        
        # Apply Gaussian blur for soft edges
        mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Apply mask to image
        img.putalpha(mask)
        return img
    
    @staticmethod
    def _compose_scene(background: Image.Image, character: Image.Image) -> Image.Image:
        """Compose character onto background with proper positioning"""
        scene = background.copy()
        
        # Position character (slightly right of center, bottom aligned)
        char_x = int(scene.width * 0.6) - character.width // 2
        char_y = scene.height - character.height - 20  # 20px from bottom
        
        # Ensure character fits within scene
        char_x = max(0, min(char_x, scene.width - character.width))
        char_y = max(0, min(char_y, scene.height - character.height))
        
        # Paste character with alpha blending
        if character.mode == 'RGBA':
            scene.paste(character, (char_x, char_y), character)
        else:
            scene.paste(character, (char_x, char_y))
        
        return scene
    
    @staticmethod
    def _apply_scene_effects(scene: Image.Image) -> Image.Image:
        """Apply artistic effects to enhance the final scene"""
        # Convert to RGB for processing
        if scene.mode == 'RGBA':
            # Create white background and paste scene
            rgb_scene = Image.new('RGB', scene.size, 'white')
            rgb_scene.paste(scene, mask=scene.split()[-1] if len(scene.split()) == 4 else None)
            scene = rgb_scene
        
        # Enhance colors slightly
        enhancer = ImageEnhance.Color(scene)
        scene = enhancer.enhance(1.1)
        
        # Add subtle vignette effect
        scene = ImageMerger._add_vignette(scene)
        
        return scene
    
    @staticmethod
    def _add_vignette(image: Image.Image) -> Image.Image:
        """Add subtle vignette effect"""
        width, height = image.size
        
        # Create vignette mask
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)
        
        # Create radial gradient
        center_x, center_y = width // 2, height // 2
        max_distance = max(width, height) // 2
        
        for i in range(0, max_distance, 10):
            alpha = int((i / max_distance) * 30)  # Subtle effect
            draw.ellipse(
                [center_x - i, center_y - i, center_x + i, center_y + i],
                outline=(0, 0, 0, alpha)
            )
        
        # Apply vignette
        image_with_alpha = image.convert('RGBA')
        final_image = Image.alpha_composite(image_with_alpha, vignette)
        
        return final_image.convert('RGB')
    
    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{img_data}"

def strip_markdown_fences(text: str) -> str:
    """Enhanced markdown fence removal with JSON extraction."""
    text = text.strip()
    
    # Remove various markdown code blocks
    if text.startswith("```json"):
        text = text[7:].lstrip()  # len("```json") = 7
    elif text.startswith("```"):
        text = text[3:].lstrip()  # len("```") = 3
    
    if text.endswith("```"):
        text = text[:-3].rstrip()
    
    # Remove any remaining markdown formatting
    text = text.replace("**", "").replace("*", "")
    
    # Extract JSON object if present
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1
    if start_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx]
    
    return text



def parse_fallback_text(text: str) -> tuple:
    """
    Fallback parser when JSON parsing fails
    Returns (story, character, background)
    """
    logger.info("Using fallback text parsing")
    
    # If it's a short response, use it as the story
    if len(text) < 500:
        return (
            text,
            "A character from this story with detailed appearance and clothing",
            "The setting where this story takes place with specific details"
        )
    
    # Try to split into sections if it's longer
    sections = text.split('\n\n')
    if len(sections) >= 3:
        return (sections, sections, sections)[1][2]
    elif len(sections) == 2:
        return (sections, sections, "A detailed story setting")[1]
    else:
        return (text, "A story character", "A story setting")

def get_image_url(description):
    """Generate images using Pollinations AI"""
    if not description.strip():
        return ""
    
    logger.info(f"Generating image for: {description[:50]}...")
    
    try:
        # Enhanced prompt engineering for better image quality
        enhanced_desc = f"high quality, detailed, 4k resolution, {description}"
        encoded_desc = quote(enhanced_desc)
        seed = abs(hash(description)) % 10000
        image_url = f"https://image.pollinations.ai/prompt/{encoded_desc}?width=512&height=512&seed={seed}&enhance=true"
        logger.info(f"Generated image URL: {image_url[:100]}...")
        return image_url
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        seed = abs(hash(description)) % 1000
        return f"https://picsum.photos/512/512?random={seed}"

def home(request):
    """Home view with UI mode switching"""
    if settings.UI_MODE == "high":
        return render(request, "mainapp/homeUIUX.html")
    return render(request, "mainapp/home.html")

def generate_story(request):
    """Generate story using Perplexity API with enhanced debugging and error handling"""
    logger.info(f"Generate story view called with method: {request.method}")
    
    if request.method == 'POST':
        try:
            user_prompt = request.POST.get('prompt', '').strip()
            logger.info(f"User prompt: {user_prompt[:100]}...")
            
            if not user_prompt:
                return render(request, 'mainapp/home.html', {'error': 'Please provide a prompt'})
            
            if not PERPLEXITY_API_KEY:
                logger.error("No API key found")
                return render(request, 'mainapp/result.html', {
                    'prompt': user_prompt,
                    'story': 'Error: PERPLEXITY_API_KEY not found in environment variables. Please check your .env file.',
                    'character': '', 'background': '', 'character_image_url': '',
                    'background_image_url': '', 'combined_image_url': '',
                })

            logger.info("Building Perplexity API request...")
            
            # Simplified messages for better compatibility
            messages = [
                {
                    "role": "system",
                    "content": "You are a creative storytelling assistant. Respond only with valid JSON containing story, character, and background fields."
                },
                {
                    "role": "user", 
                    "content": f"""Write a creative story about: {user_prompt}

Respond with this exact JSON format:
{{"story": "your story here", "character": "detailed character description", "background": "detailed scene description"}}"""
                }
            ]

            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            logger.info(f"Sending request to: {PERPLEXITY_BASE_URL}/chat/completions")
            
            response = requests.post(
                f"{PERPLEXITY_BASE_URL}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"API Error Response: {error_text}")
                return render(request, 'mainapp/result.html', {
                    'prompt': user_prompt,
                    'story': f'API Error ({response.status_code}): {error_text}',
                    'character': '', 'background': '', 'character_image_url': '',
                    'background_image_url': '', 'combined_image_url': '',
                })
            
            response.raise_for_status()
            data = response.json()
            
            # Safe debugging with type checking
            logger.info(f"API Response type: {type(data)}")
            logger.info(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Safe content extraction
            ai_text = ""
            
            try:
                # Check if response has expected structure
                if isinstance(data, dict) and 'choices' in data:
                    choices = data['choices']
                    logger.info(f"Choices type: {type(choices)}, length: {len(choices) if isinstance(choices, list) else 'Not a list'}")
                    
                    if isinstance(choices, list) and len(choices) > 0:
                        first_choice = choices[0]
                        logger.info(f"First choice type: {type(first_choice)}")
                        
                        if isinstance(first_choice, dict):
                            logger.info(f"First choice keys: {list(first_choice.keys())}")
                            
                            # Try different content extraction methods
                            if 'message' in first_choice:
                                message = first_choice['message']
                                if isinstance(message, dict) and 'content' in message:
                                    ai_text = message['content']
                                    logger.info("✅ Extracted from message.content")
                            
                            elif 'delta' in first_choice:
                                delta = first_choice['delta']
                                if isinstance(delta, dict) and 'content' in delta:
                                    ai_text = delta['content']
                                    logger.info("✅ Extracted from delta.content")
                            
                            elif 'text' in first_choice:
                                ai_text = first_choice['text']
                                logger.info("✅ Extracted from choice.text")
                            
                            elif 'content' in first_choice:
                                ai_text = first_choice['content']
                                logger.info("✅ Extracted from choice.content")
                        
                        else:
                            logger.error(f"First choice is not a dict: {first_choice}")
                    
                    else:
                        logger.error("Choices is empty or not a list")
                
                # Alternative extraction methods
                elif isinstance(data, dict):
                    if 'content' in data:
                        ai_text = data['content']
                        logger.info("✅ Extracted from data.content")
                    elif 'response' in data:
                        ai_text = data['response']
                        logger.info("✅ Extracted from data.response")
                    elif 'text' in data:
                        ai_text = data['text']
                        logger.info("✅ Extracted from data.text")
                
                else:
                    logger.error(f"Unexpected response format: {type(data)}")
                    
            except Exception as parse_error:
                logger.error(f"Error during content extraction: {parse_error}")
                import traceback
                logger.error(f"Extraction traceback: {traceback.format_exc()}")
            
            # Final check for content
            if not ai_text:
                logger.error("Could not extract any content from response")
                logger.error(f"Full response (first 500 chars): {str(data)[:500]}...")
                
                # Try to use the entire response as fallback
                if isinstance(data, str):
                    ai_text = data
                elif isinstance(data, dict):
                    ai_text = str(data)
                else:
                    return render(request, 'mainapp/result.html', {
                        'prompt': user_prompt,
                        'story': f'Error: Could not extract content from API response. Response type: {type(data)}',
                        'character': '', 'background': '', 'character_image_url': '',
                        'background_image_url': '', 'combined_image_url': '',
                    })

            logger.info(f"Successfully extracted AI text: {ai_text[:200]}...")

            # Clean and parse the extracted text
            clean_text = strip_markdown_fences(ai_text)
            logger.info(f"Clean text for parsing: {clean_text[:200]}...")

            # Try JSON parsing with comprehensive fallback
            try:
                result_json = json.loads(clean_text)
                story_text = result_json.get('story', '')
                character_desc = result_json.get('character', '')
                background_desc = result_json.get('background', '')
                logger.info("✅ JSON parsing successful")
                
                # Ensure we have content
                if not story_text:
                    story_text = clean_text
                if not character_desc:
                    character_desc = f"A character from the story: {user_prompt}"
                if not background_desc:
                    background_desc = f"The setting for the story: {user_prompt}"
                    
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing failed: {json_error}")
                logger.info("Using fallback text parsing")
                
                # Use the full text as story if JSON parsing fails
                story_text = clean_text
                character_desc = f"A character from this story about {user_prompt}"
                background_desc = f"The setting of this story about {user_prompt}"

            logger.info("Starting image generation...")
            
            # Generate images with enhanced descriptions
            character_image_url = get_image_url(character_desc) if character_desc else ""
            background_image_url = get_image_url(background_desc) if background_desc else ""
            
            # Create combined scene
            logger.info("Creating combined scene...")
            combined_image_url = ""
            if character_image_url and background_image_url:
                combined_image_url = ImageMerger.create_coherent_scene(
                    character_image_url, 
                    background_image_url
                )
            
            if not combined_image_url:
                combined_image_url = background_image_url or character_image_url

            logger.info("Rendering result template...")
            
            template_name = 'mainapp/resultUIUX.html' if settings.UI_MODE == "high" else 'mainapp/result.html'
            
            return render(request, template_name, {
                'prompt': user_prompt,
                'story': story_text,
                'character': character_desc,
                'background': background_desc,
                'character_image_url': character_image_url,
                'background_image_url': background_image_url,
                'combined_image_url': combined_image_url,
            })

        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt if 'user_prompt' in locals() else '',
                'story': 'Error: The API request timed out. Please try again.',
                'character': '', 'background': '', 'character_image_url': '',
                'background_image_url': '', 'combined_image_url': '',
            })
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return render(request, 'mainapp/result.html', {
                'prompt': user_prompt if 'user_prompt' in locals() else 'Unknown',
                'story': f'Unexpected Error: {str(e)}',
                'character': '', 'background': '', 'character_image_url': '',
                'background_image_url': '', 'combined_image_url': '',
            })

    logger.info("GET request - redirecting to home")
    return home(request)
