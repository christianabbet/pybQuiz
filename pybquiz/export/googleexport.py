
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googleapiclient
import os
from typing import Optional
import time
import random
import string
import numpy as np

from pybquiz.export.base import Export
from pybquiz.background import BackgroundManager
from pybquiz.const import Const as C
from pybquiz.const import TriviaConst as TC
from pybquiz.export.slidetemplate import SlideTemplate

SCOPES = ["https://www.googleapis.com/auth/presentations","https://www.googleapis.com/auth/spreadsheets"]


def connectGoogleAPI(crendential_file: str, dircache: str):

    # Get creads
    token_file = os.path.join(dircache, "token.json")
    creds = None

    # Token alread exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                crendential_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())
            
    return creds
    
def color_from_string(color: str):
    red = int(color[0:2], 16) / 255
    green = int(color[2:4], 16) / 255
    blue = int(color[4:6], 16) / 255
    return {"red": red, "green": green, "blue": blue}


class GoogleExport(Export):
    
    GOOGLE_SLIDE = "https://docs.google.com/presentation/d/"
    
    FONT_TITLE = 32
    FONT_SUBTITLE = 24
    FONT_QUESTION = 20
    FONT_ANSWER = 12
    
    def __init__(
        self, 
        dump_path: str, 
        dirout: str,
        crendential_file: str, 
        dircache: Optional[str] = ".cache",
    ) -> None:
        
        # Call super
        super().__init__(dump_path=dump_path, dircache=dircache, return_url=True)
        
        # Init local
        self.dirout = dirout
        self.name = os.path.splitext(os.path.basename(dump_path))[0] 
        # Connect to API
        # self.creds = connectGoogleAPI(crendential_file=crendential_file)       
        self.creds = connectGoogleAPI(crendential_file=crendential_file, dircache=dircache)
        # Create presentation
        self.service = build("slides", "v1", credentials=self.creds)
        self.presentation = GoogleExport._create_presentation(title=self.name, service=self.service)
        
        # Process slides
        self.presentation_id = self.presentation.get("presentationId", None)
        # Get slide dims
        self.unit = self.presentation.get("pageSize", {}).get("width", {}).get("unit", None)
        self.height = self.presentation.get("pageSize", {}).get("height", {}).get("magnitude", None)
        self.width = self.presentation.get("pageSize", {}).get("width", {}).get("magnitude", None)
        self.st = SlideTemplate(width=self.width, height=self.height)
        # Check first slide status
        self.is_first_slide = True
    
    def make_title(self, title: str, subtitle: str, img_bg: str):
        
        # Create new slide
        page_id = None
        
        # Check if first slide was already used
        if self.is_first_slide:
            self.is_first_slide = False
            page_id = self.presentation.get("slides", None)[0].get("objectId", None)
        
        # Add slide content
        self._add_title_subtitle(page_id=page_id, title=title, subtitle=subtitle, url_bg=img_bg) 
       
    def make_question(self, data: dict, prefix: str, show_answer: bool, type: str, img_bg: str, img_bg_blur: str):

        if type == "trivia":
            self._add_trivia_question(data=data, prefix=prefix, show_answer=show_answer, url_bg=img_bg_blur)
        else:
            raise NotImplementedError
        
    def save(self):
        # Saving file 
        url_slide = "{}{}".format(self.GOOGLE_SLIDE, self.presentation_id)
        print("Presentation availble: {}".format(url_slide))
    
    
    @staticmethod
    def _create_presentation(title: str, service: googleapiclient.discovery.Resource):
        
        try:
            body = {"title": title}
            presentation = service.presentations().create(body=body).execute()
            print(
                f"Created presentation with ID:{(presentation.get('presentationId'))}"
            )
            return presentation

        except HttpError as error:
            print(f"An error occurred: {error}")
            print("presentation not created")
            return error


    def _add_title_subtitle(self, title: str, subtitle: str = None, page_id: str = None, url_bg: str = None):

        # Create a new square textbox, using the supplied element ID.      
        request = []
        if page_id is None:
            r_slide, page_id = self._add_slide()
            request.extend(r_slide)
        
        if url_bg is not None:
            r_im = self._add_image(
                url=url_bg,
                bbox=[0, 0, self.width, self.height], 
                page_id=page_id, 
                element_id="{}_background".format(page_id), 
            )
            request.extend(r_im)
            
        x, y, w, h = self.st.get_title_bbox()
        r_title = self._add_shape(
            text=title, 
            bbox=[x, y, w, h], 
            page_id=page_id, 
            element_id="{}_title".format(page_id), 
            colorbg=self.st.COLOR_BBOX_BACKGROUND,
            colortext=self.st.COLOR_TEXT,
            fontsize=self.FONT_TITLE
        )
        request.extend(r_title)
        
        if subtitle is not None:
            x, y, w, h = self.st.get_subtitle_bbox()
            r_subtitle = self._add_shape(
                text=subtitle, 
                bbox=[x, y, w, h], 
                page_id=page_id, 
                element_id="{}_subtitle".format(page_id), 
                colorbg=self.st.COLOR_BBOX_BACKGROUND,
                colortext=self.st.COLOR_TEXT,
                fontsize=self.FONT_SUBTITLE
            )
            request.extend(r_subtitle)
        
        # Send request    
        self._send_request(requests=request)
        
    
    
    def _send_request(self, requests, wait: float = 1.0):

        try:
            # Wait time
            start_time = time.time()
            # Execute the request.
            body = {"requests": requests}
            response = (
                self.service.presentations()
                .batchUpdate(presentationId=self.presentation_id, body=body)
                .execute()
            )            
            end_time = time.time()
            time.sleep(max(wait - (end_time - start_time), 0)) 

        except HttpError as error:
            print(error)
            return error

        return response
    

    def _add_image(self, url: str, bbox: list[int], page_id: str, element_id: str):
        
        # Base bounding box
        x, y, w, h = bbox
        h_34 = h
        w_34 = h * (4/3)
        scale = w / w_34
        # Assume image cropped w/ 3/4 ratio
        offset_y = 0.5 * (1 - scale) * h
        
        requests = [
            {
                "createImage": {
                    "objectId": element_id,
                    "elementProperties": {
                        "pageObjectId": page_id,
                        "size": {
                            "height": {"magnitude": h_34, "unit": self.unit}, 
                            "width": {"magnitude": w_34, "unit": self.unit}
                        },
                        "transform": {
                            "scaleX": scale,
                            "scaleY": scale,
                            "translateX": x,
                            "translateY": y + offset_y,
                            "unit": self.unit,
                        },
                    },
                    "url": url
                }
            },                       
        ]
        return requests
        
                
    def _add_shape(self, bbox: list[int], page_id: str, element_id: str, colorbg: str, text: str = None, colortext: str = None, fontsize: int = None, shapeid: str = "ROUND_RECTANGLE"):
        
        # Extract units
        x, y, w, h = bbox
        requests = [
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": shapeid,
                    "elementProperties": {
                        "pageObjectId": page_id,
                        "size": {
                            "height": {"magnitude": h, "unit": self.unit}, 
                            "width": {"magnitude": w, "unit": self.unit}
                            },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": x,
                            "translateY": y,
                            "unit": self.unit,
                        },
                    },
                }
            },
            # Insert text into the box, using the supplied element ID.
            {
                "updateShapeProperties": {
                    "objectId": element_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {
                                "color": {"rgbColor": color_from_string(colorbg)}
                            }
                        },
                        "outline": {
                            "outlineFill": {
                                "solidFill": {
                                    "color": {"rgbColor": color_from_string(colorbg)}
                                } 
                            }
                        }
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color"
                }
            },              
        ]
        
        if text is not None:
            requests_text = [
                {
                    "insertText": {
                        "objectId": element_id,
                        "insertionIndex": 0,
                        "text": text,
                    }
                },
                {
                    "updateTextStyle": {
                        "objectId": element_id,
                        "style": {
                            "foregroundColor": {
                                "opaqueColor": {"rgbColor": color_from_string(colortext)}
                            },
                            "fontSize" : {
                                "magnitude": str(fontsize), "unit": "PT", 
                            },
                        },
                        "fields": "foregroundColor.opaqueColor,fontSize"
                    }
                },             
            ]
            requests.extend(requests_text)
        
        # Send update
        return requests
        # self.send_request(requests=requests)

    def _add_slide(self):
        
        # Check if pageid
        page_id = ''.join(random.choices(string.ascii_letters, k=10))
            
        # Build request
        requests = [
            {
                "createSlide": {
                    "objectId": page_id,
                    "slideLayoutReference": {
                        "predefinedLayout": "BLANK"
                    },
                }
            }
        ]
        # Send
        # self.send_request(requests=requests)
        return requests, page_id
    
    
    def _add_trivia_question(self, data: dict, prefix: str, show_answer: bool, url_bg: str):
        
        # Extract infos
        question = data.get(TC.KEY_QUESTION, C.KEY_ERROR)
        difficulty = data.get(TC.KEY_DIFFICULTY, C.KEY_ERROR)
        answers_order = data.get(TC.EXT_KEY_ORDER, [])
        answers = [data.get(a, None) for a in answers_order]
        answers_id = data.get(TC.EXT_KEY_ORDER_ID, [])
        
        # Create a new square textbox, using the supplied element ID.      
        request = []
        r_slide, page_id = self._add_slide()
        request.extend(r_slide)
            
        # Create a new square textbox, using the supplied element ID.
        if url_bg is not None:
            r_im = self._add_image(
                url=url_bg,
                bbox=[0, 0, self.width, self.height], 
                page_id=page_id, 
                element_id="{}_background".format(page_id), 
            )
            request.extend(r_im)
        
        # Add question title
        x, y, w, h = self.st.get_question_bbox()
        r_q = self._add_shape(
            text = "{}: {}".format(prefix, question),            
            bbox=[x, y, w, h], 
            page_id=page_id, 
            element_id="{}_title".format(page_id), 
            colorbg=self.st.COLOR_BBOX_BACKGROUND,
            colortext=self.st.COLOR_TEXT,
            fontsize=self.FONT_QUESTION
        )
        request.extend(r_q)
        
        if difficulty is not None:
            # Add difficulty
            (x, y, w, h) = self.st.get_difficulty_bbox()
            r_d = self._add_shape(
                bbox=[x, y, w, h], 
                page_id=page_id, 
                shapeid="ELLIPSE", 
                element_id="{}_difficulty".format(page_id), 
                colorbg=self.st.COLOR_DIFFICULTY[difficulty],
            )
            request.extend(r_d)
       
        # Get dimensions
        nQ = len(answers)
        nRows = np.ceil(nQ/2).astype(int)
                        
        # Check if only one proposition and no answer
        if nQ > 1 or show_answer:

            # Get total heigh based on the number of entries
            answer_height, answer_inter_height = self.st.get_answer_heights()
            col, col1, col2 = self.st.get_answer_cols()
            htot = nRows * answer_height + (nRows-1) * answer_inter_height
            (_, ay, _, ah) = self.st.get_answer_bbox()
            hoffset = (ah - htot) / 2
            
            # Add propositions
            for j in range(nQ):
                # Define col
                id_col = j % 2
                id_row = j // 2
                
                # Fix width
                if id_col == 0:
                    left = col1
                else:
                    left = col2
            
                # Add background
                local_offset = id_row * (answer_height + answer_inter_height)
                
                # Check if one or more answers
                color_bg = self.st.COLOR_BBOX_BACKGROUND
                
                if show_answer and j == answers_id:
                    color_bg = self.st.COLOR_BBOX_BACKGROUND_CORRECT
                    
                r_a = self._add_shape(
                    text=answers[j], 
                    bbox=[left, local_offset + ay + hoffset, col, answer_height], 
                    page_id=page_id, 
                    element_id="{}_answer{}".format(page_id, j), 
                    colorbg=color_bg,
                    colortext=self.st.COLOR_TEXT,
                    fontsize=self.FONT_ANSWER
                )   
                request.extend(r_a)  
        
        self._send_request(requests=request)      