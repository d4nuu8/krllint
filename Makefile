.PHONY: lint
lint:
	pylint krllint.py || true

.PHONY: test
test:
	python -m unittest discover -s test

.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

.PHONY: dist
dist: clean
	python setup.py sdist bdist_wheel

.PHONY: release
release: dist
	twine upload dist/*