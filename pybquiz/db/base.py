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


    def pprint(self):
        
        name = self.__class__.__name__    
        self.db[TriviaQ.KEY_DIFFICULTY] = self.db[TriviaQ.KEY_DIFFICULTY].fillna("none")
        df_print = pd.crosstab(
            index=self.db[TriviaQ.KEY_CATEGORY], 
            columns=self.db[TriviaQ.KEY_DIFFICULTY]
        )
        df_print.columns = [str(c) for c in df_print.columns]

        # Group by categories and create df
        data_all = {TriviaQ.KEY_CATEGORY: "All"}
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
        serie = self.db.iloc[index]
        ref_keys = TriviaQ.get_keys()
    
        return serie[ref_keys].to_dict()
    


class UnifiedTSVDB(TriviaTSVDB):
    
    
    KEY_DOMAIN = "domain"
    KEY_O_CAT = "o_category"
    KEY_O_UK = "o_is_uk"
    KEY_O_USA = "o_is_usa"
    
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
        
    @abstractmethod
    def initialize(self) -> pd.DataFrame:
        
        return pd.DataFrame(
            columns=[
                # Mandatory keys
                TriviaQ.KEY_UUID, 
                TriviaQ.KEY_CATEGORY, 
                TriviaQ.KEY_DIFFICULTY, 
                TriviaQ.KEY_QUESTION, 
                TriviaQ.KEY_CORRECT_ANSWER, 
                TriviaQ.KEY_WRONG_ANSWER1, 
                TriviaQ.KEY_WRONG_ANSWER2, 
                TriviaQ.KEY_WRONG_ANSWER3, 
                UnifiedTSVDB.KEY_DOMAIN, 
                UnifiedTSVDB.KEY_O_CAT, 
                UnifiedTSVDB.KEY_O_UK, 
                UnifiedTSVDB.KEY_O_USA, 
            ]
        )

            
    @abstractmethod
    def update(self, dbs: list[TriviaTSVDB]):
        
        # Check for duplicates
        dbs_ = []
        for db in dbs:
            # Get standardized columns
            df = db.db
            df[self.KEY_DOMAIN] = db.__class__.__name__ 
            df[self.KEY_O_CAT] = None        
            df[self.KEY_O_UK] = None        
            df[self.KEY_O_USA] = None              
            dbs_.append(df)
            
        # Merge columns
        dbs_ = pd.concat(dbs_, ignore_index=True)
        # Get trivia cols
        dbs_ = dbs_[self.db.columns]
        dbs_ = dbs_.drop_duplicates(subset=TriviaQ.KEY_UUID, keep="first")
        
        # Merge with existing database        
        self.db = pd.concat([self.db, dbs_], ignore_index=True)
        self.db = self.db.drop_duplicates(subset=TriviaQ.KEY_UUID, keep="first")
        self.db = self.db.set_index("uuid").fillna(dbs_.set_index("uuid")).reset_index()
        # Nothing to do, just save version
        
        self.save()


    def pprint(self):
        
        name = self.__class__.__name__    
        self.db[UnifiedTSVDB.KEY_O_CAT] = self.db[UnifiedTSVDB.KEY_O_CAT].fillna("miscellaneous")
        self.db[UnifiedTSVDB.KEY_O_CAT] = self.db[UnifiedTSVDB.KEY_O_CAT].str.split("|").str[0] 
        df_print = pd.crosstab(
            index=self.db[UnifiedTSVDB.KEY_O_CAT], 
            columns=self.db[TriviaQ.KEY_DIFFICULTY]
        )
        
        df_print.columns = [str(c) for c in df_print.columns]

        # Group by categories and create df
        data_all = {UnifiedTSVDB.KEY_O_CAT: "All"}
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
        data = super().__getitem__(index)
        data[self.KEY_DOMAIN] = self.db.loc[index, self.KEY_DOMAIN]

        return data
    