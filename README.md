# PybQuiz

PybQuiz is a Python package designed to help you create and manage pub quizzes effortlessly. Whether you're hosting a small quiz night at a local pub or a large trivia event, PybQuiz has the tools you need to make your quiz a success. An example generated using the is available under the official [RELEASE](https://github.com/christianabbet/pybQuiz/releases) folder. The repo is abel to generate a pptx file as well as export your quiz directely to Google slides and sheets to manage the teams scores during the quiz.

![plot](example2.png)


## Setup


### Generate Quiz

Clone repo and create environement

```bash
# Clone repo
git clone https://github.com/christianabbet/pybQuiz.git
cd pybQuiz

# Using conda
conda create -n pybquiz python=3.9
conda activate pybquiz
# Base packages
pip install numpy pyyaml tqdm py-markdown-table pandas python-pptx rich beautifulsoup4 tabulate requests
conda install -c conda-forge pycirclize
conda install umap-learn matplotlib seaborn

# To export to Google Slides / Sheets
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# To generate new backgorunds
pip install --upgrade openai
```

<!-- Create your quiz

```bash
# Run quiz creating 
python run_create_quiz.py

# To get additonal parameters infromation
python run_create_quiz.py -h
```

```bash
options:
  -h, --help            show this help message and exit
  --cfg CFG             path to config file (default if None)
  --dirout DIROUT       path to output directory for data generation (default is "output")
  --apitoken APITOKEN   path to stored API tokens (default is "config/apitoken.yml")
  --googlecreds GOOGLECREDS
                        path to stored Google credentials (default is "config/credentials.json")
```

Note that some APIs need a token to be accessed. Please refer to the API section to know how to setup tokens.  -->

### Update databases (advanced)

# Install LLM

EMBEDDING + LDA (Multilevel)

```bash
# https://ollama.com/blog/embedding-models
# Get installer
curl -fsSL https://ollama.com/install.sh | sh
# Get model embedding
ollama pull mxbai-embed-large
# Install python package
pip install ollama
```

![plot](creator.png)

## Available DBs

https://quizbowlpackets.com/

### 1. Who wants to be Millionaire

https://millionaire.fandom.com

|Lang|Candidates|Questions|   Values  | Air date|(0, 4]|(4, 9]|(9, 14]|
|----|----------|---------|-----------|---------|------|------|-------|
| us |   1948   |  17080  |100-2180000|1953-2024| 6503 | 7291 |  1508 |
| uk |   1234   |  11296  |100-1000000|1998-2024| 4833 | 4656 |  783  |

### 2. Jeopardy!

Difficulty is graded from to 0 (lowest) to 11 (highest). This correspond to the clue values from $100 to $2000

|Lang|Questions| Values | Air date|(0, 3]|(3, 7]|(7, 11]|
|----|---------|--------|---------|------|------|-------|
| us |  482067 |100-2000|1984-2024|192881|187847| 79738 |


### 3. Open Trivia DB

|               category              |easy|hard|medium|
|-------------------------------------|----|----|------|
|                 All                 |1286| 871| 1864 |
|               Animals               | 26 | 18 |  29  |
|             Celebrities             | 13 |  8 |  31  |
|      Entertainment: Board Games     | 19 | 25 |  15  |
|         Entertainment: Books        | 28 | 24 |  36  |
| Entertainment: Cartoon & Animations | 27 | 14 |  39  |
|        Entertainment: Comics        | 15 | 18 |  34  |
|         Entertainment: Film         | 88 | 43 |  119 |
|Entertainment: Japanese Anime & Manga| 58 | 45 |  79  |
|         Entertainment: Music        | 110| 68 |  189 |
|      Entertainment: Television      | 69 | 29 |  72  |
|      Entertainment: Video Games     | 329| 195|  448 |
|          General Knowledge          | 128| 60 |  124 |
|              Geography              | 80 | 56 |  139 |
|               History               | 68 | 80 |  166 |
|              Mythology              | 19 | 13 |  26  |
|               Politics              | 18 | 15 |  26  |
|           Science & Nature          | 61 | 69 |  100 |
|          Science: Computers         | 48 | 37 |  74  |
|         Science: Mathematics        | 14 | 17 |  23  |
|                Sports               | 47 | 20 |  64  |
|               Vehicles              | 21 | 17 |  31  |

### 4. The Trivia API

|      category     |easy|hard|medium|
|-------------------|----|----|------|
|        All        | 991|4843| 4363 |
|arts_and_literature| 84 | 645|  356 |
|    film_and_tv    | 105| 678|  602 |
|   food_and_drink  | 80 | 301|  364 |
| general_knowledge | 42 | 171|  175 |
|     geography     | 195| 771|  635 |
|      history      | 41 | 440|  441 |
|       music       | 127| 583|  429 |
|      science      | 115| 531|  578 |
|society_and_culture| 150| 442|  585 |
| sport_and_leisure | 52 | 281|  198 |

### 5. KenQuiz

|           category          |10.0|20.0|30.0|
|-----------------------------|----|----|----|
|             All             |3598|6145|4569|
|      Christmas Quizzes      | 227| 379| 258|
|           Culture           | 145| 320| 223|
|     Food & Drink Quizzes    | 174| 294| 172|
|  General Knowledge Quizzes  |1452|2073|1730|
|       History Quizzes       | 244| 512| 377|
|     Music Trivia Quizzes    | 271| 464| 344|
|      People and Places      | 218| 427| 295|
|Quizzes for Special Occasions| 178| 471| 350|
|       Science & Nature      | 176| 362| 222|
|        Sports Quizzes       | 231| 434| 309|
|         TV and Films        | 282| 409| 289|



### Unification of categories

* Sport:
  ["Sport and Leisure, ]

| ID | Category          | KenQuiz          | TheTriviaAPI        | OpenTriviaDB | tSNE |
|----|-------------------|------------------|---------------------|--------------|------|
|  1 | Art & Literature  | -                | arts_and_literature | Books        |  OK  |
|  2 | Computers         | -                | -                   | Science: Computers |  OK  |
|  3 | Geography         | -                | geography           | Geography    |  OK  |
|  4 | History           | -                | history             | History      |  OK  |
|  5 | Music             | Music Trivia     | music               | Music        |  OK  |
|  6 | Film & TV         | (TV and Films)   | film_and_tv         | Film / Television |  OK  |
|  7 | Food & Drink      | Food & Drink     | food_and_drink      | -            |  OK  |
|  8 | Science & Nature  | Science & Nature | science             | Science & Nature / Animals / Mathematics |  OK  |
|  9 | Society & Culture | -                | society_and_culture | Mythology    |  OK  |
| 10 | Sport & Leisure   | Sports           | sport_and_leisure   | Sports / Board Games       |  OK  |
| 11 | Video Games & Anime | -              | -                   | Video games / Japanese Anime & Manga |  OK  |
| 12 | Xmas Special      | Christmas        | -                   | -            |  OK  |
| 13 | Pot pourri        | -                | -                   | -            |  -   |


<!-- ## Available APIs

### 1. Open Trivia DB

* **Tag**: opentriviadb
* **Link**: https://opentdb.com/
* **API-Token**: Not required
* **Type** multiple choice question (MCQ)

|ID|               Category               |Easy|Medium|Hard|Text|Image|
|--|-------------------------------------|----|------|----|----|-----|
| 9|          General Knowledge          | 128|  124 | 61 | 313|  0  |
|10|         Entertainment: Books        | 31 |  41  | 27 | 99 |  0  |
|11|         Entertainment: Film         | 88 |  119 | 43 | 250|  0  |
|12|         Entertainment: Music        | 110|  189 | 68 | 367|  0  |
|13|  Entertainment: Musicals & Theatres |  9 |  13  | 10 | 32 |  0  |
|14|      Entertainment: Television      | 69 |  72  | 29 | 170|  0  |
|15|      Entertainment: Video Games     | 330|  448 | 195| 973|  0  |
|16|      Entertainment: Board Games     | 19 |  15  | 25 | 59 |  0  |
|17|           Science & Nature          | 61 |  100 | 69 | 230|  0  |
|18|          Science: Computers         | 48 |  74  | 37 | 159|  0  |
|19|         Science: Mathematics        | 14 |  24  | 17 | 55 |  0  |
|20|              Mythology              | 19 |  26  | 13 | 58 |  0  |
|21|                Sports               | 48 |  65  | 20 | 133|  0  |
|22|              Geography              | 80 |  139 | 56 | 275|  0  |
|23|               History               | 68 |  166 | 80 | 314|  0  |
|24|               Politics              | 18 |  26  | 15 | 59 |  0  |
|25|                 Art                 | 13 |  11  |  9 | 33 |  0  |
|26|             Celebrities             | 13 |  31  |  8 | 52 |  0  |
|27|               Animals               | 28 |  30  | 18 | 76 |  0  |
|28|               Vehicles              | 21 |  32  | 18 | 71 |  0  |
|29|        Entertainment: Comics        | 15 |  34  | 19 | 68 |  0  |
|30|           Science: Gadgets          | 14 |  10  |  5 | 29 |  0  |
|31|Entertainment: Japanese Anime & Manga| 59 |  80  | 45 | 184|  0  |
|32| Entertainment: Cartoon & Animations | 31 |  41  | 17 | 89 |  0  |


### 2. The Trivia API

* **Tag**: thetriviaapi
* **Link**: https://the-trivia-api.com/
* **API-Token**: Not required
* **Type** multiple choice question (MCQ)



|ID|      Category      |Easy|Medium|Hard|Text|Image*|
|--|-------------------|----|------|----|----|-----|
| 0|arts_and_literature| 84 |  375 | 708|1160|  7  |
| 1|    film_and_tv    | 157|  709 | 892|1466| 292 |
| 2|   food_and_drink  | 86 |  392 | 327| 759|  46 |
| 3| general_knowledge | 51 |  200 | 240| 393|  98 |
| 4|     geography     | 256|  764 |1019|1626| 413 |
| 5|      history      | 55 |  475 | 499| 964|  65 |
| 6|       music       | 171|  495 | 741|1217| 190 |
| 7|      science      | 118|  601 | 555|1271|  3  |
| 8|society_and_culture| 155|  604 | 495|1242|  12 |
| 9| sport_and_leisure | 52 |  216 | 309| 557|  20 |

${}^{*}$ Only available for premium users (not free). Not supported.

### 3. QuizAPI

* **Tag**: quizapi
* **Link**: https://quizapi.io/
* **API-Token**: Required
* **Type** multiple choice question (MCQ)

|ID|   Category   |Easy*|Medium*|Hard*|Text*|Image|
|--|-------------|----|------|----|----|-----|
| 1|    Linux    | -1 |  -1  | -1 | -1 |  0  |
| 2|     bash    | -1 |  -1  | -1 | -1 |  0  |
| 3|uncategorized| -1 |  -1  | -1 | -1 |  0  |
| 4|    Docker   | -1 |  -1  | -1 | -1 |  0  |
| 5|     SQL     | -1 |  -1  | -1 | -1 |  0  |
| 6|     CMS     | -1 |  -1  | -1 | -1 |  0  |
| 7|     Code    | -1 |  -1  | -1 | -1 |  0  |
| 8|    DevOps   | -1 |  -1  | -1 | -1 |  0  |

${}^{*}$ Distribution of question categories and difficulties unknown.

### 4. API Ninjas - Trivia

* **Tag**: apininjas
* **Link**: https://api-ninjas.com/api/trivia
* **API-Token**: Required
* **Type** Open-ended (Open)


|ID|     Category     |Easy**|Medium**|Hard**|Text*|Image|
|--|-----------------|----|------|----|----|-----|
| 0|  artliterature  | -1 |  -1  | -1 | -1 |  0  |
| 1|     language    | -1 |  -1  | -1 | -1 |  0  |
| 2|  sciencenature  | -1 |  -1  | -1 | -1 |  0  |
| 3|     general     | -1 |  -1  | -1 | -1 |  0  |
| 4|    fooddrink    | -1 |  -1  | -1 | -1 |  0  |
| 5|   peopleplaces  | -1 |  -1  | -1 | -1 |  0  |
| 6|    geography    | -1 |  -1  | -1 | -1 |  0  |
| 7| historyholidays | -1 |  -1  | -1 | -1 |  0  |
| 8|  entertainment  | -1 |  -1  | -1 | -1 |  0  |
| 9|    toysgames    | -1 |  -1  | -1 | -1 |  0  |
|10|      music      | -1 |  -1  | -1 | -1 |  0  |
|11|   mathematics   | -1 |  -1  | -1 | -1 |  0  |
|12|religionmythology| -1 |  -1  | -1 | -1 |  0  |
|13|  sportsleisure  | -1 |  -1  | -1 | -1 |  0  |

${}^{*}$ Distribution of question categories and difficulties unknown.
${}^{**}$ No difficulty level


### 5. Jeopardy US

* **Tag**: jeopardy
* **Link**: https://github.com/jwolle1/jeopardy_clue_dataset
* **API-Token**: None
* **Type** Open-ended (Open)

We consider questions in range  $100, $200, $300, $400 (easy), $500, $600, $800, $1000, (medium), $1200, $1600, $2000 (hard)

|ID|      Catgory      |Easy|Medium|Hard|Text|Image|
|--|-------------------|----|------|----|----|-----|
| 0|  American History | 634|  568 | 144|1346|  0  |
| 1|      Animals      | 670|  311 | 25 |1006|  0  |
| 2|Business & Industry| 707|  428 |  9 |1144|  0  |
| 3|      History      | 744|  639 | 94 |1477|  0  |
| 4|     Literature    | 588|  694 | 89 |1371|  0  |
| 5|     Potpourri     | 717|  498 | 98 |1313|  0  |
| 6|      Religion     | 548|  500 | 65 |1113|  0  |
| 7|      Science      | 739|  625 | 197|1561|  0  |
| 8|       Sports      | 890|  357 | 11 |1258|  0  |
| 9|   Transportation  | 606|  339 | 76 |1021|  0  |
|10|    Word Origins   | 546|  401 | 128|1075|  0  |
|11|  World Geography  | 517|  538 | 64 |1119|  0  |
|12|   World History   | 510|  472 | 104|1086|  0  |

## API Tokens and Google support

To access certain content, you **need** an API Token. Once obtained, create a file `apitoken.yml` under the `config` folder. For each library ([OpenTriviaDB](https://opentdb.com/api_config.php), [TheTriviaAPI](https://the-trivia-api.com/license/), [QuizAPI](https://quizapi.io/clientarea/settings/token) [APINinjas](https://api-ninjas.com/profile)), you can generate you token by folowing the instructions linked. 

The Google Slide API is not mandatory if only the pptx are wanted. To setup the Google slides API and to generate your credential file `credentials.json`, please take a look at the [doc](https://developers.google.com/slides/api/quickstart/python).


```bash
# Folder structure
└── pybQuiz
    └── config
        ├── credentials.json
        └── apitoken.yml
```

Fill the `apitoken.yml` file with your own API keys. 

```yml
---
# Optional API tokens
OpenTriviaDB: YOUR_API_KEY_1
TheTriviaAPI: YOUR_API_KEY_2
QuizAPI: YOUR_API_KEY_3
APINinjas: YOUR_API_KEY_4
...
```

## Coming Next

* [ ] Check if multiple time same question 
  * [ ] At the quiz level
  * [ ] Between multiple quizes
* [ ] Google slide export
  * [ ] Check text auto adapt to size ?
* Error quiz time
  * Retry export if failed (googl slides)
  * Check duplicates questions
  * Check answer always display for one answer cases

* Other APIs
  * https://cluebase.readthedocs.io/en/latest/
  * https://www.reddit.com/r/trivia/comments/3wzpvt/free_database_of_50000_trivia_questions/
    * https://drive.google.com/file/d/0Bzs-xvR-5hQ3SGdxNXpWVHFNWG8/view?resourcekey=0-5QvXBiHQPm_KmkhXP9RO8g
  
* Familly Feud
  * https://docs.google.com/spreadsheets/d/1y5TtM4rXHfv_9BktCiJEW621939RzJucXxhJidJZbfQ/htmlview
  * https://drive.google.com/file/d/0Bzs-xvR-5hQ3WktpWVA2RmROY1U/view?resourcekey=0-u03CutV7Ye9rxiuUE8c_UQ

* MasterMinds
  * https://fikklefame.com/?s=master+minds

* Others
  * https://quizbowlpackets.com/
  * Ding bats
  * N'oubliez pas les paroles
  * Kensquiz
  
## Thanks -->



```bash
# Quiz Style (inspiration)
https://github.com/devinardya/Quiz-Game?tab=readme-ov-file

# Trivia APIs
https://opentdb.com
https://the-trivia-api.com
https://quizapi.io
https://api-ninjas.com/profile

```
