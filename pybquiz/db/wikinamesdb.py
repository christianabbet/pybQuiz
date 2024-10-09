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
    def get_wikipedia_name(code: str, token: str):
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
        name = page.get("labels", {}).get("en", None)
        return name
          
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
        
        # Given names
        first_names = page.get("statements", {}).get("P735", [dict()])
        first_names = ",".join([n.get("value", {}).get("content", "") for n in first_names])
        
        # Given family
        family_names = page.get("statements", {}).get("P734", [dict()])
        family_names = ",".join([n.get("value", {}).get("content", "") for n in family_names])
        
        # Quick description        
        description = page.get("descriptions", {}).get("en", "")    
          
        # Description and infos
        data = {
            WC.KEY_FULLNAME: full_name,
            WC.KEY_URL: url,
            WC.KEY_FIRSTNAME: first_names,
            WC.KEY_FAMILYNAME: family_names,
            WC.KEY_DESCRIPTION: description,
        }
        
        return data
    
    
class WikiNamesDB(TSVDB):
    

    def __init__(
        self, 
        path_csvgz: Optional[str] = "~/Downloads/cross-verified-database.csv.gz",
        filename_db: Optional[str] = "wikinames",
        cache: Optional[str] = '.cache', 
        chunks: Optional[int] = 50,
        topk: Optional[int] = 10e3,
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
        self.path_csvgz = path_csvgz
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
        
        print("Read reference dataset (might take a while) ...")
        df_raw = pd.read_csv(
            self.path_csvgz, 
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
        
        df_raw = df_raw[[
            WC.KEY_UUID,            
            WC.KEY_NAME, WC.KEY_WIKIDATA, WC.KEY_REGION, WC.KEY_ERA, 
            WC.KEY_GEOGRAPHY, WC.KEY_CITIZEN, 
            WC.KEY_RANK_TOT, WC.KEY_SUBCAT, 
            WC.KEY_BIRTH_LONG, WC.KEY_BIRTH_LAT, WC.KEY_DEATH_LONG, WC.KEY_DEATH_LAT,
        ]]
        
        # Put to zero new columns
        df_raw.loc[:, [WC.KEY_FULLNAME, WC.KEY_URL, WC.KEY_FIRSTNAME, WC.KEY_FAMILYNAME, WC.KEY_DESCRIPTION, WC.KEY_O_DESCRIPTION]] = None
        
        # Merge with previous
        # self.db = pd.read_csv(self.path_db, sep="\t")
        # df_raw.loc[self.db.index, WC.KEY_FULLNAME] = self.db.loc[self.db.index, WC.KEY_FULLNAME]
        # df_raw.loc[self.db.index, WC.KEY_URL] = self.db.loc[self.db.index, WC.KEY_URL]
        # df_raw.loc[self.db.index, WC.KEY_FIRSTNAME] = self.db.loc[self.db.index, WC.KEY_FIRSTNAME]
        # df_raw.loc[self.db.index, WC.KEY_FAMILYNAME] = self.db.loc[self.db.index, WC.KEY_FAMILYNAME]
        # df_raw.loc[self.db.index, WC.KEY_DESCRIPTION] = self.db.loc[self.db.index, WC.KEY_DESCRIPTION]
        return df_raw

        
                
    def update(self):
        
        # Get addtional info from wikipedia
        need_saving = False
        for i in tqdm(self.db.index, desc="Read from wikidata ..."):
                        
            # Get existing entries
            data = self.db.loc[i].to_dict()

            # Get new data
            if pd.isnull(data.get(WC.KEY_DESCRIPTION)):
                infos = self.scapper.get_wikidata_infos(code=data[WC.KEY_WIKIDATA], token=self.token)
                self.db.loc[i, infos.keys()] = infos.values()
                need_saving = True
            
            if pd.isnull(data.get(WC.KEY_O_DESCRIPTION)):
                # Check entry in dataframe
                url = self.db.loc[i, WC.KEY_URL]
                # Get new data
                context = self.scapper.get_wikipedia_infos(url=url)
                o_context = self._o_ask_short(o_context=context)
                self.db.loc[i, WC.KEY_O_DESCRIPTION] = o_context.get("response", None)
                # Notify change
                need_saving = True
            
            if ((i % self.chunks) == 0) & need_saving:
                self.save()
                need_saving = False

        # Get actual names
        firstname_codes = [self.findcode(r) for r in self.db[WC.KEY_FIRSTNAME].dropna() if len(self.findcode(r)) != 0]
        lastname_codes = [self.findcode(r) for r in self.db[WC.KEY_FAMILYNAME].dropna() if len(self.findcode(r)) != 0]
        codes = np.unique(np.concatenate([np.concatenate(firstname_codes), np.concatenate(lastname_codes)]))
        
        for i, c in enumerate(tqdm(codes, desc="Read name codes from wikidata ...")):
            # Get name from db
            c_name = self.scapper.get_wikipedia_name(code=c, token=self.token)
            # Replace occurence
            self.db[WC.KEY_FIRSTNAME] = self.db[WC.KEY_FIRSTNAME].str.replace(c, c_name)
            self.db[WC.KEY_FAMILYNAME] = self.db[WC.KEY_FAMILYNAME].str.replace(c, c_name)
            
            # Save update
            if (i % self.chunks) == 0:
                self.save()
        
        # Final save
        self.save()
        
    
                
    @staticmethod   
    def findcode(s: str):
        return re.findall(r"Q\d{1,20}", s)
        
    @staticmethod   
    def _o_ask_short(o_context: str):

        # Get category
        o_question = "Tell me in a single an very short sentence what is so unique and peculiar about this person for without telling his name"
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