# FlowStack SDK Development Makefile

.PHONY: help docs-serve docs-build docs-deploy docs-clean install-docs test lint format

help:			## Show this help message
	@echo "FlowStack SDK Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-docs:		## Install documentation dependencies
	pip install -r requirements-docs.txt

docs-serve:		## Serve documentation locally with live reload
	mkdocs serve --dev-addr localhost:8000

docs-build:		## Build documentation static site
	mkdocs build --clean --strict

docs-deploy:		## Deploy documentation to GitHub Pages
	mkdocs gh-deploy --force

docs-clean:		## Clean documentation build artifacts
	rm -rf site/

test:			## Run SDK tests
	python -m pytest tests/ -v

lint:			## Lint code with flake8
	flake8 flowstack/ --max-line-length=100

format:			## Format code with black
	black flowstack/ tests/

install:		## Install SDK in development mode
	pip install -e .

install-dev:		## Install SDK with development dependencies
	pip install -e ".[dev]"

build:			## Build distribution packages
	python setup.py sdist bdist_wheel

clean:			## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish:		## Publish to PyPI (requires credentials)
	twine upload dist/*

publish-test:		## Publish to TestPyPI
	twine upload --repository testpypi dist/*

# Documentation shortcuts
serve: docs-serve	## Alias for docs-serve
build-docs: docs-build	## Alias for docs-build
deploy-docs: docs-deploy ## Alias for docs-deploy