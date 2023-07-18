env := .venv
enter := start.py
deps := requirements.txt
scripts := scripts

run: $(env) $(enter)
	$(env)/bin/python $(enter) --modules $(scripts)

live: $(env) $(enter)
	$(env)/bin/python $(enter) --mode live --modules $(prodmodules)

install:
	python -m venv $(env) && $(env)/bin/pip install -r $(deps)

test:
	$(env)/bin/python -m unittest

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__ logs

