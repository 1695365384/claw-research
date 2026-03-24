"""
Base classes for data collectors.

All collectors inherit from BaseCollector and return CollectorResult objects.
"""

import datetime as dt
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def now_iso():
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class CollectorResult:
    """Standard result from a collector."""
    items: List[Dict[str, Any]] = field(default_factory=list)
    source_name: str = ""
    source_type: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class SourceConfig:
    """Configuration for a data source."""
    name: str
    type: str
    requires_auth: bool = False
    auth_type: Optional[str] = None
    auth_hint: Optional[str] = None
    enabled: bool = True
    keywords: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class BaseCollector(ABC):
    """
    Base class for all data collectors.

    Subclasses must implement:
    - collect(query: str, max_items: int) -> CollectorResult
    - is_available() -> bool
    """

    def __init__(self, config: SourceConfig, keys: Optional[Dict[str, Any]] = None):
        self.config = config
        self.keys = keys or {}

    @abstractmethod
    def collect(self, query: str, max_items: int = 20) -> CollectorResult:
        """
        Collect items matching the query.

        Args:
            query: Search query or topic
            max_items: Maximum number of items to return

        Returns:
            CollectorResult with normalized items
        """
        pass

    def is_available(self) -> bool:
        """
        Check if the collector is available (has required auth, etc.)
        """
        if not self.config.requires_auth:
            return True
        return bool(self.keys)

    def get_missing_auth_message(self) -> Optional[str]:
        """Return a message if auth is missing, None if available."""
        if not self.config.requires_auth:
            return None
        if self.keys:
            return None
        return self.config.auth_hint or f"Source '{self.config.name}' requires authentication"

    def normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an item to the standard format.

        Standard format:
        {
            "source": "source_name",
            "source_type": "api|rss|search|...",
            "title": "...",
            "url": "...",
            "text": "...",
            "captured_at": "ISO-8601",
            "published_at": "ISO-8601 or empty",
        }
        """
        return {
            "source": self.config.name,
            "source_type": self.config.type,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "text": item.get("text", item.get("content", item.get("body", ""))),
            "captured_at": item.get("captured_at") or now_iso(),
            "published_at": item.get("published_at") or item.get("created_at", ""),
        }


class CollectorRegistry:
    """
    Registry for all available collectors.

    Usage:
        registry = CollectorRegistry()
        registry.register("hacker_news", HackerNewsCollector)
        collector = registry.create("hacker_news", config, keys)
    """

    def __init__(self):
        self._collectors: Dict[str, type] = {}

    def register(self, name: str, collector_class: type):
        """Register a collector class."""
        self._collectors[name] = collector_class

    def get_available_sources(self) -> List[str]:
        """Get list of registered source names."""
        return list(self._collectors.keys())

    def create(
        self,
        name: str,
        config: SourceConfig,
        keys: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseCollector]:
        """Create a collector instance."""
        collector_class = self._collectors.get(name)
        if not collector_class:
            return None
        return collector_class(config, keys)


def load_source_configs(config_path: str) -> Dict[str, SourceConfig]:
    """Load source configurations from a JSON file."""
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    configs = {}
    for name, source_data in data.get("sources", {}).items():
        configs[name] = SourceConfig(
            name=name,
            type=source_data.get("type", "unknown"),
            requires_auth=source_data.get("requires_auth", False),
            auth_type=source_data.get("auth_type"),
            auth_hint=source_data.get("auth_hint"),
            enabled=source_data.get("enabled", True),
            keywords=source_data.get("keywords", []),
            config=source_data,
        )
    return configs


def load_api_keys(keys_path: str) -> Dict[str, Any]:
    """Load API keys from a JSON file."""
    if not os.path.exists(keys_path):
        return {}
    with open(keys_path, "r", encoding="utf-8") as fh:
        return json.load(fh)
