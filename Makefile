dev:
	@export host='_gateway';./venv/bin/python droid.py

android:
	@export host='localhost';./venv/bin/python droid.py

clean:
	@rm -rf **/__pycache__
