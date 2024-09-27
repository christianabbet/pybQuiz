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
conda install matplotlib seabornumap-learn
conda install -c conda-forge pycirclize
pip install pyyaml tqdm py-markdown-table python-pptx rich beautifulsoup4 tabulate requests

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
ollama pull llama3.1
# Install python package
pip install ollama
```

![plot](creator.png)

## Available DBs

https://quizbowlpackets.com/

### A. Trivia

|      o_category      |easy| hard|medium| none|
|----------------------|----|-----|------|-----|
|          All         |5925|10384| 12500|13376|
|  animals and nature  | 289| 460 |  528 | 790 |
|authors and literature| 372| 941 |  786 | 858 |
|  film and television | 932| 1425| 1871 | 1606|
|    food and drink    | 367| 490 |  780 | 829 |
|       geography      | 746| 1557| 1608 | 1805|
|        history       | 470| 1215| 1408 | 1517|
|     miscellaneous    | 71 |  64 |  120 | 141 |
|    music and arts    | 788| 1568| 1769 | 2382|
|science and technology| 474| 723 | 1136 | 953 |
|  sports and leisure  | 596| 923 | 1148 | 1537|
|traditions and culture| 435| 760 |  812 | 902 |
|      video games     | 385| 258 |  534 |  56 |



### B. Who wants to be Millionaire


|      o_category      | easy|hard|medium|none|
|----------------------|-----|----|------|----|
|          All         |14051|2307| 12031| 215|
|  animals and nature  | 986 | 122|  651 | 11 |
|authors and literature| 429 | 226|  719 | 13 |
|  film and television | 1532| 315| 2184 | 23 |
|    food and drink    | 1221| 70 |  774 |  9 |
|       geography      | 822 | 308| 1357 | 23 |
|        history       | 636 | 358| 1111 | 20 |
|     miscellaneous    | 1738| 80 |  580 | 22 |
|    music and arts    | 1171| 271| 1451 | 30 |
|science and technology| 1416| 205| 1023 | 23 |
|  sports and leisure  | 1582| 139| 1072 | 15 |
|traditions and culture| 2419| 206| 1027 | 25 |
|      video games     |  99 |  7 |  82  |  1 |

<!-- 
### 2. Jeopardy!

Difficulty is graded from to 0 (lowest) to 11 (highest). This correspond to the clue values from $100 to $2000

|Lang|Questions| Values | Air date|(0, 3]|(3, 7]|(7, 11]|
|----|---------|--------|---------|------|------|-------|
| us |  482067 |100-2000|1984-2024|192881|187847| 79738 | -->


## API Tokens and Google support

The Google Slide API is not mandatory if only the pptx are wanted. To setup the Google slides API and to generate your credential file `credentials.json`, please take a look at the [doc](https://developers.google.com/slides/api/quickstart/python).


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
  
## Thanks 



```bash
# Quiz Style (inspiration)
https://github.com/devinardya/Quiz-Game?tab=readme-ov-file

# Trivia APIs
https://opentdb.com
https://the-trivia-api.com
https://quizapi.io
https://api-ninjas.com/profile

```
