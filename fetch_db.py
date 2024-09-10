import argparse
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy
from pybquiz.db.opentdb import OpenTriviaDB
from pybquiz.db.thetrviaapi import TheTriviaAPIDB
from pybquiz.db.kenquiz import KenQuizDB
from pybquiz.db.ninjaapi import NinjaAPI
from pybquiz.db.base import UnifiedTSVDB
import pandas as pd


def main(args):
    
    # MasterMinds
    # https://fikklefame.com/?s=master+minds
    
    # KenQuiz DB
    # https://www.kensquiz.co.uk/quizzes//
    kenquizdb = KenQuizDB()
    # kenquizdb.update()
    # kenquizdb.update_brutforce()
    kenquizdb.pprint()
        
    # OpenTrivia DB
    # https://opentdb.com/
    opentdb = OpenTriviaDB()
    # opentdb.update()
    opentdb.pprint()
    
    # The Trivia API
    # https://the-trivia-api.com/
    thetriviadb = TheTriviaAPIDB()
    # thetriviadb.update()
    thetriviadb.pprint()
    
    # API ninja 
    # https://api-ninjas.com/api/trivia
    ninjaapi = NinjaAPI()
    # ninjaapi.update()
    ninjaapi.pprint()
    
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
    
    # Merge Trivia DBs:
    dbs = [kenquizdb, opentdb, ninjaapi, thetriviadb]
    triviadb = UnifiedTSVDB()
    triviadb.update(dbs)
    triviadb.pprint()
    
    pd.concat
if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Fetch / update Databases',
        description='Fetch / update databases',
    )
    args = parser.parse_args()
    
    main(args=args)
    