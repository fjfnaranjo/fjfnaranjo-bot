compose := docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml
exec := $(compose) exec bot

.PHONY: all
all:
	@echo Default target is empty.

.PHONY: up
up:
	@$(compose) up -d

.PHONY: down
down:
	@$(compose) down

.PHONY: restart
restart:
	@$(compose) restart

.PHONY: restart-bot
restart-bot:
	@$(compose) restart bot

.PHONY: bot-up
bot-up:
	@$(compose) up -d bot

.PHONY: bot-stop
bot-stop:
	@$(compose) stop bot

.PHONY: isort
isort: bot-up
	@$(exec) isort fjfnaranjobot tests

.PHONY: black
black: bot-up
	@$(exec) black fjfnaranjobot tests

.PHONY: checks
checks: isort black

.PHONY: test
test: bot-up
	@$(exec) pytest tests/

.PHONY: test-cov
test-cov: bot-up
	@$(exec) pytest --cov=fjfnaranjobot --cov-report html tests/

.PHONY: test-cov-full
test-cov-full: bot-up
	@$(exec) pytest --cov=fjfnaranjobot --cov=tests --cov-report html tests/

.PHONY: docs
docs: bot-up
	@$(exec) $(MAKE) -C docs html

.PHONY: sh
sh: bot-up
	@$(exec) sh

.PHONY: logs
logs: up
	@$(compose) logs -f

.PHONY: logs-bot
logs-bot: bot-up
	@$(compose) logs -f bot

.PHONY: run-bot
run-bot: bot-stop
	@$(compose) run bot

.PHONY: debug-bot
debug-bot: bot-stop
	-@$(compose) run bot python3 -m fjfnaranjobot.server

.PHONY: print-compose
print-compose:
	@echo $(compose)

.PHONY: print-exec
print-exec:
	@echo $(exec)

.PHONY: clean
clean:
	@$(exec) $(MAKE) -C docs clean
	rm -rf docs/_build
	rm -rf docs/botdata
