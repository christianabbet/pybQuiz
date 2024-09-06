from pybquiz.db.opentdb import OpenTriviaDB
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.db.jeopardy import Jeopardy
from pybquiz.db.thetrviaapi import TheTriviaAPIDB


def get_all_trivia_db():
    
    # Get data and loader
    opentdb = OpenTriviaDB()  
    thetriviadb = TheTriviaAPIDB()
    wwtbam_us_db = WWTBAM(lang='us')
    wwtbam_uk_db = WWTBAM(lang='uk')
    jeopardy_us_db = Jeopardy() 
    
    dbs = {
        "opentdb": opentdb,
        "thetriviadb": thetriviadb,
        "wwtbam_us_db": wwtbam_us_db,
        "wwtbam_uk_db": wwtbam_uk_db,
        "jeopardy_us_db": jeopardy_us_db,
    }
    
    return dbs