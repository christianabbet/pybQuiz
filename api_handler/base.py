from abc import abstractmethod
from typing import List
from typing import Union, Tuple
import time
import requests
import json
import numpy as np
from py_markdown_table.markdown_table import markdown_table


class Questions:

    DIFFICULTY_UNKOWN = -1
    DIFFICULTY_EASY = 0
    DIFFICULTY_MEDIUM = 1
    DIFFICULTY_HARD = 2

    TYPE_TEXT = 0
    TYPE_IMAGE = 1
    
    def __init__(
        self, 
        question: str,
        correct_answer: str,
        incorrect_answers: List[str] = None,
        category: str = None,        
        uuid: str = None,
        difficulty: int = DIFFICULTY_UNKOWN,
        type: int = TYPE_TEXT,

    ) -> None:
        """
        Base question class

        Parameters
        ----------
        question : str
            Text string containing the question.
        correct_answer : str
            Test string with correct answer.
        incorrect_answers : List[str], optional
            List of additional propositions. If None, assume question need to be 
            answered without any propositions.
        category : str, optional
            Name of the catergory. Default is None.
        uuid : str, optional
            Unique ID of the question. Default is None.
        difficulty : int, optional
            Difficult level of the question. Can be any of [DIFFICULTY_UNKOWN, DIFFICULTY_EASY, 
            DIFFICULTY_MEDIUM, DIFFICULTY_HARD], by default is DIFFICULTY_UNKOWN.
        type : int, optional
            QUestion type. Can be any of [TYPE_TEXT, TYPE_IMAGE], by default is TYPE_TEXT.
        """
        
        # Set variables
        self.question = question
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers
        self.category = category
        self.uuid = uuid
        self.difficulty = difficulty
        self.type = type    
           
    
class BaseAPIHandler:
   
    def __init__(
        self,
        verbose: bool = False,
        delay_api: float = 5.0,
    ) -> None:
        self.verbose = verbose
        self.delay_api = delay_api
        self.categories, self.categories_id, self.categories_type, self.categories_difficulty = self.initialize_db()
    
    def slow_request(self, url: str, params: dict = None):
        """
        Send URL get request after a delay in seconds.

        Parameters
        ----------
        url : str
            URL get query to send.

        Returns
        -------
        dict
            Parsed result to URL query.
        """
        # Wait to not query too many times in a row
        time.sleep(self.delay_api) 
        result = requests.get(url=url, params=params)
        return json.loads(result.text)
    
    def __repr__(self):
        """
        Create a pretty print for DB

        Returns
        -------
        pprint: str
            Pretty print
        """
        
        data = []
        N = len(self.categories)
        # Create table
        for i in range(N):
            data.append({
                "ID": self.categories_id[i],
                "Catgory": self.categories[i],
                "Easy": int(self.categories_difficulty[i, 0]),
                "Medium": int(self.categories_difficulty[i, 1]),
                "Hard": int(self.categories_difficulty[i, 2]),
                "Text": int(self.categories_type[i, 0]),
                "Image": int(self.categories_type[i, 1]),
            })
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown').get_markdown()
        return markdown

    
    @abstractmethod 
    def initialize_db(self) -> Union[List[str], List[int], np.ndarray, np.ndarray]:
        """
        Initialize database infromation

        Returns
        -------
        categories : List[int]
            List of N categories as strings.
        categories_id : List[int]
            List of N categories as ints.
        categories_difficulty : np.ndarray
            Array of N categories and 3 difficulty level (easy, medium, hard)
        categories_type : np.ndarray
            Array of N categories types
        """
        raise NotImplementedError

    @abstractmethod 
    def get_question(self, category_id: int = None) -> Questions:
        raise NotImplementedError