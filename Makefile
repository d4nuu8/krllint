.PHONY: lint
lint:
	pylint -f colorized krlcodestyle.py || true

.PHONY: test
test:
	python -m unittest discover -s test