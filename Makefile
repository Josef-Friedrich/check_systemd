test:
	poetry run tox

install:
	poetry install

update:
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html

readme:
	poetry run tox -e readme

.PHONY: build upload test readme docs
