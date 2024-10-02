#!/bin/bash
# title="TriviaTest"
# author="Test"
# nrounds="13"
# options="A-0-10-E|A-1-10-M|A-2-10-H|A-3-10-U|A-4-10-E|A-5-10-E|A-6-10-E|A-7-10-E|A-8-10-E|A-9-10-E|A-10-10-E|A-11-10-E|A-12-10-E"
# prompts="$title|$author|$nrounds|$options"

# # Run script for trivia creation
# python run_create_quiz_v2.py --prompts="$prompts"

# title="WWTBAMTest"
# author="Test"
# nrounds="13"
# options="B-0-10|B-1-2-A|B-2-3|B-3-4|B-4-5|B-5-6|B-6-7|B-7-8|B-8-9|B-9-10|B-10-11|B-11-12|B-12-13-K"
# prompts="$title|$author|$nrounds|$options"

# # Run script for trivia creation
# python run_create_quiz_v2.py --prompts="$prompts"

title="FamilyFeudTest"
author="Test"
nrounds="6"
options="C-0-10|C-1-10-<|C-2-10-<|C-3-10-<|C-4-10->|C-5-10"
prompts="$title|$author|$nrounds|$options"

# Run script for trivia creation
python run_create_quiz_v2.py --prompts="$prompts"

