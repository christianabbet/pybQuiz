from pybquiz.api_handler.base import BaseAPIHandler
from typing import Union, List
import numpy as np
from tqdm import tqdm
from pybquiz.elements import Questions
import hashlib
import html


class OpenTriviaDB(BaseAPIHandler):

    # URLS
    URL_CATEGORY = "https://opentdb.com/api_category.php"
    URL_CATEGORY_COUNT = "https://opentdb.com/api_count.php"
    URL_QUESTION = "https://opentdb.com/api.php"
    
    KEY_TRIVIA_CAT = "trivia_categories"
    KEY_NAME = "name"
    KEY_ID = "id"
    KEY_CAT = "category"
    KEY_RESULTS = "results"
    KEY_DIFFICULTY = "difficulty"  
    KEY_TOKEN = "token"  
    KEY_AMOUNT = "amount"      

    # Keys for categories and counts
    KEY_Q_COUNT = "category_question_count"
    KEY_Q_TOTAL_COUNT = "total_question_count"
    KEY_Q_EASY_COUNT = "total_easy_question_count"
    KEY_Q_MEDIUM_COUNT = "total_medium_question_count"
    KEY_Q_HARD_COUNT = "total_hard_question_count"            
           
    # Key for quesiton requests
    KEY_R_TYPE = "type"
    KEY_R_ERROR = "error"
    KEY_R_DIFF = "difficulty"
    KEY_R_CAT = "category"
    KEY_R_QUESTION = "question"
    KEY_R_CORRECT = "correct_answer"
    KEY_R_INCORRECT = "incorrect_answers"
                
    LUT_DIFFICULTY = {
        0: "easy",
        1: "medium",
        2: "hard",
    }
    
    def __init__(
        self,
        delay_api: int = 5,
        verbose: bool = False,
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
        super().__init__(verbose=verbose, delay_api=delay_api, clear_cache=clear_cache)
        self.token = token
                
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
        result = self.slow_request_urllib3(self.URL_CATEGORY)
        result = result.get(self.KEY_TRIVIA_CAT, {})
        
        N = len(result)
        categories_name = [item.get(self.KEY_NAME, "") for item in result]
        categories_id = [item.get(self.KEY_ID, -1) for item in result]
        categories_difficulty = np.zeros((N, 3))
        categories_type= np.zeros((N, 2))
        
        for i in tqdm(np.arange(N), disable=(not self.verbose)):
            # Get category specific stats            
            result_cat = self.slow_request_urllib3(url=self.URL_CATEGORY_COUNT, params={self.KEY_CAT: categories_id[i]})
            result_cat = result_cat.get(self.KEY_Q_COUNT, {})
            # Extract counts
            n_tot = result_cat.get(self.KEY_Q_TOTAL_COUNT, 0)
            n_easy = result_cat.get(self.KEY_Q_EASY_COUNT, 0)
            n_medium = result_cat.get(self.KEY_Q_MEDIUM_COUNT, 0)
            n_hard = result_cat.get(self.KEY_Q_HARD_COUNT, 0)
            # Sanity check
            assert n_tot == n_easy + n_medium + n_hard
            # Affect variable
            categories_difficulty[i] = [n_easy, n_medium, n_hard]
            categories_type[i] = [n_tot, 0]

        # Retreive categories
        return categories_name, categories_id, categories_type, categories_difficulty

    def get_questions(self, n: int, category_id: int = None, difficulty: int = None, type: str = None) -> List[Questions]:

        # Create query dict (if None then consider any)
        params = {self.KEY_AMOUNT: n}
        # Check category
        if category_id is not None:
            params[self.KEY_CAT] = category_id
        # Check category
        if difficulty is not None:
            params[self.KEY_DIFFICULTY] = self.LUT_DIFFICULTY[difficulty]
        # Check session token
        if self.token is not None:
            params[self.KEY_TOKEN] = self.token
            
        # Send query
        result = self.slow_request_urllib3(url=self.URL_QUESTION, params=params)
        
        # Check if answer is correct
        if self.KEY_R_ERROR in result:
            if self.verbose:
                print("Error in API: {}".format(result))
            return []
                
        # Parse results as questions
        questions = []
        cat_id_lut = np.argmax(self.categories_id == category_id)
        for raw_question in result.get(self.KEY_RESULTS, []):
            # Parse question
            q_text = html.unescape(raw_question.get(self.KEY_R_QUESTION, self.KEY_R_ERROR))
            c_answers = html.unescape(raw_question.get(self.KEY_R_CORRECT, self.KEY_R_ERROR))
            i_answers = [html.unescape(a) for a in raw_question.get(self.KEY_R_INCORRECT, [])]
            q = Questions(
                question=q_text,
                correct_answers=[c_answers],
                incorrect_answers=i_answers,
                library=self.__class__.__name__.lower(), 
                category=self.categories[cat_id_lut],
                category_id=category_id,
                uuid=hashlib.md5(q_text.encode('utf8')).hexdigest(),
                difficulty=difficulty,
                type="text",
            )
            questions.append(q)
            
        return questions