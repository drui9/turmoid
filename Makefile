env := venv


prod: $(env)
	@./venv/bin/python start.py

dev:
	@python3 build.py

$(env):
	python3 -m venv venv;./venv/bin/pip install -r requirements.txt

clean:
	@rm -rf **/__pycache__ .build
