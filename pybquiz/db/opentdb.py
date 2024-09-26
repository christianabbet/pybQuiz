from pybquiz.db.base import TriviaTSVDB

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
from pybquiz.const import TriviaConst as TC


class OTDBKey:
        
    KEY_CATEGORY_ID = "category_id"
    KEY_TYPE = "type"
    KEY_TYPE_MULIPLE = "multiple"
    
    URL_KEY_ID = "id"
    URL_KEY_NAME = "name"
    URL_KEY_TRIVIA_CATEGORY = "trivia_categories"
    URL_KEY_CATEGORY = "category"
    URL_KEY_CATEGORY_COUNT = "category_question_count"
    URL_KEY_QUESTION_COUNT = "total_question_count"
    URL_KEY_TOKEN = "token"
    URL_KEY_AMOUNT = "amount"
    URL_KEY_RESULT = "results"
    URL_KEY_QUESTION = "question"
    URL_KEY_CORRECT_ANSWER = "correct_answer"
    URL_KEY_INCORRECT = "incorrect_answers"
            
    URL_CATEGORY = "https://opentdb.com/api_category.php"
    URL_CATEGORY_COUNT = "https://opentdb.com/api_count.php"
    URL_TOKEN = "https://opentdb.com/api_token.php?command=request"
    URL_QUESTION = "https://opentdb.com/api.php"


class OpenTriviaDB(TriviaTSVDB):
        
    def __init__(
        self, 
        cache: Optional[str] = '.cache',         
        filename_db: Optional[str] = "opentdb",
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
                TC.KEY_UUID, 
                TC.KEY_CATEGORY, 
                TC.KEY_DIFFICULTY, 
                TC.KEY_QUESTION, 
                TC.KEY_CORRECT_ANSWER, 
                TC.KEY_WRONG_ANSWER1, 
                TC.KEY_WRONG_ANSWER2, 
                TC.KEY_WRONG_ANSWER3, 
                # Others
                OTDBKey.KEY_TYPE,   
                OTDBKey.KEY_CATEGORY_ID,
            ]
        )
                          
    def update(self):
        
        # Get existing categories
        result = slow_get_request(OTDBKey.URL_CATEGORY)
        # If code not valid return None
        if result is None: 
            return 
        
        # Get all available categories
        categories = json.loads(result.text).get(OTDBKey.URL_KEY_TRIVIA_CATEGORY, [])
        
        # Get number of questions per category 
        categories_metadata = []
        for cat in tqdm(categories):
            # Get cat id and number of questions
            cat_id = cat.get(OTDBKey.URL_KEY_ID, -1)
            result = slow_get_request(OTDBKey.URL_CATEGORY_COUNT, params={OTDBKey.URL_KEY_CATEGORY:cat_id })
            if result is None: 
                continue 
            # Convert results
            metadata = json.loads(result.text).get(OTDBKey.URL_KEY_CATEGORY_COUNT, {})
            n_remote_question = metadata.get(OTDBKey.URL_KEY_QUESTION_COUNT, 0)
            n_local_question = len(self.db[self.db[OTDBKey.KEY_CATEGORY_ID] == cat_id])

            # Check if new questions
            if n_remote_question <= n_local_question:
                continue
            
            # Append to list to fetch
            categories_metadata.append({
                OTDBKey.KEY_CATEGORY_ID: cat_id,
                OTDBKey.URL_KEY_QUESTION_COUNT: n_remote_question,
            })
                    
        # Check if need to update
        if len(categories_metadata) == 0:
            # No need to upadate DB
            return
        
        # Get token
        result = slow_get_request(OTDBKey.URL_TOKEN)
        if result is None: 
            return 
        token = json.loads(result.text).get(OTDBKey.URL_KEY_TOKEN, "")
        
        # Run data scrapping on new set
        n_update = len(categories_metadata)
        for i, m in enumerate(categories_metadata):
            n_update_cat = np.ceil(m[OTDBKey.URL_KEY_QUESTION_COUNT] / self.chunk).astype(int)
            # Get all chunks
            for i in tqdm(range(n_update_cat), "Update categories [{}/{}]".format(i+1, n_update)):
                # Send request                
                result = slow_get_request(
                    OTDBKey.URL_QUESTION, 
                    params={
                        OTDBKey.URL_KEY_AMOUNT: self.chunk, 
                        OTDBKey.URL_KEY_CATEGORY: m[OTDBKey.KEY_CATEGORY_ID],
                        OTDBKey.URL_KEY_TOKEN: token,
                    },
                )
                # Failed continue to next
                if result is None: 
                    break
                # Parse results
                df_chunk = pd.DataFrame(self.parse_questions(api_result=json.loads(result.text)))
                df_chunk[OTDBKey.KEY_CATEGORY_ID] = m[OTDBKey.KEY_CATEGORY_ID]
                self.db = pd.concat([self.db, df_chunk], ignore_index=True)

        # Convert to dataframe and merge
        self.db.drop_duplicates(subset=TC.KEY_UUID, keep="first", inplace=True)
        self.save()        
        
    @staticmethod
    def parse_questions(api_result: dict):
        data = []
        for q in api_result[OTDBKey.URL_KEY_RESULT]:
            # Get infos
            question_str = html.unescape(q.get(OTDBKey.URL_KEY_QUESTION, ""))
            question_type = q.get(OTDBKey.KEY_TYPE, "")
            data_row = {
                OTDBKey.KEY_TYPE: question_type, 
                TC.KEY_DIFFICULTY: q.get(TC.KEY_DIFFICULTY, ""),  
                TC.KEY_CATEGORY: html.unescape(q.get(TC.KEY_CATEGORY, "")),
                TC.KEY_QUESTION: question_str,
                TC.KEY_CORRECT_ANSWER: html.unescape(q.get(OTDBKey.URL_KEY_CORRECT_ANSWER, "")),  
                TC.KEY_WRONG_ANSWER1: html.unescape(q.get(OTDBKey.URL_KEY_INCORRECT, [None]*3)[0]),  
                TC.KEY_UUID: to_uuid(question_str),                
            }
            # Check if muliple of true / false
            if question_type == OTDBKey.KEY_TYPE_MULIPLE:
                data_row[TC.KEY_WRONG_ANSWER2] = html.unescape(q.get(OTDBKey.URL_KEY_INCORRECT, [None]*3)[1])
                data_row[TC.KEY_WRONG_ANSWER3] = html.unescape(q.get(OTDBKey.URL_KEY_INCORRECT, [None]*3)[2])
            # APpend to row
            data.append(data_row)
        # Return parsed data
        return data
    