SHELL = /bin/bash

INSTALL_DIRECTORY = bin
APEX_CMD := $(INSTALL_DIRECTORY)/apex
PIP_CMD = $(INSTALL_DIRECTORY)/bin/pip
NOSE_CMD := $(INSTALL_DIRECTORY)/bin/nosetests
FLAKE8_CMD := $(INSTALL_DIRECTORY)/bin/flake8
AUTOPEP8_CMD := $(INSTALL_DIRECTORY)/bin/autopep8
PYTHON_FILES := $(shell find functions -path .venv -prune -o  -path build -prune -o -type f -name "*.py" -print)

# Linting rules
PEP8_IGNORE := "E128,E221,E241,E251,E265,E266,E272,E402,E501,E711"

# E128: continuation line under-indented for visual indent
# E221: multiple spaces before operator
# E241: multiple spaces after ':'
# E251: multiple spaces around keyword/parameter equals
# E265: block comment should start with '# '
# E266: too many leading '#' for block comment
# E272: multiple spaces before keyword
# E402: module level import not at top of file
# E501: line length 79 per default
# E711: comparison to None should be 'if cond is None:' (SQLAlchemy's filter syntax requires this ignore!)

IN_FILES = $(shell find . -type f -name '*.json.in')
JSON_FILES = $(patsubst %.json.in, %.json, $(IN_FILES))

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- all                Build the app"
	@echo "- test               Launch the tests"
	@echo "- autolint			Run the autolinter."
	@echo "- lint               Run the linter."
	@echo "- clean              Remove generated files"
	@echo "- cleanall           Remove generated files and py deps"

.PHONY: all
all: templates 
	curl https://raw.githubusercontent.com/apex/apex/master/install.sh | DEST=$(APEX_CMD) sh

templates: $(JSON_FILES)



%.json: %.json.in
	source config && \
	envsubst < $<  > $@
	echo "$<" to "$@"

.PHONY: test
test:
	${NOSE_CMD} tests

.PHONY: lint
lint:
	${FLAKE8_CMD} --ignore=${PEP8_IGNORE} $(PYTHON_FILES);

.PHONY: autolint
autolint:
	${AUTOPEP8_CMD} --in-place --aggressive --aggressive --verbose --ignore=${PEP8_IGNORE} $(PYTHON_FILES);

.PHONY: clean
clean:
	rm -i $(JSON_FILES)
	

.PHONY: cleanall
cleanall: clean
	rm -rf .venv
