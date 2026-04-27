VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

SRC_DIR = src
MAIN = $(SRC_DIR)/main.py

MAP = maps/easy/01_linear_path.txt 

all: install

$(VENV_BIN)/activate:
	@echo "🧪 A criar ambiente virtual..."
	python3 -m venv $(VENV_DIR)

install: $(VENV_BIN)/activate
	@echo "📦 A instalar dependências (mypy, flake8)..."
	@$(PIP) install --upgrade pip
	@$(PIP) install flake8 mypy
	@echo "✅ Setup concluído."

run:
	@echo "🚀 A iniciar Fly-in..."
	@$(PYTHON) $(MAIN) $(ARGS)

lint:
	@echo "🔍 A verificar estilo (flake8)..."
	@$(VENV_BIN)/flake8 $(SRC_DIR)
	@echo "🧪 A verificar tipos (mypy)..."
	@$(VENV_BIN)/mypy $(SRC_DIR)

lint-strict:
	@echo "🛡️ A correr MyPy no modo STRICT..."
	@$(VENV_BIN)/mypy --strict $(SRC_DIR)

debug:
	@echo "🐞 A iniciar debugger (PDB)..."
	@$(PYTHON) -m pdb $(MAIN) $(ARGS)

clean:
	@echo "🧹 A limpar cache do Python e MyPy..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache
	@find . -type f -name "*.pyc" -delete

fclean: clean
	@echo "🗑️ A remover ambiente virtual..."
	@rm -rf $(VENV_DIR)

.PHONY: all install run visual debug clean fclean lint lint-strict