from typing import Optional, Literal
from bs4 import BeautifulSoup
from pybquiz.db.utils import slow_get_request, to_uuid
from urllib.parse import urljoin
import string
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
import re
import hashlib
from rich.console import Console
from rich.panel import Panel
from py_markdown_table.markdown_table import markdown_table
from pybquiz.db.base import TriviaTSVDB, TriviaQ


class WWTBAMKey:
    
    # Dataframe columns
    KEY_URL = "url"
    KEY_VALUE = "value"
    KEY_DIFFICULTY = "difficulty_code"
    KEY_AIR_DATE = "air_date"
    PPRINT_BINS = [0, 4, 9, 14]
    
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

    # US: https://en.wikipedia.org/wiki/Who_Wants_to_Be_a_Millionaire_(American_game_show)
    # Value ranges 
    LUT_US_RND = [
        999, 1000, 2000, 3000, 4000, 
        4999, 5000, 10000, 20000, 30000, 
        49999, 50000, 100000, 500000, 1000000
    ]
    
    # Value ranges 1999-2004 
    LUT_US_1999_2004_2020_NOW = [
        100, 200, 300, 500, 1000, 
        2000, 4000, 8000, 16000, 32000, 
        64000, 125000, 250000, 500000, 1000000
    ]
    
    # Value ranges 1999-2009
    LUT_US_2004_2009 = [
        100, 200, 300, 500, 1000, 
        2000, 4000, 8000, 16000, 25000, 
        50000, 100000, 250000, 500000, 1000000
    ]
        
    # Value ranges 2009-2010
    LUT_US_2009_2010 = [
        500, 1000, 2000, 3000, 5000, 
        7500, 10000, 12500, 15000, 25000, 
        50000, 100000, 250000, 500000, 1000000
    ]
    
    # Value ranges 2010-2015 (rnd 99999 offset)
    LUT_US_2010_2015 = [
        100, 500, 1000, 2000, 3000, 
        5000, 7000, 10000, 15000, 25000, 
        99999, 100000, 250000, 500000, 1000000
    ]
    
    # Value ranges 2015-2019 (rnd 99999 offset)
    LUT_US_2015_2019 = [
        500, 1000, 2000, 3000, 5000, 
        7000, 10000, 20000, 30000, 50000, 
        99999, 100000, 250000, 500000, 1000000
    ]
    
    # UK: https://en.wikipedia.org/wiki/Who_Wants_to_Be_a_Millionaire%3F_(British_game_show)
    # Value ranges 1999-2004 
    LUT_UK_1998_2007_2018_NOW = [
        100, 200, 300, 500, 1000, 
        2000, 4000, 8000, 16000, 32000, 
        64000, 125000, 250000, 500000, 1000000
    ]
    # Value ranges 2007-2014 
    LUT_UK_2007_2014 = [
        499, 500, 1000, 2000, 5000, 
        9999, 10000, 20000, 50000, 75000, 
        149999, 150000, 250000, 500000, 1000000
    ]
    

class WWTBAMScrapper:
        
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
        match: Jeopardystr
            Matched value
        """
        # Get money valeu in text
        matches = re.findall(r'[$£]((?:\d{1,3},)?(?:\d{1,3},)?\d{3})', text)
        # CHeck if found
        if len(matches) == 0:
            return None
        else:
            return int(matches[0].replace(",", ""))
        
    @staticmethod
    def _extract_year(text: str):
        """Extract year from text

        Parameters
        ----------
        text : str
            Text containing the year

        Returns
        -------
        year: int
            Year of the show
        """
        # Get money valeu in text
        matches = re.findall(r'([12]\d{3})', text)
        # CHeck if found
        if len(matches) == 0:
            return None
        else:
            return int(matches[0])
        
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
        page = slow_get_request(url=url)
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
        infos_text = ""
        
        if len(infos) > 0:
            infos_text = ", ".join([i.text for i in infos])

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
            color_answer = [WWTBAMKey.WEB_ANSWER_OK in q.get("style", "") for q in qbody_lines[2:6]]
            # Get ids
            id_wrong = np.array(np.nonzero(np.logical_not(color_answer))).flatten()
            id_correct = np.array(np.nonzero(color_answer)).flatten()
            # Check if answer available
            if len(id_correct) != 1 or len(id_wrong) != 3 or len(text_answers) != 4:
                continue
            # Finale data merge
            qclean = WWTBAMScrapper._clean_text(text_question) 
            # Hash text (unique question)
            data_row = {
                # export to TSV (tab) + add hash for question
                TriviaQ.KEY_UUID: to_uuid(qclean),
                TriviaQ.KEY_QUESTION: qclean,
                TriviaQ.KEY_CORRECT_ANSWER: WWTBAMScrapper._clean_text(text_answers[id_correct.item()]),
                TriviaQ.KEY_WRONG_ANSWER1: WWTBAMScrapper._clean_text(text_answers[id_wrong[0]]),
                TriviaQ.KEY_WRONG_ANSWER2: WWTBAMScrapper._clean_text(text_answers[id_wrong[1]]),
                TriviaQ.KEY_WRONG_ANSWER3: WWTBAMScrapper._clean_text(text_answers[id_wrong[2]]),
                WWTBAMKey.KEY_AIR_DATE: WWTBAMScrapper._extract_year(infos_text),
                WWTBAMKey.KEY_URL: url,
                WWTBAMKey.KEY_VALUE: WWTBAMScrapper._extract_value(text_value),
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
        url_base = WWTBAMKey.WEB_BASE
        url_lang = WWTBAMKey.WEB_CONTESTANT_LANG.get(lang, None) 
        
        # Check if none
        if url_lang is None:
            return []
        
        # Get page
        url = urljoin(url_base, url_lang)
        page = slow_get_request(url=url, params={WWTBAMKey.WEB_CONTESTANT_PARAMS_FROM: letter.upper()})
                
        # If code not valid return None
        if page is None: 
            return []
        
        # Load from page
        soup = BeautifulSoup(page.content, features="lxml")
        candidates = soup.find_all(WWTBAMKey.WEB_CONTESTANT_LIST_TAG, class_=WWTBAMKey.WEB_CONTESTANT_LIST_CLASS)

        # Get all contestant
        url_candidates = [urljoin(WWTBAMKey.WEB_BASE, c.get("href")) for c in candidates if "href" in c.attrs]
        return url_candidates
    
    
class WWTBAM(TriviaTSVDB):
    
    def __init__(
        self, 
        lang: Literal['us', 'uk'] = 'us',
        filename_db: Optional[str] = "wwtbam",
        cache: Optional[str] = '.cache', 
        chunks: Optional[int] = 10,
    ) -> None:
        """ Who wnats to be a millionaire database

        Parameters
        ----------
        lang : Literal['us', 'uk'], optional
            Lang of the show. Either 'uk' or 'us', by default 'us'
        filename_db : Optional[str], optional
            Name of the database, by default "wwtbam"
        cache : Optional[str], optional
            Location of the database, by default '.cache'
        chunks : Optional[int], optional
            Size of the update chunks before saving, by default 10
        """        
        
        # Other variables
        self.lang = lang
        self.chunks = chunks
        self.scapper = WWTBAMScrapper()     
        
        # Call super method
        super().__init__(
            cache=cache, 
            path_db=os.path.join(cache, filename_db + lang + ".tsv"),
        )

    def initialize(self):
        
        return pd.DataFrame(
            columns=[
                # Mandatory
                TriviaQ.KEY_UUID,
                TriviaQ.KEY_CATEGORY,
                TriviaQ.KEY_DIFFICULTY,
                TriviaQ.KEY_QUESTION, TriviaQ.KEY_CORRECT_ANSWER,
                TriviaQ.KEY_WRONG_ANSWER1, TriviaQ.KEY_WRONG_ANSWER2, TriviaQ.KEY_WRONG_ANSWER3,
                # Local
                WWTBAMKey.KEY_URL, 
                WWTBAMKey.KEY_VALUE, 
                WWTBAMKey.KEY_AIR_DATE, 
                WWTBAMKey.KEY_DIFFICULTY
            ]
        )
    
    def update(self):
        """ Update database by looking up if new questions where added """
        # Get url contestant
        letters = string.ascii_uppercase
        
        # Lost of all cnadidates
        url_candidates = []
        for letter in tqdm(letters, "Get '{}' candidates by letters ...".format(self.lang)):
            # List of candidates
            url_candidates_ = self.scapper.get_contestants_by_letter(lang=self.lang, letter=letter)
            # Append to list of candidates
            url_candidates.extend(url_candidates_)
        
        # Drop duplicates
        url_candidates = pd.DataFrame(url_candidates).drop_duplicates().values.flatten().tolist()
        
        # Check only candidates that do not appear in db
        if self.db is not None:
            url_candidates_exist = self.db[WWTBAMKey.KEY_URL].unique()
            url_candidates = [u for u in url_candidates if u not in url_candidates_exist]
        
        # Parse candidates info
        for i, url in enumerate(tqdm(url_candidates, "Get '{}' candidates questions ...".format(self.lang))):
            # Get info from page
            data = self.scapper.get_contestant_questions_by_url(url)
            
            # Check if at least one entry to add
            if len(data) == 0:
                continue
            
            # Check if db exists
            df_chunk = pd.DataFrame(data)
            if self.db is None:
                self.db = df_chunk
            else:
                # Save db
                self.db = pd.concat([self.db, df_chunk], ignore_index=True)
            # Check if backup needed
            if i%self.chunks == 0:
                self.save()
                
        # End of program final backup
        self.finalize()
        self.save()
        
    def finalize(self):
        """ Check for abnormality in database """
                
        # Check duplicates in questions
        self.db.drop_duplicates(subset=TriviaQ.KEY_UUID, keep=False, inplace=True)
        self.db.dropna(subset=WWTBAMKey.KEY_VALUE, inplace=True)

        # Convert to difficulty level (year based)
        self.db[WWTBAMKey.KEY_DIFFICULTY] = np.nan
        
        for _, df_cand in self.db.groupby(WWTBAMKey.KEY_URL):
            # Check year
            year = df_cand.iloc[0][WWTBAMKey.KEY_AIR_DATE]
            numbers = WWTBAM.convert_values_to_number(
                values=df_cand[WWTBAMKey.KEY_VALUE].values.tolist(),
                year=year, 
                lang=self.lang
            )
            
            # If exists, append value
            if numbers is not None:           
                self.db.loc[df_cand.index, WWTBAMKey.KEY_DIFFICULTY] = numbers
                
        # Drop item if question of answer are empty
        self.db.dropna(
            subset=[
                TriviaQ.KEY_QUESTION, TriviaQ.KEY_CORRECT_ANSWER, 
                TriviaQ.KEY_WRONG_ANSWER1, TriviaQ.KEY_WRONG_ANSWER2, TriviaQ.KEY_WRONG_ANSWER3,
                # WWTBAMKey.KEY_AIR_DATE, WWTBAMKey.KEY_DIFFICULTY,
            ],
            inplace=True,
        )
                

    def pprint(self):
        """ Display stats on database """
        
        name = self.__class__.__name__
        n_candidates = len(self.db[WWTBAMKey.KEY_URL].unique())
        n_questions = len(self)
        v_min = self.db[WWTBAMKey.KEY_VALUE].min()
        v_max = self.db[WWTBAMKey.KEY_VALUE].max()
        d_min = self.db[WWTBAMKey.KEY_AIR_DATE].min()
        d_max = self.db[WWTBAMKey.KEY_AIR_DATE].max()
        
        # Create a console
        data = {
            "Lang": self.lang,
            "Candidates": n_candidates,
            "Questions": n_questions,
            "Values": "{}-{}".format(int(v_min), int(v_max)),
            "Air date": "{}-{}".format(int(d_min), int(d_max)),
        }
        
        # Add difficulty ranges
        difficulties = pd.cut(self.db[WWTBAMKey.KEY_DIFFICULTY], bins=WWTBAMKey.PPRINT_BINS).value_counts(sort=False)
        data.update({str(k): v for k, v in difficulties.items()})
        
        # Display final output
        console = Console() 
        console.print(Panel.fit("Database {} ({})".format(name, self.lang)))
        
        markdown = markdown_table([data]).set_params(row_sep = 'markdown')
        markdown.quote = False
        markdown = markdown.get_markdown()
        console.print(markdown)
        
    @staticmethod
    def convert_values_to_number(values: list[float], year: int, lang: Literal['us', 'uk'] = 'us'):
        
        # Conversion tables
        luts = []
        
        if lang == 'us':
            # Check dates (it's a mess I know)
            luts.append(WWTBAMKey.LUT_US_RND)
            if year <= 2004:
                luts.append(WWTBAMKey.LUT_US_1999_2004_2020_NOW)
            if year >= 2004 and year <= 2009:
                luts.append(WWTBAMKey.LUT_US_2004_2009)
            if year >= 2009 and year <= 2010:
                luts.append(WWTBAMKey.LUT_US_2009_2010)
            if year >= 2010 and year <= 2015:
                luts.append(WWTBAMKey.LUT_US_2010_2015)
            if year >= 2015 and year <= 2019:
                luts.append(WWTBAMKey.LUT_US_2015_2019)
            if year >= 2020:
                luts.append(WWTBAMKey.LUT_US_1999_2004_2020_NOW)
        elif lang == 'uk':
            # Check year
            if year >= 1998 and year <= 2007:
                luts.append(WWTBAMKey.LUT_UK_1998_2007_2018_NOW)
            if year >= 2007 and year <= 2014:
                luts.append(WWTBAMKey.LUT_UK_2007_2014)
            if year >= 2018:
                luts.append(WWTBAMKey.LUT_UK_1998_2007_2018_NOW)
        else:
            raise NotImplementedError
        
        # Process values
        matches = np.array([np.all([v in lut for v in values]) for lut in luts])
        
        # Check id luts
        id_match = np.nonzero(matches)[0]
        if len(id_match) == 0:
            # No match
            return None
        elif len(id_match) == 1:
            # Single match
            id_match = id_match[0]
        else:
            # If two possible answers, take the one with the highest first value
            highest = np.argmax([l[0] for l in luts])
            id_match = id_match[highest]
        
        # Replace dictionnary for values
        replace = {int(k): i for i, k in enumerate(luts[id_match])}
        number = [replace[v] for v in values]
        return number
    
    