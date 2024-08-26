from typing import Optional
from bs4 import BeautifulSoup
from pybquiz.db.utils import slow_request
from urllib.parse import urljoin
import string
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
import re
import hashlib

class WWRBAMKey():
    # Dataframe columns
    KEY_URL = "url"
    KEY_VALUE = "value"
    KEY_QUESTION = "question"
    KEY_WRONG_ANSWER_1 = "wrong_answers_1"
    KEY_WRONG_ANSWER_2 = "wrong_answers_2"
    KEY_WRONG_ANSWER_3 = "wrong_answers_3"
    KEY_CORRECT_ANSWER = "correct_answer"
    KEY_AIR_DATE = "air_date"
    KEY_UUID = "uuid"
    

class WWTBAMScrapper():
    
    # Base website
    WEB_BASE = "https://millionaire.fandom.com"
    
    # Contestant files
    WEB_CONTESTANT_LANG = {
        'us': 'wiki/Category:Contestants_from_the_U.S.',
        'uk': 'wiki/Category:Contestants_from_the_UK',
    }
    WEB_CONTESTANT_LIST_CLASS = "category-page__member-link"
    WEB_CONTESTANT_LIST_TAG = "a"
    WEB_CONTESTANT_PARAMS_FROM = "from"
    
    # Color answers
    WEB_ANSWER_OK = "#0bda51"
    
    @staticmethod
    def _clean_text(text: str):
        """Clean text to remove question letter (A to D) as well as new line

        Parameters
        ----------
        text : str
            Text to clean

        Returns
        -------
        text_: str
            Cleaned text
        """
        # Remove question letter
        text_ = re.sub(r'⬥ [A-D]: ', '', text)
        # Remove new line
        text_ = re.sub(r'\n', '', text_)
        return text_
        
    @staticmethod
    def _extract_value(text: str):
        """Extract question value in $ or £. The format is assumed to be $/£xxx,xxx,xxx.

        Parameters
        ----------
        text : str
            Text containing the value

        Returns
        -------
        match: str
            Matched value
        """
        # Get money valeu in text
        matches = re.findall(r'[$£]((?:\d{1,3},)?(?:\d{1,3},)?\d{3})', text)
        # CHeck if found
        if len(matches) == 0:
            return None
        else:
            return matches[0]
        
    @staticmethod
    def get_contestant_questions_by_url(url: str):
        """ Get question of the contestant based on the page url

        Parameters
        ----------
        url : str
            Url to the contestant page

        Returns
        -------
        data: dict
            DIctionnary containing all the parsed questions
        """
        # Get contestant page
        page = slow_request(url=url)
        # If code not valid return None
        if page is None: 
            return []
        
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")
        # Get all questions
        questions_body = soup.find_all("tbody")

        # general infos
        # Get other info ([0]: City, [1]: Air date, [2]: Money won)
        infos = soup.find_all("div", class_="pi-data-value pi-font")
        air_date = infos[1].text

        # Store data
        data = []

        # Drop empty versions
        for qbody in questions_body:
            # Get all lines
            qbody_lines = qbody.find_all("td")
            # Should have 6 items
            if len(qbody_lines) < 6:
                continue
            # Assume first line is amount of money
            text_value = qbody_lines[0].text
            # Second line is the question
            text_joker = qbody_lines[1].find("small")
            # Remove from list
            if text_joker is not None:
                text_joker.decompose()
            text_question = qbody_lines[1].text
            # Rest is answers
            text_answers = [q.text for q in qbody_lines[2:6]]
            color_answer = [WWTBAMScrapper.WEB_ANSWER_OK in q.get("style", "") for q in qbody_lines[2:6]]
            # Get ids
            id_wrong = np.array(np.nonzero(np.logical_not(color_answer))).flatten()
            id_correct = np.array(np.nonzero(color_answer)).flatten()
            # Check if answer available
            if len(id_correct) != 1 or len(id_wrong) != 3 or len(text_answers) != 4:
                continue
            # Finale data merge
            qclean = WWTBAMScrapper._clean_text(text_question) 
            # Hash text (unique question)
            uuid = hashlib.md5(qclean.encode('utf8')).hexdigest()
            data_row = {
                # export to TSV (tab) + add hash for question
                WWRBAMKey.KEY_URL: url,
                WWRBAMKey.KEY_VALUE: WWTBAMScrapper._extract_value(text_value),
                WWRBAMKey.KEY_QUESTION: qclean,
                WWRBAMKey.KEY_CORRECT_ANSWER: WWTBAMScrapper._clean_text(text_answers[id_correct.item()]),
                WWRBAMKey.KEY_WRONG_ANSWER_1: WWTBAMScrapper._clean_text(text_answers[id_wrong[0]]),
                WWRBAMKey.KEY_WRONG_ANSWER_2: WWTBAMScrapper._clean_text(text_answers[id_wrong[1]]),
                WWRBAMKey.KEY_WRONG_ANSWER_3: WWTBAMScrapper._clean_text(text_answers[id_wrong[2]]),
                WWRBAMKey.KEY_AIR_DATE: air_date,
                WWRBAMKey.KEY_UUID: uuid
            }

            data.append(data_row)
            
        return data
            
    @staticmethod
    def get_contestants_by_letter(lang: str, letter: str):
        """
        Reutrn the list of url link to contestant pages on the wiki.

        Parameters
        ----------
        lang : str
            Source of the show. Either 'uk' or 'us'
        letter : str
            Letter to query (any of a to z)

        Returns
        -------
        url_candidates: list
            List of urls to candidates questions
        """
        # Form URL
        url_base = WWTBAMScrapper.WEB_BASE
        url_lang = WWTBAMScrapper.WEB_CONTESTANT_LANG.get(lang, None) 
        
        # Check if none
        if url_lang is None:
            return []
        
        # Get page
        url = urljoin(url_base, url_lang)
        page = slow_request(url=url, params={WWTBAMScrapper.WEB_CONTESTANT_PARAMS_FROM: letter.upper()})
                
        # If code not valid return None
        if page is None: 
            return []
        
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")
        candidates = soup.find_all(WWTBAMScrapper.WEB_CONTESTANT_LIST_TAG, class_=WWTBAMScrapper.WEB_CONTESTANT_LIST_CLASS)

        # Get all contestant
        url_candidates = [urljoin(WWTBAMScrapper.WEB_BASE, c.get("href")) for c in candidates if "href" in c.attrs]
        return url_candidates
    
    
class WWTBAM:
    
    URL_CONTESTANT = {
        'us': 'https://millionaire.fandom.com/wiki/Category:Contestants_from_the_U.S.',
        'uk': 'https://millionaire.fandom.com/wiki/Category:Contestants_from_the_UK',
    }
    
    def __init__(
        self, 
        cache: Optional[str] = '.cache', 
        lang: Optional[str] = 'us',
        filename_db: Optional[str] = "wwtbam",
    ) -> None:
        """Who wnats to be a millionaire database

        Parameters
        ----------
        cache : Optional[str], optional
            Location of the database, by default '.cache'
        lang : Optional[str], optional
            Lang of the show. Either 'uk' or 'us', by default 'us'
        filename_db : Optional[str], optional
            Name of the database, by default "wwtbam"
        """
        # Define online scrapper
        self.cache = cache
        self.lang = lang
        self.scapper = WWTBAMScrapper()   
        self.path_db = os.path.join(self.cache, filename_db + self.lang + ".tsv")
        self.db = self.load_db()
        os.makedirs(self.cache, exist_ok=True)
    
    def load_db(self):
        """Load database from file

        Returns
        -------
        database: pd.DataFrame
            Loaded database
        """
        # If exists, reload it
        if os.path.exists(self.path_db):
            return pd.read_csv(self.path_db, sep="\t")
        else:
            return None
        
    def save_db(self):
        """Save data base
        """
        self.db.to_csv(self.path_db, sep="\t", index=False)
    
    def update(self, chuck_bcp: int = 10):
        """Update database by looking up if new questions where added

        Parameters
        ----------
        chuck_bcp : int, optional
            Number of pages to parse before dumping the results, by default 10
        """
        # Get url contestant
        letters = string.ascii_uppercase
        
        # Lost of all cnadidates
        url_candidates = []
        for letter in tqdm(letters, "Get '{}' candidates by letters ...".format(self.lang)):
            # List of candidates
            url_candidates_ = self.scapper.get_contestants_by_letter(lang=self.lang, letter=letter)
            # Append to list of candidates
            url_candidates.extend(url_candidates_)
            break
        
        # Check only candidates that do not appear in db
        if self.db is not None:
            url_candidates_exist = self.db[WWRBAMKey.KEY_URL].unique()
            url_candidates = [u for u in url_candidates if u not in url_candidates_exist]
        
        # Parse candidates info
        for i, url in enumerate(tqdm(url_candidates, "Get '{}' candidates questions ...".format(self.lang))):
            # Get info from page
            data = self.scapper.get_contestant_questions_by_url(url)
            df_chunk = pd.DataFrame(data)
            # Check if db exists
            if self.db is None:
                self.db = df_chunk
            else:
                # Save db
                self.db = pd.concat([self.db, df_chunk], ignore_index=True)
            # Check if backup needed
            if i%chuck_bcp == 0:
                self.save_db()
                
        # End of program final backup
        self.save_db()