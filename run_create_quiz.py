import argparse
import os
from pybquiz import PybQuiz
from pybquiz.export.pptx import PptxFactory
from pybquiz.background import BackgroundManager
from pybquiz.export.googleslide import GoogleSlideFactory
from pybquiz.config_generator import ConfigGenerator


def main(args):

    # Get input information
    cfg_path = args.cfg
    token_path = args.apitoken
       
    # Assist quiz creation
    if cfg_path is None or not os.path.exists(cfg_path):
        cfgGen = ConfigGenerator(yaml_api_file=token_path, dirout="config")
        cfg_path = cfgGen.run_terminal()

    # Create output directory
    os.makedirs(args.dirout, exist_ok=True)
    
    # Save to json
    name = os.path.splitext(os.path.basename(cfg_path))[0]
    outfile_json = os.path.join(args.dirout, "{}.json".format(name))
    outfile_pptx = os.path.join(args.dirout, "{}.pptx".format(name))
            
    # Create quiz
    if not os.path.exists(outfile_json):
        print("Quiz {} does not exists, create it ...".format(name))
        quiz = PybQuiz.from_yaml(yaml_path=cfg_path, yaml_token=token_path)
        quiz.dump(file=outfile_json) 
        
    # Create background handler                
    background_gen = BackgroundManager(yaml_token=token_path, dirout=args.dirout)
    
    # Reload from json
    # pptx = PptxFactory()
    # pptx.export(dump_path=outfile_json, outfile=outfile_pptx, background_gen=background_gen)
    
    # Check if google slide available
    if os.path.exists(args.googlecreds):
        gpptx = GoogleSlideFactory(name=name, crendential_file=args.googlecreds)
        gpptx.export(dump_path=outfile_json, background_gen=background_gen)



if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='PybQuiz is a Python package designed to help you create and manage pub quizzes effortlessly',
    )
    parser.add_argument('--cfg', default="output/myamazingquiz.json",
                        help='path to config file (default if None)')
    parser.add_argument('--dirout', default="output", 
                        help='path to output directory for data generation (default is "output")')
    parser.add_argument('--apitoken', default='config/apitoken.yml', 
                        help='path to stored API tokens (default is "config/apitoken.yml")')
    parser.add_argument('--googlecreds', default='config/credentials.json', 
                        help='path to stored Google credentials (default is "config/credentials.json")')
    args = parser.parse_args()
    
    main(args=args)
    