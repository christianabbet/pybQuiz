import numpy as np


class SlideTemplate:
    
    # Do not modify 
    _FRAME_MARGIN = 0.1
    _FRAME_MMARGIN = 0.025
    _FRAME_MMMARGIN = 0.0125
    _DIFFICULTY_DIAMETER = 0.02
    _QUESTION_HEIGHT = 0.15
    _ANSWER_HEIGHT = 0.1
    _ANSWER_INTER_HEIGHT = 0.025

    # COLORS - TRIVIA
    TRIVIA_COLOR_BBOX_BACKGROUND = "2881a1"
    TRIVIA_COLOR_BBOX_BACKGROUND_CORRECT = "f3a600"
    TRIVIA_COLOR_BBOX_LINE = "2881a1"
    TRIVIA_COLOR_TEXT = "ffffff"
    
    # COLORS - WWTBAM
    WWTBAM_COLOR_BBOX_BACKGROUND = "080e1a"
    WWTBAM_COLOR_BBOX_LINE = "ffffff"
    WWTBAM_COLOR_TEXT = "ffffff"
    WWTBAM_COLOR_QTEXT = "ffff00"
    
    WWTBAM_BBOX_QT = [ 28.754,  61.674, 196.495, 25.596]
    WWTBAM_BBOX_QA = [ 23.612,  97.633,  13.317, 16.703]
    WWTBAM_BBOX_QB = [137.873,  97.633,  13.317, 16.703]
    WWTBAM_BBOX_QC = [ 23.612, 125.380,  13.317, 16.703]
    WWTBAM_BBOX_QD = [137.873, 125.380,  13.317, 16.703]
    
    WWTBAM_BBOX_QAV = [ 36.482,  97.633,  79.564, 16.703]
    WWTBAM_BBOX_QBV = [150.744,  97.633,  79.564, 16.703]
    WWTBAM_BBOX_QCV = [ 36.482, 125.380,  79.564, 16.703]
    WWTBAM_BBOX_QDV = [150.744, 125.380,  79.564, 16.703]
    
    WWTBAM_BBOX_VALUE = [180.414,  43.775,  44.097,  9.507]
    
    
    COLOR_DIFFICULTY = {
        "easy": "6fbf72", # Easy
        "medium": "e3b14d", # Medium
        "hard": "c7524a", # Hard
        "none": "808080", # None
    }

    def __init__(self, width: float = 254, height: float = 190.5) -> None:
        # Rescale all variables
        self.width = width
        self.height = height
        
    def get_frame_margin(self):
        # Define frame margin w.r.t height
        return int(np.ceil(self._FRAME_MARGIN * self.height))

    def get_inner_margin(self):
        # Define frame margin w.r.t height
        return int(np.ceil(self._FRAME_MMARGIN * self.height))
    
    def get_iinner_margin(self):
        # Define frame margin w.r.t height
        return int(np.ceil(self._FRAME_MMMARGIN * self.height))
    
    def get_answer_heights(self):
        ah = int(np.ceil(self._ANSWER_HEIGHT * self.height))
        ahs = int(np.ceil(self._ANSWER_INTER_HEIGHT * self.height))
        return ah, ahs
    
    def get_chart_bbox(self):
        
        # Set bbox values
        margin = self.get_frame_margin()
        bbox_x = 2*margin
        bbox_y = margin
        bbox_w = self.width - 4*margin
        bbox_h = self.height - 2*margin  
        return (bbox_x, bbox_y, bbox_w, bbox_h)
    
    def get_difficulty_bbox(self):
        diameter = self._DIFFICULTY_DIAMETER * self.height
        mmargin = self.get_inner_margin()
        # Set bbox values
        bbox_x = self.width - diameter - mmargin
        bbox_y = self.height - diameter - mmargin
        bbox_w = diameter
        bbox_h = diameter  
        return (bbox_x, bbox_y, bbox_w, bbox_h)
            
    def get_trivia_question_bbox(self):
        # Get margin to frame
        margin = self.get_frame_margin()
        # Set bbox values
        bbox_x = margin
        bbox_y = margin
        bbox_w = self.width - 2*(margin)
        bbox_h = int(self.height*self._QUESTION_HEIGHT)
        return (bbox_x, bbox_y, bbox_w, bbox_h)

    def get_title_bbox(self):
        # Get margin to frame
        margin = self.get_frame_margin()
        # Set bbox values
        bbox_x = margin
        bbox_y = 3*margin
        bbox_w = self.width - 2*(margin)
        bbox_h = 2*margin
        return (bbox_x, bbox_y, bbox_w, bbox_h)
    
    def get_subtitle_bbox(self):
        # Get margin to frame
        margin = self.get_frame_margin()
        # Set bbox values
        bbox_x = 2*margin
        bbox_y = 6*margin
        bbox_w = self.width - 4*(margin)
        bbox_h = margin
        return (bbox_x, bbox_y, bbox_w, bbox_h)
    
    def get_answer_bbox(self):
        # Get margin to frame
        _, hy, _, hq = self.get_trivia_question_bbox()
        margin = self.get_frame_margin()
        # Set bbox values
        bbox_x = margin
        bbox_y = hq + margin
        bbox_w = self.width - 2*(margin)
        bbox_h = self.height - (hy + hq)
        
        return (bbox_x, bbox_y, bbox_w, bbox_h)
    
    def get_answer_cols(self):
        # Get margin to frame
        margin = self.get_frame_margin()
        _, _, aw, _ = self.get_answer_bbox()
        _, am = self.get_answer_heights()
        col = (aw - am) / 2
        col1 = margin
        col2 = margin + col + am
        
        return (col, col1, col2)
