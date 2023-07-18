env := .venv
src := start.py
deps := requirements.txt

run: $(src)
	@$(env)/bin/python $(src)

live: stop $(src)
	@$(env)/bin/python $(src) --mode live

install: $(env)
	@$(env)/bin/pip install -r $(deps)

$(env):
	python -m venv $@

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__ Logs

