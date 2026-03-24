"""
Hacker News collector using Algolia API.

Uses the free HN Algolia API to search posts and comments.
"""

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from .base import BaseCollector, CollectorResult, SourceConfig, now_iso


class HackerNewsCollector(BaseCollector):
    """
    Collects data from Hacker News via Algolia API.

    Free, no authentication required.
    Supports both stories and comments.
    """

    BASE_URL = "https://hn.algolia.com/api/v1"

    def __init__(self, config: SourceConfig, keys: Optional[Dict[str, Any]] = None):
        super().__init__(config, keys)
        self.search_type = config.config.get("search_type", "story")  # story or comment

    def collect(self, query: str, max_items: int = 20) -> CollectorResult:
        """
        Search Hacker News for items matching the query.

        Args:
            query: Search query
            max_items: Maximum number of items to return

        Returns:
            CollectorResult with normalized items
        """
        items = []
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"{self.BASE_URL}/search_by_date?query={encoded_query}&tags={self.search_type}&hitsPerPage={max_items}"

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "claw-research/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for hit in data.get("hits", []):
                item = {
                    "title": hit.get("title", hit.get("story_title", "")),
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    "text": hit.get("story_text") or hit.get("comment_text") or hit.get("title", ""),
                    "author": hit.get("author", ""),
                    "points": hit.get("points", 0),
                    "num_comments": hit.get("num_comments", 0),
                    "published_at": hit.get("created_at", ""),
                }
                items.append(self.normalize_item(item))

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
            metadata={"total_hits": len(items), "query": query},
        )


class HackerNewsCommentsCollector(BaseCollector):
    """Collects comments from Hacker News (more focused on discussions/pain points)."""

    def collect(self, query: str, max_items: int = 20) -> CollectorResult:
        config = SourceConfig(
            name=self.config.name,
            type=self.config.type,
            config={**self.config.config, "search_type": "comment"},
        )
        return HackerNewsCollector(config, self.keys).collect(query, max_items)
