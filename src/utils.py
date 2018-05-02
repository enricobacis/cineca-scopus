from __future__ import division
from difflib import SequenceMatcher
import sqlalchemy
import pandas
import re

def read_cineca_file(filename, encoding='latin1'):
    try: data = pandas.read_csv(open(filename))
    except: data = pandas.read_html(open(filename, 'rb').read(), encoding=encoding)[0]
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

def csv_to_db(csvfile, dbfile, tablename):
    data = pandas.read_csv(csvfile, encoding='utf-8')
    data.columns = data.columns.str.strip()
    data.columns = data.columns.str.replace('\s+', '_')
    engine = sqlalchemy.create_engine('sqlite:///' + dbfile)
    data.to_sql(tablename, engine, if_exists='replace')
