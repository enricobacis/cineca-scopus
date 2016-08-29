.PHONY  : all clean install run

VENV = venv
MAIN = src/cineca.py

all: install

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run: install
	$(VENV)/bin/python $(MAIN)

clean:
	@ rm -rf $(VENV) build dist *.egg-info
	@ rm -rf *.pyc *.pyo __pycache__

$(VENV):
	virtualenv $(VENV)
