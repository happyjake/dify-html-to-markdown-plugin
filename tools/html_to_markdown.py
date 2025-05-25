import os
import re
import tempfile
import time
from collections.abc import Generator
from typing import Any

import html2text
import pypandoc
import trafilatura
from bs4 import BeautifulSoup
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from markdownify import markdownify


class HtmlToMarkdownTool(Tool):
    """
    HTML to Markdown conversion tool with multiple conversion methods
    """

    def _extract_with_trafilatura(self, html_content: str) -> dict:
        """Extract content using Trafilatura"""
        try:
            start_time = time.time()

            # Extract with metadata - optimized for markdown output
            result = trafilatura.extract(
                html_content,
                output_format="markdown",
                with_metadata=True,
                include_comments=True,
                include_tables=True,
                include_formatting=True,
                include_links=True,
                include_images=True,
                prune_xpath=None,
                favor_precision=True,
                favor_recall=True,
            )

            # Also get metadata separately
            metadata = trafilatura.extract_metadata(html_content)

            processing_time = time.time() - start_time

            return {
                "content": result,
                "metadata": metadata,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "trafilatura",
            }
        except Exception as e:
            return {
                "content": None,
                "metadata": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "trafilatura",
            }

    def _extract_with_markdownify(self, html_content: str) -> dict:
        """Extract content using Markdownify"""
        try:
            start_time = time.time()

            # Pre-process HTML to remove unwanted content
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script, style, and other unwanted elements completely
            for element in soup(
                ["script", "style", "link", "meta", "noscript", "iframe"]
            ):
                element.decompose()

            # Remove any elements with JavaScript-heavy attributes
            for element in soup.find_all():
                # Remove elements with onclick, onload, etc.
                js_attrs = [attr for attr in element.attrs if attr.startswith("on")]
                for attr in js_attrs:
                    del element[attr]

            # Get cleaned HTML
            cleaned_html = str(soup)

            # Convert HTML to markdown with various options
            result = markdownify(
                cleaned_html,
                heading_style="UNDERLINED",
                bullets=["*", "+", "-"],
                strip=["script", "style", "nav", "footer", "header"],
            )

            # Post-process to clean up any remaining JavaScript or code blocks
            lines = result.split("\n")
            cleaned_lines = []

            skip_block = False
            for line in lines:
                # Skip lines that look like JavaScript code
                if any(
                    js_pattern in line
                    for js_pattern in [
                        "function(",
                        "&&",
                        "||",
                        "===",
                        "!==",
                        "typeof",
                        "undefined",
                        ".prototype.",
                        "return",
                        "var ",
                        "let ",
                        "const ",
                        "}.bind(",
                        ".call(",
                        ".apply(",
                    ]
                ):
                    skip_block = True
                    continue

                # Skip very long lines (likely minified code)
                if len(line) > 500:
                    skip_block = True
                    continue

                # Reset skip_block on empty lines
                if not line.strip():
                    skip_block = False

                if not skip_block:
                    cleaned_lines.append(line)

            result = "\n".join(cleaned_lines)

            # Additional cleanup
            # Remove any remaining script-like patterns
            result = re.sub(r"```javascript.*?```", "", result, flags=re.DOTALL)
            result = re.sub(r"```js.*?```", "", result, flags=re.DOTALL)
            result = re.sub(r"```[^`]*function\(.*?```", "", result, flags=re.DOTALL)

            # Clean up excessive newlines
            result = re.sub(r"\n\n\n+", "\n\n", result)

            processing_time = time.time() - start_time

            return {
                "content": result,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "markdownify",
            }
        except Exception as e:
            return {
                "content": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "markdownify",
            }

    def _extract_with_html2text(self, html_content: str) -> dict:
        """Extract content using html2text"""
        try:
            start_time = time.time()

            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap lines
            h.protect_links = True
            h.wrap_links = False

            result = h.handle(html_content)

            processing_time = time.time() - start_time

            return {
                "content": result,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "html2text",
            }
        except Exception as e:
            return {
                "content": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "html2text",
            }

    def _extract_with_pandoc(self, html_content: str) -> dict:
        """Extract content using Pandoc"""
        try:
            start_time = time.time()

            # Create a temporary HTML file for pandoc
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name

            try:
                # Use pure pandoc to convert HTML to markdown
                result = pypandoc.convert_file(
                    temp_file_path,
                    "markdown-raw_html-fenced_divs-bracketed_spans-native_divs-native_spans",
                    format="html",
                    extra_args=[
                        "--wrap=auto",  # Auto wrap for better readability
                        "--markdown-headings=atx",  # Use # style headers
                        "--strip-comments",  # Remove HTML comments
                    ],
                )

                # Clean up temporary file
                os.unlink(temp_file_path)

                # Post-process to improve readability
                lines = result.split("\n")
                cleaned_lines = []

                for line in lines:
                    # Skip lines that are just single backslashes (line breaks)
                    if line.strip() == "\\":
                        continue

                    # Remove trailing backslashes (line breaks) from lines
                    cleaned_line = line.rstrip(" \\")

                    # Skip empty lines that follow other empty lines
                    if not cleaned_line.strip():
                        # Only add empty line if previous line wasn't empty
                        if cleaned_lines and cleaned_lines[-1].strip():
                            cleaned_lines.append("")
                    else:
                        cleaned_lines.append(cleaned_line)

                # Remove multiple consecutive empty lines
                final_lines = []
                prev_empty = False
                for line in cleaned_lines:
                    is_empty = not line.strip()
                    if is_empty and prev_empty:
                        continue  # Skip consecutive empty lines
                    final_lines.append(line)
                    prev_empty = is_empty

                # Join back and clean up
                result = "\n".join(final_lines)

                # Additional cleanup
                result = result.replace("\\\n", "\n")
                result = result.replace("\\ ", " ")
                result = re.sub(r" +", " ", result)
                result = re.sub(r"\n\n\n+", "\n\n", result)

                processing_time = time.time() - start_time

                return {
                    "content": result,
                    "processing_time": processing_time,
                    "success": True,
                    "error": None,
                    "method": "pandoc",
                }

            except Exception as pandoc_error:
                # Clean up temporary file even if pandoc fails
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

                # Fallback to basic text extraction
                soup = BeautifulSoup(html_content, "html.parser")
                text_content = soup.get_text()
                lines = [
                    line.strip() for line in text_content.splitlines() if line.strip()
                ]
                fallback_result = "\n\n".join(lines[:50])

                processing_time = time.time() - start_time

                return {
                    "content": fallback_result,
                    "processing_time": processing_time,
                    "success": True,
                    "error": f"Pandoc failed, used fallback: {str(pandoc_error)}",
                    "method": "pandoc_fallback",
                }

        except Exception as e:
            return {
                "content": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "pandoc",
            }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Main tool invocation method
        """
        html_content = tool_parameters.get("html_content", "")
        conversion_method = tool_parameters.get("conversion_method", "trafilatura")

        if not html_content:
            yield self.create_text_message("Error: No HTML content provided")
            return

        # Select conversion method
        if conversion_method == "trafilatura":
            result = self._extract_with_trafilatura(html_content)
        elif conversion_method == "markdownify":
            result = self._extract_with_markdownify(html_content)
        elif conversion_method == "html2text":
            result = self._extract_with_html2text(html_content)
        elif conversion_method == "pandoc":
            result = self._extract_with_pandoc(html_content)
        else:
            yield self.create_text_message(
                f"Error: Unknown conversion method '{conversion_method}'"
            )
            return

        if not result["success"]:
            yield self.create_text_message(
                f"Error converting HTML to markdown using {conversion_method}: {result['error']}"
            )
            return

        if not result["content"]:
            yield self.create_text_message(
                f"Warning: {conversion_method} produced empty output"
            )
            return

        # Create summary information
        content_length = len(result["content"])
        processing_time = result["processing_time"]

        summary = f"""**Conversion Summary:**
- Method: {result['method']}
- Processing time: {processing_time:.3f}s
- Output length: {content_length:,} characters
- Lines: {result['content'].count(chr(10))} lines

**Converted Markdown:**

{result['content']}"""

        yield self.create_text_message(summary)
