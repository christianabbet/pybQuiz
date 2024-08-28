import os
import pandas as pd


class TriviaTSVDB:  
    
    def __init__(
        self, 
        cache: str, 
        path_db: str,
    ) -> None:
        """Who wnats to be a millionaire database

        Parameters
        ----------
        cache : str
            Location of the database folder
        path_db : str
            Path to database file
        """        
        self.cache = cache
        self.path_db = path_db
        self.db = self.load_db()
        os.makedirs(self.cache, exist_ok=True)
        
    def update(self):
        raise NotImplementedError
        
    def stats(self):
        raise NotImplementedError
    
    def load_db(self):
        """Load database from file

        Returns
        -------
        database: pd.DataFrame
            Loaded database
        """
        # If exists, reload it
        if os.path.exists(self.path_db):
            return pd.read_csv(self.path_db, sep="\t")
        else:
            return None
        
    def save_db(self):
        """Save data base
        """
        self.db.to_csv(self.path_db, sep="\t", index=False)     