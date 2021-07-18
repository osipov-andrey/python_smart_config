LIB_NAME = smart_config

test:
	@echo "--- RUNNING UNIT-TESTS: pytest"
	poetry run pytest

coverage:
	@echo "--- CHECKING COVERAGE: pytest"
	poetry run pytest --cov=./$(LIB_NAME)

check-format:
	@echo "--- CHECKING FORMAT: isort"
	poetry run isort --profile=black --diff --check ./
	@echo "--- CHECKING FORMAT: black"
	poetry run black --check --diff ./

lint:
	@echo "--- LINTING: flake8"
	poetry run flake8 --config=pyproject.toml ./
	@echo "--- LINTING: mypy"
	poetry run mypy --config-file=mypy.ini ./

fmt:
	@echo "--- FORMATTING: isort"
	poetry run isort --profile=black ./
	@echo "--- FORMATTING: black"
	poetry run black ./

build:
	poetry build

init:
	git init
	git add .
	ln -sf ../../pre-commit.sh .git/hooks/pre-commit
	poetry install
	make clean

ci:
	poetry install
	make check-format
	make lint
	make coverage
	make clean

clean:
	@echo "--- clean: Removing *.pyc, *.pyo, __pycache__ recursively"
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*.coverage' -delete
	find . -name 'dist' -type d  | xargs rm -rf
	find . -name '.pytest_cache' -type d  | xargs rm -rf
	find . -name 'htmlcov' -type d  | xargs rm -rf
	find . -name '__pycache__' -type d | xargs rm -rf
	find . -name '.mypy_cache' -type d | xargs rm -rf
