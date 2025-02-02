test:
	poetry run tox

test_unmocked:
	pytest -vvv --capture tee-sys tests/_test_unmocked.py

install: update

# https://github.com/python-poetry/poetry/issues/34#issuecomment-1054626460
install_editable:
	pip install -e .

update:
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

format:
	poetry run tox -e format

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html > /dev/null 2>&1

readme:
	poetry run tox -e readme

lint:
	poetry run tox -e lint

pin_docs_requirements:
	pipx install pip-tools
	pip-compile --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

copy_example_systemd_units:
	sudo cp -r tests/unit-files/* /etc/systemd/system/

.PHONY: test install install_editable update build publish format docs readme lint pin_docs_requirements
