.PHONY: all test cov black

all:

test:
	@pytest

cov:
	@pytest --cov=fjfnaranjobot --cov-report html tests/

black:
	@black -S fjfnaranjobot
	@black -S tests

