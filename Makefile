.PHONY  : all clean install run run2

VENV  = venv
MAIN  = src/cineca.py
MAIN2 = src/cineca2.py

all: install

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run: install
	$(VENV)/bin/python $(MAIN)

run2: install
	$(VENV)/bin/python $(MAIN2)

clean:
	@ rm -rf $(VENV) build dist *.egg-info
	@ rm -rf *.pyc *.pyo __pycache__

$(VENV):
	virtualenv $(VENV)
