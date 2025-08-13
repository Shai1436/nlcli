# NLCLI Project Makefile

.PHONY: test test-quick install clean lint format help

# Default target
help:
	@echo "NLCLI Development Commands"
	@echo "========================="
	@echo "test          - Run full test suite"
	@echo "test-quick    - Run focused tests (pattern recognition)"
	@echo "test-patterns - Test instant pattern recognition only"
	@echo "install       - Install package in development mode"
	@echo "clean         - Clean build artifacts"
	@echo "lint          - Run code linting (if available)"
	@echo "format        - Format code (if available)"
	@echo "help          - Show this help message"

# Run quick focused tests
test-quick:
	@echo "Running quick test suite..."
	@python test_automation.py

# Run pattern-specific tests
test-patterns:
	@echo "Testing instant pattern recognition..."
	@python tests/test_instant_patterns_only.py

# Run full test suite
test:
	@echo "Running full test suite..."
	@python run_tests.py

# Install package in development mode
install:
	@echo "Installing NLCLI in development mode..."
	@pip install -e .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf __pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Code formatting (if black is available)
format:
	@echo "Formatting code..."
	@python -m black nlcli/ tests/ --line-length 100 2>/dev/null || echo "Black not available, skipping formatting"

# Code linting (if flake8 is available)  
lint:
	@echo "Running linter..."
	@python -m flake8 nlcli/ tests/ --max-line-length 100 2>/dev/null || echo "Flake8 not available, skipping linting"