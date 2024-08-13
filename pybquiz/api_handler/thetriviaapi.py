from pybquiz.api_handler.base import BaseAPIHandler
from pybquiz.elements import Questions
from typing import Union, List
import numpy as np
from tqdm import tqdm


class TheTriviaAPI(BaseAPIHandler):

    URL_CATEGORY = "https://the-trivia-api.com/v2/metadata"
    URL_QUESTION = "https://the-trivia-api.com/v2/questions"
    
    KEY_BY_CAT = "byCategory"
    KEY_BY_DIFF = "byDifficulty"
    KEY_BY_TYPE = "byType"
    KEY_CAT = "categories"
    KEY_TYPE_TXT = "text_choice"
    KEY_TYPE_IMG = "image_choice"
    KEY_DIFF_EASY = "easy"
    KEY_DIFF_MEDIUM = "medium"
    KEY_DIFF_HARD = "hard"
    KEY_TOKEN = "X-API-Key"
    KEY_TEXT = "text"
    
    # Query for request
    KEY_R_LIMIT = "limit"
    KEY_R_CAT = "categories"
    KEY_R_DIFF = "difficulties"  
    KEY_R_TYPES = "types"
    KEY_R_LANG = "language"
    KEY_R_ENGLISH = "en"
    KEY_R_ID = "id"
    KEY_R_QUESTION = "question"
    KEY_R_ERROR = "error"
    KEY_R_CORRECT = "correctAnswer"
    KEY_R_INCORRECT = "incorrectAnswers"
    
    LUT_DIFFICULTY = {
        0: "easy",
        1: "medium",
        2: "hard",
    }
    LUT_TYPE = {
        "text": "text_choice",
        "image": "image_choice",
    }
        
    def __init__(
        self,
        delay_api: int = 5,
        token: str = None,
        verbose: bool = True,
        clear_cache: bool = False,
    ) -> None:
        """
        Create API handler to https://the-trivia-api.com

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
        
        self.token = token
        super().__init__(verbose=verbose, delay_api=delay_api, clear_cache=clear_cache)
                
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
        result = result.get(self.KEY_BY_CAT, {})
        
        # Get all categories
        N = len(result)
        categories_name = sorted(result.keys())
        categories_id = np.arange(len(categories_name))
        categories_difficulty = np.zeros((N, 3))
        categories_type= np.zeros((N, 2))
        
        for i in tqdm(np.arange(N), disable=(not self.verbose)):
            # Get category specific stats
            result_cat = self.slow_request_urllib3(url=self.URL_CATEGORY, params={self.KEY_CAT: categories_name[i]})
            result_diff = result_cat.get(self.KEY_BY_DIFF, {})
            result_type = result_cat.get(self.KEY_BY_TYPE, {})
            # Extract counts            
            n_easy = result_diff.get(self.KEY_DIFF_EASY, 0)
            n_medium = result_diff.get(self.KEY_DIFF_MEDIUM, 0)
            n_hard = result_diff.get(self.KEY_DIFF_HARD, 0)
            n_txt = result_type.get(self.KEY_TYPE_TXT, 0)
            n_img = result_type.get(self.KEY_TYPE_IMG, 0)
            # Sanity check            
            assert n_img + n_txt == n_easy + n_medium + n_hard
            # Affect variable
            categories_difficulty[i] = [n_easy, n_medium, n_hard]
            categories_type[i] = [n_txt, n_img]
            
        # Retreive categories
        return categories_name, categories_id, categories_type, categories_difficulty
    
    def get_questions(self, n: int, category_id: int = None, difficulty: int = None, type: str = None) -> List[Questions]:

        # Create query dict (if None then consider any)
        params = {self.KEY_R_LIMIT: n}
        header = {}
        
        # Check category
        if category_id is not None:
            params[self.KEY_R_CAT] = self.categories[category_id]
        if difficulty is not None:
            params[self.KEY_R_DIFF] = self.LUT_DIFFICULTY[difficulty]
        if type is not None:
            params[self.KEY_R_TYPES] = self.LUT_TYPE[type]
        # CHeck API token
        if self.token is not None:
            header[self.KEY_TOKEN] = self.token
            
        # Send query
        result = self.slow_request_urllib3(url=self.URL_QUESTION, header=header, params=params)     

        # Check return message
        if result is None:
            if self.verbose:
                print("Error in API: {}".format(result))
            return []

        # Parse results as questions
        questions = []
        for raw_question in result:
            # Parse question
            q = Questions(
                question=raw_question.get(self.KEY_R_QUESTION, self.KEY_R_ERROR).get(self.KEY_TEXT, self.KEY_R_ERROR),
                correct_answers=[raw_question.get(self.KEY_R_CORRECT, self.KEY_R_ERROR)],
                incorrect_answers=raw_question.get(self.KEY_R_INCORRECT, []),
                library=self.__class__.__name__.lower(), 
                category=self.categories[category_id],
                category_id=category_id,
                uuid=raw_question.get(self.KEY_R_ID, ""),
                difficulty=difficulty,
                type=type,
            )
            
            questions.append(q)
            
        return questions