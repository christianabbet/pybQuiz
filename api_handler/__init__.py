from api_handler.base import BaseAPIHandler
from api_handler.opentriviadb import OpenTriviaDB

def create_handler(name: str) -> BaseAPIHandler:
    
    if name == "opentriviadb":
        return OpenTriviaDB()
    else:
        return NotImplementedError()