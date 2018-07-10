#!/usr/bin/make

default:
	@echo "There is nothing to do."

test:
	src/tone_mapping.py
	@echo "Testing is finished."
