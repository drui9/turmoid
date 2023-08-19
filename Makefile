env := venv
target := build.zip


dev:
	@python3 build.py

prod: $(env)
	@./venv/bin/python start.py

$(env):
	python3 -m venv venv;./venv/bin/pip install -r requirements.txt

unpack: $(target)
	unzip -o $^; touch Makefile

clean:
	@rm -rf **/__pycache__ .build
