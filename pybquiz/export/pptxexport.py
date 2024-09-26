import os
from typing import Optional
from tqdm import tqdm
from pptx import Presentation     
from pptx.util import Mm
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pathlib import Path
from sys import platform
import pptx

from pybquiz.export.base import Export
from pybquiz.background import BackgroundManager
from pybquiz.const import Const as C
from pybquiz.export.slidetemplate import SlideTemplate


class PPTXExport(Export):
    
    # Class constants
    TITLE_SUBTITLE = 0
    TITLE_CONTENT = 1
    SECTION_HEADER = 2
    TWO_CONTENT = 3
    COMPARISON = 4
    TITLE = 5
    BLANK = 6
    CONTENT_CAPTION = 7
    IMAGE_CAPTION = 8

    # Font
    FONT_TITLE = 40
    FONT_SUBTITLE = 28
    FONT_QUESTION = 28
    FONT_ANSWER = 20

    # Font location linux
    FONT_PATH = "/usr/share/fonts"
    
    def __init__(
        self, 
        dump_path: str, 
        dirout: str,
        width: Optional[float] = 254, 
        height: Optional[float] = 190.5,
        dircache: Optional[str] = ".cache",
    ) -> None:
        
        # Call super
        super().__init__(dump_path=dump_path, dircache=dircache)
        
        # Init local
        self.dirout = dirout
        self.fileout = os.path.join(dirout, os.path.splitext(os.path.basename(dump_path))[0] + ".pptx")

        self.width = width
        self.height = height
        self.root = Presentation() 
        self.st = SlideTemplate(width=width, height=height)
        self.pfont = self._get_system_fonts()
    
    def make_title(self, title: str, subtitle: str, img_bg: str):
        self._add_title_subtitle(
            title=title,
            subtitle=subtitle,
            img_bg=img_bg,
            pfont=self.pfont
        )
        
    def make_question(self, data: dict, index: int, show_answer: bool, type: str, img_bg: str, img_bg_blur: str):

        if type == "trivia":
            self._add_trivia_question(data=data, index=index, show_answer=show_answer, img_bg=img_bg_blur)
        
    def save(self):
        # Saving file 
        self.root.save(self.fileout)  
    
    def _add_trivia_question(self, data: dict, index: int, show_answer: bool, img_bg: str):
            
            
        # Extract infos
        difficulty = ""
        
        # Add slide and question            
        question_slide = self.root.slides.add_slide(self.root.slide_layouts[PPTXExport.BLANK]) 
        
        # Add text shape
        shapes =  question_slide.shapes

        if img_bg is not None:
            shapes.add_picture(img_bg, Mm(0), Mm(0), height=Mm(self.height))
            
        # Add question
        (x, y, w, h) = self.st.get_question_bbox()
        PPTXExport._add_frame(
            shapes=shapes,
            bbox=[Mm(x), Mm(y), Mm(w), Mm(h)],
            text=None,
            font_file=self.pfont,
            color_bg=RGBColor.from_string(self.st.COLOR_BBOX_BACKGROUND), 
            color_text=RGBColor.from_string(self.st.COLOR_TEXT), 
            color_line=RGBColor.from_string(self.st.COLOR_BBOX_LINE), 
        )
        
        # def _add_question(self, i: int = 1, question: str = "", difficulty: int = None, answers: list[str] = [], answers_id: int = None, img_bg: str = None, pfont: str = None):

        if difficulty is not None:
            # Add difficulty
            (x, y, w, h) = self.st.get_difficulty_bbox()
            PptxFactory._add_frame(
                shapes=shapes,
                bbox=[Mm(x), Mm(y), Mm(w), Mm(h)],
                text=None,
                font_file=pfont,
                shapeid=MSO_SHAPE.OVAL,         
                color_bg=RGBColor.from_string(self.st.COLOR_DIFFICULTY[difficulty]), 
                color_line=RGBColor.from_string(self.st.COLOR_DIFFICULTY[difficulty]), 
            )
                    
        (x, y, w, h) = self.st.get_question_bbox()
        m_in = self.st.get_inner_margin()
        PptxFactory._add_frame(
            shapes=shapes,
            bbox=[Mm(x + m_in), Mm(y + m_in), Mm(w - 2*m_in), Mm(h - 2*m_in)],
            text = "Q{}: {}".format(i, question),
            color_bg=None,
            color_line=None,                    
            font=PptxFactory.FONT_QUESTION,
            alignement=PP_ALIGN.LEFT,
            font_file=pfont,
        )

        self._add_answers(question_slide, answers, answers_id, pfont=pfont)       
            
             
    def _get_system_fonts(self, template: str = "Amiri-Regular"):
        # On linux need to look for font
        if "linux" in platform:
            # Find fonts
            fonts = [str(r) for r in Path(self.FONT_PATH).rglob("*.ttf")]
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
            
    def _add_title_subtitle(self, title: str = "", subtitle: str = None, img_bg: str = None, pfont: str = None):
        
        # Add slide
        title_slide = self.root.slides.add_slide(self.root.slide_layouts[PPTXExport.BLANK]) 
        shapes =  title_slide.shapes            
                    
        # Add background
        if img_bg is not None:
            shapes.add_picture(img_bg, Mm(0), Mm(0), height=Mm(self.height))
        
        (x, y, w, h) = self.st.get_title_bbox()
        PPTXExport._add_frame(
            shapes=shapes,
            bbox=[Mm(x), Mm(y), Mm(w), Mm(h)],
            text=title,
            font=PPTXExport.FONT_TITLE,
            font_file=pfont,
            color_bg=RGBColor.from_string(self.st.COLOR_BBOX_BACKGROUND), 
            color_text=RGBColor.from_string(self.st.COLOR_TEXT), 
            color_line=RGBColor.from_string(self.st.COLOR_BBOX_LINE), 
        )
        
        if subtitle is not None:
            (x, y, w, h) = self.st.get_subtitle_bbox()
            PPTXExport._add_frame(
                shapes=shapes,
                bbox=[Mm(x), Mm(y), Mm(w), Mm(h)],
                text=subtitle,
                font= PPTXExport.FONT_SUBTITLE,
                font_file=pfont,
                color_bg=RGBColor.from_string(self.st.COLOR_BBOX_BACKGROUND), 
                color_text=RGBColor.from_string(self.st.COLOR_TEXT), 
                color_line=RGBColor.from_string(self.st.COLOR_BBOX_LINE), 
            )
            
    @staticmethod
    def _add_frame(
        shapes: pptx.shapes.shapetree.SlideShapes, 
        bbox: list[int], 
        text: str, 
        font: int = 0, 
        color_bg: str = None, 
        color_text: str = None, 
        color_line: str = None, 
        shapeid: int = MSO_SHAPE.ROUNDED_RECTANGLE,         
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
        