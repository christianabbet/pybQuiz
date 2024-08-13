import numpy as np


class SlideTemplate:
    
    # Do not modify 
    _FRAME_MARGIN = 0.1
    _FRAME_MMARGIN = 0.025
    _FRAME_MMMARGIN = 0.0125
    _QUESTION_HEIGHT = 0.15
    _ANSWER_HEIGHT = 0.1
    _ANSWER_INTER_HEIGHT = 0.025

    # # COLORS
    COLOR_BBOX_BACKGROUND = "2881a1"
    COLOR_BBOX_BACKGROUND_CORRECT = "f3a600"
    COLOR_BBOX_LINE = "2881a1"
    COLOR_TEXT = "ffffff"
    
    def __init__(self, width: float = 254, height: float = 190.5) -> None:
        # Rescale all variables
        self.width = width
        self.height = height
        
    def get_frame_margin(self):
        # Define frame margin w.r.t height
        return np.ceil(self._FRAME_MARGIN * self.height).astype(int)

    def get_inner_margin(self):
        # Define frame margin w.r.t height
        return np.ceil(self._FRAME_MMARGIN * self.height).astype(int)
    
    def get_iinner_margin(self):
        # Define frame margin w.r.t height
        return np.ceil(self._FRAME_MMMARGIN * self.height).astype(int)
    
    def get_answer_heights(self):
        ah = np.ceil(self._ANSWER_HEIGHT * self.height).astype(int)
        ahs = np.ceil(self._ANSWER_INTER_HEIGHT * self.height).astype(int)
        return ah, ahs
            
    def get_question_bbox(self):
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
        _, hy, _, hq = self.get_question_bbox()
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
