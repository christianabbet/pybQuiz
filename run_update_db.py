import argparse
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy
from pybquiz.db.opentdb import OpenTriviaDB
from pybquiz.db.thetrviaapi import TheTriviaAPIDB
from pybquiz.db.kenquiz import KenQuizDB
from pybquiz.db.ninjaapi import NinjaAPI
from pybquiz.db.base import UnifiedTSVDB


def main(args):
    
    # MasterMinds
    # https://fikklefame.com/?s=master+minds
    
    # KenQuiz DB
    # https://www.kensquiz.co.uk/quizzes//
    # print("####### KenQuizDB #######")
    # kenquizdb = KenQuizDB()
    # kenquizdb.update()
    # kenquizdb.update_brutforce()
    # kenquizdb.pprint()
        
    # OpenTrivia DB
    # https://opentdb.com/
    # print("####### OpenTriviaDB #######")
    # opentdb = OpenTriviaDB()
    # opentdb.update()
    # opentdb.pprint()
    
    # The Trivia API
    # https://the-trivia-api.com/
    # print("####### TheTriviaAPIDB #######")
    # thetriviadb = TheTriviaAPIDB()
    # thetriviadb.update()
    # thetriviadb.pprint()
    
    # API ninja 
    # https://api-ninjas.com/api/trivia
    # print("####### NinjaAPI #######")
    # ninjaapi = NinjaAPI()
    # ninjaapi.update()
    # ninjaapi.pprint()
    
    # Merge Trivia DBs:
    # print("####### Unified Trivia #######")
    # dbs = [kenquizdb, opentdb, ninjaapi, thetriviadb]
    # triviadb = UnifiedTSVDB()
    # triviadb.update(dbs)
    # triviadb.pprint()
    
    # WWTBAM US
    # print("####### WWTBAM US #######")
    wwtbam_us_db = WWTBAM(lang='us')
    # wwtbam_us_db.update()
    wwtbam_us_db.pprint()
    
    # WWTBAM UK
    # print("####### WWTBAM UK #######")
    wwtbam_uk_db = WWTBAM(lang='uk')
    # wwtbam_uk_db.update()
    wwtbam_uk_db.pprint()
    
    print("####### Unified WWTBAM #######")
    dbs = [wwtbam_us_db, wwtbam_uk_db]
    triviadb = UnifiedTSVDB(filename_db="wwtbam")
    triviadb.update(dbs)
    triviadb.pprint()
    
    # Jeopardy
    # print("####### Jeopardy US #######")
    # jeopardy_us_db = Jeopardy()
    # jeopardy_us_db.pprint()
    


if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Fetch / update Databases',
        description='Fetch / update databases',
    )
    args = parser.parse_args()
    
    main(args=args)
    