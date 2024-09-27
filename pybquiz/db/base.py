import os
import pandas as pd
from abc import abstractmethod
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
import numpy as np

from pybquiz.const import TriviaConst as TC


class TriviaDB:
    
    def __init__(
        self, 
        cache: str, 
    ) -> None:
        """ 
        Trivia database

        Parameters
        ----------
        cache : str
            Location of the database folder
        """        
        self.cache = cache
        os.makedirs(self.cache, exist_ok=True)
    
    @abstractmethod
    def __len__(self):
        """ Return length of database """
        raise NotImplementedError


class TriviaTSVDB(TriviaDB):  
    
    def __init__(
        self, 
        cache: str, 
        path_db: str,
    ) -> None:
        """ Trivia TSV database

        Parameters
        ----------
        cache : str
            Location of the database folder
        path_db : str
            Path to database file
        """        
        # Init main cach location
        super().__init__(cache=cache)          
        self.path_db = path_db
                    
        # Load db
        self.load()
        
            
    def load(self):
        # Check if DB exists otherwise init it
        if os.path.exists(self.path_db):
            self.db = pd.read_csv(self.path_db, sep="\t")
        else:
            self.db = self.initialize()
        
        # self.db = pd.concat([db, self.db], ignore_index=True)
        # Check columns
        ref_keys = TC.get_keys()
        assert all([k in self.db.columns for k in ref_keys])
        
    def save(self):
        """ Save database to file """
        self.db.to_csv(self.path_db, sep="\t", index=False)     
        
    def __len__(self):
        """ Return length of database 

        Returns
        -------
        int
            Length of the database
        """
        return len(self.db)
        
    @abstractmethod
    def initialize(self) -> pd.DataFrame:
        raise NotImplementedError
            
    @abstractmethod
    def update(self):
        raise NotImplementedError


    def pprint(self):
        
        name = self.__class__.__name__    
        self.db[TC.KEY_DIFFICULTY] = self.db[TC.KEY_DIFFICULTY].fillna("none")
        df_print = pd.crosstab(
            index=self.db[TC.KEY_CATEGORY], 
            columns=self.db[TC.KEY_DIFFICULTY]
        )
        df_print.columns = [str(c) for c in df_print.columns]

        # Group by categories and create df
        data_all = {TC.KEY_CATEGORY: "All"}
        data_all.update(df_print.sum().to_dict())
        # Add all other values
        data = [data_all]
        for _, d in df_print.reset_index().iterrows():
            data.append(d.to_dict())
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {}".format(name)))
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        
   
    def __getitem__(self, index: int):
        
        # Get row and params
        data = self.db.iloc[index].to_dict()
        
        # Build answer to shuffle
        answers = [TC.KEY_CORRECT_ANSWER, TC.KEY_WRONG_ANSWER1, TC.KEY_WRONG_ANSWER2, TC.KEY_WRONG_ANSWER3]
        answers = [a for a in answers if not pd.isnull(data.get(a))]
        answers = np.random.permutation(answers)
        data[TC.EXT_KEY_ORDER] = answers.tolist()
        data[TC.EXT_KEY_ORDER_ID] = int(np.argmax(answers == TC.KEY_CORRECT_ANSWER))
        
        return data
    


class UnifiedTSVDB(TriviaTSVDB):
    
    def __init__(
        self, 
        filename_db: Optional[str] = "trivia",
        cache: Optional[str] = '.cache', 
    ) -> None:
        """ Trivia TSV database

        Parameters
        ----------
        cache : str
            Location of the database folder
        path_db : str
            Path to database file
        update : Optional[bool], optional
            Update database, by default True
        """        

        # Call super method
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + ".tsv"),
        )
        # Remove multiple cats
        self.db[TC.EXT_KEY_O_CAT] = self.db[TC.EXT_KEY_O_CAT].fillna("").str.split("|").str[0]
        
    @abstractmethod
    def initialize(self) -> pd.DataFrame:
        
        return pd.DataFrame(
            columns=[
                # Mandatory keys
                TC.KEY_UUID, 
                TC.KEY_CATEGORY, 
                TC.KEY_DIFFICULTY, 
                TC.KEY_QUESTION, 
                TC.KEY_CORRECT_ANSWER, 
                TC.KEY_WRONG_ANSWER1, 
                TC.KEY_WRONG_ANSWER2, 
                TC.KEY_WRONG_ANSWER3, 
                TC.EXT_KEY_DOMAIN, 
                TC.EXT_KEY_O_CAT, 
                TC.EXT_KEY_O_UK, 
                TC.EXT_KEY_O_USA, 
            ]
        )

            
    @abstractmethod
    def update(self, dbs: list[TriviaTSVDB]):
        
        # Check for duplicates
        dbs_ = []
        for db in dbs:
            # Get standardized columns
            df = db.db
            if TC.EXT_KEY_DOMAIN not in df.columns:
                df[TC.EXT_KEY_DOMAIN] = db.__class__.__name__ 
            if TC.EXT_KEY_O_CAT not in df.columns:
                df[TC.EXT_KEY_O_CAT] = None
            if TC.EXT_KEY_O_UK not in df.columns:
                df[TC.EXT_KEY_O_UK] = None 
            if TC.EXT_KEY_O_USA not in df.columns:
                df[TC.EXT_KEY_O_USA] = None
            dbs_.append(df)
            
        # Merge columns
        dbs_ = pd.concat(dbs_, ignore_index=True)
        # Get trivia cols
        dbs_ = dbs_[self.db.columns]
        dbs_ = dbs_.drop_duplicates(subset=TC.KEY_UUID, keep="first")
        
        # Merge with existing database        
        self.db = pd.concat([self.db, dbs_], ignore_index=True)
        self.db = self.db.drop_duplicates(subset=TC.KEY_UUID, keep="first")
        self.db = self.db.set_index("uuid").fillna(dbs_.set_index("uuid")).reset_index()
        # Nothing to do, just save version
        
        self.save()


    def pprint(self):
        
        name = self.__class__.__name__    
        self.db[TC.EXT_KEY_O_CAT] = self.db[TC.EXT_KEY_O_CAT].fillna("miscellaneous")
        self.db[TC.EXT_KEY_O_CAT] = self.db[TC.EXT_KEY_O_CAT].str.split("|").str[0] 
        df_print = pd.crosstab(
            index=self.db[TC.EXT_KEY_O_CAT], 
            columns=self.db[TC.KEY_DIFFICULTY]
        )
        
        df_print.columns = [str(c) for c in df_print.columns]

        # Group by categories and create df
        data_all = {TC.EXT_KEY_O_CAT: "All"}
        data_all.update(df_print.sum().to_dict())
        # Add all other values
        data = [data_all]
        for _, d in df_print.reset_index().iterrows():
            data.append(d.to_dict())
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {}".format(name)))
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
