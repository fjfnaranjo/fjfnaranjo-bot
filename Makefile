.PHONY: all isort test cov cov-full black docs up down restart checks sh logs restart-bot stop-bot run-bot run-bot-in-host print-cmd

compose := docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml
exec := $(compose) exec bot

all:

isort:
	@$(exec) isort fjfnaranjobot tests

test:
	@$(exec) pytest tests/

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

restart-bot:
	@$(compose) restart bot

stop-bot:
	@$(compose) stop bot

run-bot:
	@$(compose) run bot

run-bot-in-host:
	-@$(compose) run bot python3 -m fjfnaranjobot.server

print-cmd:
	@echo $(exec)
