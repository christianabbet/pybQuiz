
import time
import os
import yaml
import re
import string
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.table import Table
from rich.layout import Layout
import pandas as pd
import numpy as np
from typing import Optional
from pybquiz.generator.base import QGenerator
import json

from pybquiz.const import Const as C
     
class GeneratorTerminal:
    
    # Intro
    STR_TITLE = "PybQuiz Creator"
    
    def __init__(
        self, 
        dirout: str,
        dbs: list[QGenerator],
    ) -> None:
        self.console = Console() 
        self.dirout = dirout    
        
        # Databases
        self.dbs = dbs
    
    def run_terminal(self):
        
        # Get all categories
        # dfs = []
        codes = [d.get_codes() for d in self.dbs]
        letters = string.ascii_uppercase

        for i, c in enumerate(codes):
            
            # Get infos
            title = "({}) {}".format(letters[i], c.get("title", "Error"))
            content = c.get("content", [])
            description = c.get("description", "Error")
            option = c.get("option", "")
            
            # New group
            print(Align.center(Panel(title), vertical="middle"))
            print(description)
            print("[red]Options[/red]: " + option)
            print(self.build_table(content=content))
            
        # Question quiz
        # input_qname = Prompt.ask("Enter quiz name", default="My Amazing quiz")
        # input_qauthor = Prompt.ask("Enter author name", default="Your Quizmaster")
        # input_rcount = int(Prompt.ask("Enter number of rounds", default="1"))
        input_qname = "sdsdsd"
        input_qauthor = "sdsdsdsdssd"
        input_rcount = 1
        
        dump_data = {
            C.KEY_TITLE: input_qname,
            C.KEY_AUTHOR: input_qauthor,
            C.KEY_ROUNDS: []
        }
        
        for r in range(input_rcount):
            # Get answer
            # answer = Prompt.ask("Round {}: Enter code".format(r+1))
            answer = "A-2-10-HEK"
            # answer = "B-1"
            # Parse anser
            code = answer.split("-")[0]
            code = string.ascii_uppercase.find(code)
            # Check code
            if code == -1:
                print("Error unknown code {}".format(code))
                continue
            # Get round info
            qs = self.dbs[code].get_round(options=answer)
            dump_data[C.KEY_ROUNDS].append(qs)
        
        # Dump data
        # # Export as config file
        name_simple = re.sub('[^A-Za-z0-9]+', '', input_qname).lower()
        dump_file = os.path.join(self.dirout, "{}.json".format(name_simple))
        os.makedirs(self.dirout, exist_ok=True)
        # # Save output
        with open(dump_file, 'w') as outfile:
            json.dump(dump_data, outfile, indent=4, sort_keys=True)

        return dump_file


    @staticmethod
    def build_table(content, title: Optional[str] = None):
        
        # Build table
        table = Table(title=title, expand=True)

        table.add_column("ID", justify="left", style="cyan", no_wrap=True)
        table.add_column("Category", justify="left", style="magenta")
        table.add_column("# Questions", justify="left", style="green")

        for row in content:
            index = row.get("index", 0)
            category = row.get("category", "")
            number = row.get("number", 0)
            table.add_row(str(index), category, str(number))

        return table
        

        # # Iterate over all rounds creations
        # base_info = {"title": input_qname, "author": input_qauthor}
        # rounds_info = []
        
        # for r in range(input_rcount):
        #     # Get answer
        #     answer = Prompt.ask("Round {}: Enter categories and difficulty".format(r+1), default="{}, 0".format(dfs.loc[0, "p_id"]))
        #     # Parse result
        #     _cat, _diff = answer.split(',')
        #     _cat = in        
        # with open(dump_file, "w") as f:C
        #     _diff = int(_diff) - 1
        #     # Get dfficulty
        #     _, diff_ratio = self.DIFF_LUT[_diff]
        #     if diff_ratio is None:
        #         diff_ratio = np.random.rand(3)
        #         diff_ratio /= diff_ratio.sum()
        #     # Get actual numbers
        #     diff_ratio = (diff_ratio * input_qcount).round().astype(int)
        #     diff_ratio[-1] = input_qcount - np.sum(diff_ratio[:-1])
        #     # Fix ratio
        #     df_row = dfs[dfs["p_id"] == _cat]
        #     round_info = {
        #         "title": df_row["c"].values[0].replace("_", " ").title(), 
        #         "api": df_row["api"].values[0], 
        #         "theme_id": int(df_row["c_id"].values[0]), 
        #         "difficulty": diff_ratio.tolist(),
        #     }
        #     rounds_info.append(round_info)
            
        # # Merge data
        # data = {
        #     "BaseInfo": base_info,
        #     "Rounds": rounds_info
        # }
        
        # # Export as config file
        # name_simple = re.sub('[^A-Za-z0-9]+', '', input_qname).lower()
        # cfg_file = os.path.join(self.dirout, "{}.yml".format(name_simple))
        
        # # Save output
        # with open(cfg_file, 'w') as outfile:
        #     yaml.dump(data, outfile, default_flow_style=False)
        
        # self.console.print("Config saved {}...".format(cfg_file))
        # return cfg_file