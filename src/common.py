# Filename: common.py
# Programmer(s): Abdurrahman Alyajouri
# Date: 4/25/2025
# Purpose: The purpose of this file is to provide commonly used functions and data structures
#          throughout this project.

total_sentences = 100
sheet_resolution = (784, 612)

people = [
    "alyajouri",
    "scalzone",
    "brodowicz",
    "le"
]

def get_input_path(person, id):
    return f"../dataset/style_{person}/raw_sentence_sheets/{person}_{id}.jpeg"

def get_output_path(person, id):
    return f"../dataset/style_{person}/processed_sentences/{person}_sentence_{id}.png"