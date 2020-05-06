.PHONY: all test cov black

all:

isort:
	@isort -y

test:
	@pytest

cov:
	@pytest --cov=fjfnaranjobot --cov-report html tests/

black:
	@black -S fjfnaranjobot tests

