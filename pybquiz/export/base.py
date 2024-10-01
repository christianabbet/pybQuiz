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
        return_url: bool = False,
        dircache: Optional[str] = ".cache",
    ) -> None:
        
        # Load data
        self.dump_path = dump_path
        self.data = None
        self.bg_manager = BackgroundManager(dircache=dircache, return_url=return_url)
        
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
            n_questions = len(questions)

            # Title
            self.make_title(title=title, subtitle=None, img_bg=img_bg, type=type)
            
            # Add rules
            # TODO            
            
            # Example
            self.make_question(
                data=questions[0], 
                prefix="Ex",
                show_answer=False,
                type=type, 
                img_bg=img_bg, 
                img_bg_blur=img_bg_blur
            )
            
            self.make_question(
                data=questions[0], 
                prefix="Ex",
                show_answer=True,
                type=type, 
                img_bg=img_bg, 
                img_bg_blur=img_bg_blur
            )
            
            # Add questions
            for j in tqdm(range(1, n_questions), desc="Questions ..."):
                self.make_question(
                    data=questions[j], 
                    prefix="Q{}".format(j),
                    show_answer=False,
                    type=type, 
                    img_bg=img_bg, 
                    img_bg_blur=img_bg_blur
                )

            # Add swap
            self.make_title(title=Export.TXT_SWAP, subtitle=None, img_bg=img_paper_bg)
            
            # Add answers
            self.make_title(title=title, subtitle="Answers", img_bg=img_bg, type=type)
            for j in tqdm(range(1, n_questions), desc="Answers ..."):
                self.make_question(
                    data=questions[j], 
                    prefix="A{}".format(j),
                    show_answer=True,
                    type=type, 
                    img_bg=img_bg, 
                    img_bg_blur=img_bg_blur
                )

            # Add bring back
            self.make_title(title=Export.TXT_HANDIN, subtitle=None, img_bg=img_paper_bg)
        
        self.save()
        
    
    def make_title(self, title: str, subtitle: str, img_bg: str, type: Optional[str] = None):
        raise NotImplementedError
    
    def make_question(self, data: dict, prefix: str, show_answer: bool, type: str, img_bg: str, img_bg_blur: str):
        raise NotImplementedError
    
    def save(self):
        raise NotImplementedError