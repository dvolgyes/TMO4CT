#!/usr/bin/make

default:
	@echo "There is nothing to do."

ci-test:
	make -C test-data
	python3 -m coverage src/TMO4CT.py
	python3 -m coverage src/TMO4CT.py test-data/ship1k.png -O . -vvv -c 5.0 -e 1.2 -b 256 -x 8 -o png
	python3 -m coverage src/TMO4CT.py test-data/ship1k.png -O .  -c 5.0 -e 1.2 -b 8 -o png
	@echo "Testing is finished."
