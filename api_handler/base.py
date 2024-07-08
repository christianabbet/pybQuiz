from abc import abstractmethod
from typing import List
from typing import Union, Tuple
import time
import requests
import json


def slow_request(url: str, delay: float = 0.5):
    """
    Send URL get request after a delay in seconds.

    Parameters
    ----------
    url : str
        URL get query to send.
    delay: float, optional
        Delay before sending request. Deafult value is 0.5 seconds.

    Returns
    -------
    dict
        Parsed result to URL query.
    """
    # Wait to not query too many times in a row
    time.sleep(5.5) 
    result = requests.get(url)
    return json.loads(result.text)


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
   
    def __init__(self) -> None:
        pass
    
    @abstractmethod 
    def get_categories(self, return_ids: bool = False) -> Union[list, Tuple[list, list]]:
        raise NotImplementedError
    
    @abstractmethod 
    def get_question(self, category_id: int = None) -> Questions:
        raise NotImplementedError