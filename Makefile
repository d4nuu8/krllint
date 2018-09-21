.PHONY: lint
lint:
	pylint krlcodestyle.py || true

.PHONY: test
test:
	python -m unittest discover -s test