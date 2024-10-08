from typing import Optional, Literal
from bs4 import BeautifulSoup
from pybquiz.db.utils import slow_get_request, to_uuid
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
from pybquiz.db.base import TSVDB
from pybquiz.db.utils import check_code
import re
from pybquiz.const import TriviaConst as TC
from pybquiz.const import WikiConst as WC
import pandas as pd
from tqdm import tqdm
from urllib.parse import urljoin
from rich.prompt import Prompt
import json
import ollama


class WikiScrapper:
        
    # Base for research
    URL_WIKIDATA = "https://www.wikidata.org/w/rest.php/wikibase/v0/entities/items/"
    
    @staticmethod
    def _clean_name_row(text: str):
        # Remove in parenthesis or brackets
        text = re.sub(pattern=r"(\(.{1,}\))", repl="", string=text)
        text = re.sub(pattern=r"(\[.{1,}\])", repl="", string=text)
        # Remove spaces or line break
        text = re.sub(pattern=r"(\n)", repl="", string=text)
        text = re.sub(pattern=r", ", repl=",", string=text)
        text = re.sub(pattern=r"NA", repl="", string=text)

        return text
    

    @staticmethod
    def get_wikipedia_infos(url: str, nmax: Optional[int] = 1500):
        """Clean text to remove question letter (A to D) as well as new line

        Parameters
        ----------
        text : str
            Name of the base url

        Returns
        -------
        urls: list[str]
            Links to pages
        """
        # Remove question letter
        page = slow_get_request(
            url=url,
            header={
                "Content-Type": "application/json",
            },
            delay=0.5, 
            delay_rnd=0.5,
        )  
        
        # If code not valid return None
        if page is None: 
            return []
        
        soup = BeautifulSoup(page.content, features="lxml")     
        sp_body = soup.find_all("div", {"id": "bodyContent"})
        
        if len(sp_body) == 0:
            return None
        
        # Get heading
        sp_h2 = sp_body[0].find_all("div", class_="mw-heading mw-heading2")
        
        if len(sp_h2) == 0:
            return None
        
        # Get title of first text
        sp_h2 = sp_h2[0].text
        # Find header in text
        intro = sp_body[0].text
        intro = intro[:min(intro.find(sp_h2), nmax)]
        # Replace 
        intro = intro.replace("\n", ". ")
        return intro
        
    @staticmethod
    def get_wikidata_infos(code: str, token: str):
        """Clean text to remove question letter (A to D) as well as new line

        Parameters
        ----------
        text : str
            Name of the base url

        Returns
        -------
        urls: list[str]
            Links to pages
        """
        # Remove question letter
        page = slow_get_request(
            url=WikiScrapper.URL_WIKIDATA + code,
            header={
                "Content-Type": "application/json",
                "Authorization": token,
            },
            delay=0.5, 
            delay_rnd=0.5,
        )  
        
        # If code not valid return None
        if page is None: 
            return []
    
        # Final name    
        page = json.loads(page.text)
        full_name = page.get("labels", {}).get("en", None)
        url = page.get("sitelinks", {}).get("enwiki", {}).get("url", None)
        first_name = page.get("statements", {}).get("P735", [dict()])[0].get("value", {}).get("content", "")
        family_name = page.get("statements", {}).get("P734", [dict()])[0].get("value", {}).get("content", "")
        description = page.get("descriptions", {}).get("en", "")    
          
        # Description and infos
        data = {
            WC.KEY_FULLNAME: full_name,
            WC.KEY_URL: url,
            WC.KEY_FIRSTNAME: first_name,
            WC.KEY_FAMILYNAME: family_name,
            WC.KEY_DESCRIPTION: description,
        }
        
        return data
    
    
class WikiNamesDB(TSVDB):
    

    def __init__(
        self, 
        filename_db: Optional[str] = "wikinames",
        cache: Optional[str] = '.cache', 
        chunks: Optional[int] = 50,
        topk: Optional[int] = 10e4,
    ) -> None:
        """ Who wnats to be a millionaire database

        Parameters
        ----------
        filename_db : Optional[str], optional
            Name of the database, by default "wwtbam"
        cache : Optional[str], optional
            Location of the database, by default '.cache'
        chunks : Optional[int], optional
            Size of the update chunks before saving, by default 10
        """        
        
        # Other variables
        self.chunks = chunks
        self.scapper = WikiScrapper()  
        self.topk = topk
        self.token_path = os.path.join(cache, filename_db + ".key")

        # Call super method
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + ".tsv"),
        )
        
        # Check if token exists
        if not os.path.exists(self.token_path):
            # Ask for token
            self.token = Prompt.ask("Enter API Token")
            # Ask if store for next time
            store = Prompt.ask("Store API Token", default="yes")
            if 'y' in store[0].lower():
                # Store key
                f = open(self.token_path, "w+")
                f.write(self.token)
                f.close()
        else:
            f = open(self.token_path, "r")
            self.token = f.read()
            f.close() 

    def initialize(self):
        return pd.DataFrame(
            columns=[
                # Mandatory keys
                WC.KEY_UUID,            
                WC.KEY_NAME, WC.KEY_WIKIDATA, WC.KEY_REGION, WC.KEY_ERA, 
                WC.KEY_GEOGRAPHY, WC.KEY_CITIZEN, 
                WC.KEY_RANK_TOT, WC.KEY_SUBCAT, 
                WC.KEY_BIRTH_LONG, WC.KEY_BIRTH_LAT, WC.KEY_DEATH_LONG, WC.KEY_DEATH_LAT,
                WC.KEY_FULLNAME, WC.KEY_URL, WC.KEY_FIRSTNAME, WC.KEY_FAMILYNAME, 
                WC.KEY_DESCRIPTION, WC.KEY_O_DESCRIPTION,              
            ]
        )
            
        
    def update_bio(self):
        
        # Get addtional info from wikipedia
        for i in tqdm(self.db.index, desc="Read from bio ..."):
            
            # Check entry in dataframe
            url = self.db.loc[i, WC.KEY_URL]
            # Get new data
            context = self.scapper.get_wikipedia_infos(url=url)
            o_context = self._o_ask_short(o_context=context)

            print(o_context)
            
            # If update add 
            
            # if (i % self.chunks) == 0:
            #     self.save()
                
                
    def update(self):
        
        # Set path to file base
        path_csvgz = "~/Downloads/cross-verified-database.csv.gz"
        
        # Find hits per names
        print("Read reference dataset (might take a while) ...")
        df_raw = pd.read_csv(
            path_csvgz, 
            usecols=[
                WC.KEY_NAME, WC.KEY_WIKIDATA, WC.KEY_REGION, WC.KEY_ERA, 
                WC.KEY_GEOGRAPHY, WC.KEY_CITIZEN, 
                WC.KEY_RANK_TOT, WC.KEY_SUBCAT, 
                WC.KEY_BIRTH_LONG, WC.KEY_BIRTH_LAT, WC.KEY_DEATH_LONG, WC.KEY_DEATH_LAT,
            ],
            encoding='iso-8859-1', on_bad_lines='warn'
        )
    
        # Sort dataframe by ranking
        df_raw = df_raw.sort_values(by=WC.KEY_RANK_TOT).reset_index(drop=True)
        # Only keep topk
        df_raw = df_raw[:int(self.topk)]
        # Get first names
        df_raw[WC.KEY_UUID] = [to_uuid(v) for v in df_raw[WC.KEY_NAME].values]
        
        # Get addtional info from wikipedia
        for i in tqdm(df_raw.index, desc="Read from wikidata ..."):
                        
            # Get existing entries
            data = df_raw.loc[i].to_dict()
            
            # Check entry in dataframe
            if data[WC.KEY_UUID] in self.db[WC.KEY_UUID].values:
                continue
            
            # Get new data
            infos = self.scapper.get_wikidata_infos(code=data[WC.KEY_WIKIDATA], token=self.token)
            data.update(infos)
            
            # If update add 
            self.db = pd.concat([self.db, pd.DataFrame([data])], ignore_index=True)
            
            if (i % self.chunks) == 0:
                self.save()
                
        # Final save
        self.save()
        
    
    @staticmethod   
    def _o_ask_short(o_context: str):

        # Get category
        o_question = "Tell me in a single an very short sentence what is so special about this person for without telling his name"
        # Ask main categorys
        response = ollama.generate(
            model='llama3.1', 
            # prompt='Give me a general category title as well as a short description that mostly suits these questions: \n\n "{}"'.format(query)
            prompt="""
                Use the following pieces of context to answer the question at the end.
                \n\nContext: {}
                \n\nQuestion: {}
            """.format(o_context, o_question),
        )
        return response