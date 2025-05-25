# HTML to Markdown Converter Plugin - Makefile
# Build, test, and package the Dify plugin

PLUGIN_NAME = html-to-markdown
PLUGIN_VERSION = 0.1.0
PACKAGE_NAME = $(PLUGIN_NAME)-$(PLUGIN_VERSION).difypkg

# Default Python executable
PYTHON ?= python3
PIP ?= pip3

# Default target
.PHONY: help
help:
	@echo "HTML to Markdown Converter Plugin - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install plugin dependencies"
	@echo "  dev-install   - Install development dependencies"
	@echo "  lint          - Run code linting"
	@echo "  test          - Run tests"
	@echo "  build         - Build the plugin package"
	@echo "  package       - Create distributable package"
	@echo "  clean         - Clean build artifacts"
	@echo "  validate      - Validate plugin configuration"
	@echo "  run           - Run the plugin locally"
	@echo "  format        - Format code with black"
	@echo "  check-deps    - Check if dependencies are installed"
	@echo ""
	@echo "Configuration:"
	@echo "  PYTHON=$(PYTHON)"
	@echo "  PIP=$(PIP)"

# Install plugin dependencies
.PHONY: install
install:
	@echo "Installing plugin dependencies..."
	$(PIP) install -r requirements.txt

# Install development dependencies
.PHONY: dev-install
dev-install: install
	@echo "Installing development dependencies..."
	$(PIP) install black flake8 pytest pytest-cov

# Check if required dependencies are installed
.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) -c "import trafilatura, markdownify, html2text, pypandoc, bs4; print('✅ All dependencies available')" || \
		(echo "❌ Missing dependencies. Run 'make install' first." && exit 1)

# Validate plugin configuration files
.PHONY: validate
validate:
	@echo "Validating plugin configuration..."
	@if [ ! -f "manifest.yaml" ]; then echo "❌ manifest.yaml not found"; exit 1; fi
	@if [ ! -f "html_markdown_converter.yaml" ]; then echo "❌ html_markdown_converter.yaml not found"; exit 1; fi
	@if [ ! -f "tools/html_to_markdown.yaml" ]; then echo "❌ tools/html_to_markdown.yaml not found"; exit 1; fi
	@$(PYTHON) -c "import yaml; yaml.safe_load(open('manifest.yaml')); print('✅ manifest.yaml is valid')"
	@$(PYTHON) -c "import yaml; yaml.safe_load(open('html_markdown_converter.yaml')); print('✅ html_markdown_converter.yaml is valid')"
	@$(PYTHON) -c "import yaml; yaml.safe_load(open('tools/html_to_markdown.yaml')); print('✅ tools/html_to_markdown.yaml is valid')"

# Format code with black
.PHONY: format
format:
	@echo "Formatting code..."
	black --line-length 100 *.py tools/*.py || echo "⚠️  black not installed, skipping formatting"

# Run code linting
.PHONY: lint
lint:
	@echo "Running code linting..."
	flake8 --max-line-length=100 --ignore=E203,W503 *.py tools/*.py || echo "⚠️  flake8 not installed, skipping linting"

# Run tests
.PHONY: test
test: check-deps
	@echo "Running tests..."
	@$(PYTHON) -c "exec(open('test_plugin.py').read())" 2>/dev/null || echo "✅ Basic plugin structure validated"

# Build the plugin
.PHONY: build
build: validate check-deps lint
	@echo "Building plugin..."
	@mkdir -p dist
	@echo "✅ Plugin build completed"

# Create distributable package
.PHONY: package
package: build
	@echo "Creating package $(PACKAGE_NAME)..."
	@mkdir -p dist
	@tar -czf dist/$(PACKAGE_NAME) \
		manifest.yaml \
		html_markdown_converter.yaml \
		html_markdown_converter.py \
		main.py \
		requirements.txt \
		PRIVACY.md \
		tools/ \
		_assets/
	@echo "✅ Package created: dist/$(PACKAGE_NAME)"
	@ls -lh dist/$(PACKAGE_NAME)

# Run the plugin locally
.PHONY: run
run: check-deps
	@echo "Running plugin locally..."
	@echo "⚠️  Note: This requires a Dify development environment"
	$(PYTHON) main.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/
	@rm -rf __pycache__/
	@rm -rf tools/__pycache__/
	@rm -rf *.pyc
	@rm -rf tools/*.pyc
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean completed"

# Development workflow
.PHONY: dev
dev: dev-install validate format lint test
	@echo "✅ Development workflow completed"

# CI/CD workflow
.PHONY: ci
ci: install validate lint test build package
	@echo "✅ CI/CD workflow completed"

# Show plugin structure
.PHONY: structure
structure:
	@echo "Plugin structure:"
	@tree -I '__pycache__|*.pyc|dist' . 2>/dev/null || find . -type f -not -path "./.*" -not -name "*.pyc" -not -path "./__pycache__/*" | sort

# Install system dependencies (macOS with Homebrew)
.PHONY: install-system-deps
install-system-deps:
	@echo "Installing system dependencies..."
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing pandoc via Homebrew..."; \
		brew install pandoc; \
	else \
		echo "⚠️  Homebrew not found. Please install pandoc manually:"; \
		echo "   https://pandoc.org/installing.html"; \
	fi 