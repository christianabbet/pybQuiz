


class Const:

    KEY_DIFFICULTY = "difficulty"
    KEY_ANSWERS = "answers"
    KEY_AUTHOR = "author"
    KEY_TYPE = "type"
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
            