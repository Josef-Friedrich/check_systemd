build:
	rm -rf dist
	python3 setup.py sdist

upload:
	pip3 install twine
	twine upload --skip-existing dist/*

readme:
	tox -e py38 -- test/test_readme.py

test:
	pyenv update
	pyenv install --skip-existing 3.6.13
	pyenv install --skip-existing 3.7.10
	pyenv install --skip-existing 3.9.2
	pyenv local 3.6.13 3.7.10 3.9.2
	pip3 install tox
	tox

test_38:
	tox -e py38

docs:
	poetry run tox -e docs
	xdg-open .tox/docs/tmp/html/index.html

.PHONY: build upload test readme docs
