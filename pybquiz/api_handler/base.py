from abc import abstractmethod
from typing import List
from typing import Union, Tuple
import time
import requests
import json
import numpy as np
from py_markdown_table.markdown_table import markdown_table
import pickle
import os
from pybquiz.elements import Questions
import urllib3

CACHE_FOLDER = ".cache"

class BaseAPIHandler:
   
    def __init__(
        self,
        verbose: bool = False,
        delay_api: float = 5.0,
        clear_cache: bool = False,
    ) -> None:
        
        # Laod variables
        self.force_reload = False
        self.verbose = verbose
        self.delay_api = delay_api
        # Define cache file
        self.cache_dir = os.path.join(os.path.dirname(__file__), ".cache")
        self.cache_file = os.path.join(self.cache_dir, self.__class__.__name__.lower() + ".npy")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Check if already exists:
        if not os.path.exists(self.cache_file) or clear_cache:
            # Reload from web (update)
            cats, cats_id, cats_type, cats_diff = self.initialize_db()
            with open(self.cache_file, 'wb') as f:
                np.save(f, cats)
                np.save(f, cats_id)
                np.save(f, cats_type)
                np.save(f, cats_diff)                

        # Relaod from cache
        with open(self.cache_file, 'rb') as f:
            self.categories = np.load(f)
            self.categories_id = np.load(f)
            self.categories_type = np.load(f)
            self.categories_difficulty = np.load(f)
    
        
    def slow_request(self, url: str, header: dict = None, params: dict = None):
        """
        Send URL get request after a delay in seconds.

        Parameters
        ----------
        url : str
            URL get query to send.

        Returns
        -------
        dict
            Parsed result to URL query.
        """
        # Wait to not query too many times in a row            
        time.sleep(self.delay_api) 
        
        if self.verbose:
            print("Send request url: {}, key: {}".format(url, params))
            
        # Build request
        result = urllib3.request(
            method="GET", 
            url=url,
            headers=header,
            fields=params, #  Add custom form fields
        )
        
        # Old method
        # result = requests.get(url=url, params=params)
        
        return json.loads(result.data)
    
    def __repr__(self):
        """
        Create a pretty print for DB

        Returns
        -------
        pprint: str
            Pretty print
        """
        
        data = []
        N = len(self.categories)
        # Create table
        for i in range(N):
            data.append({
                "ID": self.categories_id[i],
                "Catgory": self.categories[i],
                "Easy": int(self.categories_difficulty[i, 0]),
                "Medium": int(self.categories_difficulty[i, 1]),
                "Hard": int(self.categories_difficulty[i, 2]),
                "Text": int(self.categories_type[i, 0]),
                "Image": int(self.categories_type[i, 1]),
            })
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown').get_markdown()
        pprint = "{}\n\n{}".format(self.__class__.__name__.lower(), markdown)
        return pprint

    
    @abstractmethod 
    def initialize_db(self) -> Union[List[str], List[int], np.ndarray, np.ndarray]:
        """
        Initialize database infromation

        Returns
        -------
        categories : List[int]
            List of N categories as strings.
        categories_id : List[int]
            List of N categories as ints.
        categories_difficulty : np.ndarray
            Array of N categories and 3 difficulty level (easy, medium, hard)
        categories_type : np.ndarray
            Array of N categories types
        """
        raise NotImplementedError

    @abstractmethod 
    def get_questions(self, category_id: int = None, n: int = 10, difficulty: int = 0, type: str = "text") -> List[Questions]:
        raise NotImplementedError

           
