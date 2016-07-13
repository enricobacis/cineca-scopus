.PHONY  : all clean install run

VENV = venv
MAIN = cineca.py
OUT  = out.txt

all: install

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run: install
	$(VENV)/bin/python $(MAIN) | tee $(OUT)

clean:
	@ rm -rf $(VENV) build dist *.egg-info
	@ rm -rf *.pyc *.pyo __pycache__

$(VENV):
	virtualenv $(VENV)
