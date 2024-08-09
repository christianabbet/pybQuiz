from pptx.util import Mm
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
import pptx
from pptx.presentation import Presentation as PObject
from pptx import Presentation     
import numpy as np
import json
from pybquiz.const import PYBConst as C
from sys import platform
import os
from pathlib import Path


def pos_to_char(pos):
    return chr(pos + 97)


class PptxFactory:
        
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
    S_FRAME_MARGIN_TINY = 5
    S_FRAME_MARGIN_TTINY = 2
    # Question frame
    S_QUEST_BBOX_W = S_FRAME_WITDH - (2 * S_FRAME_MARGIN)
    S_QUEST_BBOX_H = 30
    # Answer frames
    S_ANSWERS_WIDTH = S_QUEST_BBOX_W
    S_ANSWERS_TOP = S_QUEST_BBOX_H + 2*S_FRAME_MARGIN
    S_ANSWERS_HEIGHT = S_FRAME_HEIGH - S_ANSWERS_TOP - S_FRAME_MARGIN
    
    S_ANSWER_COL_MARGIN = S_FRAME_MARGIN / 2
    S_ANSWER_SPACE = 5
    S_ANSWER_COL_WIDTH = (S_ANSWERS_WIDTH - S_ANSWER_SPACE) / 2
    S_ANSWER_COL1_LEFT = S_FRAME_MARGIN
    S_ANSWER_COL2_LEFT = S_FRAME_MARGIN + S_ANSWER_COL_WIDTH + S_ANSWER_SPACE
    S_ANSWER_ROW_HEIGHT_MAX = 20

    # Font
    FONT_TITLE = 40
    FONT_SUBTITLE = 28
    FONT_QUESTION = 28
    FONT_ANSWER = 20
    
    # COLORS
    COLOR_BBOX_BACKGROUND = RGBColor.from_string("2881a1")
    COLOR_BBOX_BACKGROUND_CORRECT = RGBColor.from_string("f3a600")
    COLOR_BBOX_LINE = RGBColor.from_string("2881a1")
    COLOR_TEXT = RGBColor.from_string("ffffff")
    
    # Font location linux
    FONT_PATH = "/usr/share/fonts"
    
    @staticmethod
    def export(dump_path: str, outfile: str, background_gen = None):
        
        # Reload data
        with open(dump_path, "r") as f:
            data = json.load(f)
            
        # Save results
        root = Presentation() 
        
        # Get font reference
        pfont = PptxFactory.get_system_fonts()

        # Add splide to presetation
        img_bg = background_gen.get_background("Pub Quiz")
        PptxFactory._add_title_subtitle(title=data[C.TITLE], subtitle=data[C.AUTHOR], root=root, img_bg=img_bg, pfont=pfont) 
                    
        # Create rounds
        Nround = len(data[C.ROUNDS])
        for i in range(Nround):
            # Create title slide
            catname = data[C.ROUNDS][i][C.QUESTIONS][0][C.CATEGORY]
            img_bg = background_gen.get_background(catname, blurred=False)
            img_bg_blurred = background_gen.get_background(catname, blurred=True)
            str_round = "Round {}: {}".format(i+1, data[C.ROUNDS][i][C.TITLE])
            PptxFactory._add_title_subtitle(root=root, title=str_round, img_bg=img_bg, pfont=pfont)            
            
            Nquestion = len(data[C.ROUNDS][i][C.QUESTIONS])
            for j in range(Nquestion):
                # Add question slide
                answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.ANSWERS]
                PptxFactory._add_question(
                    root=root, 
                    i=j+1, 
                    question=data[C.ROUNDS][i][C.QUESTIONS][j][C.QUESTIONS], 
                    answers=answers,
                    img_bg=img_bg_blurred,
                    pfont=pfont,
                ) 
                
            PptxFactory._add_title_subtitle(root=root, title=str_round, subtitle="Answers", img_bg=img_bg, pfont=pfont)            
               
            # Iterate over questions (answers)
            for j in range(Nquestion):
                # Add question slide
                answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.ANSWERS]
                correct_answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.CORRECT_ANSWERS]
                PptxFactory._add_question(
                    root=root, 
                    i=j+1, 
                    question=data[C.ROUNDS][i][C.QUESTIONS][j][C.QUESTIONS], 
                    answers=answers,
                    answers_id=correct_answers,
                    img_bg=img_bg_blurred,
                    pfont=pfont,
                )                 

                
        # Saving file 
        root.save(outfile)             
        
    @staticmethod
    def get_system_fonts(template: str = "Amiri-Regular"):
        # On linux need to look for font
        if "linux" in platform:
            # Find fonts
            fonts = [str(r) for r in Path(PptxFactory.FONT_PATH).rglob("*.ttf")]
            tfonts = [f for f in fonts if "{}.ttf".format(template) in f]
            if len(tfonts) == 0:
                # Not font, take random
                pfont = fonts[0]
            else:
                # Take tmeplate font
                pfont = tfonts[0]
            # Look for template
            return pfont
        else:
            return None


    @staticmethod
    def _add_frame(
        shapes: pptx.shapes.shapetree.SlideShapes, 
        bbox: list[int], 
        text: str, 
        font: int = FONT_TITLE, 
        shapeid: int = MSO_SHAPE.ROUNDED_RECTANGLE, 
        color_bg: pptx.dml.color.RGBColor = COLOR_BBOX_BACKGROUND, 
        color_text: pptx.dml.color.RGBColor = COLOR_TEXT, 
        color_line: pptx.dml.color.RGBColor =  COLOR_BBOX_LINE, 
        alignement: int = PP_ALIGN.CENTER,
        font_file: str = None,
    ):
        
        shape = shapes.add_shape(
            shapeid, 
            bbox[0], bbox[1], bbox[2], bbox[3],
        )
        shape.shadow.inherit = False            
        tf = shape.text_frame
        
        if color_bg is not None:
            shape.fill.solid()
            shape.fill.fore_color.rgb = color_bg
        else:
            shape.fill.background()
            
        if color_line is not None:
            shape.line.fill.solid()
            shape.line.fill.fore_color.rgb = color_line
        else:
            shape.line.fill.background()

        if text is not None:
            tf.text = text
            tf.fit_text(max_size=font, font_file=font_file) 
            tf.paragraphs[0].alignment = alignement
        
        if color_text is not None:
            tf.paragraphs[0].font.color.rgb = color_text
        
    @staticmethod
    def _add_title_subtitle(root: PObject, title: str = "", subtitle: str = None, img_bg: str = None, pfont: str = None):
        
            # Add slide
            title_slide = root.slides.add_slide(root.slide_layouts[PptxFactory.BLANK]) 
            shapes =  title_slide.shapes            
                        
            # Add background
            if img_bg is not None:
                shapes.add_picture(img_bg, Mm(0), Mm(0), height=Mm(PptxFactory.S_FRAME_HEIGH))
            
            PptxFactory._add_frame(
                shapes=shapes,
                bbox=[                
                    Mm(PptxFactory.S_FRAME_MARGIN), 
                    Mm(3*PptxFactory.S_FRAME_MARGIN), 
                    Mm(PptxFactory.S_FRAME_WITDH-2*PptxFactory.S_FRAME_MARGIN), 
                    Mm(2*PptxFactory.S_FRAME_MARGIN),
                ],
                text=title,
                font=PptxFactory.FONT_TITLE,
                font_file=pfont,
            )
            
            if subtitle is not None:
                PptxFactory._add_frame(
                    shapes=shapes,
                    bbox=[                
                        Mm(2*PptxFactory.S_FRAME_MARGIN), 
                        Mm(6*PptxFactory.S_FRAME_MARGIN), 
                        Mm(PptxFactory.S_FRAME_WITDH-4*PptxFactory.S_FRAME_MARGIN), 
                        Mm(PptxFactory.S_FRAME_MARGIN),
                    ],
                    text=subtitle,
                    font= PptxFactory.FONT_SUBTITLE,
                    font_file=pfont,
                )
                        
            
    @staticmethod
    def _add_question(root: PObject, i: int = 1, question: str = "", answers: list[str] = [], answers_id: list[int] = None, img_bg: str = None, pfont: str = None):
        
            # Add slide and question            
            question_slide = root.slides.add_slide(root.slide_layouts[PptxFactory.BLANK]) 
            
            # Add text shape
            shapes =  question_slide.shapes

            if img_bg is not None:
                shapes.add_picture(img_bg, Mm(0), Mm(0), height=Mm(PptxFactory.S_FRAME_HEIGH))
                
            # Add question
            PptxFactory._add_frame(
                shapes=shapes,
                bbox=[                
                    Mm(PptxFactory.S_FRAME_MARGIN), 
                    Mm(PptxFactory.S_FRAME_MARGIN), 
                    Mm(PptxFactory.S_QUEST_BBOX_W), 
                    Mm(PptxFactory.S_QUEST_BBOX_H),
                ],
                text=None,
                font_file=pfont,
            )
            
            PptxFactory._add_frame(
                shapes=shapes,
                bbox=[                
                    Mm(PptxFactory.S_FRAME_MARGIN + PptxFactory.S_FRAME_MARGIN_TINY), 
                    Mm(PptxFactory.S_FRAME_MARGIN + PptxFactory.S_FRAME_MARGIN_TINY), 
                    Mm(PptxFactory.S_QUEST_BBOX_W - 2*PptxFactory.S_FRAME_MARGIN_TINY), 
                    Mm(PptxFactory.S_QUEST_BBOX_H - 2*PptxFactory.S_FRAME_MARGIN_TINY),
                ],
                text = "Q{}: {}".format(i, question),
                color_bg=None,
                color_line=None,                    
                font=PptxFactory.FONT_QUESTION,
                alignement=PP_ALIGN.LEFT,
                font_file=pfont,
            )

            PptxFactory._add_answers(question_slide, answers, answers_id, pfont=pfont)

            
    @staticmethod
    def _add_answers(slide, answers: list[str], answers_id: list[int] = None, pfont: str = None):
                           
            nQ = len(answers)
            nRows = np.ceil(nQ/2).astype(int)
                                    
            # Check if only one proposition and no answer
            if nQ <= 1 and answers_id is None:
                return
            
            # Get total heigh based on the number of entries
            htot = nRows * PptxFactory.S_ANSWER_ROW_HEIGHT_MAX + (nRows-1) * PptxFactory.S_ANSWER_SPACE
            hoffset = (PptxFactory.S_ANSWERS_HEIGHT - htot) / 2
            
            # Add propositions
            for j in range(nQ):
                # Define col
                id_col = j % 2
                id_row = j // 2
                
                # Fix width
                if id_col == 0:
                    left = PptxFactory.S_ANSWER_COL1_LEFT
                else:
                    left = PptxFactory.S_ANSWER_COL2_LEFT
            
                # Add background
                local_offset = id_row * (PptxFactory.S_ANSWER_ROW_HEIGHT_MAX + PptxFactory.S_ANSWER_SPACE)
                shapes =  slide.shapes
                
                # Check if one or more answers
                a = answers[j]
    
                if answers_id is not None and j in answers_id:
                    color_bg = PptxFactory.COLOR_BBOX_BACKGROUND_CORRECT
                else:
                    color_bg = PptxFactory.COLOR_BBOX_BACKGROUND
                    
                PptxFactory._add_frame(
                    shapes=shapes,
                    bbox=[                
                        Mm(left), 
                        Mm(PptxFactory.S_ANSWERS_TOP + local_offset + hoffset), 
                        Mm(PptxFactory.S_ANSWER_COL_WIDTH), 
                        Mm(PptxFactory.S_ANSWER_ROW_HEIGHT_MAX)
                    ],
                    text = None,
                    color_bg=color_bg,
                    color_line=color_bg,
                    font_file=pfont,
                )
                            
                PptxFactory._add_frame(
                    shapes=shapes,
                    bbox=[                
                        Mm(left + PptxFactory.S_FRAME_MARGIN_TTINY), 
                        Mm(PptxFactory.S_ANSWERS_TOP + local_offset + hoffset + PptxFactory.S_FRAME_MARGIN_TTINY), 
                        Mm(PptxFactory.S_ANSWER_COL_WIDTH - 2*PptxFactory.S_FRAME_MARGIN_TTINY), 
                        Mm(PptxFactory.S_ANSWER_ROW_HEIGHT_MAX - 2*PptxFactory.S_FRAME_MARGIN_TTINY)
                    ],
                    text=a,
                    color_bg=None,
                    color_line=None,
                    font=PptxFactory.FONT_ANSWER,
                    alignement=PP_ALIGN.LEFT,
                    font_file=pfont,
                )
                                
            