#!/bin/bash

# Local CI Test Script
# This script runs the same checks that GitHub Actions CI runs

set -e # Exit on any error

echo "🔧 Setting up Python environment..."

# Check if we have the required Python version
python3 --version

# Install dependencies if not already installed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt

echo "🔍 Running code quality checks..."

# Check code formatting with black
echo "  ✅ Checking code formatting with black..."
python3 -m black --check --diff .

# Check import sorting with isort
echo "  ✅ Checking import sorting with isort..."
python3 -m isort --check-only --diff .

# Run flake8 linting
echo "  ✅ Running flake8 linting..."
python3 -m flake8 .

# Run security checks with bandit
echo "  ✅ Running security checks with bandit..."
python3 -m bandit -r . -x ./venv/,./env/

# Check for security vulnerabilities with safety
echo "  ✅ Checking for security vulnerabilities..."
python3 -m safety check

# Run tests
echo "  ✅ Running tests..."
python3 -m pytest test_plugin.py -v

echo "🎉 All checks passed! Ready to push to GitHub."
