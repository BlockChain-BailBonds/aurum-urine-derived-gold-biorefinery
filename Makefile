.PHONY: test lint package example

test:
	python -m pytest

lint:
	python -m ruff check .

package:
	python -m build

example:
	python -m aurum_biorefinery run examples/reference_scenario.json --pretty

