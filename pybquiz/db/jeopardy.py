from pybquiz.db.base import TriviaTSVDB

import os
from typing import Optional, Literal
import urllib
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table


class Jeopardy(TriviaTSVDB):
    
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
        
        # Define online scrapper
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + lang + ".tsv")
        )
        self.lang = lang
        self.simplified_tresh = simplified_tresh
        
        if self.db is None:
            # Download db if needed
            self._download_db(path_db=self.path_db)
            # Reload db if needed after download
            self.db = self.load_db()
            # Init db
            self._init_db()

    @staticmethod
    def _download_db(path_db: str):
        # Check if file exists
        if not os.path.exists(path_db):
            # Otherwise download it
            urllib.request.urlretrieve(Jeopardy.URL_JEOPARDY, path_db)
                
    def _init_db(self):
        
        # Get categories above threshold
        simplifed_cats = self.db[Jeopardy.KEY_CAT].value_counts()
        simplifed_cats = simplifed_cats[simplifed_cats > self.simplified_tresh].index.tolist()
        
        # Add dumy class for the rest
        simplifed_cats.append(Jeopardy.CAT_OTHERS)
        self.db[Jeopardy.KEY_CAT_SIMPLIFIED] = pd.Categorical(self.db[Jeopardy.KEY_CAT], categories=simplifed_cats)
        self.db[Jeopardy.KEY_CAT_SIMPLIFIED] = self.db[Jeopardy.KEY_CAT_SIMPLIFIED].fillna(Jeopardy.CAT_OTHERS)

        # Drop daily double (values not ranked)
        is_valid_clue = (self.db[Jeopardy.KEY_CLUE] != 0) & (self.db[Jeopardy.KEY_DOUBLE_CLUE] == 0)
        self.db = self.db[is_valid_clue]
        self.db.drop(columns=[Jeopardy.KEY_NOTES, Jeopardy.KEY_COMMENTS], inplace=True, errors="ignore")
    
        # Define difficulty
        value_range = self.db[Jeopardy.KEY_CLUE].unique()
        value_range.sort()
        self.db[Jeopardy.KEY_DIFFICULTY] = self.db[Jeopardy.KEY_CLUE].replace({v: k for k, v in enumerate(value_range)})
        
        # Override tsv
        year_str = self.db[Jeopardy.KEY_AIR_DATE].str.slice(start=0, stop=4)
        self.db[Jeopardy.KEY_AIR_DATE] = pd.to_numeric(year_str, errors='coerce')
        
        self.save_db()
        
    def update(self):
        pass
    
    def stats(self):
                
        name = self.__class__.__name__
        n_questions = len(self.db)
        v_min = self.db[Jeopardy.KEY_CLUE].min()
        v_max = self.db[Jeopardy.KEY_CLUE].max()
        d_min = self.db[Jeopardy.KEY_AIR_DATE].min()
        d_max = self.db[Jeopardy.KEY_AIR_DATE].max()
        
        # Create a console
        data = {            
            "Lang": self.lang,
            "Questions": n_questions,
            "Values": "{}-{}".format(int(v_min), int(v_max)),
            "Air date": "{}-{}".format(int(d_min), int(d_max)),
        }
        
        difficulties = pd.cut(self.db[Jeopardy.KEY_DIFFICULTY], bins=[0, 3, 7, 11]).value_counts(sort=False)
        data.update({str(k): v for k, v in difficulties.items()})
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {} ({})".format(name, self.lang)))
        
        markdown = markdown_table([data]).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        
    