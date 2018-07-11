#!/usr/bin/make

default:
	@echo "There is nothing to do."

test:
	python3 src/TMO4CT.py
	python3 src/TMO4CT.py test-data/ship1k.png -O . -vvv -c 5.0 -e 1.2 -b 256 -x 8-o png
	python3 src/TMO4CT.py test-data/ship1k.png -O .  -c 5.0 -e 1.2 -b 8 -o png
	@echo "Testing is finished."
