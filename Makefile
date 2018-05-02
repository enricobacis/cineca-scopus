.PHONY  : all clean run run2 run3

VENV   = venv
MAIN   = src/cineca.py
MAIN2  = src/cineca2b.py
MAIN3  = src/cineca3.py

all:
	@ echo 'This will run all three phases'
	@ echo 'Do you really want it?'
	@ read -p 'Enter to advance, Ctrl-c to stop'
	@ echo 'Starting phase 1 (interactive)'
	@ make run
	@ echo 'Starting phase 2 (not-interactive)'
	@ make run2
	@ echo 'Starting phase 3 (not-interactive)'
	@ make run3

run: $(VENV)
	$(VENV)/bin/python $(MAIN)

run2: $(VENV)
	$(VENV)/bin/python $(MAIN2)

run3: $(VENV)
	$(VENV)/bin/python $(MAIN3)

clean:
	@ rm -rf $(VENV) build dist *.egg-info
	@ rm -rf *.pyc *.pyo __pycache__

$(VENV): requirements.txt
	virtualenv --system-site-packages $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
