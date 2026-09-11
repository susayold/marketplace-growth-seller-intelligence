PYTHON ?= python
PROJECT_DIR ?= .

setup:
	$(PYTHON) -m pip install -r requirements.txt

profile:
	$(PYTHON) src/ingest.py --project-dir $(PROJECT_DIR)
	$(PYTHON) src/profile.py --project-dir $(PROJECT_DIR)

build:
	$(PYTHON) src/build_database.py --project-dir $(PROJECT_DIR)
	$(PYTHON) src/build_marts.py

test:
	$(PYTHON) -m pytest -q

export:
	$(PYTHON) src/export_marts.py --project-dir $(PROJECT_DIR)

all: profile build test export

