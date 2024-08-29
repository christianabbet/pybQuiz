from pybquiz.db.base import TriviaTSVDB

import os
from typing import Optional, Literal
import urllib
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table


class JeopardyCst:
    
    URL_JEOPARDY = "https://raw.githubusercontent.com/jwolle1/jeopardy_clue_dataset/main/combined_season1-40.tsv"
    
    KEY_CAT = "category"
    KEY_CAT_ID = "category_id"
    KEY_CAT_SIMPLIFIED = "category_simplified"
    KEY_CLUE = "clue_value"
    KEY_DOUBLE_CLUE = "daily_double_value"
    KEY_DIFFICULTY = "difficulty"
    KEY_NOTES = "notes"
    KEY_COMMENTS = "comments"
    KEY_AIR_DATE = "air_date"
    
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
            update=False,
            path_db=os.path.join(cache, filename_db + lang + ".tsv")
        )

    def initialize(self):
        # Download db if needed
        if not os.path.exists(self.path_db):
            # Otherwise download it
            urllib.request.urlretrieve(JeopardyCst.URL_JEOPARDY, self.path_db)  
                  
        
    def update(self):
        pass
    
    def finalize(self):
        
        # Get categories above threshold
        simplifed_cats = self.db[JeopardyCst.KEY_CAT].value_counts()
        simplifed_cats = simplifed_cats[simplifed_cats > self.simplified_tresh].index.tolist()
        
        # Add dumy class for the rest
        simplifed_cats.append(JeopardyCst.CAT_OTHERS)
        self.db[JeopardyCst.KEY_CAT_SIMPLIFIED] = pd.Categorical(self.db[JeopardyCst.KEY_CAT], categories=simplifed_cats)
        self.db[JeopardyCst.KEY_CAT_SIMPLIFIED] = self.db[JeopardyCst.KEY_CAT_SIMPLIFIED].fillna(JeopardyCst.CAT_OTHERS)

        # Drop daily double (values not ranked)
        is_valid_clue = (self.db[JeopardyCst.KEY_CLUE] != 0) & (self.db[JeopardyCst.KEY_DOUBLE_CLUE] == 0)
        self.db = self.db[is_valid_clue]
        self.db.drop(columns=[JeopardyCst.KEY_NOTES, JeopardyCst.KEY_COMMENTS], inplace=True, errors="ignore")
    
        # Define difficulty
        value_range = self.db[JeopardyCst.KEY_CLUE].unique()
        value_range.sort()
        self.db[JeopardyCst.KEY_DIFFICULTY] = self.db[JeopardyCst.KEY_CLUE].replace({v: k for k, v in enumerate(value_range)})
        
        # Convert years if needed
        if isinstance(self.db[JeopardyCst.KEY_AIR_DATE].dtype, str):
            year_str = self.db[JeopardyCst.KEY_AIR_DATE].str.slice(start=0, stop=4)
            self.db[JeopardyCst.KEY_AIR_DATE] = pd.to_numeric(year_str, errors='coerce')
        
        
    def pprint(self):
                
        name = self.__class__.__name__
        n_questions = len(self.db)
        v_min = self.db[JeopardyCst.KEY_CLUE].min()
        v_max = self.db[JeopardyCst.KEY_CLUE].max()
        d_min = self.db[JeopardyCst.KEY_AIR_DATE].min()
        d_max = self.db[JeopardyCst.KEY_AIR_DATE].max()
        
        # Create a console
        data = {            
            "Lang": self.lang,
            "Questions": n_questions,
            "Values": "{}-{}".format(int(v_min), int(v_max)),
            "Air date": "{}-{}".format(int(d_min), int(d_max)),
        }
        
        difficulties = pd.cut(self.db[JeopardyCst.KEY_DIFFICULTY], bins=JeopardyCst.PPRINT_BINS).value_counts(sort=False)
        data.update({str(k): v for k, v in difficulties.items()})
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {} ({})".format(name, self.lang)))
        
        markdown = markdown_table([data]).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        
    