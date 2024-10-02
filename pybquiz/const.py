


class Const:

    KEY_ANSWERS = "answers"
    KEY_AUTHOR = "author"
    KEY_TYPE = "type"
    KEY_RULES = "rules"
    KEY_ROUNDS = "rounds"
    KEY_QUESTION = "question"
    KEY_ORDER = "order"
    KEY_ORDER_ID = "order_id"
    KEY_INDEX = "index"
    KEY_CATEGORY = "category"
    KEY_NUMBER = "number"
    KEY_TITLE = "title"
    KEY_DESCRIPTION = "description"
    KEY_CONTENT = "content"
    KEY_OPTION = "option"
    KEY_ERROR = "ERROR"
    
    
class TriviaConst:
        
    # Define base keys that should exists in databases
    KEY_UUID = "uuid"
    KEY_CATEGORY = "category"
    KEY_DIFFICULTY = "difficulty"
    
    KEY_QUESTION = "question"
    KEY_CORRECT_ANSWER = "correct_answer"
    KEY_WRONG_ANSWER1 = "wrong_answers_1"
    KEY_WRONG_ANSWER2 = "wrong_answers_2"
    KEY_WRONG_ANSWER3 = "wrong_answers_3"
    
        # Define base keys that should exists in databases
    EXT_KEY_DOMAIN = "domain"
    EXT_KEY_O_CAT = "o_category"
    EXT_KEY_O_UK = "o_is_uk"
    EXT_KEY_O_USA = "o_is_usa"
    EXT_KEY_ORDER = "order"
    EXT_KEY_ORDER_ID = "order_id"
    
    @staticmethod
    def get_keys():
        return [v for k, v in TriviaConst.__dict__.items() if k.startswith("KEY")]
            
class WWTBAMConst:      
    KEY_URL = "url"
    KEY_VALUE = "value"
    KEY_DIFFICULTY = "difficulty_code"
    KEY_AIR_DATE = "air_date"
    
            
class FamilyFeudConst:      
    KEY_UUID = "uuid"
    KEY_NAME = "name"
    KEY_CATEGORY = "category"
    KEY_QUESTION = "question"
    KEY_ANSWER1 = "answer1"
    KEY_ANSWER1_VALUE = "#1"
    KEY_ANSWER2 = "answer2"
    KEY_ANSWER2_VALUE = "#2"
    KEY_ANSWER3 = "answer3"
    KEY_ANSWER3_VALUE = "#3"
    KEY_ANSWER4 = "answer4"
    KEY_ANSWER4_VALUE = "#4"
    KEY_ANSWER5 = "answer5"
    KEY_ANSWER5_VALUE = "#5"
    KEY_ANSWER6 = "answer6"
    KEY_ANSWER6_VALUE = "#6"
    KEY_ANSWER7 = "answer7"
    KEY_ANSWER7_VALUE = "#7"
    KEY_N_ANSWER = "n_answers"    
    