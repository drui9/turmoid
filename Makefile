run:
	src/venv/bin/python src/droid.py

dev: clean
	make -s -f build/Makefile.build

clean:
	rm -rf .build
