import argparse
from pybquiz.db.wwtbam import WWTBAM


def main(args):
    
    # WWTBAM US
    wwtbam_us_db = WWTBAM(lang='us')
    wwtbam_us_db.update()
    wwtbam_us_db.clean()
    wwtbam_us_db.stats()
    
    # WWTBAM UK
    wwtbam_uk_db = WWTBAM(lang='uk')
    wwtbam_uk_db.update()
    wwtbam_uk_db.clean()
    wwtbam_uk_db.stats()

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
    