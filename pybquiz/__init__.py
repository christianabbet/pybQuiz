from pybquiz.api_handler import create_handler
from typing import List
import yaml
import json

    
class Round():
    
    def __init__(
        self,
        title: str,
        api: str,
        theme_id: int,
        difficulty: List[int] = None,
        type: str = None,
        verbose: bool = False,
        delay_api: float = 5.0,
        clear_cache: bool = False,    
    ):
        
        # Store variables
        self.title = title
        self.theme_id = theme_id
        self.difficulty = difficulty
        self.type = type 
        self.api = api
        
        # Create pybquiz from config file
        self.api = create_handler(name=api, delay_api=delay_api, verbose=verbose, clear_cache=clear_cache)

        self.questions = []
        for i, n in enumerate(self.difficulty):
            # Get question with difficulty level
            qs = self.api.get_questions(category_id=self.theme_id, difficulty=i, n=n, type=self.type)
            # Append to list
            self.questions.extend(qs)
            
    def to_json(self):
        # Create response
        json = {
            "title": self.title,
            "questions": [q.to_json() for q in self.questions]
        }
        
        return json        
            
            
class PybQuiz:
        
    def __init__(
        self,
        title: str,
        delay_api: float,
        cfg_rounds: dict,
        clear_cache: bool = False,
        verbose: bool = False,
    ):
    
        self.title = title
        self.verbose = verbose        
        self.rounds = self._create_rounds(cfg_rounds=cfg_rounds, delay_api=delay_api, clear_cache=clear_cache)
        
    def _create_rounds(self, cfg_rounds: dict, delay_api: float, clear_cache: float):
        
        # Round infos
        rounds = []
        Nr = len(cfg_rounds)
        
        if self.verbose:
            print("Quiz: {}".format(self.title))
            print("Start rounds creation ...")
        
        for i, cfg_round in enumerate(cfg_rounds):
            
            # Update dict
            cfg_round.update({"verbose": self.verbose, "delay_api": delay_api, "clear_cache": clear_cache})
            
            # Display current info
            if self.verbose:
                print("\n--------------")
                print("Round [{}/{}]".format(i+1, Nr))
                print("--------------\n")
                print("Params: {}".format(cfg_round))
                
            # Get round handler
            rounds.append(Round(**cfg_round))
        
        # Return rounds
        return rounds
        
    def to_json(self, file: str):
        # Dump all questions to given file
        json_data = {
            "title": self.title,
            "rounds": [r.to_json() for r in self.rounds]
        }
        # Save file
        with open(file, "w") as f:
            json.dump(json_data, f, indent=4, sort_keys=True)

        # Display result
        if self.verbose:
            print("Saved to {}".format(file))
        
    @staticmethod
    def from_yaml(yaml_path: dict):
        
        # Parse input file
        with open(yaml_path) as stream:
            data = yaml.safe_load(stream)
        
        # Base infos
        cfg_base = data.get("BaseInfo", {})
        delay_api = cfg_base.get("delay_api", 5.)
        title = cfg_base.get("title", "")
        verbose = cfg_base.get("verbose", False) 
        clear_cache = cfg_base.get("clear_cache", False) 
        cfg_rounds = data.get("Rounds", [])

        # Create quiz
        quiz = PybQuiz(
            title = title,
            delay_api = delay_api,
            cfg_rounds=cfg_rounds, 
            clear_cache=clear_cache,
            verbose=verbose
        )
        return quiz