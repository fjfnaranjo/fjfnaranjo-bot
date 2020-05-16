.PHONY: all isort test cov black docs

all:

isort:
	@isort -y

test:
	@pytest

cov:
	@pytest --cov=fjfnaranjobot --cov-report html tests/

black:
	@black -S fjfnaranjobot tests

docs:
	$(MAKE) -C $@ html
