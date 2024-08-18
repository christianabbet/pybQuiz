from pybquiz.api_handler.base import BaseAPIHandler
from typing import Union, List
import numpy as np
from tqdm import tqdm
from pybquiz.elements import Questions
import hashlib
import html
import os
import urllib
import pandas as pd


class JeopardyUS(BaseAPIHandler):

    # URLS
    URL_JEOPARDY = "https://raw.githubusercontent.com/jwolle1/jeopardy_clue_dataset/main/combined_season1-40.tsv"
    COL_CAT = "category"
    COL_CAT_ID = "category_id"
    COL_CLUE = "clue_value"
    COL_DIFF = "difficulty"
    COL_DIFF_TXT = "difficulty_txt"
    DB_NAME = "jeopardy.tsv"
    EASY_THRESH = 400
    HARD_THRESH = 1200
    
    def __init__(
        self,
        delay_api: int = 5,
        verbose: bool = True,
        clear_cache: bool = False,
        token: str = None,
        cat_thresh=1000,
    ) -> None:
        """
        
        Create API handler to https://opentdb.com/

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
        self.cat_thresh = cat_thresh
        super().__init__(verbose=verbose, delay_api=delay_api, clear_cache=clear_cache, qtype="Open")
        self.token = token
        self.path_db = os.path.join(self.cache_dir, self.DB_NAME)
        self.db = pd.read_csv(self.path_db, sep="\t", index_col=0)

    def _download_db(self):
        
        db_file = os.path.join(self.cache_dir, self.DB_NAME)
        # Check if file exists
        if not os.path.exists(db_file):
            # Otherwise download it
            urllib.request.urlretrieve(self.URL_JEOPARDY, db_file)
        return db_file
        

    def initialize_db(self) -> Union[List[str], List[int], np.ndarray, np.ndarray]:
        """
        Initialize database infromation

        Returns
        -------
        categories : List[str]
            List of N categories as strings.
        categories_id : List[int]
            List of N categories as ints.
        categories_type : np.ndarray
            Array of N categories 2 types ("text", "image")            
        categories_difficulty : np.ndarray
            Array of N categories and 3 difficulty level ("easy", "medium", "hard")
        """
        
        # Get main infos
        path_db = self._download_db()
        
        # Read tsv with pandas
        self.db = pd.read_csv(path_db, sep="\t")
        
        # Get categories abve threshold
        df_cats = self.db["category"].value_counts()
        df_cats = df_cats[df_cats > self.cat_thresh]
        # Filter names
        df_cats = [v in df_cats for v in self.db["category"].values]
        self.db = self.db[(df_cats) & (self.db["clue_value"] != 0).values]
        self.db[self.COL_CAT] = self.db[self.COL_CAT].str.title()
        # Set difficulty to medium
        # Easy:     100, 200, 300, 400
        # Medium:   500, 600, 800, 1000
        # Hard :    1200, 1600, 2000,
        self.db[self.COL_DIFF] = -1
        self.db.loc[(self.db[self.COL_CLUE] <= self.EASY_THRESH), self.COL_DIFF] = 0
        self.db.loc[(self.db[self.COL_CLUE] > self.EASY_THRESH) & (self.db[self.COL_CLUE] < self.HARD_THRESH), self.COL_DIFF] = 1
        self.db.loc[(self.db[self.COL_CLUE] >= self.HARD_THRESH), self.COL_DIFF] = 2
        size = self.db.groupby([self.COL_CAT, self.COL_DIFF]).size().reset_index()
        size = size.pivot(index=self.COL_CAT, columns=self.COL_DIFF, values=0)
        size.sort_index(inplace=True)
        
        # Filter out missing
        categories_name = size.index.tolist()
        categories_id = list(range(len(categories_name)))
        categories_difficulty = size.values
        categories_type= np.zeros_like(categories_difficulty)
        categories_type[:, 0] = categories_difficulty.sum(axis=1)
        cat_to_id = {k: v for k, v in zip(categories_name, categories_id)}
    
        # Override tsv
        self.db[self.COL_CAT_ID] = self.db[self.COL_CAT].replace(cat_to_id)
        self.db.to_csv(path_db, sep='\t')

        # Retreive categories
        return categories_name, categories_id, categories_type, categories_difficulty

    def get_questions(self, n: int, category_id: int = None, difficulty: int = None, type: str = None) -> List[Questions]:

        # Create query dict (if None then consider any)
        is_valid = np.ones(len(self.db)).astype(bool)
        
        if category_id is not None:
            is_valid = is_valid & (category_id == self.db[self.COL_CAT_ID])
        # Check category
        if difficulty is not None:
            is_valid = is_valid & (difficulty == self.db[self.COL_DIFF])

        # Send query
        question_ids = np.random.permutation(np.nonzero(is_valid)[0])[:n]
                        
        # Parse results as questions
        questions = []
        # cat_id_lut = np.argmax(self.categories_id == category_id)
        for question_id in question_ids:
            # Parse question
            q_text = self.db.iloc[question_id]["answer"]
            c_answers = self.db.iloc[question_id]["question"]
            i_answers = []
            q = Questions(
                question=q_text,
                correct_answers=[c_answers],
                incorrect_answers=i_answers,
                library=self.__class__.__name__.lower(), 
                category=self.db.iloc[question_id][self.COL_CAT],
                category_id=int(self.db.iloc[question_id][self.COL_CAT_ID]),
                uuid=hashlib.md5(q_text.encode('utf8')).hexdigest(),
                difficulty=difficulty,
                type="text",
            )
            questions.append(q)
            
        return questions