port := 9798
env := .venv
src := start.py
deps := requirements.txt

run: stop $(src)
	@$(env)/bin/python $(src) --port $(port)

live: stop $(src)
	@$(env)/bin/python $(src) --mode live --port $(port)

stop:
	@echo droid.SHUTDOWN | nc localhost $(port); sleep 3

install: $(env)
	@$(env)/bin/pip install -r $(deps)

$(env):
	python -m venv $@

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__ Logs

