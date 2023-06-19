MAIN = src/main.py
PY = python
DISPLAY ?= web
METHOD ?= local
UPDATE_PATH ?= 'input/track.gpx'
ifdef VERBOSE
    verbose := -v
endif



update:
	$(PY) $(MAIN) -u $(UPDATE_PATH) $(verbose)
web:
	$(PY) $(MAIN) -d web -m $(METHOD) $(verbose)
console:
	$(PY) $(MAIN) -d console -m $(METHOD) $(verbose)

requirement:
	pip install -r 'requirements.txt'
