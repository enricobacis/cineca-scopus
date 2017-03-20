from __future__ import division
from difflib import SequenceMatcher
import pandas
import re

def read_cineca_file(filename):
    try: data = pandas.read_csv(filename, sep=';')
    except: data = pandas.read_html(filename)[0]
    data['Cognome e Nome'] = data['Cognome e Nome'].str.normalize('NFKD')
    return list(row for idx, row in data.T.iteritems())

def split_name(string):
    surname, name = re.search(r'^([A-Z\'\.\s]+)\s(.+)$', string).groups()
    return name, surname

def iterate_names(name, surname):
    yield name, surname
    while ' ' in name:
        name = name.rsplit(' ', 1)[0]
        yield name, surname
    while ' ' in surname:
        surname = surname.rsplit(' ', 1)[0]
        yield name, surname

def normalize(string):
    return re.sub(r'\W', ' ', string).strip().lower()

def fuzzy_score(query, string):
    if not query or not string: return 0.0
    query, string = normalize(query), normalize(string)
    blocks = SequenceMatcher(None, string, query).get_matching_blocks()
    match = ''.join(string[i:i+n] for i,j,n in blocks if n > 1)
    return len(match) / len(query)
