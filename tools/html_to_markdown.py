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
            
            # Extract title from metadata or HTML
            title = None
            if metadata and hasattr(metadata, 'title') and metadata.title:
                title = metadata.title
            else:
                # Fallback to BeautifulSoup for title extraction
                soup = BeautifulSoup(html_content, "html.parser")
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()

            processing_time = time.time() - start_time

            return {
                "content": result,
                "metadata": metadata,
                "title": title,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "trafilatura",
            }
        except Exception as e:
            return {
                "content": None,
                "metadata": None,
                "title": None,
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
            
            # Extract title before removing elements
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

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
                "title": title,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "markdownify",
            }
        except Exception as e:
            return {
                "content": None,
                "title": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "markdownify",
            }

    def _extract_with_html2text(self, html_content: str) -> dict:
        """Extract content using html2text"""
        try:
            start_time = time.time()
            
            # Extract title from HTML
            soup = BeautifulSoup(html_content, "html.parser")
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

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
                "title": title,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "html2text",
            }
        except Exception as e:
            return {
                "content": None,
                "title": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "html2text",
            }

    def _extract_with_pandoc(self, html_content: str) -> dict:
        """Extract content using Pandoc"""
        try:
            start_time = time.time()
            
            # Extract title from HTML
            soup = BeautifulSoup(html_content, "html.parser")
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

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
                    "title": title,
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
                    "title": title,
                    "processing_time": processing_time,
                    "success": True,
                    "error": f"Pandoc failed, used fallback: {str(pandoc_error)}",
                    "method": "pandoc_fallback",
                }

        except Exception as e:
            return {
                "content": None,
                "title": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "pandoc",
            }

    def _extract_with_beautifulsoup(self, html_content: str) -> dict:
        """Extract content using BeautifulSoup with custom conversion"""
        try:
            start_time = time.time()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Remove unwanted elements
            for element in soup(["script", "style", "link", "meta", "noscript", "iframe"]):
                element.decompose()
            
            # Convert common HTML elements to markdown
            # Headers
            for i in range(1, 7):
                for header in soup.find_all(f'h{i}'):
                    header_text = header.get_text().strip()
                    if header_text:
                        header.replace_with(f"{'#' * i} {header_text}\n\n")
            
            # Bold and italic
            for tag in soup.find_all(['strong', 'b']):
                tag.replace_with(f"**{tag.get_text()}**")
            
            for tag in soup.find_all(['em', 'i']):
                tag.replace_with(f"*{tag.get_text()}*")
            
            # Code
            for tag in soup.find_all('code'):
                tag.replace_with(f"`{tag.get_text()}`")
            
            for tag in soup.find_all('pre'):
                tag.replace_with(f"```\n{tag.get_text()}\n```\n")
            
            # Links
            for tag in soup.find_all('a', href=True):
                text = tag.get_text().strip()
                href = tag['href']
                if text:
                    tag.replace_with(f"[{text}]({href})")
            
            # Lists
            for ul in soup.find_all('ul'):
                list_items = []
                for li in ul.find_all('li'):
                    list_items.append(f"- {li.get_text().strip()}")
                ul.replace_with('\n'.join(list_items) + '\n\n')
            
            for ol in soup.find_all('ol'):
                list_items = []
                for i, li in enumerate(ol.find_all('li'), 1):
                    list_items.append(f"{i}. {li.get_text().strip()}")
                ol.replace_with('\n'.join(list_items) + '\n\n')
            
            # Paragraphs
            for p in soup.find_all('p'):
                p.replace_with(f"{p.get_text().strip()}\n\n")
            
            # Line breaks
            for br in soup.find_all('br'):
                br.replace_with('\n')
            
            # Get final text and clean up
            result = soup.get_text()
            
            # Clean up excessive whitespace
            result = re.sub(r'\n\n\n+', '\n\n', result)
            result = re.sub(r'  +', ' ', result)
            result = result.strip()
            
            processing_time = time.time() - start_time
            
            return {
                "content": result,
                "title": title,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "beautifulsoup",
            }
        except Exception as e:
            return {
                "content": None,
                "title": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "beautifulsoup",
            }

    def _extract_with_simple(self, html_content: str) -> dict:
        """Extract content using simple regex-based conversion"""
        try:
            start_time = time.time()
            
            # Extract title using regex
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else None
            
            # Remove script and style tags
            content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Convert headers
            content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert bold and italic
            content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert code
            content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```\n', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert links
            content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert paragraphs
            content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert line breaks
            content = re.sub(r'<br[^>]*/?>', '\n', content, flags=re.IGNORECASE)
            
            # Convert list items (simple version)
            content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove remaining HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            
            # Decode HTML entities
            content = content.replace('&nbsp;', ' ')
            content = content.replace('&amp;', '&')
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace('&quot;', '"')
            content = content.replace('&#39;', "'")
            
            # Clean up whitespace
            content = re.sub(r'\n\n\n+', '\n\n', content)
            content = re.sub(r'  +', ' ', content)
            content = content.strip()
            
            processing_time = time.time() - start_time
            
            return {
                "content": content,
                "title": title,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "method": "simple",
            }
        except Exception as e:
            return {
                "content": None,
                "title": None,
                "processing_time": 0,
                "success": False,
                "error": str(e),
                "method": "simple",
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
        elif conversion_method == "beautifulsoup":
            result = self._extract_with_beautifulsoup(html_content)
        elif conversion_method == "simple":
            result = self._extract_with_simple(html_content)
        else:
            yield self.create_text_message(
                f"Error: Unknown conversion method '{conversion_method}'. Supported methods: trafilatura, markdownify, html2text, pandoc, beautifulsoup, simple"
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

        # Prepare conversion info
        content_length = len(result["content"])
        processing_time = result["processing_time"]
        lines_count = result['content'].count('\n') + 1
        
        conversion_info = f"""Method: {result['method']}
Processing time: {processing_time:.3f}s
Output length: {content_length:,} characters
Lines: {lines_count}"""

        # Prepare title (fallback if none found)
        title = result.get('title') or 'No title found'
        
        # Log the conversion details
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"HTML to Markdown conversion completed - Method: {result['method']}, "
                   f"Processing time: {processing_time:.3f}s, "
                   f"Output length: {content_length:,} characters, "
                   f"Lines: {lines_count}")

        # Create a structured output with all information
        structured_output = {
            'markdown': result['content'],
            'conversion_info': conversion_info,
            'title': title
        }
        
        # Return as JSON for structured access
        yield self.create_json_message(structured_output)
        
        # Also return as text for direct use
        text_output = f"**Title:** {title}\n\n**Markdown:**\n{result['content']}\n\n**Conversion Info:**\n{conversion_info}"
        yield self.create_text_message(text_output)
