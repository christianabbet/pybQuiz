from pybquiz.const import Const as C
from pybquiz.db.wikinamesdb import WikiNamesDB
from pybquiz.generator.base import QGenerator
import pandas as pd
import numpy as np
import re
from typing import Optional


class QGeneratoWikiNames(QGenerator):
    
    TXT_OPTIONS = [
        ("top100", "E"),
        ("top500", "M"),
        ("top1k ", "H"),
        ("top10k", "U"),
    ]
    TXT_DESCRIPTION = "TODO (e.g.: D-x-x)"
    TEXT_RULES = ["TODO"]

    def __init__(
        self, 
        wikinames: WikiNamesDB,
    ) -> None:
        super().__init__()
        
        # Get categories
        self.wikinames = wikinames
        # Existing modes
        # Same first name
        print("lll")
        # Same last names
        print("llll")
        # Find pseudo 
        print("ssss")
        # self.splits.insert(0, 0)
        # self.splits_label = ["Top {:,0f}".format(l) for l in self.splits[1:]]
        # self.values = pd.cut(self.wikinames.db.index, bins=self.splits, right=False, labels=self.splits_label)
        # self.values = np.cumsum(self.values.value_counts())

    def get_codes(self):
        
        # Build content
        content = [{
                C.KEY_INDEX: i, 
                C.KEY_CATEGORY: str(k).title(), 
                C.KEY_NUMBER: v
            } for i, (k, v) in enumerate(self.values.items())
        ]
        return {
            C.KEY_TITLE: "Family Feud", 
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
            
        use_upper = True if ">" in o_o.upper() else False
        use_lower = True if "<" in o_o.upper() else False

        # Select questions based on criteria
        qs = self._select_questions(
            category=self.values.index[o_id],
            use_upper=use_upper,
            use_lower=use_lower,
            n=o_n,
        )
        
        data = {
            C.KEY_TYPE: "familyfeud", 
            C.KEY_CATEGORY: "family feud", 
            C.KEY_QUESTION: qs,
            C.KEY_RULES: self.TEXT_RULES,
        }
        return data
    
    def _select_questions(
        self,
        category: str,
        n: int,
        use_upper: bool,
        use_lower: bool,
    ):
                
        index = self.familyfeud.db.index
        
        if category != "any":
            # Base reference
            category_ = [category]
            # Filter cat
            ucategories = self.familyfeud.db[FC.KEY_CATEGORY].unique()
            vcategories = [int(re.findall("\d", c)[0]) for c in ucategories]
            vcategory = int(re.findall("\d", category)[0]) 
            
            # Check if upper and lower accepted
            if use_upper:
                category_.extend(ucategories[vcategory < np.array(vcategories)])
            if use_lower:
                category_.extend(ucategories[vcategory > np.array(vcategories)])
        
            # Apply filter
            f_index = np.any([self.familyfeud.db[FC.KEY_CATEGORY] == c for c in category_], axis=0)
            index = self.familyfeud.db[f_index].index          

        index = np.random.permutation(index)[:min(n+1, len(index))]
        
        # Return questions
        qs = []
        for i in index:
            qs.append(self.familyfeud[i])
            
        # Return questions            
        return qs
        