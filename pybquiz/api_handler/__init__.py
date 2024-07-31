from pybquiz.api_handler.base import BaseAPIHandler
from pybquiz.api_handler.opentriviadb import OpenTriviaDB
from pybquiz.api_handler.thetriviaapi import TheTriviaAPI
from pybquiz.api_handler.quizapi import QuiAPI
from pybquiz.api_handler.apininjas import APINinjas

def create_handler(name: str, delay_api: float = 5., token: str = None, verbose: bool = False, clear_cache: bool = False) -> BaseAPIHandler:
    
    if name == "opentriviadb":
        return OpenTriviaDB(delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)
    elif name == "thetriviaapi":
        return TheTriviaAPI(delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)
    elif name == "quizapi":
        return QuiAPI(delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)
    elif name == "apininjas":
        return APINinjas(delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)
    else:
        return NotImplementedError()
    
