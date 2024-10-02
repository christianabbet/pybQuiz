from pybquiz.db.base import TriviaDB    
from pybquiz.const import FamilyFeudConst as FC
from pybquiz.db.utils import to_uuid

import pandas as pd
import os
from typing import Optional
from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table


class FamilyFeudDB(TriviaDB):  
    
    DOC_ID = "1y5TtM4rXHfv_9BktCiJEW621939RzJucXxhJidJZbfQ"
    SHEEDS_IDS = ["1784297399", "796551874", "1842874377", "65377693", "1151340645"]
    COL_QUESTION = "Question"
    def __init__(
        self, 
        filename_db: Optional[str] = "familyfeud",
        cache: Optional[str] = '.cache', 
        ext: Optional[str] = '.tsv', 
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
        self.path_db = os.path.join(cache, filename_db + ext)
                    
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
        return len(self.db)
        
    def initialize(self) -> pd.DataFrame:
        return pd.DataFrame(
            columns=[
                # Mandatory keys
                FC.KEY_UUID,
                FC.KEY_QUESTION,
                FC.KEY_CATEGORY,
                FC.KEY_ANSWER1,
                FC.KEY_ANSWER1_VALUE,
                FC.KEY_ANSWER2,
                FC.KEY_ANSWER2_VALUE,
                FC.KEY_ANSWER3,
                FC.KEY_ANSWER3_VALUE,
                FC.KEY_ANSWER4,
                FC.KEY_ANSWER4_VALUE,
                FC.KEY_ANSWER5,
                FC.KEY_ANSWER5_VALUE,
                FC.KEY_ANSWER6,
                FC.KEY_ANSWER6_VALUE,
                FC.KEY_ANSWER7,
                FC.KEY_ANSWER7_VALUE,
            ]
        )            
    def update(self):
               
        # Build URLs and query data
        n_sheets = len(self.SHEEDS_IDS)
        dfs = []
        for i in tqdm(range(n_sheets), desc="Download sheets ..."):
            sheet_url = self._build_sheet_url(self.DOC_ID, self.SHEEDS_IDS[i])
            # Get dataframe
            df = pd.read_csv(sheet_url)
            # Remove nans
            df.dropna(axis=0, how="any", inplace=True)
            # Apply uuid
            df[FC.KEY_UUID] = df[self.COL_QUESTION].apply(to_uuid)
            dfs.append(df)

        # Concatenate dataframes
        dfs = pd.concat(dfs, ignore_index=True)
        dfs.columns = [c.lower().replace(" ", "") for c in dfs.columns]

        # Post processing - number of questions
        col_answer = [c for c in dfs.columns if c.startswith("answer")]
        dfs[FC.KEY_N_ANSWER] = dfs[col_answer].notnull().sum(axis=1)
        dfs[FC.KEY_CATEGORY] = "Top " + dfs[FC.KEY_N_ANSWER].astype(str)
         

        # Affect final result
        self.db = dfs.loc[:, self.db.columns]
        self.db[FC.KEY_NAME] = self.__class__.__name__
        self.save()
        
    def pprint(self):
        
        name = self.__class__.__name__  
        # Check if categor exists

        df_print = pd.crosstab(
            index=self.db[FC.KEY_CATEGORY], 
            columns=self.db[FC.KEY_NAME]
        )
        df_print.columns = [str(c) for c in df_print.columns]

        # Add all other values
        data = []
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
        return data
    
    @staticmethod
    def _build_sheet_url(doc_id: str, sheet_id: str):
        return 'https://docs.google.com/spreadsheets/d/{}/export?format=csv&gid={}'.format(doc_id, sheet_id)