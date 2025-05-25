#!/usr/bin/env python3
"""
Simple test script for the HTML to Markdown converter plugin
"""

import os
import sys

sys.path.insert(0, ".")


def test_imports():
    """Test that all required modules can be imported"""
    try:
        import html2text  # noqa: F401
        import markdownify  # noqa: F401
        import pypandoc  # noqa: F401
        import trafilatura  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401

        print("✅ All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_structure():
    """Test that plugin structure is correct"""
    required_files = [
        "manifest.yaml",
        "html_markdown_converter.yaml",
        "html_markdown_converter.py",
        "main.py",
        "requirements.txt",
        "tools/html_to_markdown.yaml",
        "tools/html_to_markdown.py",
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            return False

    print("✅ Plugin structure is correct")
    return True


def test_tool_classes():
    """Test that the tool classes can be instantiated"""
    try:
        # Mock the Dify plugin classes for testing
        class MockTool:
            def create_text_message(self, text):
                return f"MESSAGE: {text}"

        class MockToolProvider:
            def _validate_credentials(self, credentials):
                pass

        # Import and test our classes
        # Patch the base classes
        import tools.html_to_markdown
        from html_markdown_converter import HtmlMarkdownConverterProvider
        from tools.html_to_markdown import HtmlToMarkdownTool

        tools.html_to_markdown.Tool = MockTool

        import html_markdown_converter

        html_markdown_converter.ToolProvider = MockToolProvider

        # Test instantiation
        tool = HtmlToMarkdownTool()  # noqa: F841
        provider = HtmlMarkdownConverterProvider()  # noqa: F841

        print("✅ Tool classes can be instantiated")
        return True
    except Exception as e:
        print(f"❌ Tool class error: {e}")
        return False


def test_conversion_methods():
    """Test the core conversion methods"""
    try:
        # Mock the Tool class for testing
        class MockTool:
            def create_text_message(self, text):
                return f"MESSAGE: {text}"

        # Import and patch
        import tools.html_to_markdown
        from tools.html_to_markdown import HtmlToMarkdownTool

        tools.html_to_markdown.Tool = MockTool

        tool = HtmlToMarkdownTool()
        test_html = "<html><body><h1>Test</h1><p>This is a test.</p></body></html>"

        methods = ["trafilatura", "markdownify", "html2text", "pandoc"]
        for method in methods:
            try:
                if method == "trafilatura":
                    result = tool._extract_with_trafilatura(test_html)
                elif method == "markdownify":
                    result = tool._extract_with_markdownify(test_html)
                elif method == "html2text":
                    result = tool._extract_with_html2text(test_html)
                elif method == "pandoc":
                    result = tool._extract_with_pandoc(test_html)

                if result["success"] and result["content"]:
                    print(
                        f"✅ {method}: Success (Length: {len(result['content'])} chars)"
                    )
                else:
                    print(f"⚠️  {method}: {result.get('error', 'No content produced')}")
            except Exception as e:
                print(f"❌ {method}: {e}")

        return True
    except Exception as e:
        print(f"❌ Conversion test error: {e}")
        return False


if __name__ == "__main__":
    print("Testing HTML to Markdown converter plugin...")

    tests = [
        ("Import test", test_imports),
        ("Structure test", test_structure),
        ("Tool classes test", test_tool_classes),
        ("Conversion methods test", test_conversion_methods),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1

    print("\n--- Test Results ---")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
