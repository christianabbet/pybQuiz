from pybquiz.api_handler import create_handler
from typing import List
import yaml


# class Round():
    
#     def __init__(
#         self,
#         title: str,
#         api: str,
#         theme_id: int,
#         difficulty: List[int] = None,
#         type: str = None,
#         verbose: bool = False,
#         delay_api: float = 5.0,
#         force_reload: bool = False,    
#         **kwrags     
#     ):
        
#         # Store variables
#         self.title = title
#         self.theme_id = theme_id
#         self.difficulty = difficulty
        # self.type = type 
        

class Round:
    pass
    
    
class PybQuiz:
    
        
    def __init__(
        self,
        rounds: List[Round]
    ):
        self.rounds = rounds
        

    @staticmethod
    def from_yaml(config: dict):
        
        
        # Get input information
        cfg_path = args.cfg
        if not os.path.exists(cfg_path):
            raise FileNotFoundError
        
        # Parse input file
        with open(args.cfg) as stream:
            data = yaml.safe_load(stream)
        
        # Base infos
        cfg_base = data.get("BaseInfo", {})
        delay_api = cfg_base.get("delay_api", 5.)
        verbose = cfg_base.get("verbose", False)    
        # Round infos
        cfg_rounds = data.get("Rounds", [])


        # Create pybquiz from config file
        r = create_handler()