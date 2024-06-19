env := .venv
src := start.py
ossl := openssl
keydir := secrets
deps := requirements.txt
pkey := $(keydir)/private.key
signreq := $(keydir)/signreq.csr
ckey := $(keydir)/certificate.pem

run: prep $(ckey) $(src)
	@python $(src)

$(ckey): $(signreq)
	$(ossl) x509 -req --days 365 -in $< -signkey $(pkey) -out $@

$(signreq): $(pkey)
	openssl req -new -key $< -out $@

$(pkey): $(keydir)
	$(ossl) genrsa -out $@ 4096

$(keydir):
	mkdir $@

prep: $(keydir)
	@touch $</*

clean:
	@rm -rf **/__pycache__ **/**/__pycache__ **/**/**/__pycache__

$(env):
	python -m venv $@

install: $(env)
	@./$(env)/bin/pip install -r $(deps)

