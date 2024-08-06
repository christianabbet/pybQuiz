from pptx.util import Mm
from pptx.dml.color import RGBColor
from pptx.presentation import Presentation as PObject
import numpy as np


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
    def add_question(root: PObject, i: int = 1, question: str = "", answers: list[str] = [], answers_id: list[int] = None):
        
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
            # Add question below
            SlideFactory._add_answers(question_slide, answers, answers_id)
            
            
    @staticmethod
    def _add_answers(slide, answers: list[str], answers_id: list[int] = None):
                                
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
                txBox = slide.shapes.add_textbox(left, top, Mm(SlideFactory.S_ANSWER_COL_WIDTH), Mm(SlideFactory.S_ANSWER_ROW_HEIGHT_MAX))
                tf = txBox.text_frame
                # CHeck if one or more answers
                a = answers[j]
                if nQ > 1:
                    a = "{}: {}".format(pos_to_char(j), a)
                # Set text
                tf.text = a
                tf.fit_text(max_size=SlideFactory.FONT_QUESTION, font_file=SlideFactory.get_system_fonts())
                
                if answers_id is not None and j in answers_id:
                    tf.paragraphs[0].font.color.rgb = RGBColor.from_string("8fce00")
            
            