import os
import yaml

from pybquiz.api_handler.base import BaseAPIHandler
from pybquiz.api_handler.opentriviadb import OpenTriviaDB
from pybquiz.api_handler.thetriviaapi import TheTriviaAPI
from pybquiz.api_handler.quizapi import QuizAPI
from pybquiz.api_handler.apininjas import APINinjas
import pybquiz.api_handler as API

__all__ = ['OpenTriviaDB', "TheTriviaAPI", "QuizAPI", "APINinjas"]


def create_handler(name: str, delay_api: float = 5., token: str = None, verbose: bool = False, clear_cache: bool = False) -> BaseAPIHandler:
    
    if not hasattr(API, name):
        return NotImplementedError()
    
    cls = getattr(API, name) 
    return cls(delay_api=delay_api, token=token, verbose=verbose, clear_cache=clear_cache)


def from_yaml(yaml_file: str):
    
    
    # Check if file exists
    if os.path.exists(yaml_file):
        with open(yaml_file) as stream:
            data_token = yaml.safe_load(stream)
            
    # Define apis
    apis = {}
    
    for api_name in __all__:
        # Check if attributes exists
        api_token = data_token.get(api_name, None)
        try:
            apis[api_name] = create_handler(name=api_name, token=api_token)
        except NotImplementedError:
            continue
        
    return apis