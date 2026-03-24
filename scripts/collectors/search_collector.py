"""
Search engine collector using browser simulation.

Supports multiple search engines:
- Google (browser simulation, no API key required)
- Bing (browser simulation, no API key required)
- DuckDuckGo (HTML parsing, no API key required)
- Baidu (browser simulation, no API key required)

All engines work without any API key by simulating real browser requests.
"""

import time
import urllib.parse
import urllib.request
import re
from typing import Any, Dict, List, Optional

from .base import BaseCollector, CollectorResult, SourceConfig, now_iso


# Realistic browser headers for simulating user traffic
# Note: Accept-Encoding is set to "identity" to get uncompressed content
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "identity",  # Request uncompressed content
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class SearchCollector(BaseCollector):
    """
    Search engine collector using browser simulation.

    Configuration:
        engine: google | bing | duckduckgo | baidu (default: duckduckgo)
        delay_seconds: Delay between requests to avoid rate limiting (default: 2)
    """

    def __init__(self, config: SourceConfig, keys: Optional[Dict[str, Any]] = None):
        super().__init__(config, keys)
        self.engine = config.config.get("engine", "duckduckgo")
        self.delay_seconds = config.config.get("delay_seconds", 2)

    def collect(self, query: str, max_items: int = 20) -> CollectorResult:
        """
        Search for items matching the query.

        Args:
            query: Search query
            max_items: Maximum number of items to return

        Returns:
            CollectorResult with normalized items
        """
        if self.engine == "google":
            return self._search_google(query, max_items)
        elif self.engine == "bing":
            return self._search_bing(query, max_items)
        elif self.engine == "duckduckgo":
            return self._search_duckduckgo(query, max_items)
        elif self.engine == "baidu":
            return self._search_baidu(query, max_items)
        else:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"Unknown search engine: {self.engine}",
            )

    def _search_google(self, query: str, max_items: int) -> CollectorResult:
        """Search Google by simulating a real browser."""
        items = []
        try:
            time.sleep(self.delay_seconds)

            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={max_items}&hl=en"

            req = urllib.request.Request(url, headers=BROWSER_HEADERS)

            with urllib.request.urlopen(req, timeout=30) as resp:
                html_content = resp.read().decode("utf-8", errors="replace")

            items = self._parse_google_html(html_content, max_items)

        except Exception as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"Google search error: {e}",
            )

        return CollectorResult(
            items=items,
            source_name=self.config.name,
            source_type=self.config.type,
            metadata={"engine": "google", "method": "browser", "query": query},
        )

    def _search_bing(self, query: str, max_items: int) -> CollectorResult:
        """Search Bing by simulating a real browser."""
        items = []
        try:
            time.sleep(self.delay_seconds)

            encoded_query = urllib.parse.quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}&count={max_items}"

            req = urllib.request.Request(url, headers=BROWSER_HEADERS)

            with urllib.request.urlopen(req, timeout=30) as resp:
                html_content = resp.read().decode("utf-8", errors="replace")

            items = self._parse_bing_html(html_content, max_items)

        except Exception as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"Bing search error: {e}",
            )

        return CollectorResult(
            items=items,
            source_name=self.config.name,
            source_type=self.config.type,
            metadata={"engine": "bing", "method": "browser", "query": query},
        )

    def _search_duckduckgo(self, query: str, max_items: int) -> CollectorResult:
        """
        Search using DuckDuckGo HTML interface.

        DuckDuckGo doesn't require an API key and respects privacy.
        """
        items = []
        try:
            time.sleep(self.delay_seconds)

            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "identity",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                html_content = resp.read().decode("utf-8", errors="replace")

            items = self._parse_duckduckgo_html(html_content, max_items)

        except Exception as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"DuckDuckGo search error: {e}",
            )

        return CollectorResult(
            items=items,
            source_name=self.config.name,
            source_type=self.config.type,
            metadata={"engine": "duckduckgo", "method": "browser", "query": query},
        )

    def _search_baidu(self, query: str, max_items: int) -> CollectorResult:
        """Search Baidu by simulating a real browser."""
        items = []
        try:
            time.sleep(self.delay_seconds)

            encoded_query = urllib.parse.quote(query)
            url = f"https://www.baidu.com/s?wd={encoded_query}&rn={max_items}"

            # Baidu-specific headers
            headers = BROWSER_HEADERS.copy()
            headers["Accept-Language"] = "zh-CN,zh;q=0.9,en;q=0.8"

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as resp:
                html_content = resp.read().decode("utf-8", errors="replace")

            items = self._parse_baidu_html(html_content, max_items)

        except Exception as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"Baidu search error: {e}",
            )

        return CollectorResult(
            items=items,
            source_name=self.config.name,
            source_type=self.config.type,
            metadata={"engine": "baidu", "method": "browser", "query": query},
        )

    def _parse_google_html(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse Google search results from HTML."""
        items = []

        # Pattern for Google search results
        result_pattern = re.compile(
            r'<div[^>]*class="[^"]*g[^"]*"[^>]*>.*?'
            r'<a[^>]*href="(/url\?q=([^"&]+)|([^"]+))"[^>]*>.*?'
            r'<h3[^>]*>([^<]+)</h3>.*?'
            r'(?:<div[^>]*class="[^"]*VwiC3b[^"]*"[^>]*>([^<]+)</div>)?',
            re.DOTALL | re.IGNORECASE
        )

        matches = result_pattern.findall(html)

        for match in matches[:max_items]:
            # Extract URL - handle both /url?q= format and direct links
            if match[1]:  # /url?q= format
                url = urllib.parse.unquote(match[1])
            else:
                url = match[2]

            # Skip Google internal links
            if url.startswith("/") or "google.com" in url:
                continue

            title = self._clean_html(match[3])
            snippet = self._clean_html(match[4]) if len(match) > 4 else ""

            if title and url:
                item = {
                    "title": title,
                    "url": url,
                    "text": snippet,
                    "published_at": "",
                }
                items.append(self.normalize_item(item))

        return items

    def _parse_bing_html(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse Bing search results from HTML."""
        items = []

        # Bing uses h2 > a for main results
        # Pattern: <h2><a href="URL">TITLE</a></h2>
        result_pattern = re.compile(
            r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>\s*</h2>',
            re.IGNORECASE
        )

        matches = result_pattern.findall(html)

        for url, title in matches[:max_items]:
            title = self._clean_html(title)

            # Skip Bing internal links
            if url.startswith('/') or 'bing.com' in url:
                continue

            if title and url:
                item = {
                    "title": title,
                    "url": url,
                    "text": "",  # Snippet extraction is complex, skip for now
                    "published_at": "",
                }
                items.append(self.normalize_item(item))

        return items

    def _parse_duckduckgo_html(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML response to extract search results."""
        items = []

        # Pattern to match result entries in DuckDuckGo HTML
        result_pattern = re.compile(
            r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>([^<]*)</a>',
            re.DOTALL | re.IGNORECASE
        )

        # Alternative pattern for different DDG HTML structure
        alt_pattern = re.compile(
            r'<div[^>]+class="[^"]*result[^"]*"[^>]*>.*?'
            r'<a[^>]+class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            re.DOTALL | re.IGNORECASE
        )

        # Try primary pattern
        matches = result_pattern.findall(html)

        # Fallback to alternative pattern
        if not matches:
            matches = alt_pattern.findall(html)

        for match in matches[:max_items]:
            url = match[0]
            title = self._clean_html(match[1])
            snippet = match[2] if len(match) > 2 else ""
            snippet = self._clean_html(snippet)

            # Skip ad results and empty URLs
            if not url or url.startswith("javascript:") or "y.js" in url:
                continue

            # DuckDuckGo uses redirect URLs, extract actual URL
            if "uddg=" in url:
                actual_url = urllib.parse.unquote(
                    url.split("uddg=")[-1].split("&")[0]
                )
            else:
                actual_url = url

            item = {
                "title": title.strip(),
                "url": actual_url.strip(),
                "text": snippet.strip(),
                "published_at": "",
            }
            items.append(self.normalize_item(item))

        return items

    def _parse_baidu_html(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse Baidu search results from HTML."""
        items = []

        # Pattern for Baidu search results
        result_pattern = re.compile(
            r'<div[^>]*class="[^"]*result[^"]*"[^>]*>.*?'
            r'<h3[^>]*class="[^"]*t[^"]*"[^>]*>.*?'
            r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?'
            r'(?:<div[^>]*class="[^"]*c-abstract[^"]*"[^>]*>([^<]+)</div>)?',
            re.DOTALL | re.IGNORECASE
        )

        matches = result_pattern.findall(html)

        for match in matches[:max_items]:
            url = match[0]
            title = self._clean_html(match[1])
            snippet = self._clean_html(match[2]) if len(match) > 2 else ""

            if title and url:
                item = {
                    "title": title,
                    "url": url,
                    "text": snippet,
                    "published_at": "",
                }
                items.append(self.normalize_item(item))

        return items

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text."""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # Decode HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&nbsp;", " ")
        # Clean whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# Convenience factory functions
def google_collector(config: SourceConfig, keys: Optional[Dict] = None) -> SearchCollector:
    """Create Google search collector (no API key required)."""
    config.config["engine"] = "google"
    return SearchCollector(config, keys)


def bing_collector(config: SourceConfig, keys: Optional[Dict] = None) -> SearchCollector:
    """Create Bing search collector (no API key required)."""
    config.config["engine"] = "bing"
    return SearchCollector(config, keys)


def duckduckgo_collector(config: SourceConfig, keys: Optional[Dict] = None) -> SearchCollector:
    """Create DuckDuckGo search collector (no API key required)."""
    config.config["engine"] = "duckduckgo"
    return SearchCollector(config, keys)


def baidu_collector(config: SourceConfig, keys: Optional[Dict] = None) -> SearchCollector:
    """Create Baidu search collector (no API key required)."""
    config.config["engine"] = "baidu"
    return SearchCollector(config, keys)
