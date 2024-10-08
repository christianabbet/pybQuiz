from typing import List
import numpy as np
from pybquiz.const import PYBConst as C


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
        correct_answers: List[str],
        incorrect_answers: List[str] = None,
        library: str = None, 
        category: str = None,        
        category_id: int = None,        
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
        correct_answers : List[str]
            List of correct propositions. 
        incorrect_answers : List[str]
            List of additional propositions. If None, assume question need to be 
            answered without any propositions.
        library : str
            Name of the API library.            
        category : str, optional
            Name of the catergory. Default is None.
        category : int, optional
            ID of the catergory. Default is None.
        uuid : str, optional
            Unique ID of the question. Default is None.
        difficulty : int, optional
            Difficult level of the question. Can be any of [DIFFICULTY_UNKOWN, DIFFICULTY_EASY, 
            DIFFICULTY_MEDIUM, DIFFICULTY_HARD], by default is DIFFICULTY_UNKOWN.
        type : int, optional
            QUestion type. Can be any of [TYPE_TEXT, TYPE_IMAGE], by default is TYPE_TEXT.
        """
        
        # Set variables
        self.question =  self.capitalize([question])[0]
        
        # Set random order for questions
        self.correct_answers = self.capitalize(correct_answers)
        self.incorrect_answers = self.capitalize(incorrect_answers)
        self.order = np.random.permutation(len(self.correct_answers) + len(self.incorrect_answers)).tolist()
        self.library=library
        self.category = category
        self.category_id = category_id
        self.uuid = uuid
        self.difficulty = difficulty
        self.type = type    
        
    @staticmethod
    def capitalize(strings: list[str]):
            return [s[0].capitalize() + s[1:] for s in strings]
        
    def get_shuffled_answers(self):
        # Concat values
        answer = self.correct_answers.copy()
        answer.extend(self.incorrect_answers.copy())
        # Get correct ids
        cgt = [1] * len(self.correct_answers) + [0] * len(self.incorrect_answers)
        # Shuffle results
        answer = np.array(answer)[self.order]
        ids_correct = np.nonzero(np.array(cgt)[self.order])[0].tolist()
        return answer.tolist(), ids_correct
    
    def dump(self):
        
        answers, correct_answers = self.get_shuffled_answers()
        data = {
            C.QUESTIONS: self.question,
            C.ANSWERS: answers,
            C.CORRECT_ANSWERS: correct_answers,
            C.CATEGORY: self.category,
            C.CATEGORY_ID: self.category_id,
            C.DIFFICULTY: self.difficulty,
            C.TYPE: self.type,
        }
        return data
    
    