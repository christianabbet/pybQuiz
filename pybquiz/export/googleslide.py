import os.path
import json
import string
import random
import numpy as np
from tqdm import tqdm
import time
import string

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googleapiclient
from pybquiz.export.slidetemplate import SlideTemplate
from pybquiz.const import PYBConst as C


SCOPES = ["https://www.googleapis.com/auth/presentations","https://www.googleapis.com/auth/spreadsheets"]

def connectGoogleAPI(crendential_file: str):
    # Get creads
    creds_folder = os.path.dirname(crendential_file)
    token_file = os.path.join(creds_folder, "token.json")
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


class GoogleSheetFactory:

    # Url
    GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/"
    
    # Values
    TXT_TEAMS = "Teams"
    TXT_TEAM = "Team"    
    TXT_TOTAL = "Total"
    
    # Table margin
    MARGIN_TOP = 2
    MARGIN_LEFT = 1
    NTEAMS = 20
    
    def __init__(self, name: str, crendential_file: str) -> None:

        # Connect to API
        self.name = name
        self.creds = connectGoogleAPI(crendential_file=crendential_file)
        # # Create presentation
        self.service = build("sheets", "v4", credentials=self.creds)
        self.spreadsheet = GoogleSheetFactory._create_spreadsheet(title=name, service=self.service)
        self.spreadsheet_id = self.spreadsheet.get("spreadsheetId", None)

        
    @staticmethod
    def _create_spreadsheet(title: str, service: googleapiclient.discovery.Resource):
        
        try:
            # Call the Sheets API
            spreadsheet = {"properties": {"title": title}}
            spreadsheet = (
                service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            return spreadsheet

        except HttpError as err:
            print(err)

        
    @staticmethod
    def toColumn(val: int):
        letters = string.ascii_uppercase
        valb = GoogleSheetFactory.toBase(val, base=len(letters))
        return "".join([letters[b] for b in valb])
        
    @staticmethod        
    def toBase(val: int, base: int):
        valb = []
        rest = val
        while rest > 0:
            # Get rest
            modulo = rest % base
            rest = int((rest-modulo) / base)
            valb.append(modulo)
        
        return valb[::-1]
    
    def export(self, dump_path: str):
        
        # Reload data
        with open(dump_path, "r") as f:
            data = json.load(f)
    
        print("Generating spreadsheet for scoring ...")
        # Get info
        Nr = len(data.get(C.ROUNDS, {})) 
        # ROUNDS = ["R{}".format(i+1) for i in range(Nr)]
        ROUNDS = ["{}".format(r[C.TITLE]) for r in data.get(C.ROUNDS, {})]
        HEADERS = np.concat(([self.TXT_TEAMS], ROUNDS, [self.TXT_TOTAL])).tolist()
        TEAMS = [["{}{}".format(self.TXT_TEAM.upper(), i+1)] for i in range(self.NTEAMS)]
        
        # Create first tabel
        TABLE_TOP = self.MARGIN_TOP + 1
        TABLE_LEFT = self.MARGIN_LEFT 
        TABLE_BOTTOM = TABLE_TOP + self.NTEAMS - 1 
        TABLE_RIGHT = TABLE_LEFT + len(HEADERS) - 1

        # ---------- Unsorted
        # Add legend on top
        self.add_values(
            values=[["Unsorted"]], 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT), TABLE_TOP-1, self.toColumn(TABLE_LEFT), TABLE_TOP-1)
        )    
        self.add_values(
            values=[HEADERS], 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT), TABLE_TOP, self.toColumn(TABLE_RIGHT), TABLE_TOP)
        )
        self.add_values(
            values=TEAMS, 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT), TABLE_TOP+1, self.toColumn(TABLE_LEFT), TABLE_TOP + self.NTEAMS)
        )        
        
        # Add random predictions
        rnd_preds = np.random.randint(low=0, high=10, size=(self.NTEAMS, Nr)).tolist()
        self.add_values(
            values=rnd_preds, 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT+1), TABLE_TOP+1, self.toColumn(TABLE_RIGHT-1), TABLE_TOP + self.NTEAMS)
        )        
        # Add average over rounds
        sums = []
        for r in range(TABLE_TOP+1, TABLE_TOP + self.NTEAMS + 1):
            sums.append(["=sum({}{}:{}{})".format(self.toColumn(TABLE_LEFT + 1), r, self.toColumn(TABLE_RIGHT - 1), r)])
        
        self.add_values(
            values=sums, 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_RIGHT), TABLE_TOP+1, self.toColumn(TABLE_RIGHT), TABLE_TOP + self.NTEAMS)
        )       
        
        # ---------- Sorted
        TABLE_TOP2 = self.MARGIN_TOP + 1
        TABLE_LEFT2 = self.MARGIN_LEFT + len(HEADERS) + self.MARGIN_LEFT 
        TABLE_BOTTOM2 = TABLE_TOP2 + self.NTEAMS - 1 
        TABLE_RIGHT2 = TABLE_LEFT2 + len(HEADERS) - 1
        
        self.add_values(
            values=[["Sorted"]], 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT2), TABLE_TOP2-1, self.toColumn(TABLE_LEFT2), TABLE_TOP2-1)
        )    
        self.add_values(
            values=[HEADERS], 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT2), TABLE_TOP2, self.toColumn(TABLE_RIGHT2), TABLE_TOP2)
        )
        
        sort_op = "=sort({}{}:{}{}, {}, False)".format(
            self.toColumn(TABLE_LEFT), TABLE_TOP + 1,
            self.toColumn(TABLE_RIGHT), TABLE_BOTTOM + 1,
            TABLE_RIGHT,
        )        
        self.add_values(
            values=[[sort_op]], 
            range_name="{}{}:{}{}".format(self.toColumn(TABLE_LEFT2), TABLE_TOP2 + 1, self.toColumn(TABLE_LEFT2), TABLE_TOP2 + 1)
        )   
    
        chart_id = self.add_chart(
            n=Nr,
            left=TABLE_LEFT2,
            right=0,
            top=TABLE_TOP2,
            bottom=TABLE_BOTTOM2
        )
        
        url = "{}{}".format(self.GOOGLE_SHEET, self.spreadsheet_id)
        print("Spreadsheet availble: {}".format(url))
        return url, self.spreadsheet_id, chart_id

    def add_chart(self, n: int, left: int, right: int, top: int, bottom: int):
                                        
        r_series = []
        for i in range(n):
            r_serie = {
                "series": {
                    "sourceRange": {
                    "sources": [
                        {
                        "sheetId": 0,
                        "startRowIndex": top-1,
                        "endRowIndex": bottom+1,
                        "startColumnIndex": left+1+i,
                        "endColumnIndex": left+2+i
                        }
                    ]
                    }
                },
                "targetAxis": "LEFT_AXIS"
            }
            r_series.append(r_serie)

        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/charts#BasicChartSpec
        request_body = {
            "requests": [
                {
                "addChart": {
                    "chart": {
                    "spec": {
                        "basicChart": {
                        "chartType": "COLUMN",
                        "stackedType": "STACKED",
                        "legendPosition": "TOP_LEGEND",
                        "domains": [
                            {
                            "domain": {
                                "sourceRange": {
                                "sources": [
                                    {
                                    "sheetId": 0,
                                    "startRowIndex": top-1, 
                                    "endRowIndex": bottom+1,
                                    "startColumnIndex": left,
                                    "endColumnIndex": left+1
                                    }
                                ]
                                }
                            }
                            }
                        ],
                        "series": r_series,
                        "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                        "anchorCell": {
                            "sheetId": 0,
                            "rowIndex": bottom,
                            "columnIndex": left
                        },
                        "offsetXPixels": 50,
                        "offsetYPixels": 50
                        }
                    }
                }
                }
                }
            ]
            }
        
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=request_body
        ).execute()

        # Get chart ID
        response.get("replies", {})
        return response["replies"][0]["addChart"]["chart"]["chartId"]


    def add_values(self, values, range_name: str, wait: float = 1.0):

        try:
            # Wait time
            start_time = time.time()
            # Execute the request.
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            end_time = time.time()
            time.sleep(max(wait - (end_time - start_time), 0)) 
            # print(response)
        except HttpError as error:
            print(error)
            return error

        return result
            
            
class GoogleSlideFactory:
    
    # Requests https://developers.google.com/slides/api/reference/rest/v1/presentations/request
    
    # If modifying these scopes, delete the file token.json.
    GITHUB_RELEASE = "https://github.com/christianabbet/pybQuiz/releases/download/googleslide/"
    GOOGLE_SLIDE = "https://docs.google.com/presentation/d/"
    
    FONT_TITLE = 32
    FONT_SUBTITLE = 24
    FONT_QUESTION = 20
    FONT_ANSWER = 12

    def __init__(self, name: str, crendential_file: str) -> None:

        # Connect to API
        self.name = name
        self.creds = connectGoogleAPI(crendential_file=crendential_file)
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
        
    def export(self, dump_path: str, spreadsheet_id = None, sheet_chart_id = None, background_gen = None):
                
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
            
            # Add scores
            if spreadsheet_id is not None and sheet_chart_id is not None:
                self._add_chartslide(spreadsheet_id=spreadsheet_id, sheet_chart_id=sheet_chart_id, url_bg=url_bg_blurred)   

        # Display link
        url = "{}{}".format(self.GOOGLE_SLIDE, self.presentation_id)
        return url
    
    @staticmethod
    def _get_url(path_img: str):
        url = GoogleSlideFactory.GITHUB_RELEASE + os.path.basename(path_img)
        return url


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
    
    def _add_chartslide(self, spreadsheet_id, sheet_chart_id, page_id: str = None, url_bg: str = None):
        
        # emu4m = {"magnitude": 4000000, "unit": "EMU"}
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
            
        x, y, w, h = self.st.get_chart_bbox()
        r_chart = [
            {
                "createSheetsChart": {
                    "objectId": "{}_chart".format(page_id),
                    "spreadsheetId": spreadsheet_id,
                    "chartId": sheet_chart_id,
                    "linkingMode": "LINKED",
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
                            "unit": "EMU",
                        },
                    },
                }
            }
        ]
                    
        request.extend(r_chart)
        
        self.send_request(requests=request)


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
    