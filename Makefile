env := build/venv
pip := $(env)/bin/pip
python := $(env)/bin/python
build_deps := build/requirements.txt

dev: $(clean) $(python)
	@python3 -c "import build; build.run()"

$(python): $(pip)

$(pip): $(build_deps) $(env)
# 	$@ install -r $(build_deps) # todo: toggle this with internet availability

$(env):
	python3 -m venv $@

clean:
	@rm -rf **/__pycache__ **/.build
