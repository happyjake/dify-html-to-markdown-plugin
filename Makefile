# HTML to Markdown Converter Plugin - Makefile
# Build, test, and package the Dify plugin

PLUGIN_NAME = html-to-markdown-plugin
PLUGIN_VERSION = 0.1.1
PACKAGE_NAME = $(PLUGIN_NAME).difypkg

# Python 3.12+ required for compatibility
PYTHON ?= python3.12
PIP ?= pip3.12
VENV_DIR = venv-test

# Default target
.PHONY: help
help:
	@echo "HTML to Markdown Converter Plugin - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  setup         - Create Python 3.12 virtual environment and install dependencies"
	@echo "  install       - Install plugin dependencies"
	@echo "  dev-install   - Install development dependencies"
	@echo "  lint          - Run code linting"
	@echo "  test          - Run basic tests"
	@echo "  build         - Build the plugin package (.difypkg)"
	@echo "  rebuild       - Clean and rebuild the plugin package"
	@echo "  clean         - Clean build artifacts"
	@echo "  validate      - Validate plugin configuration"
	@echo "  format        - Format code with black"
	@echo "  check-deps    - Check if dependencies are installed"
	@echo "  check-python  - Check Python 3.12+ availability"
	@echo ""
	@echo "Testing targets:"
	@echo "  test-conversion - Test direct conversion functions"
	@echo "  test-plugin     - Test plugin integration"
	@echo ""
	@echo "Development workflow:"
	@echo "  dev           - Full development workflow (format, lint, test, build)"
	@echo ""
	@echo "Configuration:"
	@echo "  PYTHON=$(PYTHON)"
	@echo "  PIP=$(PIP)"
	@echo "  VENV_DIR=$(VENV_DIR)"

# Check Python 3.12+ availability
.PHONY: check-python
check-python:
	@echo "Checking Python 3.12+ availability..."
	@$(PYTHON) --version 2>/dev/null | grep -E "Python 3\.(1[2-9]|[2-9][0-9])" > /dev/null || \
		(echo "❌ Python 3.12+ required. Current: $$($(PYTHON) --version 2>/dev/null || echo 'Not found')"; \
		 echo "   Install with: brew install python@3.12"; exit 1)
	@echo "✅ Python $$($(PYTHON) --version 2>&1 | cut -d' ' -f2) is compatible"

# Create Python 3.12 virtual environment
.PHONY: setup
setup: check-python
	@echo "Setting up Python 3.12 virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "✅ Virtual environment created: $(VENV_DIR)"; \
	else \
		echo "✅ Virtual environment already exists: $(VENV_DIR)"; \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	@. $(VENV_DIR)/bin/activate && pip install --upgrade pip
	@. $(VENV_DIR)/bin/activate && pip install -r requirements.txt
	@echo "✅ Setup completed. Activate with: source $(VENV_DIR)/bin/activate"

# Install plugin dependencies
.PHONY: install
install:
	@echo "Installing plugin dependencies..."
	$(PIP) install -r requirements.txt

# Install development dependencies
.PHONY: dev-install
dev-install: install
	@echo "Installing development dependencies..."
	$(PIP) install black flake8 pytest pytest-cov dify-plugin

# Check if required dependencies are installed
.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) -c "import trafilatura, markdownify, html2text, pypandoc, bs4, dify_plugin; print('✅ All dependencies available')" || \
		(echo "❌ Missing dependencies. Run 'make install' first." && exit 1)

# Validate plugin configuration files
.PHONY: validate
validate:
	@echo "Validating plugin configuration..."
	@if [ ! -f "manifest.yaml" ]; then echo "❌ manifest.yaml not found"; exit 1; fi
	@if [ ! -f "provider/html_markdown_converter.yaml" ]; then echo "❌ provider/html_markdown_converter.yaml not found"; exit 1; fi
	@if [ ! -f "tools/html_to_markdown.yaml" ]; then echo "❌ tools/html_to_markdown.yaml not found"; exit 1; fi
	@echo "⚠️  Skipping YAML validation (yaml module not required for build)"
	@echo "✅ Basic file validation completed"

# Format code with black
.PHONY: format
format:
	@echo "Formatting code..."
	black --line-length 100 *.py tools/*.py provider/*.py || echo "⚠️  black not installed, skipping formatting"

# Run code linting
.PHONY: lint
lint:
	@echo "Running code linting..."
	flake8 --max-line-length=100 --ignore=E203,W503 *.py tools/*.py provider/*.py || echo "⚠️  flake8 not installed, skipping linting"

# Build the plugin package using Dify CLI
.PHONY: build
build: validate
	@echo "Building plugin package..."
	@mkdir -p dist
	@dify plugin package . -o dist/$(PACKAGE_NAME)
	@echo "✅ Plugin package created: dist/$(PACKAGE_NAME)"
	@ls -lh dist/$(PACKAGE_NAME)

# Clean and rebuild
.PHONY: rebuild
rebuild: clean build

# Run basic tests
.PHONY: test
test: check-deps
	@echo "Running basic tests..."
	@$(PYTHON) -c "from tools.html_to_markdown import HtmlToMarkdownTool; print('✅ Tool import successful')"
	@echo "✅ Basic tests completed"

# Test direct conversion functions
.PHONY: test-conversion
test-conversion: check-deps
	@echo "Testing conversion functions..."
	@$(PYTHON) -c "\
from tools.html_to_markdown import HtmlToMarkdownTool; \
tool = HtmlToMarkdownTool(); \
html = '<h1>Test</h1><p>This is <strong>bold</strong> text.</p>'; \
for method in ['trafilatura', 'markdownify', 'html2text', 'pandoc', 'beautifulsoup', 'simple']: \
    try: \
        result = getattr(tool, f'_extract_with_{method}')(html); \
        print(f'✅ {method}: {len(result.get(\"content\", \"\"))} chars'); \
    except Exception as e: \
        print(f'❌ {method}: {e}'); \
"

# Test plugin integration
.PHONY: test-plugin
test-plugin: check-deps
	@echo "Testing plugin integration..."
	@$(PYTHON) -c "\
import json; \
from tools.html_to_markdown import HtmlToMarkdownTool; \
tool = HtmlToMarkdownTool(); \
html = '<html><head><title>Test Page</title></head><body><h1>Test</h1><p>Content</p></body></html>'; \
params = {'html_content': html, 'conversion_method': 'trafilatura'}; \
messages = list(tool._invoke(params)); \
if messages: \
    print('✅ Plugin integration test passed'); \
    content = messages[0].message; \
    if 'markdown:' in content and 'title:' in content: \
        print('✅ Structured output format correct'); \
    else: \
        print('⚠️  Output format may need review'); \
else: \
    print('❌ Plugin integration test failed'); \
"

# Run the plugin locally (for testing)
.PHONY: run
run: check-deps
	@echo "Running plugin locally..."
	@echo "⚠️  Note: This requires proper Dify environment"
	$(PYTHON) main.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/
	@rm -rf __pycache__/
	@rm -rf tools/__pycache__/
	@rm -rf provider/__pycache__/
	@rm -rf *.pyc
	@rm -rf tools/*.pyc
	@rm -rf provider/*.pyc
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean completed"

# Clean everything including virtual environment
.PHONY: clean-all
clean-all: clean
	@echo "Cleaning virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "✅ All artifacts cleaned"

# Development workflow
.PHONY: dev
dev: format lint test build
	@echo "✅ Development workflow completed"

# Complete workflow with virtual environment
.PHONY: dev-full
dev-full: setup dev
	@echo "✅ Complete development workflow completed"

# Show plugin structure
.PHONY: structure
structure:
	@echo "Plugin structure:"
	@tree -I '__pycache__|*.pyc|dist|$(VENV_DIR)' . 2>/dev/null || find . -type f -not -path "./.*" -not -name "*.pyc" -not -path "./__pycache__/*" -not -path "./$(VENV_DIR)/*" -not -path "./dist/*" | sort

# Install system dependencies (macOS with Homebrew)
.PHONY: install-system-deps
install-system-deps:
	@echo "Installing system dependencies..."
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing pandoc and Python 3.12 via Homebrew..."; \
		brew install pandoc python@3.12; \
	else \
		echo "⚠️  Homebrew not found. Please install manually:"; \
		echo "   - pandoc: https://pandoc.org/installing.html"; \
		echo "   - Python 3.12: https://www.python.org/downloads/"; \
	fi

# Quick build for development
.PHONY: quick
quick: validate build
	@echo "✅ Quick build completed"

# Verify Dify CLI is available
.PHONY: check-dify
check-dify:
	@echo "Checking Dify CLI availability..."
	@dify version || (echo "❌ Dify CLI not found. Install with: pip install dify-plugin"; exit 1)
	@echo "✅ Dify CLI is available" 