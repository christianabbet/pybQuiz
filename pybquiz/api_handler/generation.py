from openai import OpenAI
import os
import urllib.request
import time
import zipfile
import yaml
import re
from PIL import Image, ImageFilter


def standardize_text(text: str):
    return re.sub('[^A-Za-z0-9]+', '', text).lower()
            

class BackgroundManager():
    
    URL_BACKGROUND = "https://github.com/christianabbet/pybQuiz/releases/download/v1.0/backgrounds.zip"
    FILE_ZIP = "backgrounds.zip"    
    FOLDER_NAME = "backgrounds"
    
    def __init__(self, yaml_token: str, delay_api: int = 20, dirout: str = "output") -> None:
        
        # Define filenames
        filename_zip = os.path.join(dirout, BackgroundManager.FILE_ZIP)
        filename_out = os.path.join(dirout, BackgroundManager.FOLDER_NAME)
        
        # Check if download needed
        if not os.path.exists(filename_out):
            # Download file
            urllib.request.urlretrieve(self.URL_BACKGROUND, filename_zip)
            # Unzip
            with zipfile.ZipFile(filename_zip, 'r') as zip_ref:
                zip_ref.extractall(dirout)
            # Remove zip
            os.remove(filename_zip)
            
        # Get local list
        self.bgs = {os.path.splitext(f)[0]: os.path.join(filename_out, f) for f in os.listdir(filename_out)}
        
        # # Set openai api
        # if os.path.exists(yaml_token):
        #     # Get from file
        #     with open(yaml_token) as stream:
        #         data_token = yaml.safe_load(stream)
        #     # Get key
        #     self.openai = OpenAIAPI(api_key=data_token.get("openai", ""), delay_api=delay_api)
                
    def get_background(self, name: str, blurred: bool = False, default: str = "random"):
        # Get image
        name_standard = standardize_text(name)
        path_img = self.bgs.get(name_standard, None)
        
        # Backup if not found
        if path_img is None:
            path_img = self.bgs.get(default, None)
            
        # Check if blurred needed
        if blurred and path_img is not None:
            filename, ext = os.path.splitext(os.path.basename(path_img))
            path_blur = os.path.join(os.path.dirname(path_img), "{}_blurred{}".format(filename, ext))
            img = Image.open(path_img)
            img.filter(ImageFilter.BoxBlur(radius=10)).save(path_blur)
            return path_blur
        else:
            return path_img
        
        
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
