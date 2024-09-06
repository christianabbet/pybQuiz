import argparse
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy
from pybquiz.db.opentdb import OpenTriviaDB
from pybquiz.db.thetrviaapi import TheTriviaAPIDB


def main(args):
    
    # MasterMinds
    # https://fikklefame.com/?s=master+minds
    
    # Trivia DB
    # https://opentdb.com/
    opentdb = OpenTriviaDB()
    # opentdb.update()
    # opentdb.pprint()
    
    # The Trivia API
    # https://the-trivia-api.com/
    # thetriviadb = TheTriviaAPIDB()
    # thetriviadb.update()
    # thetriviadb.pprint()
    
    # API ninja (check liscence)
    # https://api.api-ninjas.com/v1/riddles
    # https://api-ninjas.com/api/trivia
    # https://api-ninjas.com/api/embeddings
    
    # WWTBAM US
    # wwtbam_us_db = WWTBAM(lang='us')
    # wwtbam_us_db.update()
    # wwtbam_us_db.pprint()
    
    # WWTBAM UK
    # wwtbam_us_db = WWTBAM(lang='uk')
    # wwtbam_us_db.update()
    # wwtbam_us_db.pprint()
    
    # Jeopardy
    # jeopardy_us_db = Jeopardy()
    # jeopardy_us_db.pprint()

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Fetch / update Databases',
        description='Fetch / update databases',
    )
    # parser.add_argument('--cfg', default=None,
    #                     help='path to config file (default if None)')
    args = parser.parse_args()
    
    main(args=args)
    