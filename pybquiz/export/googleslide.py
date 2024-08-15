import os.path
import json
import string
import random
import numpy as np
from tqdm import tqdm
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googleapiclient
from pybquiz.export.slidetemplate import SlideTemplate
from pybquiz.const import PYBConst as C


def color_from_string(color: str):
    red = int(color[0:2], 16) / 255
    green = int(color[2:4], 16) / 255
    blue = int(color[4:6], 16) / 255
    return {"red": red, "green": green, "blue": blue}

class GoogleSlideFactory:
    
    # Requests https://developers.google.com/slides/api/reference/rest/v1/presentations/request
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/presentations"]
    GITHUB_RELEASE = "https://github.com/christianabbet/pybQuiz/releases/download/googleslide/"
    
    # The ID of a sample presentation.
    PRESENTATION_ID = "1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc"
    
    FONT_TITLE = 32
    FONT_SUBTITLE = 24
    FONT_QUESTION = 20
    FONT_ANSWER = 12

    def __init__(self, name: str, crendential_file: str) -> None:

        # Connect to API
        self.name = name
        self.creds = GoogleSlideFactory._connect(crendential_file=crendential_file)
        # Create presentation
        self.service = build("slides", "v1", credentials=self.creds)
        self.presentation = GoogleSlideFactory._create_presentation(title=name, service=self.service)
        
        # Process slides
        self.presentation_id = self.presentation.get("presentationId", None)
        # Get slide dims
        self.unit = self.presentation.get("pageSize", {}).get("width", {}).get("unit", None)
        self.height = self.presentation.get("pageSize", {}).get("height", {}).get("magnitude", None)
        self.width = self.presentation.get("pageSize", {}).get("width", {}).get("magnitude", None)
        self.st = SlideTemplate(width=self.width, height=self.height)
        
    def export(self, dump_path: str, background_gen = None):
        
        # Reload data
        with open(dump_path, "r") as f:
            data = json.load(f)
        
        # First slide already exists, get if from presentation
        print("Generate title slide")
        page_id = self.presentation.get("slides", None)[0].get("objectId", None)
        url_bg_title = self._get_url(background_gen.get_background("Pub Quiz"))        
        url_bg_paper = self._get_url(background_gen.get_background("Quiz paper sheets"))        
        self._add_title_subtitle(page_id=page_id, title=data[C.TITLE], subtitle=data[C.AUTHOR], url_bg=url_bg_title) 
                            
        # Create rounds
        Nround = len(data[C.ROUNDS])
        for i in range(Nround):            
            # Variables
            str_round = "Round {}: {}".format(i+1, data[C.ROUNDS][i][C.TITLE])
            catname = data[C.ROUNDS][i][C.QUESTIONS][0][C.CATEGORY]
            url_bg = self._get_url(background_gen.get_background(catname, blurred=False))
            url_bg_blurred = self._get_url(background_gen.get_background(catname, blurred=True))
                      
            print("[{}/{}] Generating round {} ...".format(i+1, Nround, catname))                        
            self._add_title_subtitle(title=str_round, url_bg=url_bg) 
                
            Nquestion = len(data[C.ROUNDS][i][C.QUESTIONS])
            for j in tqdm(range(Nquestion), desc="Questions"):
                # Add question slide
                answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.ANSWERS]
                difficulty = data[C.ROUNDS][i][C.QUESTIONS][j][C.DIFFICULTY]                
                self._add_question(
                    i=j+1, 
                    question=data[C.ROUNDS][i][C.QUESTIONS][j][C.QUESTIONS], 
                    answers=answers,
                    difficulty=difficulty,
                    url_bg=url_bg_blurred,
                ) 
                
            self._add_title_subtitle(title="Exchange paper sheets", url_bg=url_bg_paper)                      
            self._add_title_subtitle(title=str_round, subtitle="Answers", url_bg=url_bg)                 
                        
            # Iterate over questions (answers)
            for j in tqdm(range(Nquestion), desc="Answers"):
                # Add question slide
                answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.ANSWERS]
                difficulty = data[C.ROUNDS][i][C.QUESTIONS][j][C.DIFFICULTY]                                
                correct_answers = data[C.ROUNDS][i][C.QUESTIONS][j][C.CORRECT_ANSWERS]

                self._add_question(
                    i=j+1, 
                    question=data[C.ROUNDS][i][C.QUESTIONS][j][C.QUESTIONS], 
                    answers=answers,
                    difficulty=difficulty,
                    answers_id=correct_answers,                    
                    url_bg=url_bg_blurred,
                )    

            # Final slide
            self._add_title_subtitle(title="Bring back paper sheets", url_bg=url_bg_paper)        

    
    @staticmethod
    def _get_url(path_img: str):
        url = GoogleSlideFactory.GITHUB_RELEASE + os.path.basename(path_img)
        return url
    
    @staticmethod
    def _connect(crendential_file: str):
                # Get creads
        creds_folder = os.path.dirname(crendential_file)
        token_file = os.path.join(creds_folder, "token.json")
        creds = None

        # Token alread exists
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, GoogleSlideFactory.SCOPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    crendential_file, GoogleSlideFactory.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, "w") as token:
                token.write(creds.to_json())
                
        return creds

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
        self.send_request(requests=request)
        

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
        # Send update
        # self.send_request(requests=requests)
        return requests
        
    def _add_question(self, i: int, question: str, difficulty: int = None, answers: list[str] = None, answers_id: list[int] = None, page_id: str = None, url_bg: str = None):
        
        # Create a new square textbox, using the supplied element ID.      
        request = []
        if page_id is None:
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
            text = "Q{}: {}".format(i, question),
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
        if nQ <= 1 and answers_id is None:
            return

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
            
            if answers_id is not None and j in answers_id:
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
        
        self.send_request(requests=request)           

                
    def _add_shape(self, bbox: list[int], page_id: str, element_id: str, colorbg: str, text: str = None, colortext: str = None, fontsize: int = None, shapeid: str = "ROUND_RECTANGLE"):
        
        # Extract units
        x, y, w, h = bbox
        requests = [
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": "ROUND_RECTANGLE",
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
    
    
    def send_request(self, requests, wait: float = 1.0):

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
            # print(response)
        except HttpError as error:
            print(error)
            return error

        return response
    