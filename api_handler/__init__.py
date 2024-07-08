from api_handler.base import BaseAPIHandler
from api_handler.opentriviadb import OpenTriviaDB
from api_handler.thetriviaapi import TheTriviaAPI

def create_handler(name: str, verbose: bool = False) -> BaseAPIHandler:
    
    if name == "opentriviadb":
        return OpenTriviaDB(verbose=verbose)
    elif name == "thetriviaapi":
        return TheTriviaAPI(verbose=verbose)
    else:
        return NotImplementedError()