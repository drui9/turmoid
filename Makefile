env := venv
deps := requirements.txt

dev: $(env)
	@./venv/bin/python droid.py

$(env):
	python3 -m venv venv;./venv/bin/pip install -r $(deps)

clean:
	@rm -rf **/__pycache__
