from csv import DictReader
import re

def read_csv(filename):
    with open(filename) as csvfile:
        return list(DictReader(csvfile, dialect='excel'))

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
