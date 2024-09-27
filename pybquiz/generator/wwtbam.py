from pybquiz.db.wwtbam import WWTBAM
from pybquiz.const import Const as C
from pybquiz.generator.base import QGenerator


class QGeneratorWWTBAM(QGenerator):
    
    TXT_OPTIONS = [
        ("include UK", "K"),
        ("include USA", "A"),
    ]
    TXT_DESCRIPTION = ""
    
    def __init__(self, wwtbams: list[WWTBAM]) -> None:
        super().__init__()
        self.wwtbams = wwtbams
            
                    
    def get_codes(self):

        # Build content
        content = [{
                C.KEY_INDEX: i, 
                C.KEY_CATEGORY: d.lang.upper(), 
                C.KEY_DESCRIPTION: self.TXT_DESCRIPTION, 
                C.KEY_NUMBER: len(d)
            } for i, d in enumerate(self.wwtbams)
        ]
        
        return {
            C.KEY_TITLE: "Trivia", 
            C.KEY_DESCRIPTION: self.TXT_DESCRIPTION, 
            C.KEY_CONTENT: content,
            C.KEY_OPTION: self.parse_options(self.TXT_OPTIONS)
        }
        
    
    