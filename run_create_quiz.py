import argparse
import os
from pybquiz import PybQuiz


def main(args):

    # Get input information
    cfg_path = args.cfg
    if not os.path.exists(cfg_path):
        raise FileNotFoundError
        
    # Create quiz
    PybQuiz.from_yaml(yaml_path=cfg_path)
    

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='Create a pub quiz',
    )
    parser.add_argument('--cfg', default='config/template.yml')
    args = parser.parse_args()
    
    main(args=args)
    