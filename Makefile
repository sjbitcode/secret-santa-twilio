PY=python3
VENV=venv
BIN=$(VENV)/bin
PYTHON=$(BIN)/python
NUMBERS_CSV_FILE=$(PWD)/numbers.csv

# -------------------------------------------------------------------
# Development-related commands
# Run commands inside virtualenv - https://earthly.dev/blog/python-makefile/
# -------------------------------------------------------------------

$(VENV)/bin/activate: requirements.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -r requirements.txt


## Remove cached files and dirs from workspace
clean:
	@echo "\033[1;37m---- Cleaning workspace 🧹💨 ----\033[0m\n"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.DS_Store" -delete


## Remove virtualenv directory
clean-venv:
	@echo "\033[1;37m---- Removing virtualenv 🗂 🧹💨 ----\033[0m\n"
	rm -rf $(VENV)


## Read recipients from numbers.csv
numbers:
	@echo "\033[1;37m---- Reading $(NUMBERS_CSV_FILE) 👀🗒  ----\033[0m\n"
	@cat $(NUMBERS_CSV_FILE)


## Run a shell
shell: $(VENV)/bin/activate
	@echo "\033[1;37m---- Spinning up a Python shell 🐍🐚 ----\033[0m\n"
	$(PYTHON)


## Format the codebase
format: $(VENV)/bin/activate
	@echo "\033[1;37m---- Running isort 🔤 ---- \033[0m\n"
	$(BIN)/isort secret_santa test.py
	@echo "\n\033[1;37m---- Running black 🖤 ---- \033[0m\n"
	$(BIN)/black secret_santa test.py --verbose
	@echo "\n\033[1;37m---- Running flake8 ❄️  ---- \033[0m\n"
	$(BIN)/flake8 secret_santa test.py


## Run formatting in diff mode
format-dry: $(VENV)/bin/activate
	@echo "\033[1;37m----  Running isort 🔤 ---- \033[0m\n"
	$(BIN)/isort secret_santa test.py --diff
	@echo "\n\033[1;37m---- Running black 🖤 ---- \033[0m\n"
	$(BIN)/black secret_santa test.py --verbose --diff
	@echo "\n\033[1;37m---- Running flake8 ❄️ ---- \033[0m\n"
	$(BIN)/flake8 secret_santa test.py


## Run ngrok tunnel on port 8000
tunnel:
	ngrok http 8000


## Run flask app
app: $(VENV)/bin/activate
	@echo "\033[1;37m---- Running flask app 🤖 ----\033[0m\n"
	$(PYTHON) -m secret_santa.app


## Run the test cli with a recipient number (to=+1234567891)
test-twilio: $(VENV)/bin/activate
	@echo "\033[1;37m---- Sending a test message to $(to) 📲💥 ----\033[0m\n"
	$(PYTHON) test.py --to $(to)


## Run tests with coverage
test: $(VENV)/bin/activate
	@echo "\033[1;37m---- Running unittests 🧪✨ ---- \033[0m\n"
	$(BIN)/coverage run -m unittest discover && $(BIN)/coverage report


## Install step for Travis
install: $(VENV)/bin/activate
	@echo "\033[1;37m---- Running travis install 👷‍♂️ ---- \033[0m\n"


# -------------------------------------------------------------------
# Self-documenting Makefile targets - https://git.io/Jg3bU
# -------------------------------------------------------------------

.DEFAULT_GOAL := help

help:
	@echo "Usage:"
	@echo "  make <target>"
	@awk '/^[a-zA-Z\-\_0-9]+:/ \
		{ \
			helpMessage = match(lastLine, /^## (.*)/); \
			if (helpMessage) { \
				helpCommand = substr($$1, 0, index($$1, ":")-1); \
				helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
				helpGroup = match(helpMessage, /^@([^ ]*)/); \
				if (helpGroup) { \
					helpGroup = substr(helpMessage, RSTART + 1, index(helpMessage, " ")-2); \
					helpMessage = substr(helpMessage, index(helpMessage, " ")+1); \
				} \
				printf "%s|  %-15s %s\n", \
					helpGroup, helpCommand, helpMessage; \
			} \
		} \
		{ lastLine = $$0 }' \
		$(MAKEFILE_LIST) \
	| sort -t'|' -sk1,1 \
	| awk -F '|' ' \
			{ \
			cat = $$1; \
			if (cat != lastCat || lastCat == "") { \
				if ( cat == "0" ) { \
					print "\nTargets:" \
				} else { \
					gsub("_", " ", cat); \
					printf "\n%s\n", cat; \
				} \
			} \
			print $$2 \
		} \
		{ lastCat = $$1 }'
	@echo ""
