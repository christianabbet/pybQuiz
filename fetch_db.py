import argparse
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy

def main(args):
    
    # WWTBAM US
    wwtbam_us_db = WWTBAM(lang='us', update=False)
    
    # WWTBAM UK
    wwtbam_uk_db = WWTBAM(lang='uk', update=False)
    
    # Jeopardy
    jeopardy_us_db = Jeopardy()

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Fetch / update Databases',
        description='Fetch / update databases',
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
    