from django.db import models

# Create your models here.
from django.db import models

class StoryGeneration(models.Model):
    user_prompt = models.TextField()
    story = models.TextField()
    character_description = models.TextField()
    background_description = models.TextField()
    character_image_url = models.URLField(blank=True)
    background_image_url = models.URLField(blank=True)
    combined_image = models.ImageField(upload_to='combined/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Story: {self.user_prompt[:50]}..."
