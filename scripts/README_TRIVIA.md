# Trivia 

The package provide trivia question scrapped from multiple sources . Here is the statistics of the databases and how they were merged. The used packages are [KensQuiz](https://www.kensquiz.co.uk/the-quiz-vault/), [OpenTriviaDB](https://opentdb.com/api_config.php), [TheTriviaAPI](https://the-trivia-api.com/license/), [APINinjas](https://api-ninjas.com/profile).

## Setup

The embedding and the categorization if performed using [ollama](https://ollama.com/). 

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

### 0. Unified

|      o_category      |easy| hard|medium| none|
|----------------------|----|-----|------|-----|
|          All         |5906|10316| 12432|13343|
|  animals and nature  | 288| 457 |  525 | 790 |
|authors and literature| 372| 931 |  781 | 858 |
|  film and television | 928| 1419| 1865 | 1602|
|    food and drink    | 364| 484 |  775 | 827 |
|       geography      | 745| 1546| 1596 | 1800|
|        history       | 468| 1211| 1400 | 1513|
|     miscellaneous    | 71 |  64 |  121 | 145 |
|    music and arts    | 786| 1560| 1766 | 2379|
|science and technology| 472| 717 | 1128 | 952 |
|  sports and leisure  | 592| 914 | 1138 | 1522|
|traditions and culture| 435| 755 |  803 | 899 |
|      video games     | 385| 258 |  534 |  56 |


Projection: Categories             |  Projection: Culture
:-------------------------:|:-------------------------:
![plot](viz_embedding_ollama.png)  |  ![plot](viz_embedding_ukusa.png) 

### 1. KensQuiz

|           category          |easy|hard|medium|none|
|:----------------------------|----|----|------|----|
|             All             |3598|4569| 6145 |5787|
|      Christmas Quizzes      | 227| 258|  379 | 147|
|           Culture           | 145| 223|  320 | 308|
|     Food & Drink Quizzes    | 174| 172|  294 | 279|
|  General Knowledge Quizzes  |1452|1730| 2073 |2136|
|       History Quizzes       | 244| 377|  512 | 411|
|     Music Trivia Quizzes    | 271| 344|  464 | 469|
|      People and Places      | 218| 295|  427 | 387|
|Quizzes for Special Occasions| 178| 350|  471 | 507|
|       Science & Nature      | 176| 222|  362 | 262|
|        Sports Quizzes       | 231| 309|  434 | 425|
|         TV and Films        | 282| 289|  409 | 456|

### 2. Open Trivia DB

|               category              |easy|hard|medium|
|:------------------------------------|----|----|------|
|                 All                 |1295| 879| 1874 |
|               Animals               | 28 | 18 |  29  |
|             Celebrities             | 13 |  8 |  31  |
|      Entertainment: Board Games     | 19 | 25 |  15  |
|         Entertainment: Books        | 30 | 26 |  40  |
| Entertainment: Cartoon & Animations | 30 | 17 |  41  |
|        Entertainment: Comics        | 15 | 19 |  34  |
|         Entertainment: Film         | 88 | 43 |  119 |
|Entertainment: Japanese Anime & Manga| 59 | 45 |  80  |
|         Entertainment: Music        | 110| 68 |  189 |
|      Entertainment: Television      | 69 | 29 |  72  |
|      Entertainment: Video Games     | 329| 195|  448 |
|          General Knowledge          | 128| 61 |  124 |
|              Geography              | 80 | 56 |  139 |
|               History               | 68 | 80 |  166 |
|              Mythology              | 19 | 13 |  26  |
|               Politics              | 18 | 15 |  26  |
|           Science & Nature          | 61 | 69 |  100 |
|          Science: Computers         | 48 | 37 |  74  |
|         Science: Mathematics        | 14 | 17 |  24  |
|                Sports               | 48 | 20 |  65  |
|               Vehicles              | 21 | 18 |  32  |

### 3. The Trivia API

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



### 4. ApiNinja

|     category    |none|
|-----------------|----|
|       All       |7678|
|  artliterature  | 503|
|  entertainment  | 393|
|    fooddrink    | 422|
|     general     |1922|
|    geography    | 756|
| historyholidays | 697|
|     language    | 58 |
|   mathematics   | 44 |
|      music      | 943|
|   peopleplaces  | 456|
|religionmythology| 153|
|  sciencenature  | 723|
|  sportsleisure  | 493|
|    toysgames    | 115|


![plot](viz_embedding.png)
