from pybquiz.api_handler import create_handler
from typing import List
import yaml
import json
import os
from pptx import Presentation     
from pptx.presentation import Presentation as PObject
import numpy as np
from pptx.util import Inches, Pt, Mm
from pptx.dml.color import RGBColor

def pos_to_char(pos):
    return chr(pos + 97)

class SlideFactory:
    
    TITLE_SUBTITLE = 0
    TITLE_CONTENT = 1
    SECTION_HEADER = 2
    TWO_CONTENT = 3
    COMPARISON = 4
    TITLE = 5
    BLANK = 6
    CONTENT_CAPTION = 7
    IMAGE_CAPTION = 8
        
    # Base slide frame in mm
    S_FRAME_WITDH = 254  # 10 Inches
    S_FRAME_HEIGH = 190.5  # 7.5 Inches
    S_FRAME_MARGIN = 20
    # Question frame
    S_QUEST_BBOX_W = S_FRAME_WITDH - (2 * S_FRAME_MARGIN)
    S_QUEST_BBOX_H = 40
    # Answer frames
    S_ANSWERS_WIDTH = S_QUEST_BBOX_W
    S_ANSWERS_TOP = S_QUEST_BBOX_H + S_FRAME_MARGIN
    S_ANSWERS_HEIGHT = S_FRAME_HEIGH - 3*S_FRAME_MARGIN
    
    S_ANSWER_COL_MARGIN = S_FRAME_MARGIN / 2
    S_ANSWER_COL1_LEFT = S_FRAME_MARGIN
    S_ANSWER_COL_WIDTH = (S_ANSWERS_WIDTH - S_ANSWER_COL_MARGIN) / 2
    S_ANSWER_COL2_LEFT = S_FRAME_MARGIN + S_ANSWER_COL_WIDTH + S_ANSWER_COL_MARGIN
    S_ANSWER_ROW_HEIGHT_MAX = 20
    S_ANSWER_ROW_HEIGHT_MARGIN = 10

    # Font
    FONT_TILE = 32
    FONT_QUESTION = 24
    
    @staticmethod
    def get_system_fonts():
        return "/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf"
    
    @staticmethod
    def add_title_subtitle(root: PObject, title: str = "", subtitle: str = ""):
            # Add slide
            title_slide = root.slides.add_slide(root.slide_layouts[SlideFactory.TITLE_SUBTITLE]) 
            # First place holder (title)
            # Second place holder (subtitle)
            title_slide.placeholders[0].text = title
            title_slide.placeholders[1].text = subtitle       
            
    @staticmethod
    def add_question(root: PObject, i: int = 1, question: str = "", answers: list[str] = [], answers_id: int = None):
        
            # Add slide and question            
            question_slide = root.slides.add_slide(root.slide_layouts[SlideFactory.BLANK]) 
            txBoxTitle = question_slide.shapes.add_textbox(
                Mm(SlideFactory.S_FRAME_MARGIN), 
                Mm(SlideFactory.S_FRAME_MARGIN), 
                Mm(SlideFactory.S_QUEST_BBOX_W), 
                Mm(SlideFactory.S_QUEST_BBOX_H),
            )
            
            tf = txBoxTitle.text_frame
            tf.text = "Q{}: {}".format(i, question)
            # tf.font.size = Pt(SlideFactory.FONT_TILE)
            tf.fit_text(max_size=SlideFactory.FONT_TILE, font_file=SlideFactory.get_system_fonts())
                        
            nQ = len(answers)
            nRows = np.ceil(nQ/2).astype(int)
            row_offset = (SlideFactory.S_ANSWERS_HEIGHT - (nRows * SlideFactory.S_ANSWER_ROW_HEIGHT_MAX + (nRows - 1) * SlideFactory.S_ANSWER_ROW_HEIGHT_MARGIN)) / 2
            
            # Check if only one proposition and no answer
            if nQ <= 1 and answers_id is None:
                return
            
            # Add propositions
            for j in range(nQ):
                # Define col
                id_col = j % 2
                id_row = j // 2
                
                # Fix width
                if id_col == 0:
                    left = Mm(SlideFactory.S_ANSWER_COL1_LEFT)
                else:
                    left = Mm(SlideFactory.S_ANSWER_COL2_LEFT)
            
                # Fix height
                local_offset = id_row * SlideFactory.S_ANSWER_ROW_HEIGHT_MAX + (id_row-1) * SlideFactory.S_ANSWER_ROW_HEIGHT_MARGIN
                top = Mm(SlideFactory.S_ANSWERS_TOP + local_offset + row_offset)
                txBox = question_slide.shapes.add_textbox(left, top, Mm(SlideFactory.S_ANSWER_COL_WIDTH), Mm(SlideFactory.S_ANSWER_ROW_HEIGHT_MAX))
                tf = txBox.text_frame
                tf.text = "{}) {}".format(pos_to_char(j), answers[j])
                tf.fit_text(max_size=SlideFactory.FONT_QUESTION, font_file=SlideFactory.get_system_fonts())
                
                if answers_id is not None and j in answers_id:
                    tf.paragraphs[0].font.color.rgb = RGBColor.from_string("8fce00")
            
class Round():
    
    def __init__(
        self,
        title: str,
        api: str,
        theme_id: int,
        shuffle: bool = True,
        difficulty: List[int] = None,
        type: str = None,
        token: str = None,
        verbose: bool = False,
        delay_api: float = 5.0,
        clear_cache: bool = False,    
    ):
        
        # Store variables
        self.title = title
        self.shuffle = shuffle
        self.theme_id = theme_id
        self.difficulty = difficulty
        self.type = type 
        self.token = token
        self.api = api
        
        # Create pybquiz from config file
        self.api = create_handler(name=api, delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)

        self.questions = []
        for i, n in enumerate(self.difficulty):
            # Get question with difficulty level
            qs = self.api.get_questions(category_id=self.theme_id, difficulty=i, n=n, type=self.type)
            # Append to list
            self.questions.extend(qs)
        
        # Check if shuffle is needed
        if self.shuffle:
            # Reorder
            N = len(self.questions)
            id_shuffle = np.random.permutation(N)
            self.questions = np.array(self.questions)[id_shuffle].tolist()
            
            
    def to_json(self):
        # Create response
        json = {
            "title": self.title,
            "questions": [q.to_json() for q in self.questions]
        }
        
        return json        
            
            
class PybQuiz:
        
    def __init__(
        self,
        title: str,
        author: str,
        delay_api: float,
        cfg_rounds: dict,
        clear_cache: bool = False,
        tokens: dict = None,
        verbose: bool = False,
    ):
    
        self.title = title
        self.author = author
        self.verbose = verbose  
        self.tokens = tokens      
        self.rounds = self._create_rounds(cfg_rounds=cfg_rounds, delay_api=delay_api, clear_cache=clear_cache)
        
    def _create_rounds(self, cfg_rounds: dict, delay_api: float, clear_cache: float):
        
        # Round infos
        rounds = []
        Nr = len(cfg_rounds)
        
        if self.verbose:
            print("Quiz: {}".format(self.title))
            print("Start rounds creation ...")
        
        for i, cfg_round in enumerate(cfg_rounds):
            
            # Update dict
            cfg_round.update({"verbose": self.verbose, "delay_api": delay_api, "clear_cache": clear_cache})
            
            # Update API token
            cfg_round["token"] = self.tokens.get(cfg_round["api"], None)
            
            # Display current info
            if self.verbose:
                print("\n--------------")
                print("Round [{}/{}]".format(i+1, Nr))
                print("--------------\n")
                print("Params: {}".format(cfg_round))
                
            # Get round handler
            rounds.append(Round(**cfg_round))
        
        # Return rounds
        return rounds
        
    def to_json(self, file: str):
        # Dump all questions to given file
        json_data = {
            "title": self.title,
            "rounds": [r.to_json() for r in self.rounds]
        }
        # Save file
        with open(file, "w") as f:
            json.dump(json_data, f, indent=4, sort_keys=True)

        # Display result
        if self.verbose:
            print("Saved to {}".format(file))
            
    def to_pptx(self, file: str):
        """ 
        Ref for slide types:  
        0 ->  title and subtitle 
        1 ->  title and content 
        2 ->  section header 
        3 ->  two content 
        4 ->  Comparison 
        5 ->  Title only  
        6 ->  Blank 
        7 ->  Content with caption 
        8 ->  Pic with caption 
        """
        
        # Creating presentation object 
        root = Presentation() 

        # Add splide to presetation
        SlideFactory.add_title_subtitle(title=self.title, subtitle=self.author, root=root) 
        
        # Create rounds
        Nround = len(self.rounds)
        for i in range(Nround):
            # Create title slide
            SlideFactory.add_title_subtitle(root=root, title=self.rounds[i].title) 
            
            # Iterate over questions
            Nquestion = len(self.rounds[0].questions)
            for j in range(Nquestion):
                # Add question slide
                answers, _ = self.rounds[i].questions[j].get_shuffled_answers()
                SlideFactory.add_question(
                    root=root, 
                    i=j+1, 
                    question=self.rounds[i].questions[j].question, 
                    answers=answers,
                ) 
                
            # Create title slide
            SlideFactory.add_title_subtitle(root=root, title=self.rounds[i].title, subtitle="Answers") 
            
            # Iterate over questions (answers)
            for j in range(Nquestion):
                # Add question slide
                answers, answers_id = self.rounds[i].questions[j].get_shuffled_answers()
                SlideFactory.add_question(
                    root=root, 
                    i=j+1, 
                    question=self.rounds[i].questions[j].question, 
                    answers=answers,
                    answers_id=answers_id,
                ) 
            
        # Saving file 
        root.save(file) 
            
    @staticmethod
    def from_yaml(yaml_path: dict, yaml_token: dict = None):
        
        # Default tokens empty
        data_token = {}
        
        # Parse input file
        with open(yaml_path) as stream:
            data_cfg = yaml.safe_load(stream)
            
        # Check if file exists
        if os.path.exists(yaml_token):
            with open(yaml_token) as stream:
                data_token = yaml.safe_load(stream)
        
        # Base infos
        cfg_base = data_cfg.get("BaseInfo", {})
        delay_api = cfg_base.get("delay_api", 5.)
        author = cfg_base.get("author", "")
        title = cfg_base.get("title", "")
        verbose = cfg_base.get("verbose", False) 
        clear_cache = cfg_base.get("clear_cache", False) 
        cfg_rounds = data_cfg.get("Rounds", [])
        
        # Create quiz
        quiz = PybQuiz(
            title = title,
            author = author,
            delay_api = delay_api,
            cfg_rounds=cfg_rounds, 
            clear_cache=clear_cache,
            tokens=data_token,
            verbose=verbose
        )
        return quiz