# Define Python version and virtual environment directory
PYTHON_VERSION = 3.11.4
VENV_DIR = venv

# Define requirements file
REQUIREMENTS = requirements.txt

# Command to create virtual environment with specified Python version
$(VENV_DIR)/bin/python:
	@echo "Creating virtual environment with Python $(PYTHON_VERSION)..."
	pyenv install -s $(PYTHON_VERSION)
	pyenv local $(PYTHON_VERSION)
	python3 -m venv $(VENV_DIR)

# Install dependencies in the virtual environment
.PHONY: build
build: $(VENV_DIR)/bin/python
	@echo "Installing dependencies from $(REQUIREMENTS)..."
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)

# Clean up virtual environment
.PHONY: clean
clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)
