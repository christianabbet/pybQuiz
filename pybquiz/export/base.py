import json
from typing import Optional
from tqdm import tqdm

from pybquiz.background import BackgroundManager
from pybquiz.const import Const as C

class Export():
    
    
    TXT_SWAP = "Bring back paper sheets"
    TXT_HANDIN = "Exchange paper sheets"
    
    def __init__(
        self, 
        dump_path: str,
        dircache: Optional[str] = ".cache",
    ) -> None:
        
        # Load data
        self.dump_path = dump_path
        self.data = None
        self.bg_manager = BackgroundManager(dircache=dircache)
        
        # Reload data
        with open(self.dump_path, "r") as f:
            self.data = json.load(f)
            
            
    def export(self):
        
        # Log
        print("Creating Quiz ...")
                
        # Read title
        author = self.data.get(C.KEY_AUTHOR, C.KEY_ERROR)
        title = self.data.get(C.KEY_TITLE, C.KEY_ERROR)
        rounds = self.data.get(C.KEY_ROUNDS, [])
        N_rounds = len(rounds)
        
        # Iterate over rounds
        print("Title page ...")
        img_main_bg = self.bg_manager.get_background(self.bg_manager.KEY_MAIN)
        img_paper_bg = self.bg_manager.get_background(self.bg_manager.KEY_PAPER)           

        self.make_title(title=title, subtitle=author, img_bg=img_main_bg)
        
        for i, round in enumerate(rounds):
            
            # Log rounds
            print("[{}/{}]: Rounds ...".format(i+1, N_rounds))
            
            # Check number of questions
            category = round.get(C.KEY_CATEGORY, None)
            questions = round.get(C.KEY_QUESTION, [])
            type = round.get(C.KEY_TYPE, None)
            img_bg = self.bg_manager.get_background(category, blurred=False)
            img_bg_blur = self.bg_manager.get_background(category, blurred=True)
            title = "Round {}: {}".format(i+1, category.title())
            
            # Add rules
            # TODO
            
            # Add questions
            self.make_title(title=title, subtitle=None, img_bg=img_bg)
            # for j, data in enumerate(tqdm(questions, desc="Questions ...")):
            #     self.make_question(
            #         data=data, 
            #         index=j,
            #         show_answer=False,
            #         type=type, 
            #         img_bg=img_bg, 
            #         img_bg_blur=img_bg_blur
            #     )

            # Add swap
            self.make_title(title=Export.TXT_SWAP, subtitle=None, img_bg=img_paper_bg)
            
            # Add answers
            self.make_title(title=title, subtitle="Answers", img_bg=img_bg)
            # for j, data in enumerate(tqdm(questions, desc="Answers ...")):
            #     self.make_question(
            #         data=data, 
            #         index=j,
            #         show_answer=True,
            #         type=type, 
            #         img_bg=img_bg, 
            #         img_bg_blur=img_bg_blur
            #     )
            
            # Add bring back
            self.make_title(title=Export.TXT_HANDIN, subtitle=None, img_bg=img_paper_bg)
            
            # if type == "trivia":
            #     self.make_trivia_round()
            # elif type == "wwtbam":
            #     self.make_wwtbam_round()
            # else:
            #     raise NotImplementedError
        
        self.save()
        
    
    def make_title(self, title: str, subtitle: str, img_bg: str):
        raise NotImplementedError
    
    def make_question(self, data: dict, index: int, show_answer: bool, type: str, img_bg: str, img_bg_blur: str):
        raise NotImplementedError
    
    def save(self):
        raise NotImplementedError