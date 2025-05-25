#!/usr/bin/env python3
"""
HTML to Markdown Converter - Dify Plugin
Main entry point for the plugin
"""

import os
import sys
from dify_plugin import DifyPlugin
from html_markdown_converter import HtmlMarkdownConverterProvider

def main():
    """Main function to run the plugin"""
    
    # Get plugin configuration from environment or use defaults
    plugin_config = {
        'name': 'html-to-markdown',
        'version': '0.1.0',
        'description': 'Convert HTML content to markdown using different conversion methods'
    }
    
    # Initialize the plugin
    plugin = DifyPlugin(
        provider_class=HtmlMarkdownConverterProvider,
        config=plugin_config
    )
    
    # Run the plugin
    plugin.run()

if __name__ == "__main__":
    main() 