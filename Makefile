VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

SRC_DIR = src
MAIN = $(SRC_DIR)/main.py

# ARGS ?= maps/easy/01_linear_path.txt
# ARGS ?= maps/easy/02_simple_fork.txt
# ARGS ?= maps/easy/03_basic_capacity.txt
# ARGS ?= maps/medium/01_dead_end_trap.txt
# ARGS ?= maps/medium/02_circular_loop.txt
# ARGS ?= maps/medium/03_priority_puzzle.txt
# ARGS ?= maps/hard/01_maze_nightmare.txt
# ARGS ?= maps/hard/02_capacity_hell.txt
ARGS ?= maps/hard/03_ultimate_challenge.txt
# ARGS ?= maps/challenger/01_the_impossible_dream.txt


all: install

$(VENV_BIN)/activate:
	@echo "🧪 Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)

install: $(VENV_BIN)/activate
	@echo "📦 Installing dependencies (mypy, flake8, pygame)..."
	@$(PIP) install --upgrade pip >/dev/null 2>&1
	@$(PIP) install flake8 mypy >/dev/null 2>&1
	@$(PIP) install pygame >/dev/null 2>&1
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
	@$(VENV_BIN)/mypy $(SRC_DIR) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

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

re: fclean all

.PHONY: all install run visual debug clean fclean lint lint-strict
