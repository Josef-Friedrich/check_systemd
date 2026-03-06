all: test format docs lint type_check

test:
	uv run --isolated --python=3.10 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.11 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.12 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.13 pytest -m "not (slow or gui)"

test_quick:
	uv run --isolated --python=3.12 pytest

test_unmocked:
	pytest -vvv --capture tee-sys tests/_test_unmocked.py

install: update

install_editable: install
	uv pip install --editable .

update:
	uv sync --upgrade

upgrade: update

build:
	uv build

publish:
	uv build
	uv publish

format:
	uv tool run ruff check --select I --fix .
	uv tool run ruff format

docs: docs_readme_patcher docs_sphinx

docs_readme_patcher:
	uv tool run --isolated --with check_systemd readme-patcher

docs_sphinx:
	rm -rf docs/_build
	uv tool run --isolated --from sphinx --with check_systemd --with sphinx_rtd_theme --with sphinx-argparse sphinx-build -W -q docs docs/_build
	xdg-open docs/_build/index.html

pin_docs_requirements:
	rm -rf docs/requirements.txt
	uv run pip-compile --strip-extras --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

lint:
	uv tool run ruff check

type_check:
	uv tool run mypy check_systemd.py tests

copy_example_systemd_units:
	sudo cp -r tests/unit-files/* /etc/systemd/system/
