from pybquiz.db.base import TriviaTSVDB

import os
from typing import Optional, Literal
import urllib
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
from pybquiz.db.utils import to_uuid


class JeopardyKey:
    
    URL_JEOPARDY = "https://raw.githubusercontent.com/jwolle1/jeopardy_clue_dataset/main/combined_season1-40.tsv"
    
    # Base TSV
    KEY_ROUND = "round"
    KEY_CLUE = "clue_value"
    KEY_DOUBLE_CLUE = "daily_double_value"
    KEY_CAT = "category"
    KEY_COMMENTS = "comments"
    KEY_ANSWER = "answer"
    KEY_QUESTION = "question"
    KEY_AIR_DATE = "air_date"
    KEY_NOTES = "notes"
    # New columns
    KEY_DIFFICULTY = "difficulty"
    KEY_UUID = "uuid"
    # Others
    CAT_OTHERS = "OTHERS"
    PPRINT_BINS = [0, 3, 7, 11]
    

class Jeopardy(TriviaTSVDB):
        
    def __init__(
        self, 
        cache: Optional[str] = '.cache',         
        lang: Literal['us'] = 'us',
        filename_db: Optional[str] = "jeopardy",
        simplified_tresh: Optional[int] = 1000,
    ) -> None:
        """Who wnats to be a millionaire database

        Parameters
        ----------
        cache : Optional[str], optional
            Location of the database, by default '.cache'
        lang : Literal['us', 'uk'], optional
            Lang of the show. Either 'uk' or 'us', by default 'us'
        filename_db : Optional[str], optional
            Name of the database, by default "jeopardy"
        """
        
        self.lang = lang
        self.simplified_tresh = simplified_tresh
        
        # Define online scrapper
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + lang + ".tsv")
        )

    def initialize(self) -> pd.DataFrame:
        
        # Otherwise download it
        urllib.request.urlretrieve(JeopardyKey.URL_JEOPARDY, self.path_db)  
            
        # Notes not needed
        db = pd.read_csv(self.path_db, sep="\t")
        db.drop(columns=[JeopardyKey.KEY_NOTES], inplace=True)
        # Comments not needed
        db.drop(columns=[JeopardyKey.KEY_COMMENTS], inplace=True)
        # Round information not needed
        db.drop(columns=[JeopardyKey.KEY_ROUND], inplace=True)
                
        # Check for values
        is_valid_clue = (db[JeopardyKey.KEY_CLUE] != 0) & (db[JeopardyKey.KEY_DOUBLE_CLUE] == 0)
        db = db[is_valid_clue]
        
        # Get possible values
        value_range = db[JeopardyKey.KEY_CLUE].unique()
        # Rank them
        value_range.sort()
        # Add difficulty indicator
        db[JeopardyKey.KEY_DIFFICULTY] = db[JeopardyKey.KEY_CLUE].replace({v: k for k, v in enumerate(value_range)})
        
        # Add uuid for entires
        db[JeopardyKey.KEY_UUID] = [to_uuid(s) for s in db[JeopardyKey.KEY_ANSWER].values]
        
        # Convert years if needed
        year_str = db[JeopardyKey.KEY_AIR_DATE].str.slice(start=0, stop=4)
        db[JeopardyKey.KEY_AIR_DATE] = pd.to_numeric(year_str, errors='coerce')
            
        return db
        
    def update(self):
        pass

    def pprint(self):
                
        name = self.__class__.__name__
        n_questions = len(self.db)
        v_min = self.db[JeopardyKey.KEY_CLUE].min()
        v_max = self.db[JeopardyKey.KEY_CLUE].max()
        d_min = self.db[JeopardyKey.KEY_AIR_DATE].min()
        d_max = self.db[JeopardyKey.KEY_AIR_DATE].max()
        
        # Create a console
        data = {            
            "Lang": self.lang,
            "Questions": n_questions,
            "Values": "{}-{}".format(int(v_min), int(v_max)),
            "Air date": "{}-{}".format(int(d_min), int(d_max)),
        }
        
        difficulties = pd.cut(self.db[JeopardyKey.KEY_DIFFICULTY], bins=JeopardyKey.PPRINT_BINS).value_counts(sort=False)
        data.update({str(k): v for k, v in difficulties.items()})
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {} ({})".format(name, self.lang)))
        
        markdown = markdown_table([data]).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        