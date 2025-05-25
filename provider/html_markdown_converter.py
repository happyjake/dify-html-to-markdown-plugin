from typing import Any

from dify_plugin import ToolProvider


class HtmlMarkdownConverterProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the HTML to Markdown converter.
        Since this tool doesn't require any credentials, this is a no-op.
        """
        pass
