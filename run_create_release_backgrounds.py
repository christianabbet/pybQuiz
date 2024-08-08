import argparse
import os
from pybquiz.background import standardize_text
from pybquiz.api_handler.openai import OpenAIAPI
import yaml

def main(args):

    # Get input information
    path_list = args.list
    path_token = args.token
       
    if not os.path.exists(path_list) or not os.path.exists(path_token):
        raise FileNotFoundError

    # Create output directory
    os.makedirs(args.dirout, exist_ok=True)

    # Create quiz
    with open(path_list) as stream:
        data_cat = yaml.safe_load(stream)
        
    # Check if file exists
    with open(path_token) as stream:
        data_token = yaml.safe_load(stream)
                
    # Create openai link
    if "openai" not in data_token:
        return 
    
    # Iterate over background to create
    openai_api = OpenAIAPI(api_key=data_token['openai'])                   
    
    for i, cat in enumerate(data_cat):
        
        # Define path
        print("[{}/{}]: {}".format(i+1, len(data_cat), cat))
        filename = standardize_text(cat)
        path_bg = os.path.join(args.dirout, filename + ".png")
        
        # Check if alread exists
        if os.path.exists(path_bg):
            continue
        
        # Get image
        openai_api.generate_image(
            path=path_bg,
            prompt="A {} simple and flat illustration".format(cat)
        )        

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Background creations',
        description='Create background for quiz caegoires',
    )
    parser.add_argument('--dirout', default='output/backgrounds')
    parser.add_argument('--list', default='config/categories.yml')
    parser.add_argument('--token', default='config/apitoken.yml')
    args = parser.parse_args()
    
    main(args=args)
    