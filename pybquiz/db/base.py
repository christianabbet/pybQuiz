import os
import pandas as pd
from abc import abstractmethod
from typing import Optional


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