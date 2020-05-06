.PHONY: all test cov black

all:

isort:
	@isort -c

test:
	@pytest

cov:
	@pytest --cov=fjfnaranjobot --cov-report html tests/

black:
	@black -S fjfnaranjobot tests

