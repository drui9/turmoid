env := .venv
enter := start.py
deps := requirements.txt
prodmodules := module
devmodules:= mod

run: $(env) $(enter)
	@$(env)/bin/python $(enter) --modules $(devmodules)

live: $(env) $(enter)
	@$(env)/bin/python $(enter) --mode live --modules $(prodmodules)

test:
	$(env)/bin/python -m unittest

$(env): $(deps)
	./install.sh; touch $(env)

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__ logs

