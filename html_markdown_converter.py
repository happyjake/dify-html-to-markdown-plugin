from typing import Any
from dify_plugin import ToolProvider

class HtmlMarkdownConverterProvider(ToolProvider):
    """
    HTML to Markdown Converter Provider
    
    This provider offers HTML to markdown conversion using multiple libraries:
    - Trafilatura: Best for content extraction from web articles
    - Markdownify: Preserves HTML styling and structure
    - html2text: Clean, readable markdown output
    - Pandoc: Universal document converter
    """
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate provider credentials
        Since this tool doesn't require external API credentials, 
        this method performs basic validation
        """
        # No credentials needed for this provider
        pass 