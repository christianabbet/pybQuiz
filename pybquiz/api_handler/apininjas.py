from pybquiz.api_handler.base import BaseAPIHandler
from typing import Union, List
import numpy as np
from tqdm import tqdm
from pybquiz.elements import Questions
import hashlib


class APINinjas(BaseAPIHandler):

    
    KEY_CAT = "category"
    KEY_TOKEN = "X-Api-Key"
    URL_QUESTION = "https://api.api-ninjas.com/v1/trivia"

    KEY_R_ERROR = "error"
    KEY_R_CAT = "category"
    KEY_R_QUESTION = "question"
    KEY_R_ANSWER = "answer"
    
    # Hard coded :(
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
    
    def __init__(
        self,
        delay_api: int = 5,
        verbose: bool = True,
        clear_cache: bool = False,
        token: str = None,
    ) -> None:
        """
        
        Create API handler to https://opentdb.com/

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
        
        # Key is needed for this api
        if token is None:
            raise NotImplementedError()
        
        self.token = token
        super().__init__(verbose=verbose, delay_api=delay_api, clear_cache=clear_cache, qtype="Open")
                
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
        N = len(self.CATEGORIES) 
        
        categories_name = self.CATEGORIES
        categories_id = np.arange(N)
        categories_difficulty = -1 * np.ones((N, 3))
        categories_type= -1 * np.ones((N, 2))
        categories_type[:, 1] = 0
        
        # Retreive categories
        return categories_name, categories_id, categories_type, categories_difficulty
    
    def get_questions(self, n: int, category_id: int = None, difficulty: int = None, type: str = None) -> List[Questions]:

        params = {}
        header = {}
        
        # Check category
        if category_id is not None:
            params[self.KEY_CAT] = self.categories[category_id]
        # Check session token
        if self.token is not None:
            header[self.KEY_TOKEN] = self.token
                        
        # Create query dict (if None then consider any)
        questions = []
        for i in range(n):
            # Send request
            result = self.slow_request_urllib3(url=self.URL_QUESTION, header=header, params=params)[0]
            q_text = result.get(self.KEY_R_QUESTION, self.KEY_R_ERROR)
            # Create question
            q = Questions(
                question=q_text,
                correct_answers=[result.get(self.KEY_R_ANSWER, self.KEY_R_ERROR)],
                incorrect_answers=[],
                library=self.__class__.__name__.lower(), 
                category=result.get(self.KEY_R_CAT, self.KEY_R_ERROR),
                category_id=category_id,
                uuid=hashlib.md5(q_text.encode('ascii')).hexdigest(),
                difficulty=None,
                type="text",
            )
            questions.append(q)

            
        return questions