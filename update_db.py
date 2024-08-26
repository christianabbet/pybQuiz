import argparse
from pybquiz.db.wwtbam import WWTBAM


def main(args):
    
    wwtbam_db = WWTBAM()
    wwtbam_db.update()
    

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Update Databases',
        description='Update remote databases',
    )
    # parser.add_argument('--cfg', default=None,
    #                     help='path to config file (default if None)')
    # parser.add_argument('--dirout', default="output", 
    #                     help='path to output directory for data generation (default is "output")')
    # parser.add_argument('--apitoken', default='config/apitoken.yml', 
    #                     help='path to stored API tokens (default is "config/apitoken.yml")')
    # parser.add_argument('--googlecreds', default='config/credentials.json', 
    #                     help='path to stored Google credentials (default is "config/credentials.json")')
    args = parser.parse_args()
    
    main(args=args)
    