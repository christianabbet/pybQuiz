from pybquiz.api_handler.base import BaseAPIHandler
from typing import Union, List
import numpy as np
from tqdm import tqdm
from pybquiz.elements import Questions
import hashlib


class QuizAPI(BaseAPIHandler):

    
    URL_CATEGORIES = "https://quizapi.io/api/v1/categories"
    URL_QUESTIONS = "https://quizapi.io/api/v1/questions"
    
    KEY_TOKEN = "X-Api-Key"
    KEY_ID = "id"
    KEY_NAME = "name"
    KEY_AMOUNT = "limit"
    KEY_CAT = "category"
    KEY_DIFFICULTY = "difficulty"
    KEY_R_ERROR = "error"
    KEY_QUESTION = "question"
    KEY_IS_CORRECT = "correct_answers"
    KEY_ANSWER = "answers"
    
    LUT_DIFFICULTY = {
        0: "easy",
        1: "medium",
        2: "hard",
    }
    
    def __init__(
        self,
        token: str,
        delay_api: int = 5,
        verbose: bool = True,
        clear_cache: bool = False,
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
        super().__init__(verbose=verbose, delay_api=delay_api, clear_cache=clear_cache, qtype="MCQ")
                
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
        
        # Set token
        header = {self.KEY_TOKEN: self.token}
        
        # Get main infos
        result = self.slow_request_urllib3(self.URL_CATEGORIES, header=header)        
        N = len(result) 
        
        categories_name = [item.get(self.KEY_NAME, "") for item in result]
        categories_id = [item.get(self.KEY_ID, -1) for item in result]
        categories_difficulty = -1 * np.ones((N, 3))
        categories_type= -1 * np.ones((N, 2))
        categories_type[:, 1] = 0
        
        # Retreive categories
        return categories_name, categories_id, categories_type, categories_difficulty

    def get_questions(self, n: int, category_id: int = None, difficulty: int = None, type: str = None) -> List[Questions]:

        # Create query dict (if None then consider any)
        header = {self.KEY_TOKEN: self.token}
        params = {self.KEY_AMOUNT: n}
        # Check category
        if category_id is not None:
            cat_id_lut = np.argmax(self.categories_id == category_id)
            params[self.KEY_CAT] = self.categories[cat_id_lut]
        # Check category
        if difficulty is not None:
            params[self.KEY_DIFFICULTY] = self.LUT_DIFFICULTY[difficulty]
            
        # Get question
        result = self.slow_request_httpclient(url=self.URL_QUESTIONS, header=header, params=params)
        
        # Check if answer is correct
        if self.KEY_R_ERROR in result:
            if self.verbose:
                print("Error in API: {}".format(result))
            return []
        
        # Parse results as questions
        questions = []
        for raw_question in result:
            # Make sur category is correct
            cat = raw_question.get(self.KEY_CAT, self.KEY_R_ERROR)
            keys_q = raw_question.get(self.KEY_IS_CORRECT, self.KEY_R_ERROR)
            qs = raw_question.get(self.KEY_ANSWER, self.KEY_R_ERROR)
            
            # Parse answer and split correct and incorrect
            keys_corr = [k.replace("_correct", "") for k, v in keys_q.items() if v == "true"]
            keys_incorr = [k.replace("_correct", "") for k, v in keys_q.items() if v == "false"]
            # Get questions
            q_corr = [v for q, v in qs.items() if q in keys_corr]
            q_incorr = [v for q, v in qs.items() if q in keys_incorr and v is not None]
            
            q = Questions(
                question=raw_question.get(self.KEY_QUESTION, self.KEY_R_ERROR),
                correct_answers=q_corr,
                incorrect_answers=q_incorr,
                library=self.__class__.__name__.lower(), 
                category=cat,
                category_id=int(self.categories_id[np.argmax(self.categories == cat)]),
                uuid=raw_question.get(self.KEY_ID, self.KEY_R_ERROR),
                difficulty=difficulty,
                type="text",
            )
            # Append question
            questions.append(q)           
            
        return questions