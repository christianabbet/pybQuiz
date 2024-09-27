#!/bin/bash
title="TriviaTest"
author="Test"
nrounds="13"
options="A-0-1-E|A-1-1-M|A-2-1-H|A-3-1-U|A-4-1-E|A-5-1-E|A-6-1-E|A-7-1-E|A-8-1-E|A-9-1-E|A-10-1-E|A-11-1-E|A-12-1-E"
prompts="$title|$author|$nrounds|$options"

# Run script for trivia creation
python run_create_quiz_v2.py --prompts="$prompts"
