from pybquiz.api_handler import create_handler
from typing import List
import yaml


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
        **kwrags     
    ):
        
        # Store variables
        self.title = title
        self.theme_id = theme_id
        self.difficulty = difficulty
        self.type = type 
        
        # Create pybquiz from config file
        self.api = create_handler(name=api, delay_api=delay_api, verbose=verbose, clear_cache=clear_cache)
        
    
    
class PybQuiz:
    
        
    def __init__(
        self,
        rounds: List[Round]
    ):
        self.rounds = rounds
        

    @staticmethod
    def from_yaml(yaml_path: dict):
        
        # Parse input file
        with open(yaml_path) as stream:
            data = yaml.safe_load(stream)
        
        # Base infos
        cfg_base = data.get("BaseInfo", {})
        delay_api = cfg_base.get("delay_api", 5.)
        verbose = cfg_base.get("verbose", False) 
        clear_cache = cfg_base.get("clear_cache", False) 
           
        # Round infos
        cfg_rounds = data.get("Rounds", [])
        rounds = []
        
        for cfg_round in cfg_rounds:
            
            # Display current info
            if verbose:
                print(cfg_round)
                
            # Get round handler
            cfg_round.update({"verbose": verbose, "delay_api": delay_api, "clear_cache": clear_cache})
            rounds.append(Round(**cfg_round))
            
        # Create quiz
        quiz = PybQuiz(rounds=rounds)
        return quiz