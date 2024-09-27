import os
import urllib.request
import zipfile
import re
from PIL import Image, ImageFilter


def standardize_text(text: str):
    return re.sub('[^A-Za-z0-9]+', '', text).lower()
            

class BackgroundManager():
    
    KEY_MAIN = "Pub Quiz"
    KEY_PAPER = "Quiz paper sheets"
    
    URL_BACKGROUND = "https://github.com/christianabbet/pybQuiz/releases/download/v1.0/backgrounds.zip"
    GITHUB_RELEASE = "https://github.com/christianabbet/pybQuiz/releases/download/googleslide/"
    
    FILE_ZIP = "backgrounds.zip"    
    FOLDER_NAME = "backgrounds"
    
    def __init__(
        self, 
        # yaml_token: str, 
        # delay_api: int = 20, 
        return_url: str = False,
        dircache: str = ".cache",
    ) -> None:
        
        # Define filenames
        self.return_url = return_url
        filename_zip = os.path.join(dircache, BackgroundManager.FILE_ZIP)
        filename_out = os.path.join(dircache, BackgroundManager.FOLDER_NAME)
        
        # Check if download needed
        if not os.path.exists(filename_out):
            # Download file
            urllib.request.urlretrieve(self.URL_BACKGROUND, filename_zip)
            # Unzip
            with zipfile.ZipFile(filename_zip, 'r') as zip_ref:
                zip_ref.extractall(dircache)
            # Remove zip
            os.remove(filename_zip)
            
        # Get local list
        self.bgs = {os.path.splitext(f)[0]: os.path.join(filename_out, f) for f in os.listdir(filename_out)}
    
                
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
            path_img = path_blur
        
        # Check if url wanted
        if self.return_url:        
            path_img = self.GITHUB_RELEASE + os.path.basename(path_img)
        
        return path_img


        