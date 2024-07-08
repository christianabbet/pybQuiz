from api_handler.base import BaseAPIHandler, Questions
from typing import Union, Tuple, List
import numpy as np
from tqdm import tqdm


class OpenTriviaDB(BaseAPIHandler):

    # URLS
    URL_CATEGORY = "https://opentdb.com/api_category.php"
    URL_CATEGORY_COUNT = "https://opentdb.com/api_count.php"
    
    KEY_TRIVIA_CAT = "trivia_categories"
    KEY_NAME = "name"
    KEY_ID = "id"
    KEY_CAT = "category"
    KEY_Q_COUNT = "category_question_count"
    KEY_Q_TOTAL_COUNT = "total_question_count"
    KEY_Q_EASY_COUNT = "total_easy_question_count"
    KEY_Q_MEDIUM_COUNT = "total_medium_question_count"
    KEY_Q_HARD_COUNT = "total_hard_question_count"            
            
    def __init__(
        self,
        delay_api: int = 5,
        verbose: bool = False,
    ) -> None:
        """
        
        Create API handler to https://opentdb.com/

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
        super().__init__(verbose=verbose, delay_api=delay_api)
        
                
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
        result = self.slow_request(self.URL_CATEGORY)
        result = result.get(self.KEY_TRIVIA_CAT, {})
        
        N = len(result)
        categories_name = [item.get(self.KEY_NAME, "") for item in result]
        categories_id = [item.get(self.KEY_ID, -1) for item in result]
        categories_difficulty = np.zeros((N, 3))
        categories_type= np.zeros((N, 2))
        
        for i in tqdm(np.arange(N), disable=(not self.verbose)):
            # Get category specific stats            
            result_cat = self.slow_request(url=self.URL_CATEGORY_COUNT, params={self.KEY_CAT: categories_id[i]})
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
