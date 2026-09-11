setup:
	python -m pip install -r requirements.txt

build:
	python src/build_project.py

test:
	pytest -q

