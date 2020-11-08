.PHONY: all isort test cov cov-full black docs up down restart checks sh logs host-stop-bot host-run host-checks

compose := docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml
exec := $(compose) exec bot

all:

isort:
	@$(exec) isort fjfnaranjobot tests

test:
	@$(exec) pytest $(TEST_EXTRA)

cov:
	@$(exec) pytest --cov=fjfnaranjobot --cov-report html tests/

cov-full:
	@$(exec) pytest --cov=fjfnaranjobot --cov=tests --cov-report html tests/

black:
	@$(exec) black fjfnaranjobot tests

docs:
	@$(exec) $(MAKE) -C $@ html

up:
	@$(compose) up -d

down:
	@$(compose) down

restart: down up

checks: isort black

sh:
	@$(exec) sh

logs:
	@$(compose) logs -f

host-stop-bot:
	@$(compose) stop bot

host-run:
	@$(compose) run bot python -m fjfnaranjobot.server

host-checks:
	@$(compose) run bot isort fjfnaranjobot tests
	@$(compose) run bot black fjfnaranjobot tests
	@$(compose) run bot pytest --cov=fjfnaranjobot --cov-report html tests/
