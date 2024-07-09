from pybquiz.api_handler.base import BaseAPIHandler
from typing import Union, List
import numpy as np
from tqdm import tqdm



class TheTriviaAPI(BaseAPIHandler):

    URL_CATEGORY = "https://the-trivia-api.com/v2/metadata"
    
    KEY_BY_CAT = "byCategory"
    KEY_BY_DIFF = "byDifficulty"
    KEY_BY_TYPE = "byType"
    KEY_CAT = "categories"
    KEY_TYPE_TXT = "text_choice"
    KEY_TYPE_IMG = "image_choice"
    KEY_DIFF_EASY = "easy"
    KEY_DIFF_MEDIUM = "medium"
    KEY_DIFF_HARD = "hard"
        
    def __init__(
        self,
        delay_api: int = 5,
        verbose: bool = False,
        clear_cache: bool = False,
    ) -> None:
        """
        Create API handler to https://the-trivia-api.com

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
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
        result = self.slow_request(self.URL_CATEGORY)
        result = result.get(self.KEY_BY_CAT, {})
        
        # Get all categories
        N = len(result)
        categories_name = sorted(result.keys())
        categories_id = np.arange(len(categories_name))
        categories_difficulty = np.zeros((N, 3))
        categories_type= np.zeros((N, 2))
        
        for i in tqdm(np.arange(N), disable=(not self.verbose)):
            # Get category specific stats
            result_cat = self.slow_request(url=self.URL_CATEGORY, params={self.KEY_CAT: categories_name[i]})
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
 
