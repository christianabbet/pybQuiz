import argparse
import os
from pybquiz import PybQuiz


def main(args):

    # Get input information
    cfg_path = args.cfg
    token_path = args.token
    
    if not os.path.exists(cfg_path):
        raise FileNotFoundError
        
    # Create quiz
    quiz = PybQuiz.from_yaml(yaml_path=cfg_path, yaml_token=token_path)
    # Create output directory
    os.makedirs(args.dirout, exist_ok=True)
    # Save to json
    outfile_json = os.path.join(args.dirout, "{}.json".format(args.name))
    quiz.to_json(file=outfile_json)    
        

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='Create a pub quiz',
    )
    parser.add_argument('--name', default='myquiz')
    parser.add_argument('--dirout', default='output')
    parser.add_argument('--cfg', default='config/template.yml')
    parser.add_argument('--token', default='config/apitoken.yml')
    args = parser.parse_args()
    
    main(args=args)
    