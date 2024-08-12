
import time
import os
from pybquiz.api_handler import from_yaml
import yaml
import re

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
import pandas as pd
import numpy as np
     
class ConfigGenerator:
    
    # Intro
    STR_TITLE = "PybQuiz Creator"
    STR_WELCOME = "Welcome to the PybQuiz creator, we will help you to generate your own quiz from scratch. Answer the following questions please."
    DIFF_LUT = [
        ("Random", None),
        ("Easy", np.array([1., 0., 0.])),
        ("Somewhat Easy", np.array([0.5, 0.5, 0.])),
        ("Balanced", np.array([0.2, 0.6, 0.2])),
        ("Somewhat Hard", np.array([0., 0.5, 0.5])),
        ("Hard", np.array([0., 0., 1.])),
    ]
    
    def __init__(self, yaml_api_file: str, dirout: str) -> None:
        self.console = Console() 
        self.dirout = dirout
        self.apis = from_yaml(yaml_file=yaml_api_file)        
    
    def run_terminal(self):
        
        # Get all categories
        offset = 100
        dfs = []
        for j, api_name in enumerate(self.apis.keys()):
            # Get stats
            c = self.apis[api_name].categories
            c_id = self.apis[api_name].categories_id
            # Create data frame
            df = pd.DataFrame({"c": c, "c_id": c_id, "p_id": c_id + (j+1)*offset})
            df["api"] = api_name
            dfs.append(df)
            
        # Create categoriy display
        dfs = pd.concat(dfs)
            
        # Create list
        cat_print = []
        for n, d in dfs.sort_values(by="p_id", ascending=True).groupby("api", sort=False):
            cat_print.append("[red]{}".format(n))
            cat_print.extend(["  {}: {}".format(a, b) for a, b in zip(d["p_id"], d["c"])])
        
        # Difficulties
        diff_print = ["{}: {}".format(i, d) for (i, (d, _)) in enumerate(self.DIFF_LUT)]
        
        self.console.print(Align.center(Panel(self.STR_TITLE), vertical="middle"))
        self.console.print(self.STR_WELCOME)
        self.console.print(Panel(Columns(cat_print, equal=True, expand=True, column_first=True, title="Available categories")))
        self.console.print(Panel(Columns(diff_print, equal=True, expand=True, column_first=True, title="Available Difficulties")))
                
        # Question quiz
        input_qname = Prompt.ask("Enter quiz name", default="My Amazing quiz")
        input_qauthor = Prompt.ask("Enter author name", default="Your Quizmaster")
        input_rcount = int(Prompt.ask("Enter number of rounds", default="5"))
        input_qcount = int(Prompt.ask("Enter number of questions per round", default="10"))
        
        # Iterate over all rounds creations
        base_info = {"title": input_qname, "author": input_qauthor}
        rounds_info = []
        
        for r in range(input_rcount):
            # Get answer
            answer = Prompt.ask("Round {}: Enter categories and difficulty".format(r+1), default="109, 0")
            # Parse result
            _cat, _diff = answer.split(',')
            _cat = int(_cat)
            _diff = int(_diff)
            # Get dfficulty
            _, diff_ratio = self.DIFF_LUT[_diff]
            if diff_ratio is None:
                diff_ratio = np.random.rand(3)
                diff_ratio /= diff_ratio.sum()
            # Get actual numbers
            diff_ratio = (diff_ratio * input_qcount).round().astype(int)
            diff_ratio[-1] = input_qcount - np.sum(diff_ratio[:-1])
            # Fix ratio
            df_row = dfs[dfs["p_id"] == _cat]
            round_info = {
                "title": df_row["c"].values[0].replace("_", " ").title(), 
                "api": df_row["api"].values[0], 
                "theme_id": int(df_row["c_id"].values[0]), 
                "difficulty": diff_ratio.tolist(),
            }
            rounds_info.append(round_info)
            
        # Merge data
        data = {
            "BaseInfo": base_info,
            "Rounds": rounds_info
        }
        
        # Export as config file
        name_simple = re.sub('[^A-Za-z0-9]+', '', input_qname).lower()
        cfg_file = os.path.join(self.dirout, "{}.yml".format(name_simple))
        
        # Save output
        with open(cfg_file, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        
        self.console.print("Config saved {}...".format(cfg_file))
        return cfg_file