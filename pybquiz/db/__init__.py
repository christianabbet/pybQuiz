from pybquiz.db.opentdb import OpenTriviaDB
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy
from pybquiz.db.thetrviaapi import TheTriviaAPIDB
from pybquiz.db.kenquiz import KenQuizDB
from pybquiz.db.ninjaapi import NinjaAPI


def get_all_trivia_db():
    
    # Get data and loader
    opentdb = OpenTriviaDB()  
    thetriviadb = TheTriviaAPIDB()
    kenquizdb = KenQuizDB()
    # ninjaapi = NinjaAPI()

    dbs = {
        "opentdb": opentdb,
        "thetriviadb": thetriviadb,
        "kenquizdb": kenquizdb,
        # "ninjaapi": ninjaapi,
    }
    
    return dbs