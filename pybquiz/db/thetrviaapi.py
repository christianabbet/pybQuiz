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


class TTAPIKey:
    
    # KEY_DIFFICULTY = "difficulty"
    # KEY_CATEGORY = "category"
    # KEY_QUESTION = "question"
    # KEY_CORRECT_ANSWER = "correct_answer"
    # KEY_WRONG_ANSWER_1 = "wrong_answers_1"
    # KEY_WRONG_ANSWER_2 = "wrong_answers_2"
    # KEY_WRONG_ANSWER_3 = "wrong_answers_3"
    # KEY_UUID = "uuid"
    
    KEY_TAGS = "tags"
    KEY_IS_NICHE = "isNiche"
    
    URL_KEY_ID = "id"
    URL_KEY_TAGS = "tags"
    URL_KEY_CATEGORY = "category"
    URL_KEY_CORRECT_ANSWER = "correctAnswer"
    URL_KEY_INCORRECT = "incorrectAnswers"
    URL_KEY_QUESTION = "question"
    URL_KEY_DIFFICULTY = "difficulty"
    URL_IS_NICHE = "isNiche"
    URL_KEY_TRIVIA_TYPE = "byType"
    URL_KEY_TRIVIA_TEXT = "text_choice"
    URL_KEY_R_LIMIT = "limit"
    
    URL_CATEGORY = "https://the-trivia-api.com/v2/metadata"
    URL_QUESTION = "https://the-trivia-api.com/v2/questions"


class TheTriviaAPIDB(TriviaTSVDB):
            
    def __init__(
        self, 
        cache: Optional[str] = '.cache',
        filename_db: Optional[str] = "thetriviaapi",
        chunk: Optional[int] = 50,
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
        self.chunk = chunk
        
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + ".tsv")
        )
        
             
    def initialize(self):
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
                # Others
                TTAPIKey.KEY_TAGS,
                TTAPIKey.KEY_IS_NICHE, 
            ]
        )

    
    def update(self):
        
        # Get existing categories
        result = slow_get_request(TTAPIKey.URL_CATEGORY)
        # If code not valid return None
        if result is None: 
            return 
        
        # Get all available categories
        types = json.loads(result.text).get(TTAPIKey.URL_KEY_TRIVIA_TYPE, {})
        n_type_text = types.get(TTAPIKey.URL_KEY_TRIVIA_TEXT, -1)
 
        # Run data scrapping on new set
        n_update = np.ceil(n_type_text / self.chunk).astype(int)
        for _ in tqdm(range(n_update), "Update database"):
            # Send request                
            result = slow_get_request(
                TTAPIKey.URL_QUESTION, 
                params={TTAPIKey.URL_KEY_R_LIMIT: self.chunk},
            )
            
            # Failed continue to next
            if result is None: 
                continue
            
            # Parse results
            df_chunk = pd.DataFrame(self.parse_questions(api_result=json.loads(result.text)))
            self.db = pd.concat([self.db, df_chunk], ignore_index=True)

        # Convert to dataframe and merge
        self.db.drop_duplicates(subset=TriviaQ.KEY_UUID, keep="first", inplace=True)
        self.save()        
        
    @staticmethod
    def parse_questions(api_result: dict):
        data = []
        for q in api_result:
            # Get infos
            data_row = {
                TriviaQ.KEY_CATEGORY: q.get(TTAPIKey.URL_KEY_CATEGORY, ""), 
                TriviaQ.KEY_DIFFICULTY: q.get(TTAPIKey.URL_KEY_DIFFICULTY, ""), 
                TTAPIKey.KEY_TAGS: q.get(TTAPIKey.URL_KEY_TAGS, ""),
                TTAPIKey.KEY_IS_NICHE: q.get(TTAPIKey.URL_IS_NICHE, ""), 
                TriviaQ.KEY_QUESTION: q.get(TTAPIKey.URL_KEY_QUESTION, {}).get("text", ""), 
                TriviaQ.KEY_CORRECT_ANSWER: q.get(TTAPIKey.URL_KEY_CORRECT_ANSWER, None), 
                TriviaQ.KEY_WRONG_ANSWER1: q.get(TTAPIKey.URL_KEY_INCORRECT, [None]*3)[0], 
                TriviaQ.KEY_WRONG_ANSWER2: q.get(TTAPIKey.URL_KEY_INCORRECT, [None]*3)[1],
                TriviaQ.KEY_WRONG_ANSWER3: q.get(TTAPIKey.URL_KEY_INCORRECT, [None]*3)[2],
                TriviaQ.KEY_UUID: q.get(TTAPIKey.URL_KEY_ID, None),            
            }

            # APpend to row
            data.append(data_row)
        # Return parsed data
        return data
