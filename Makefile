compose := docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml
exec := $(compose) exec bot

.PHONY: all
all:

.PHONY: isort
isort:
	@$(exec) isort fjfnaranjobot tests

.PHONY: test
test:
	@$(exec) pytest tests/

.PHONY: cov
cov:
	@$(exec) pytest --cov=fjfnaranjobot --cov-report html tests/

.PHONY: cov-full
cov-full:
	@$(exec) pytest --cov=fjfnaranjobot --cov=tests --cov-report html tests/

.PHONY: black
black:
	@$(exec) black fjfnaranjobot tests

.PHONY: docs
docs:
	@$(exec) $(MAKE) -C $@ html

.PHONY: up
up:
	@$(compose) up -d

.PHONY: down
down:
	@$(compose) down

.PHONY: restart
restart: down up

.PHONY: checks
checks: isort black

.PHONY: sh
sh:
	@$(exec) sh

.PHONY: logs
logs:
	@$(compose) logs -f

.PHONY: restart-bot
restart-bot:
	@$(compose) restart bot

.PHONY: stop-bot
stop-bot:
	@$(compose) stop bot

.PHONY: run-bot
run-bot:
	@$(compose) run bot

.PHONY: run-bot-in-host
run-bot-in-host:
	-@$(compose) run bot python3 -m fjfnaranjobot.server

.PHONY: print-cmd
print-cmd:
	@echo $(exec)
