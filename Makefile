env := build/venv
pip := $(env)/bin/pip
python := $(env)/bin/python
build_deps := build/requirements.txt

dev: $(clean) $(env)
	@$(python) -c "import build; build.run()"

$(env):
	python3 -m venv $@ && $(pip) install -r $(build_deps)

clean:
	@rm -rf **/__pycache__ **/.build
