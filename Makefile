# Makefile - DDC Core v2.0 DEFINITIVE STANDARD

.PHONY: setup run security clean test lint format

PYTHON_COMMAND = python

# Essential environment file copy
security:
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "✅ Created .env file from template. Please populate it with your keys."; \
	fi

# Command: make setup
setup: security
	@echo "🛠️ Configuring Definitive Environment (Cross-Platform)..."
	$(PYTHON_COMMAND) -m venv .venv
	. .venv/bin/activate; pip install -r requirements.txt
	# Robust Python version check using Python itself
	@export PYTHON_VERSION=`$(PYTHON_COMMAND) -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"`; \
		echo "✅ Setup Complete. Python Version: $$PYTHON_VERSION"

# Command: make run (Runs the app with maximum local security)
run:
	@echo "🚀 Starting Definitive Dashboard (http://localhost:8501)..."
	# Mandate loopback binding for maximum security
	. .venv/bin/activate; \
		export PYTHON_VERSION=`$(PYTHON_COMMAND) -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"`; \
		streamlit run app.py --server.address 127.0.0.1
	@echo "⚠️ SECURITY NOTE: Application is only accessible via localhost."

# Development commands
test:
	. .venv/bin/activate; pytest

lint:
	. .venv/bin/activate; ruff check .

format:
	. .venv/bin/activate; black .
	. .venv/bin/activate; ruff check --fix .

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .venv __pycache__ .pytest_cache app_errors.log*
	@echo "✅ Cleanup complete."