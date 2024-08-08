from openai import OpenAI
import os
import urllib.request
import time
from PIL import Image


class OpenAIAPI:
    
    
    ENV_KEY = "OPENAI_API_KEY"
    
    def __init__(self, api_key: str, delay_api: int = 20) -> None:
        # Store key
        self.api_key = api_key
        self.delay_api = delay_api 
        os.environ[OpenAIAPI.ENV_KEY] = self.api_key
        # Open client
        self.client = OpenAI(
            api_key=os.environ.get(OpenAIAPI.ENV_KEY),
        )

    def generate_image(self, path: str, prompt: str, size: str = "1792x1024", quality: str = "standard", crop: list[int] = [1365, 1024]):
        
        # Sending prompt to openAI
        start = time.time()
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        end = time.time()
        
        # Get url and download image
        image_url = response.data[0].url
        urllib.request.urlretrieve(image_url, path)
        
        # Wait for api time
        time.sleep(max(self.delay_api - (end - start), 0)) 
        
        # Resize image to final shape        
        img = Image.open(path)
        left_margin = max(img.size[0] - crop[0], 0) // 2
        top_margin = max(img.size[1] - crop[1], 0) // 2
        # Save with blur
        img.crop(box=(left_margin, top_margin, left_margin + crop[0], top_margin + crop[1])).save(path)

        # TODO
        from PIL import Image, ImageFilter
        img.filter(ImageFilter.GaussianBlur(radius=10)).save("tmp2.png")