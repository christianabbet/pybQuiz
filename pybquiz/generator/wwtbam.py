from pybquiz.db.wwtbam import WWTBAM
from pybquiz.const import Const as C
from pybquiz.const import TriviaConst as TC
from pybquiz.generator.base import QGenerator
import pandas as pd


class QGeneratorWWTBAM(QGenerator):
    
    TXT_OPTIONS = [
        ("Easy", "E"),
        ("Medium", "M"),
        ("Hard", "H"),
        ("include UK", "K"),
        ("include USA", "A"),
    ]
    TXT_DESCRIPTION = "WWTBAM round that includes a wide range of topics. Select round by typing the category index, number of question and potential options (e.g.: [red]B-0-10-K[/red]). "
    
    def __init__(self, wwtbam: WWTBAM) -> None:
        super().__init__()
        
        # Get categories
        self.wwtbam = wwtbam
        self.values = self.wwtbam.db[TC.EXT_KEY_O_CAT].value_counts()
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
                C.KEY_INDEX: i, 
                C.KEY_CATEGORY: k.title(), 
                C.KEY_NUMBER: v
            } for i, (k, v) in enumerate(self.values.items())
        ]
        return {
            C.KEY_TITLE: "WWTBAM", 
            C.KEY_DESCRIPTION: self.TXT_DESCRIPTION, 
            C.KEY_CONTENT: content,
            C.KEY_OPTION: self.parse_options(self.TXT_OPTIONS)
        }
            
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
        use_difficulty = [use_easy, use_medium, use_hard]
        
        use_uk = True if "K" in o_o.upper() else False
        use_usa = True if "A" in o_o.upper() else False
        
        # Select questions based on criteria
        raise NotImplementedError
        qs = self._select_questions(
            category=self.values.index[o_id],
            n=o_n,
            use_difficulty=use_difficulty,
            use_uk=use_uk,
            use_usa=use_usa,
        )
        
        data = {
            C.KEY_TYPE: "wwtbam", 
            C.KEY_CATEGORY: self.values.index[o_id], 
            C.KEY_QUESTION: qs,
        }
        return data