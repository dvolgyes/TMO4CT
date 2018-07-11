#!/usr/bin/make

default:
	@echo "There is nothing to do."

ci-test:
	make -C test-data
	python3 -m coverage run src/tools.py
	python3 -m coverage run src/TMO4CT.py
	python3 -m coverage run src/TMO4CT.py -h
	python3 -m coverage run src/TMO4CT.py -v
	python3 -m coverage run src/TMO4CT.py test-data/ship1k.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png
	python3 -m coverage run src/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png
	python3 -m coverage run src/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png --distance-metric 2.3
	python3 -m coverage run src/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png --distance-metric manhattan
	python3 -m coverage run src/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png --distance-metric maximum
	@echo "Testing is finished."
