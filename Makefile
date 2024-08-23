env := .venv
src := start.py
deps := requirements.txt
prod := module

run: $(src)
	@$(env)/bin/python $(src)

live: $(src)
	@$(env)/bin/python $(src) --mode live --modules $(prod)

install: $(env)
	@$(env)/bin/pip install -r $(deps)

$(env):
	python -m venv $@

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__ logs

