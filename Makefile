env := venv

dev:
	@python3 build.py

prod: $(env)
	@./venv/bin/python start.py

$(env):
	python3 -m venv venv;./venv/bin/pip install -r requirements.txt

clean:
	@rm -rf **/__pycache__
