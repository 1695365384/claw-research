"""
Generic RSS/Atom feed collector.

Can be used for any RSS feed including:
- woshipm.com (人人都是产品经理)
- pmcaff.com
- mindtheproduct.com
- lennynewsletter.com
- techcrunch.com
"""

import email.utils
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error
import re

from .base import BaseCollector, CollectorResult, SourceConfig, now_iso


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def parse_rss_date(date_str: str) -> str:
    """Parse various RSS date formats to ISO format."""
    if not date_str:
        return ""

    # Try RFC 2822 format (common in RSS)
    try:
        parsed = email.utils.parsedate_to_datetime(date_str)
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        pass

    return date_str


class RSSCollector(BaseCollector):
    """
    Generic RSS/Atom feed collector.

    Configuration:
        url: RSS feed URL (required)
        max_items: Maximum items to fetch (default: 20)
    """

    def __init__(self, config: SourceConfig, keys: Optional[Dict[str, Any]] = None):
        super().__init__(config, keys)
        self.feed_url = config.config.get("url", "")
        self.max_items = config.config.get("max_items", 50)

    def collect(self, query: str, max_items: int = 20) -> CollectorResult:
        """
        Fetch items from RSS feed.

        Note: RSS feeds don't support search queries directly.
        We fetch recent items and optionally filter by query keywords.
        """
        items = []

        if not self.feed_url:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error="No RSS feed URL configured",
            )

        try:
            req = urllib.request.Request(
                self.feed_url,
                headers={"User-Agent": "claw-research/1.0 (+https://github.com/claw-research)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode("utf-8", errors="replace")

            # Parse XML
            root = ET.fromstring(content)

            # Detect RSS vs Atom
            is_atom = root.tag.endswith("feed")

            if is_atom:
                entries = self._parse_atom(root, query, max_items)
            else:
                entries = self._parse_rss(root, query, max_items)

            for entry in entries:
                items.append(self.normalize_item(entry))

        except urllib.error.HTTPError as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"HTTP error {e.code}: {e.reason}",
            )
        except urllib.error.URLError as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"URL error: {e.reason}",
            )
        except ET.ParseError as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=f"XML parse error: {e}",
            )
        except Exception as e:
            return CollectorResult(
                items=[],
                source_name=self.config.name,
                source_type=self.config.type,
                error=str(e),
            )

        return CollectorResult(
            items=items,
            source_name=self.config.name,
            source_type=self.config.type,
            metadata={"feed_url": self.feed_url, "query": query},
        )

    def _parse_rss(self, root: ET.Element, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse standard RSS 2.0 feed."""
        items = []
        query_lower = query.lower() if query else ""
        query_words = set(query_lower.split()) if query else set()

        for item in root.findall(".//item")[:self.max_items]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")
            creator = item.findtext("{http://purl.org/dc/elements/1.1/}creator", "")
            creator = creator or item.findtext("author", "")

            # Optional query filtering
            content = f"{title} {description}".lower()
            if query_words and not any(w in content for w in query_words):
                continue

            items.append({
                "title": title,
                "url": link,
                "text": strip_html(description),
                "author": creator,
                "published_at": parse_rss_date(pub_date),
            })

            if len(items) >= max_items:
                break

        return items

    def _parse_atom(self, root: ET.Element, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse Atom feed."""
        items = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        query_lower = query.lower() if query else ""
        query_words = set(query_lower.split()) if query else set()

        for entry in root.findall(".//atom:entry", ns)[:self.max_items]:
            title_el = entry.find("atom:title", ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else ""

            # Get link
            link = ""
            for link_el in entry.findall("atom:link", ns):
                href = link_el.get("href", "")
                rel = link_el.get("rel", "")
                if href and rel != "edit":
                    link = href
                    break

            # Get content/summary
            content_el = entry.find("atom:content", ns)
            if content_el is None:
                content_el = entry.find("atom:summary", ns)
            content = content_el.text if content_el is not None and content_el.text else ""

            # Get date
            updated_el = entry.find("atom:updated", ns)
            published_el = entry.find("atom:published", ns)
            pub_date = (published_el.text if published_el is not None else
                        updated_el.text if updated_el is not None else "")

            # Get author
            author_el = entry.find("atom:author/atom:name", ns)
            author = author_el.text if author_el is not None and author_el.text else ""

            # Optional query filtering
            full_content = f"{title} {content}".lower()
            if query_words and not any(w in full_content for w in query_words):
                continue

            items.append({
                "title": title,
                "url": link,
                "text": strip_html(content),
                "author": author,
                "published_at": pub_date,
            })

            if len(items) >= max_items:
                break

        return items


# Convenience factory functions
def woshipm_collector(config: SourceConfig, keys: Optional[Dict] = None) -> RSSCollector:
    """Create collector for 人人都是产品经理."""
    config.config["url"] = config.config.get("url", "https://www.woshipm.com/feed")
    return RSSCollector(config, keys)


def pmcaff_collector(config: SourceConfig, keys: Optional[Dict] = None) -> RSSCollector:
    """Create collector for PMCAFF."""
    config.config["url"] = config.config.get("url", "https://www.pmcaff.com/rss")
    return RSSCollector(config, keys)


def techcrunch_collector(config: SourceConfig, keys: Optional[Dict] = None) -> RSSCollector:
    """Create collector for TechCrunch."""
    config.config["url"] = config.config.get("url", "https://techcrunch.com/feed/")
    return RSSCollector(config, keys)


def mindtheproduct_collector(config: SourceConfig, keys: Optional[Dict] = None) -> RSSCollector:
    """Create collector for Mind the Product."""
    config.config["url"] = config.config.get("url", "https://www.mindtheproduct.com/feed/")
    return RSSCollector(config, keys)
