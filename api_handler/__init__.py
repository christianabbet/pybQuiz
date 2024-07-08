from api_handler.base import BaseAPIHandler
from api_handler.opentriviadb import OpenTriviaDB
from api_handler.thetriviaapi import TheTriviaAPI

def create_handler(name: str, delay_api: float = 5., verbose: bool = False) -> BaseAPIHandler:
    
    if name == "opentriviadb":
        return OpenTriviaDB(delay_api=delay_api, verbose=verbose)
    elif name == "thetriviaapi":
        return TheTriviaAPI(delay_api=delay_api, verbose=verbose)
    else:
        return NotImplementedError()