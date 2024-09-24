from pybquiz.db.base import UnifiedTSVDB, TriviaQ
from pybquiz.db.wwtbam import WWTBAM
import pandas as pd
import numpy as np

    
    
class QGenerator:
    
        
    # Define constant for variables dump
    # # For rounds

            
    # # For question
    # CATEGORY_ID = "category_id"
    
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
    
    def __init__(self) -> None:
        pass
    
    def get_codes(self):
        raise NotImplementedError
    
    def get_round(self, options: str):
        raise NotImplementedError

        
    @staticmethod
    def parse_options(l):
        return ", ".join(["{} ([red]{}[/red])".format(o[0], o[1]) for o in l])
    
    
    
class QGeneratorTrivia(QGenerator):
    
    TXT_DESCRIPTION = "Trivia round that includes a wide range of topics. Select round by typing the category index, number of question and potential options (e.g.: [red]A-0-10-HK[/red]). "
        
    TXT_OPTIONS = [
        ("Easy", "E"),
        ("Medium", "M"),
        ("Hard", "H"),
        ("Unknown", "U"),
        ("include True/False", "T"),
        ("include UK", "K"),
        ("include USA", "A"),
    ]
    
    def __init__(self, trivia: UnifiedTSVDB) -> None:
        super().__init__()
        self.trivia = trivia
        
        # Get categories
        self.values = self.trivia.db[UnifiedTSVDB.KEY_O_CAT].value_counts()
        self.values = self.values.sort_index()

        # Get values
        values_all = pd.DataFrame(
            [{self.values.index.name: "any", "count": self.values.sum()}]
            ).set_index(self.values.index.name)["count"]
        
        # Merge
        self.values = pd.concat([values_all, self.values])

                
    def get_codes(self):

        # Build content
        content = [{
                self.KEY_INDEX: i, 
                self.KEY_CATEGORY: k.title(), 
                self.KEY_NUMBER: v
            } for i, (k, v) in enumerate(self.values.items())
        ]
        return {
            self.KEY_TITLE: "Trivia", 
            self.KEY_DESCRIPTION: self.TXT_DESCRIPTION, 
            self.KEY_CONTENT: content,
            self.KEY_OPTION: self.parse_options(self.TXT_OPTIONS)
        }
        
    #
    def _select_questions(
        self,
        category: str,
        n: int,
        use_difficulty: list[str],
        use_tf: bool,
        use_uk: bool,
        use_usa: bool,
    ):
        
        # Filter difficulty
        f_diff = pd.concat([self.trivia.db[TriviaQ.KEY_DIFFICULTY] == k for k in use_difficulty], axis=1)
        f_diff = f_diff.any(axis=1)
        
        # Filter cat
        f_cat = f_diff.copy()
        if category != "any":
            f_cat = self.trivia.db[UnifiedTSVDB.KEY_O_CAT] == category
        
        # Filter T/F
        f_tf = ~(self.trivia.db[TriviaQ.KEY_WRONG_ANSWER1].notnull() & self.trivia.db[TriviaQ.KEY_WRONG_ANSWER2].isna()) | use_tf
        # Filter uk / us
        f_us = (self.trivia.db[UnifiedTSVDB.KEY_O_USA] == 0) | ((self.trivia.db[UnifiedTSVDB.KEY_O_USA] == 1) & use_usa)
        f_uk = (self.trivia.db[UnifiedTSVDB.KEY_O_UK] == 0) | ((self.trivia.db[UnifiedTSVDB.KEY_O_UK] == 1) & use_uk)

        # f_us = (self.trivia.db[UnifiedTSVDB.KEY_O_USA] == use_usa) | (self.trivia.db[UnifiedTSVDB.KEY_O_UK] == use_uk)
        f = f_diff & f_cat & f_us & f_uk & f_tf
        
        # Choose random questions
        index = self.trivia.db.loc[f].index
        index = np.random.permutation(index)[:min(n, len(index))]
        
        # Return questions
        qs = []
        for i in index:
            qs.append(self.trivia[i])
            
        return qs
        
    def get_round(self, options: str):
        # Read options
        o = options.split("-")        
        
        # Check consistency
        if len(o) != 4:
            return None
        
        # Get info
        o_id = int(o[1])
        o_n = int(o[2])
        o_o = o[3]
        
        # Get difficulty
        use_easy = "easy" if "E" in o_o.upper() else None
        use_medium = "medium" if "M" in o_o.upper() else None
        use_hard = "hard" if "H" in o_o.upper() else None
        use_unkown = "none" if "U" in o_o.upper() else None
        use_difficulty = [use_easy, use_medium, use_hard, use_unkown]
        
        use_tf = True if "T" in o_o.upper() else False
        use_uk = True if "K" in o_o.upper() else False
        use_usa = True if "A" in o_o.upper() else False
        
        # Select questions based on criteria
        qs = self._select_questions(
            category=self.values.index[o_id],
            n=o_n,
            use_difficulty=use_difficulty,
            use_tf=use_tf,
            use_uk=use_uk,
            use_usa=use_usa,
        )
        
        data = {
            QGenerator.KEY_TYPE: "trivia", 
            QGenerator.KEY_CATEGORY: self.values.index[o_id], 
            QGenerator.KEY_QUESTION: qs,
        }
        return data
        
    
class QGeneratorWWTBAM(QGenerator):
    
    
    def __init__(self, wwtbams: list[WWTBAM]) -> None:
        super().__init__()
        self.wwtbams = wwtbams
        
    def get_codes(self):
        # Get classes
        content = [{
                self.KEY_INDEX: i, 
                self.KEY_CATEGORY: d.lang.upper(), 
                self.KEY_NUMBER: len(d)
            } for i, d in enumerate(self.wwtbams)
        ]

        # Build content
        return {self.KEY_TITLE: "Who Wants to Be a Millionaire?", self.KEY_CONTENT: content}
    
    