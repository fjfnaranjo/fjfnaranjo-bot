.PHONY: all isort test cov cov-full black docs up down restart

all:

isort:
	@isort -y

test:
	@pytest

cov:
	@pytest --cov=fjfnaranjobot --cov-report html tests/

cov-full:
	@pytest --cov=fjfnaranjobot --cov=tests --cov-report html tests/

black:
	@black -S fjfnaranjobot tests

docs:
	$(MAKE) -C $@ html

up:
	@docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d

down:
	@docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml down

restart: down up
