# from pybquiz.api_handler.base import BaseAPIHandler
# from typing import Union, List
# import numpy as np
# from tqdm import tqdm
# from pybquiz.elements import Questions
# import hashlib


from pybquiz.db.base import TriviaTSVDB, TriviaQ

import os
from typing import Optional, Literal
import urllib
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
import json
from tqdm import tqdm
import numpy as np
from pybquiz.db.utils import slow_get_request, to_uuid
import html
from rich.prompt import Prompt


class NinjaDBKey:
    
    KEY_CATEGORY = "category"
    KEY_QUESTION = "question"
    KEY_CORRECT_ANSWER = "correct_answer"
    KEY_UUID = "uuid"

    URL_KEY_QUESTION = "question"
    URL_KEY_CATEGORY = "category"
    URL_KEY_ANSWER = "answer"
    URL_KEY_TOKEN = "X-Api-Key"
    URL_QUESTION = "https://api.api-ninjas.com/v1/trivia"

    CATEGORIES = [
        "artliterature",
        "language",
        "sciencenature",
        "general",
        "fooddrink",
        "peopleplaces",
        "geography",
        "historyholidays",
        "entertainment",
        "toysgames",
        "music",
        "mathematics",
        "religionmythology",
        "sportsleisure",
    ]

class NinjaAPI(TriviaTSVDB):
        
    def __init__(
        self, 
        cache: Optional[str] = '.cache',         
        filename_db: Optional[str] = "ninjaapi",
        n_try: Optional[int] = 10,
        n_max: Optional[int] = 500,
        chunks: Optional[int] = 10,
    ) -> None:
        """Who wnats to be a millionaire database

        Parameters
        ----------
        cache : Optional[str], optional
            Location of the database, by default '.cache'
        chunk: Optional[int], optional
            Size of the chunks to query to external db, by default 50
        filename_db : Optional[str], optional
            Name of the database, by default "jeopardy"
        """
                
        # Define online scrapper
        self.n_try = n_try
        self.n_max = n_max
        self.chunks = chunks
        super().__init__(
            cache=cache, 
            update=False,
            path_db=os.path.join(cache, filename_db + ".tsv")
        )
        
        # Path to token
        self.token_path = os.path.join(cache, filename_db + ".key")
        
        # Check if token exists
        if not os.path.exists(self.token_path):
            # Ask for token
            self.token = Prompt.ask("Enter API Token")
            # Ask if store for next time
            store = Prompt.ask("Store API Token", default="yes")
            if 'y' in store[0].lower():
                # Store key
                f = open(self.token_path, "w+")
                f.write(self.token)
                f.close()
        else:
            f = open(self.token_path, "r")
            self.token = f.read()
            f.close() 
            
    def initialize(self):
        return pd.DataFrame(
            columns=[
                NinjaDBKey.KEY_CATEGORY, NinjaDBKey.KEY_QUESTION,  
                NinjaDBKey.KEY_CORRECT_ANSWER, NinjaDBKey.KEY_UUID,
            ]
        )
        
                          
    def update(self):
        
        # Header
        header = {NinjaDBKey.URL_KEY_TOKEN: self.token}
        
        # Check category
        n_cat = len(NinjaDBKey.CATEGORIES)
        rnd_cat = np.random.permutation(NinjaDBKey.CATEGORIES)
        for n, c in enumerate(rnd_cat):
            
            # Progress
            print("[{}/{}]: {}".format(n+1, n_cat, c))
            # Check for duplicates
            n_category_try = 0
            params = {NinjaDBKey.URL_KEY_CATEGORY: c}
            
            # Send reuqesuts
            for i in tqdm(range(self.n_max)):
            
                # Check max tries
                if n_category_try >= self.n_try:
                    break
                
                # Request
                result = slow_get_request(url=NinjaDBKey.URL_QUESTION, header=header, params=params)
                if result is None: 
                    return 
                
                # Extract parameters
                result = json.loads(result.text)
                question = result[0].get(NinjaDBKey.URL_KEY_QUESTION, None)
                uuid = to_uuid(question)
                
                if uuid in self.db[NinjaDBKey.KEY_UUID].values:
                    n_category_try += 1
                    continue
                
                data = pd.DataFrame([{
                    NinjaDBKey.KEY_QUESTION: question,
                    NinjaDBKey.KEY_CORRECT_ANSWER: result[0].get(NinjaDBKey.URL_KEY_ANSWER, None),
                    NinjaDBKey.KEY_CATEGORY: result[0].get(NinjaDBKey.URL_KEY_CATEGORY, None),
                    NinjaDBKey.KEY_UUID: uuid,
                }])
                
                self.db = pd.concat([self.db, data], ignore_index=True)
                
                if (i % self.chunks) == 0:
                    self.save()
            
            # Save
            self.save()


    def pprint(self):
        
        pass
        # Define name
        # name = self.__class__.__name__        
        # df_print = pd.crosstab(index=self.db[OTDBKey.KEY_CATEGORY], columns=self.db[OTDBKey.KEY_DIFFICULTY])

        # # Group by categories and create df
        # data_all = {OTDBKey.KEY_CATEGORY: "All"}
        # data_all.update(df_print.sum().to_dict())
        # # Add all other values
        # data = [data_all]
        # for _, d in df_print.reset_index().iterrows():
        #     data.append(d.to_dict())
        
        # # Display final output
        # console = Console() 
        # console.print(Panel.fit("Database {}".format(name)))
        
        # markdown = markdown_table(data).set_params(row_sep = 'markdown')
        # markdown.quote = False
        # markdown = markdown.get_markdown()
        # console.print(markdown)
        
        
    def __getitem__(self, index: int):
        
        # Get row
        serie = self.db.iloc[index]
        
        data = {
            TriviaQ.KEY_QUESTION: serie[NinjaDBKey.KEY_QUESTION],
            TriviaQ.KEY_CATEGORY: serie[NinjaDBKey.KEY_CATEGORY],
            TriviaQ.KEY_UUID: serie[NinjaDBKey.KEY_UUID],
        }
    
        return data
