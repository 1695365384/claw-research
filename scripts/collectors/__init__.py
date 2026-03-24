"""
Claw Research Data Collectors

This module provides data collection capabilities for market research.
Each collector fetches data from a specific source and returns normalized items.

Usage:
    from collectors import CollectorRegistry, load_source_configs

    # Load configs from sources.json
    configs = load_source_configs("config/sources.json")

    # Create registry and register collectors
    registry = CollectorRegistry()
    registry.register("hacker_news", HackerNewsCollector)
    registry.register("rss", RSSCollector)
    registry.register("search", SearchCollector)

    # Create collector instance
    config = configs["hacker_news"]
    collector = registry.create("hacker_news", config, keys)
    result = collector.collect("product pain points", max_items=20)
"""

from .base import (
    BaseCollector,
    CollectorResult,
    CollectorRegistry,
    SourceConfig,
    load_source_configs,
    load_api_keys,
)
from .selector import SourceSelector
from .hacker_news import HackerNewsCollector, HackerNewsCommentsCollector
from .rss_generic import RSSCollector
from .search_collector import SearchCollector

__all__ = [
    # Base classes
    "BaseCollector",
    "CollectorResult",
    "CollectorRegistry",
    "SourceConfig",
    "load_source_configs",
    "load_api_keys",
    # Selectors
    "SourceSelector",
    # Collectors
    "HackerNewsCollector",
    "HackerNewsCommentsCollector",
    "RSSCollector",
    "SearchCollector",
]
