src := start.py
ossl := openssl
keydir := crypt
pkey := $(keydir)/private.key
signreq := $(keydir)/signreq.csr
ckey := $(keydir)/certificate.pem

run: $(ckey) $(src)
	python $(src)

$(ckey): $(signreq)
	$(ossl) x509 -req --days 365 -in $< -signkey $(pkey) -out $@

$(signreq): $(pkey)
	openssl req -new -key $< -out $@

$(pkey): $(keydir)
	$(ossl) genrsa -out $@ 4096

$(keydir):
	mkdir $@

build: clean
	@make -s -f build/Makefile.build

clean:
	@rm -rf .build

