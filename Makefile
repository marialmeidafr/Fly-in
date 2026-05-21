VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

SRC_DIR = src
MAIN = $(SRC_DIR)/main.py

# ARGS ?= maps/easy/01_linear_path.txt
ARGS ?= maps/challenger/01_the_impossible_dream.txt

all: install

$(VENV_BIN)/activate:
	@echo "🧪 Creating virtual environment..."
	python3 -m venv $(VENV_DIR)

install: $(VENV_BIN)/activate
	@echo "📦 Installing dependencies (mypy, flake8, pygame)..."
	@$(PIP) install --upgrade pip
	@$(PIP) install flake8 mypy
	@$(PIP) install pygame
	@echo "✅ Setup complete."

run:
	@echo "🚀 Starting Fly-in..."
	@$(PYTHON) $(MAIN) $(ARGS)

visual: install
	@echo "🎮 Starting Fly-in with Visual Mode..."
	@$(PYTHON) $(MAIN) $(ARGS) --visual

lint:
	@echo "🔍 Checking style (flake8)..."
	@$(VENV_BIN)/flake8 $(SRC_DIR)
	@echo "🧪 Checking types (mypy)..."
	@$(VENV_BIN)/mypy $(SRC_DIR)

lint-strict:
	@echo "🛡️ Running MyPy in STRICT mode..."
	@$(VENV_BIN)/mypy --strict $(SRC_DIR)

debug:
	@echo "🐞 Starting debugger (PDB)..."
	@$(PYTHON) -m pdb $(MAIN) $(ARGS)

clean:
	@echo "🧹 Cleaning Python and MyPy cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache
	@find . -type f -name "*.pyc" -delete

fclean: clean
	@echo "🗑️ Removing virtual environment..."
	@rm -rf $(VENV_DIR)

.PHONY: all install run visual debug clean fclean lint lint-strict