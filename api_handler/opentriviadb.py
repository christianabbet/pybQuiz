from api_handler.base import BaseAPIHandler, Questions, slow_request
from typing import Union, Tuple


class OpenTriviaDB(BaseAPIHandler):

    # URLS
    URL_CATEGORY = "https://opentdb.com/api_category.php"
    # URL_CATEGORY_COUNT = "https://opentdb.com/api_count.php?category={}"
    # URL_API = "https://opentdb.com/api.php?amount={}&category={}&difficulty={}&type={}"
    
    # # Keys
    # KEY_ID = "id"
    # KEY_NAME = "name"        
    # KEY_TRIVIA_CAT = "trivia_categories"
    # KEY_QUESTION_COUNT = "category_question_count"
    # KEY_QUESTION_COUNT_EASY = "total_easy_question_count"
    # KEY_QUESTION_COUNT_MEDIUM = "total_medium_question_count"
    # KEY_QUESTION_COUNT_HARD = "total_hard_question_count"

    
    def __init__(
        self,
        delay_api: int = 5,
    ) -> None:
        """
        Create API handler to https://opentdb.com/

        Parameters
        ----------
        delay_api : int, optional
            Default time between queries to API in seconds. By default 5 seconds.
        """
        super().__init__()
        self.delay_api = delay_api
        
    def get_categories(self, return_ids: bool = False) -> Union[list, Tuple[list, list]]:
        # Send request
        result = slow_request(self.URL_CATEGORY)
        # Parse resutls
        categories_name = [item["name"] for item in result["trivia_categories"]]
        categories_id = [item["id"] for item in result["trivia_categories"]]
        # Check return result
        if return_ids:
            return categories_name, categories_id
        else:
            return categories_name
        
    def get_question(self, category_id: int = None) -> Questions:
        
        return NotImplementedError