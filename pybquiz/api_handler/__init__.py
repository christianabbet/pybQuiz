from pybquiz.api_handler.base import BaseAPIHandler
from pybquiz.api_handler.opentriviadb import OpenTriviaDB
from pybquiz.api_handler.thetriviaapi import TheTriviaAPI


def create_handler(name: str, delay_api: float = 5., verbose: bool = False, clear_cache: bool = False) -> BaseAPIHandler:
    
    if name == "opentriviadb":
        return OpenTriviaDB(delay_api=delay_api, verbose=verbose, clear_cache=clear_cache)
    elif name == "thetriviaapi":
        return TheTriviaAPI(delay_api=delay_api, verbose=verbose, clear_cache=clear_cache)
    else:
        return NotImplementedError()
    
