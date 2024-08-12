import argparse
import os
from pybquiz import PybQuiz
from pybquiz.export.pptx import PptxFactory
from pybquiz.background import BackgroundManager
from pybquiz.export.googleslide import GoogleSlideFactory


def main(args):

    # Get input information
    cfg_path = args.cfg
    token_path = args.token
       
    if not os.path.exists(cfg_path):
        raise FileNotFoundError

    # Create output directory
    os.makedirs(args.dirout, exist_ok=True)
    # Save to json
    outfile_json = os.path.join(args.dirout, "{}.json".format(args.name))
    outfile_pptx = os.path.join(args.dirout, "{}.pptx".format(args.name))
            
    # Create quiz
    if not os.path.exists(outfile_json):
        print("Quiz {} does not exists, create it ...".format(args.name))
        quiz = PybQuiz.from_yaml(yaml_path=cfg_path, yaml_token=token_path)
        quiz.dump(file=outfile_json) 
        
    # Create background handler                
    background_gen = BackgroundManager(yaml_token=token_path, dirout=args.dirout)
    
    # Reload from json
    PptxFactory.export(dump_path=outfile_json, outfile=outfile_pptx, background_gen=background_gen)
    
    # # Check if google slide available
    # if os.path.exists(args.googleslide):
    #     GoogleSlideFactory.export(title=args.name, crendential_file=args.googleslide)



if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='Create a pub quiz',
    )
    parser.add_argument('--name', default='quiztest')
    parser.add_argument('--dirout', default='output')
    parser.add_argument('--cfg', default='config/quiztest.yml')
    parser.add_argument('--token', default='config/apitoken.yml')
    parser.add_argument('--googleslide', default='config/credentials.json')
    args = parser.parse_args()
    
    main(args=args)
    