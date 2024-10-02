from pybquiz.db.wwtbam import UnifiedWWTBAM
from pybquiz.const import Const as C
from pybquiz.const import WWTBAMConst as WC
from pybquiz.const import TriviaConst as TC
from pybquiz.generator.base import QGenerator
import pandas as pd
import numpy as np

class QGeneratorWWTBAM(QGenerator):
    
    TXT_OPTIONS = [
        ("include UK", "K"),
        ("include USA", "A"),
    ]
    TXT_DESCRIPTION = "WWTBAM round that includes a wide range of topics. Select round by typing the category index, number of question and potential options (e.g.: [red]B-0-10-K[/red]). "
    TEXT_RULES = ["'Who wants to be a millionaire?' round", "1 pt per correct answer", "1 wrong answer accepted (joker)", "After second wrong answer, no more points"]

    def __init__(self, wwtbam: UnifiedWWTBAM) -> None:
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
        if len(o) < 3:
            return None
        
        # Get info
        o_id = int(o[1])
        o_n = int(o[2])
        o_o = ""
        if len(o) == 4:
            o_o = o[3]
        
        # Get difficulty
        use_uk = True if "K" in o_o.upper() else False
        use_usa = True if "A" in o_o.upper() else False
        
        # Select questions based on criteria
        qs = self._select_questions(
            category=self.values.index[o_id],
            n=o_n,
            use_uk=use_uk,
            use_usa=use_usa,
        )
        
        data = {
            C.KEY_TYPE: "wwtbam", 
            C.KEY_CATEGORY: "wwtbam", 
            C.KEY_QUESTION: qs,
            C.KEY_RULES: self.TEXT_RULES,
        }
        return data
    
    def _select_questions(
        self,
        category: str,
        n: int,
        use_uk: bool,
        use_usa: bool,
    ):
                
        # Filter uk / us
        f_us = (self.wwtbam.db[TC.EXT_KEY_O_USA].fillna(0) == 0) | ((self.wwtbam.db[TC.EXT_KEY_O_USA].fillna(0) == 1) & use_usa)
        f_uk = (self.wwtbam.db[TC.EXT_KEY_O_UK].fillna(0) == 0) | ((self.wwtbam.db[TC.EXT_KEY_O_UK].fillna(0) == 1) & use_uk)
        f_diff = self.wwtbam.db[WC.KEY_DIFFICULTY].notnull()

        # Filter cat
        f_cat = f_diff.copy()
        if category != "any":
            f_cat = self.wwtbam.db[TC.EXT_KEY_O_CAT] == category
        
        # f_us = (self.trivia.db[UnifiedTSVDB.KEY_O_USA] == use_usa) | (self.trivia.db[UnifiedTSVDB.KEY_O_UK] == use_uk)
        f = f_cat & f_us & f_uk & f_diff
        
        # Get difficulty range
        codes = self.wwtbam.db.loc[f, WC.KEY_DIFFICULTY].unique()
        codes = sorted(codes)
        bins = np.concatenate([np.arange(min(n+1, np.max(codes) - 1)), [np.max(codes)+1]])
        
        codes = pd.cut(self.wwtbam.db[WC.KEY_DIFFICULTY], bins=bins, right=False)
        self.wwtbam.db["temp"] = codes.cat.codes
        
        # Choose random questions        
        qs = []
        for _, d in self.wwtbam.db[f].groupby("temp"):
            # Pick random
            i = np.random.permutation(d.index)[0]
            data = self.wwtbam[i]
            qs.append(data)
            
        # Return questions            
        return qs
        