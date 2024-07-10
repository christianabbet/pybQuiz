# PybQuiz

PybQuiz is a Python package designed to help you create and manage pub quizzes effortlessly. Whether you're hosting a small quiz night at a local pub or a large trivia event, PybQuiz has the tools you need to make your quiz a success.


```bash
# Using conda
conda create env -n pybquiz
conda activate pybquiz
pip install numpy tqdm py-markdown-table
```

Create you quiz

```
# Run quiz creating based on given config file
python run_create_quiz.py --cfg="config/template.yml"
```


# APIs Stats

[Open Trivia DB](https://opentdb.com/)

|ID|               Catgory               |Easy|Medium|Hard|Text|Image|
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

[The Trivia API](https://the-trivia-api.com/)

|ID|      Catgory      |Easy|Medium|Hard|Text|Image*|
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

* Only available for premium users (not free)

# Custom config file

TODO