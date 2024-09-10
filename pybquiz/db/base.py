import os
import pandas as pd
from abc import abstractmethod
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table


class TriviaQ:
    
    # Define base keys that should exists in databases
    KEY_UUID = "uuid"
    KEY_CATEGORY = "category"
    KEY_DIFFICULTY = "difficulty"
    
    KEY_QUESTION = "question"
    KEY_CORRECT_ANSWER = "correct_answer"
    KEY_WRONG_ANSWER1 = "wrong_answers_1"
    KEY_WRONG_ANSWER2 = "wrong_answers_2"
    KEY_WRONG_ANSWER3 = "wrong_answers_3"
    
    @staticmethod
    def get_keys():
        return [v for k, v in TriviaQ.__dict__.items() if "KEY" in k]
            

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
        update: Optional[bool] = True,
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
        ref_keys = TriviaQ.get_keys()
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

    @abstractmethod        
    def pprint(self):
        raise NotImplementedError
   
    def __getitem__(self, index: int):
        
        # Get row and params
        serie = self.db.iloc[index]
        ref_keys = TriviaQ.get_keys()
    
        return serie[ref_keys].to_dict()
    


class UnifiedTSVDB(TriviaTSVDB):
    
    def __init__(
        self, 
        dbs: list[TriviaTSVDB],
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
        self.dbs = dbs
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + ".tsv"),
        )
        
    @abstractmethod
    def initialize(self) -> pd.DataFrame:
        
        # Get databases
        dfs = []
        for db in self.dbs:
            # Get standardized columns
            df = db.db
            df["source"] = self.__class__.__name__        
            dfs.append(df)
            
        # Merge columns
        dfs = pd.concat(dfs, ignore_index=True)
        # Get trivia cols
        ref_keys = TriviaQ.get_keys()
        dfs = dfs[ref_keys]
        return dfs

            
    @abstractmethod
    def update(self):
        pass

    @abstractmethod        
    def pprint(self):
        
        # Define name
        name = self.__class__.__name__        
        df_print = self.db[TriviaQ.KEY_CATEGORY].value_counts().reset_index()
        df_print.columns = [TriviaQ.KEY_CATEGORY, "count"]
        # Group by categories and create df
        data_all = {TriviaQ.KEY_CATEGORY: "All", "count": df_print["count"].sum()}
        # Add all other values
        data = [data_all]
        for _, d in df_print.iterrows():
            data.append(d.to_dict())
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {}".format(name)))
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
