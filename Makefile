.PHONY: lint
lint:
	pylint krllint || true

.PHONY: test
test:
	coverage run -m unittest
	coverage html --omit="tests*/"
	coverage report --omit="tests*/"

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

.PHONY: release_test
release_test: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*