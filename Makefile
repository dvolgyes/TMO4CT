#!/usr/bin/make

default:
	@echo "There is nothing to do."

ci-test:
	make -C test-data
	python3 -m coverage src/TMO4CT.py
	python3 -m coverage src/TMO4CT.py test-data/ship1k.png -O . -vvv -c 5.0 -e 1.2 -b 64 -x 8 -o png
	python3 -m coverage src/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 64 -x 8 -o png
	@echo "Testing is finished."
