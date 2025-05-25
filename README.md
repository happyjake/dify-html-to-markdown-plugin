# HTML to Markdown Converter - Dify Plugin

A powerful Dify plugin that converts HTML content to markdown format using multiple conversion libraries, each optimized for different use cases.

## 🚀 Features

- **Multiple Conversion Methods**: Choose from 4 different conversion libraries
- **Trafilatura**: Best for content extraction from web articles
- **Markdownify**: Preserves HTML styling and structure  
- **html2text**: Clean, readable markdown output
- **Pandoc**: Universal document converter
- **No External Dependencies**: All processing done locally
- **Content Sanitization**: Removes JavaScript and unwanted elements
- **Performance Metrics**: Shows processing time and output statistics

## 📦 Installation

### Prerequisites

- Python 3.12+
- Dify development environment
- Pandoc (for Pandoc conversion method)

### System Dependencies

Install Pandoc (required for one of the conversion methods):

```bash
# macOS with Homebrew
make install-system-deps

# Manual installation
# Visit: https://pandoc.org/installing.html
```

### Plugin Dependencies

```bash
# Install all dependencies
make install

# Or install manually
pip install -r requirements.txt
```

## 🔧 Development

### Quick Start

```bash
# Install development dependencies
make dev-install

# Validate configuration
make validate

# Run tests
make test

# Build the plugin
make build

# Create distributable package
make package
```

### Available Make Commands

```bash
make help                 # Show all available commands
make install             # Install plugin dependencies
make dev-install         # Install development dependencies
make validate            # Validate plugin configuration
make test                # Run tests
make build               # Build the plugin
make package             # Create distributable package
make clean               # Clean build artifacts
make format              # Format code with black
make lint                # Run code linting
make run                 # Run plugin locally (requires Dify environment)
```

## 🎯 Usage in Dify

### Tool Parameters

1. **HTML Content** (required): The HTML content to convert
2. **Conversion Method** (optional): Choose conversion library
   - `trafilatura` (default) - Best for content extraction
   - `markdownify` - Preserves styling
   - `html2text` - Clean output
   - `pandoc` - Universal converter

### Example Usage

```html
<!-- Input HTML -->
<html>
<body>
  <h1>Welcome to My Blog</h1>
  <p>This is a <strong>sample</strong> blog post with <em>formatting</em>.</p>
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</body>
</html>
```

**Output** (with Trafilatura):
```markdown
# Welcome to My Blog

This is a **sample** blog post with *formatting*.

- Item 1
- Item 2
```

## 🔍 Conversion Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Trafilatura** | Web articles, blog posts | Excellent content extraction, metadata | May miss some formatting |
| **Markdownify** | Styled content | Preserves structure, handles complex HTML | Can include unwanted elements |
| **html2text** | Clean documents | Simple, reliable output | Basic conversion only |
| **Pandoc** | Universal conversion | Standards compliant, powerful | Requires system installation |

## 📁 Plugin Structure

```
html-to-markdown-plugin/
├── manifest.yaml                 # Plugin manifest
├── html_markdown_converter.yaml  # Tool provider config
├── html_markdown_converter.py    # Provider implementation
├── main.py                      # Plugin entry point
├── requirements.txt             # Python dependencies
├── PRIVACY.md                   # Privacy policy
├── README.md                    # This file
├── Makefile                     # Build system
├── tools/
│   ├── html_to_markdown.yaml    # Tool configuration
│   └── html_to_markdown.py      # Tool implementation
└── _assets/
    └── icon.svg                 # Plugin icon
```

## 🛠️ Development Details

### Key Components

1. **Manifest** (`manifest.yaml`): Plugin metadata and configuration
2. **Provider** (`html_markdown_converter.py`): Main provider class
3. **Tool** (`tools/html_to_markdown.py`): Core conversion logic
4. **Build System** (`Makefile`): Automated building and testing

### Testing

The plugin includes comprehensive tests for all conversion methods:

```bash
# Run all tests
make test

# Test specific components
python -c "
from tools.html_to_markdown import HtmlToMarkdownTool
tool = HtmlToMarkdownTool()
result = tool._extract_with_trafilatura('<h1>Test</h1>')
print('Success:', result['success'])
"
```

### Code Quality

- **Linting**: flake8 for code quality
- **Formatting**: black for consistent code style
- **Validation**: YAML configuration validation

## 🔒 Security & Privacy

- **Local Processing**: All HTML content processed locally
- **No External APIs**: No data sent to external services
- **Content Sanitization**: JavaScript and harmful content removed
- **Temporary Files**: Cleaned up immediately after processing

See [PRIVACY.md](PRIVACY.md) for full privacy policy.

## 🐛 Troubleshooting

### Common Issues

1. **Pandoc not found**
   ```bash
   make install-system-deps
   ```

2. **Dependencies missing**
   ```bash
   make install
   ```

3. **YAML validation errors**
   ```bash
   make validate
   ```

4. **Import errors**
   ```bash
   make check-deps
   ```

### Debug Mode

```bash
# Run with verbose output
PYTHONPATH=. python main.py

# Test individual conversion methods
python -c "
from tools.html_to_markdown import HtmlToMarkdownTool
tool = HtmlToMarkdownTool()
# Test each method...
"
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

### Development Workflow

```bash
# Set up development environment
make dev-install

# Make changes...

# Validate and test
make dev

# Build and package
make ci
```

## 📄 License

This plugin is open source. See the original CLI tool license for details.

## 🤝 Support

For issues and support:
1. Check the troubleshooting section
2. Run `make test` to identify issues
3. Review the privacy policy
4. Submit issues with detailed error messages

---

**Made for Dify** - Transform HTML to Markdown with precision and choice. 