.PHONY = clean
.DEFAULT = help

VENV = .venv
PYTHON = $(VENV)/bin/python

help:
	@echo "Welcome to WebM2MP4Bot source code!"
	@echo "    make bootstrap - setup virtual environment and install dependencies"
	@echo "    make lint      - source code static analysis"
	@echo "    make clean     - clean up artifacts"
	@echo "    make deploy    - deploy latest git commit to Heroku

bootstrap:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -r requirements.txt

lint: $(VENV)
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy src

clean:
	rm -rf $(VENV)

deploy:
	git push heroku main
