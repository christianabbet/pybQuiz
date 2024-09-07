from typing import Optional, Literal
from bs4 import BeautifulSoup
from pybquiz.db.utils import slow_get_request, to_uuid
from urllib.parse import urljoin
import string
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
from pybquiz.db.base import TriviaTSVDB, TriviaQ
from pybquiz.db.utils import check_code
import re
import time
import requests


class KenQuizKey:
    
    # # Dataframe columns
    KEY_URL = "url"
    KEY_QUESTION = "question"
    KEY_CORRECT_ANSWER = "correct_answer"
    KEY_UUID = "uuid"
    KEY_CATEGORY = "category"
    KEY_CATEGORY_SUB = "category_sub"
    KEY_DIFFICULTY = "difficulty"

    
    # # Base website
    WEB_HOME = "https://www.kensquiz.co.uk/quizzes/"

    WEB_CLASS_MAIN = "kensquizsite_frontpagewidget"
    WEB_CLASS_SUB = "kensquizsite_categorylistlink"
    WEB_CLASS_QUESTION_LIST = "kensquizsite_questionlistitem"
    WEB_CLASS_QUESTION = "kensquizsite_questionlist_question"
    WEB_CLASS_ANSWER = "kensquizsite_questionlist_answer"
    
    WEB_POST_URL = "https://www.kensquiz.co.uk/the-quiz-vault/"
    WEB_POST_HEADER = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    N_DIFF = [10, 20, 30]
            
class KenQuizScrapper:
        
    @staticmethod
    def get_base_urls(url_base: str):
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
        page = slow_get_request(url=url_base)
                
        # If code not valid return None
        if page is None: 
            return []
    
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")     
        sp_quiz_list = soup.find_all("div", class_=KenQuizKey.WEB_CLASS_MAIN)
        
        urls = []
        titles = []
        for item in sp_quiz_list:
            # Find url and title
            url = item.find("a").get("href", None)
            title = item.find("h2").text
            # Append
            urls.append(url)
            titles.append(title)

        return urls, titles
    
        
    @staticmethod
    def get_sub_url(sub_base: str, suffix: Optional[str] = "answers"):
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
        page = slow_get_request(url=sub_base)
                
        # If code not valid return None
        if page is None: 
            return []
    
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")     
        sp_quiz_list = soup.find_all("a", class_=KenQuizKey.WEB_CLASS_SUB)
        
        urls = []
        titles = []
        for item in sp_quiz_list:
            # Find url and title
            url = item.get("href", None)
            title = item.text
            if suffix is not None:
                url = urljoin(url + "/", suffix)
            # Append
            urls.append(url)
            titles.append(title)

        return urls, titles
    
    @staticmethod
    def slow_post_diff(
        url: str, 
        data: dict,
        delay: Optional[float] = 6.0, 
        delay_rnd: Optional[float] = 1.0
    ):

        # Add random delays to avoid detections
        delay = delay + delay_rnd*(np.random.rand())
            
        # Build request
        start = time.time()    
        page = requests.post(
            url, 
            headers=KenQuizKey.WEB_POST_HEADER,
            data=data
        )
        is_valid = check_code(status_code=page.status_code)
        end = time.time()

        # Wait for api time
        time.sleep(max(delay - (end - start), 0)) 
        
        # If not valid
        if not is_valid:
            return None
                    
        return page

    @staticmethod
    def get_question_post(url: str, data: dict):                    
        page = KenQuizScrapper.slow_post_diff(url=url, data=data)
        return KenQuizScrapper.get_questions(page)
    
    @staticmethod
    def get_question_get(url: str):
        page = slow_get_request(url=url)
        return KenQuizScrapper.get_questions(page)
                
    @staticmethod
    def get_questions(page):
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
                
        # If code not valid return None
        if page is None: 
            return [], []
    
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")     
        sp_quiz_list = soup.find_all("li", class_= KenQuizKey.WEB_CLASS_QUESTION_LIST)

        # iterate over questions
        text_questions = []
        text_answers = []
        
        for i, q in enumerate(sp_quiz_list):
            # Check if two line in aswer
            sp_question = q.find("span", class_= KenQuizKey.WEB_CLASS_QUESTION)
            sp_answer = q.find("span", class_= KenQuizKey.WEB_CLASS_ANSWER)
            
            # Error in question
            if sp_question is None or sp_answer is None:
                continue
            
            # Get texts
            text_question = sp_question.text
            text_answer = sp_answer.text
            
            # Check if mulitple answer
            mcq = len(re.findall(pattern="(\[[a-e]\])", string=text_question)) != 0
            if mcq:
                continue
            
            # Append
            text_questions.append(text_question)
            text_answers.append(text_answer)

        return text_questions, text_answers
    
    
    
class KenQuizDB(TriviaTSVDB):
    
    def __init__(
        self, 
        filename_db: Optional[str] = "kenquiz",
        cache: Optional[str] = '.cache', 
        chunks: Optional[int] = 10,
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
        self.scapper = KenQuizScrapper()     
        
        # Call super method
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + ".tsv"),
        )

    def initialize(self):
        return pd.DataFrame(
            columns=[
                KenQuizKey.KEY_URL, KenQuizKey.KEY_QUESTION, 
                KenQuizKey.KEY_DIFFICULTY, KenQuizKey.KEY_CORRECT_ANSWER,
                KenQuizKey.KEY_UUID, KenQuizKey.KEY_CATEGORY, KenQuizKey.KEY_CATEGORY_SUB,
            ]
        )
            
    def update(self):
        
        # Get existing entries
        exist_urls = self.db[KenQuizKey.KEY_URL].unique()
        
        # Get main quiz categories
        main_urls, main_categories = self.scapper.get_base_urls(url_base=KenQuizKey.WEB_HOME)

        # Get all quiz for given category
        n_main = len(main_urls)
        for i in range(n_main):
            
            # Get main url to query
            main_url = main_urls[i]
            main_cat = main_categories[i]
            # Progress
            print("[{}/{}] {}".format(i+1, n_main, main_cat))
            # Get sub urls
            sub_urls, sub_categories = self.scapper.get_sub_url(sub_base=main_url)
                        
            # Check if url exists in db
            sub_urls = [s for s in sub_urls if s not in exist_urls]
            
            # Itrate over remainings
            n_sub = len(sub_urls)
            for j in tqdm(range(n_sub), desc="Sub topics ..."):
                
                # Get main url to query
                sub_url = sub_urls[j]
                sub_cat = sub_categories[j]
                # Read questions
                text_questions, text_answers = self.scapper.get_question_get(sub_url)
                n_q = len(text_questions)
                
                # Store questions
                datas = []
                for k in range(n_q):
                    
                    # Question
                    data = {
                        KenQuizKey.KEY_URL: sub_url, 
                        KenQuizKey.KEY_CATEGORY: main_cat, 
                        KenQuizKey.KEY_CATEGORY_SUB: sub_cat,
                        KenQuizKey.KEY_QUESTION: text_questions[k], 
                        KenQuizKey.KEY_DIFFICULTY: None, 
                        KenQuizKey.KEY_CORRECT_ANSWER: text_answers[k],
                        KenQuizKey.KEY_UUID: to_uuid(text_questions[k]), 
                    }
                    
                    datas.append(data)
            
                # Check if value to append
                if len(datas) == 0:
                    continue
                
                # Append to value
                datas = pd.DataFrame(datas)
                self.db = pd.concat([self.db, datas])
                
                if j%self.chunks == 0:
                    self.save()
        
        # Final save
        self.save()
        

    def update_brutforce(self, n_tot: int = 500, n_query: int = 20):
             
        # Clean database
        # base = self.db[KenQuizKey.KEY_DIFFICULTY].isna()
        # df_base = self.db[base].drop_duplicates(subset="uuid").drop("difficulty", axis=1)
        # df_new = self.db[~base].drop_duplicates(subset="uuid").dropna(axis=1)[["uuid", "difficulty"]]
        # df = pd.merge(df_base, df_new, on=KenQuizKey.KEY_UUID, how="left")
        
        # Get random questions to have difficulty set
        for i, nd in enumerate(KenQuizKey.N_DIFF):
            print("[{}] Difficulty: {}".format(i+1, nd))
            for j in tqdm(range(n_tot)):
                # Get set of questions
                text_questions, text_answers = self.scapper.get_question_post(
                    url=KenQuizKey.WEB_POST_URL,
                    data={
                        "quantity": n_query, 
                        "quizvaultsubmit": "Go!", 
                        "category_id": -1, 
                        "question_difficulty": nd,
                    },
                )
          
                # Store questions
                uuids = np.unique([to_uuid(t) for t in text_questions])
                uuids = pd.DataFrame(uuids, columns=[KenQuizKey.KEY_UUID])
                uuids[KenQuizKey.KEY_DIFFICULTY] = nd

                # Check if value to append
                if len(uuids) == 0:
                    continue
                
                #Merge with existing
                df_merge = self.db.merge(right=uuids, how="left", on=KenQuizKey.KEY_UUID, indicator=True)
                is_new = df_merge[(df_merge['_merge'] == "both")].index
                self.db.loc[is_new, KenQuizKey.KEY_DIFFICULTY] = nd
                
                if j%self.chunks == 0:
                    self.save()
                    
            # Final save
            self.save()
         
    def finalize(self):
        pass
        """ Check for abnormality in database """
                
        # # Check duplicates in questions
        # self.db.drop_duplicates(subset=WWTBAMKey.KEY_UUID, keep=False, inplace=True)
        # self.db.dropna(subset=WWTBAMKey.KEY_VALUE, inplace=True)

        # # Convert to difficulty level (year based)
        # self.db[WWTBAMKey.KEY_DIFFICULTY] = np.nan
        
        # for _, df_cand in self.db.groupby(WWTBAMKey.KEY_URL):
        #     # Check year
        #     year = df_cand.iloc[0][WWTBAMKey.KEY_AIR_DATE]
        #     numbers = WWTBAM.convert_values_to_number(
        #         values=df_cand[WWTBAMKey.KEY_VALUE].values.tolist(),
        #         year=year, 
        #         lang=self.lang
        #     )
            
        #     # If exists, append value
        #     if numbers is not None:           
        #         self.db.loc[df_cand.index, WWTBAMKey.KEY_DIFFICULTY] = numbers
                
        # # Drop item if question of answer are empty
        # self.db.dropna(
        #     subset=[
        #         WWTBAMKey.KEY_QUESTION, WWTBAMKey.KEY_CORRECT_ANSWER, 
        #         # WWTBAMKey.KEY_AIR_DATE, WWTBAMKey.KEY_DIFFICULTY,
        #     ],
        #     inplace=True,
        # )
                

    def pprint(self):
        
        name = self.__class__.__name__        
        df_print = pd.crosstab(
            index=self.db[KenQuizKey.KEY_CATEGORY], 
            columns=self.db[KenQuizKey.KEY_DIFFICULTY]
        )
        df_print.columns = [str(c) for c in df_print.columns]

        # Group by categories and create df
        data_all = {KenQuizKey.KEY_CATEGORY: "All"}
        data_all.update(df_print.sum().to_dict())
        # Add all other values
        data = [data_all]
        for _, d in df_print.reset_index().iterrows():
            data.append(d.to_dict())
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {}".format(name)))
        
        markdown = markdown_table(data).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        
        """ Display stats on database """
        
        # name = self.__class__.__name__
        # n_candidates = len(self.db[WWTBAMKey.KEY_URL].unique())
        # n_questions = len(self)
        # v_min = self.db[WWTBAMKey.KEY_VALUE].min()
        # v_max = self.db[WWTBAMKey.KEY_VALUE].max()
        # d_min = self.db[WWTBAMKey.KEY_AIR_DATE].min()
        # d_max = self.db[WWTBAMKey.KEY_AIR_DATE].max()
        
        # # Create a console
        # data = {
        #     "Lang": self.lang,
        #     "Candidates": n_candidates,
        #     "Questions": n_questions,
        #     "Values": "{}-{}".format(int(v_min), int(v_max)),
        #     "Air date": "{}-{}".format(int(d_min), int(d_max)),
        # }
        
        # # Add difficulty ranges
        # difficulties = pd.cut(self.db[WWTBAMKey.KEY_DIFFICULTY], bins=WWTBAMKey.PPRINT_BINS).value_counts(sort=False)
        # data.update({str(k): v for k, v in difficulties.items()})
        
        # # Display final output
        # console = Console() 
        # console.print(Panel.fit("Database {} ({})".format(name, self.lang)))
        
        # markdown = markdown_table([data]).set_params(row_sep = 'markdown')
        # markdown.quote = False
        # markdown = markdown.get_markdown()
        # console.print(markdown)
        
        
    def __getitem__(self, index: int):
        pass
        # # Get row
        # serie = self.db.iloc[index]
        
        # # data = {
        # #     TriviaQ.KEY_QUESTION: serie[WWTBAMKey.KEY_QUESTION],
        # #     TriviaQ.KEY_CATEGORY: None,
        # #     TriviaQ.KEY_UUID: serie[WWTBAMKey.KEY_UUID],
        # # }
    
        # return data
    