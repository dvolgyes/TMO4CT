#!/usr/bin/make

default:
	@echo "There is nothing to do."

ci-test:
	@make -C test-data
	python3 -m coverage run -a --source TMO4CT TMO4CT/__main__.py
	python3 -m coverage run -a --source TMO4CT TMO4CT/tools.py
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py -h
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py test-data/ship1k.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py test-data/CT-MONO2-16-ankle.tiff -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png --distance_metric 2.3
	python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 16 -x 16 -o png --distance_metric manhattan
	NUMBA_DISABLE_JIT=1 python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py -v
	NUMBA_DISABLE_JIT=1 python3 -m coverage run -a --source TMO4CT TMO4CT/TMO4CT.py test-data/CT-MONO2-16-ankle.png -O . -vvv -c 5.0 -e 1.2 -b 2 -x 64 -o png --distance_metric maximum
	@echo "Testing is finished."

example:
	@make -C examples
