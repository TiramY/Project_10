import json
import string
import re

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Change budget var if it's not the right syntax.
def adapt_budget(budget):
    # Check if it's a number
    try:
        float(budget)
    except ValueError:
        return None

    # Split budget with '.'
    split_budget = budget.replace(',', '.').split('.')[0]

    # check if it's < 0 
    if int(float(split_budget)) < 0:
        return None

    if int(float(split_budget)) < 100:
        return str(int(float(budget) * 1000))
    
    return split_budget

def format_val(val):
    # Sometime you can found -1
    if val == -1:
        return None

    remove_characters = (",", ".")

    for char in remove_characters:
        val = val.replace(char, '')
    return val

def get_example_label(utterance, entity_name, value):
        return {
            'entityName': entity_name,
            'startCharIndex': utterance.find(value),
            'endCharIndex': utterance.find(value) + len(value)
        }

def format_train_file(train):
    train_set = []

    for key, val in train.items():
        train_set.append({
            'text': key if key != None else 'empty',
            'intent': 'BookFlightIntent',
            "entities": [{
                "entity": "BookFlight",
                "startPos": 0 if key.find(val['intent']) == -1 else key.find(val['intent']),
                "endPos": len(key)
                }]})

    return train_set

# Return train(70%)/test(30%) dict with booking intents only.
def data_preparation(file_path : str):
    with open(file_path) as f:
        data = json.load(f)

    dic = {}

    for values in data:
        info = values.get('turns')[0].get('labels').get('frames')[0].get('info')

        intent = info.get('intent', None)
        budget = info.get('budget', None)
        dst_city = info.get('dst_city', None)
        or_city = info.get('or_city', None)
        str_date = info.get('str_date', None)
        end_date = info.get('end_date', None)

        #Normalisation
        text = values['turns'][0]['text'].lower()

        #Replace Char
        remove_characters = (",", ".", "?", "!")
        for char in remove_characters:
            text = text.replace(char, '')
        
        if (intent != None):
            dic[text] = {
                "budget" :      adapt_budget(budget[0].get('val').lower()) if budget else None,
                "intent" :      format_val(intent[0].get('val').lower()) if intent else None,
                "dst_city" :    format_val(dst_city[0].get('val').lower()) if dst_city else None,
                "or_city" :     format_val(or_city[0].get('val').lower()) if or_city else None,
                "str_date" :    format_val(str_date[0].get('val').lower()) if str_date else None,
                "end_date" :    format_val(end_date[0].get('val').lower()) if end_date else None,
            }

    df = pd.DataFrame.from_dict(dic, orient='index', columns=['budget', 'intent', 'dst_city', 'or_city', 'str_date', 'end_date'])
    train, test = train_test_split(df, test_size=0.3, random_state=42)
    test_set = format_train_file(test.to_dict('index'))
    return train.to_dict('index'), test_set