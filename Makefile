run := podman run --rm -ti -v "$$(pwd):/bot" -w /bot localhost/fjfnaranjo-bot:dev

.PHONY: all
all:
	@echo Default target is empty.

.PHONY: build-dev
build-dev:
	@podman build -f Containerfile.dev -t localhost/fjfnaranjo-bot:dev .

.PHONY: isort
isort:
	@$(run) isort fjfnaranjobot tests tests_new

.PHONY: black
black:
	@$(run) black fjfnaranjobot tests tests_new

.PHONY: checks
checks: isort black

.PHONY: test
test:
	@$(run) pytest tests/
	@$(run) pytest tests_new/

.PHONY: test-cov
test-cov:
	@$(run) pytest --cov=fjfnaranjobot --cov-report html tests/
	@$(run) pytest --cov=fjfnaranjobot --cov-report html tests_new/

.PHONY: test-cov-full
test-cov-full:
	@$(run) pytest --cov=fjfnaranjobot --cov=tests --cov-report html tests/
	@$(run) pytest --cov=fjfnaranjobot --cov=tests_new --cov-report html tests_new/

.PHONY: debug-bot
debug-bot: bot-stop
	-@podman-compose stop bot
	-@podman-compose run bot python3 -m fjfnaranjobot.server
