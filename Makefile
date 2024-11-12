# Makefile

# Variables
VENV_DIR := .venv
PYTHON := python3

# Target to create virtual environment and install dependencies
.PHONY: build
build: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
	touch $(VENV_DIR)/bin/activate

# Target to clean the virtual environment
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
