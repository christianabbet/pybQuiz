import os
import urllib.request
import zipfile
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
            # Check if blured image exists
            if not os.path.exists(path_blur):
                img = Image.open(path_img)
                img.filter(ImageFilter.GaussianBlur(radius=10)).save(path_blur)
            return path_blur
        else:
            return path_img
        
        