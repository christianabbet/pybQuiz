import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth


class GoogleSlideFactory:
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/presentations"]

    # The ID of a sample presentation.
    PRESENTATION_ID = "1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc"

    @staticmethod
    def export(title: str, crendential_file: str):
        
        # Connect to API
        creds = GoogleSlideFactory._connect(crendential_file=crendential_file)
        # Create presentation
        presentation = GoogleSlideFactory._create_presentation(title=title, creds=creds)
        # Process slides
        print("lol")
        
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
    def _create_presentation(title: str, creds: google.oauth2.credentials.Credentials):
        
        try:
            service = build("slides", "v1", credentials=creds)

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
