.PHONY  : all clean run run2

VENV  = venv
MAIN  = src/cineca.py
MAIN2 = src/cineca2.py

all run: $(VENV)
	$(VENV)/bin/python $(MAIN)

run2: $(VENV)
	$(VENV)/bin/python $(MAIN2)

clean:
	@ rm -rf $(VENV) build dist *.egg-info
	@ rm -rf *.pyc *.pyo __pycache__

$(VENV): requirements.txt
	virtualenv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
