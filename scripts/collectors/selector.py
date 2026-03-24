"""
Intelligent source selector.

Analyzes research charter and user query to automatically select relevant data sources.
"""

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import SourceConfig, load_source_configs


# Keyword to source type mappings
PERSONA_KEYWORDS = {
    "产品经理": ["woshipm", "pmcaff", "zhihu", "product_school", "mind_the_product", "reddit_pm"],
    "product manager": ["product_school", "mind_the_product", "lenny_newsletter", "reddit_pm", "product_hunt"],
    "开发者": ["hacker_news", "stack_overflow", "dev_to", "reddit_prog"],
    "developer": ["hacker_news", "stack_overflow", "dev_to", "reddit_prog"],
    "designer": ["dribbble", "behance", "figma_community", "designer_news"],
    "设计师": ["dribbble", "behance", "zhihu_design"],
    "创业者": ["indie_hackers", "hacker_news", "product_hunt", "yc"],
    "founder": ["indie_hackers", "hacker_news", "product_hunt", "yc"],
    "运营": ["zhihu", "xiaohongshu", "weibo"],
    "marketing": ["growth_hackers", "product_hunt", "twitter"],
}

TOPIC_KEYWORDS = {
    "痛点": ["reddit", "zhihu", "hacker_news", "twitter"],
    "pain point": ["reddit", "hacker_news", "twitter", "indie_hackers"],
    "问题": ["zhihu", "stack_overflow", "reddit"],
    "problem": ["reddit", "stack_overflow", "hacker_news"],
    "工作流": ["hacker_news", "product_hunt", "reddit"],
    "workflow": ["hacker_news", "product_hunt", "reddit"],
    "工具": ["product_hunt", "hacker_news", "alternative_to"],
    "tool": ["product_hunt", "hacker_news", "alternative_to"],
    "竞品": ["g2", "capterra", "alternative_to", "app_store"],
    "competitor": ["g2", "capterra", "alternative_to"],
    "市场": ["cb_insights", "techcrunch", "36kr"],
    "market": ["cb_insights", "techcrunch", "venturebeat"],
    "趋势": ["twitter", "techcrunch", "product_hunt"],
    "trend": ["twitter", "techcrunch", "product_hunt"],
}

LANGUAGE_HINTS = {
    "chinese": ["woshipm", "pmcaff", "zhihu", "xiaohongshu", "weibo", "jike", "36kr"],
    "english": ["hacker_news", "reddit", "product_hunt", "techcrunch"],
}


@dataclass
class SourceSelection:
    """Result of source selection."""
    selected_sources: List[str]
    matching_keywords: Dict[str, List[str]]
    language_detected: str
    confidence: str  # high, medium, low


class SourceSelector:
    """
    Intelligently selects data sources based on research context.

    Usage:
        selector = SourceSelector(config_path="config/sources.json")
        selection = selector.select(charter, query)
        print(selection.selected_sources)  # ["woshipm", "reddit_pm", "zhihu"]
    """

    def __init__(self, config_path: Optional[str] = None):
        self.configs: Dict[str, SourceConfig] = {}
        if config_path and os.path.exists(config_path):
            self.configs = load_source_configs(config_path)

        # Default built-in source configs if no config file
        if not self.configs:
            self.configs = self._default_configs()

    def _default_configs(self) -> Dict[str, SourceConfig]:
        """Return default source configurations."""
        return {
            "hacker_news": SourceConfig(
                name="hacker_news",
                type="api",
                keywords=["技术", "产品", "startup", "痛点", "developer", "tool"],
            ),
            "reddit": SourceConfig(
                name="reddit",
                type="api",
                keywords=["产品", "痛点", "反馈", "SaaS", "discussion"],
            ),
            "woshipm": SourceConfig(
                name="woshipm",
                type="rss",
                keywords=["产品经理", "产品", "PM", "运营"],
            ),
            "zhihu": SourceConfig(
                name="zhihu",
                type="search",
                keywords=["产品", "痛点", "工作", "问题"],
            ),
            "product_hunt": SourceConfig(
                name="product_hunt",
                type="api",
                keywords=["tool", "product", "startup", "launch"],
            ),
            "google": SourceConfig(
                name="google",
                type="search",
                keywords=["通用"],
            ),
            "bing": SourceConfig(
                name="bing",
                type="search",
                keywords=["通用"],
            ),
            "baidu": SourceConfig(
                name="baidu",
                type="search",
                keywords=["中文", "通用"],
            ),
            "duckduckgo": SourceConfig(
                name="duckduckgo",
                type="search",
                keywords=["通用", "privacy"],
            ),
        }

    def detect_language(self, text: str) -> str:
        """Detect if text contains Chinese characters."""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        total_chars = len(re.sub(r"\s", "", text))
        if total_chars > 0 and chinese_chars / total_chars > 0.2:
            return "chinese"
        return "english"

    def extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        text = text.lower()
        keywords = set()

        # Extract Chinese keywords
        chinese_matches = re.findall(r"[\u4e00-\u9fff]+", text)
        keywords.update(chinese_matches)

        # Extract English keywords (2+ chars)
        english_matches = re.findall(r"\b[a-z]{2,}\b", text)
        keywords.update(english_matches)

        return keywords

    def select(
        self,
        charter: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
    ) -> SourceSelection:
        """
        Select relevant data sources based on context.

        Args:
            charter: Research charter with target_personas, research_questions
            query: User's search query

        Returns:
            SourceSelection with selected sources and metadata
        """
        # Gather all text for analysis
        all_text = []
        matching_keywords: Dict[str, List[str]] = {}

        if query:
            all_text.append(query)

        if charter:
            # Extract from research questions
            for rq in charter.get("research_questions", []):
                all_text.append(rq.get("question", ""))
                all_text.append(rq.get("hypothesis", ""))

            # Extract from target personas
            for persona in charter.get("target_personas", []):
                all_text.append(persona.get("label", ""))
                all_text.extend(persona.get("characteristics", []))

        combined_text = " ".join(all_text)
        detected_lang = self.detect_language(combined_text)
        keywords = self.extract_keywords(combined_text)

        # Score each source
        source_scores: Dict[str, Tuple[int, List[str]]] = {}

        for source_name, config in self.configs.items():
            if not config.enabled:
                continue

            score = 0
            matched: List[str] = []

            # Check keyword matches
            for kw in keywords:
                if kw in config.keywords:
                    score += 1
                    matched.append(kw)

            # Check persona keywords
            for persona, sources in PERSONA_KEYWORDS.items():
                if persona.lower() in combined_text.lower():
                    if source_name in sources:
                        score += 2
                        matched.append(f"persona:{persona}")

            # Check topic keywords
            for topic, sources in TOPIC_KEYWORDS.items():
                if topic.lower() in combined_text.lower():
                    if source_name in sources:
                        score += 2
                        matched.append(f"topic:{topic}")

            # Language preference
            lang_sources = LANGUAGE_HINTS.get(detected_lang, [])
            if source_name in lang_sources:
                score += 1
                matched.append(f"lang:{detected_lang}")

            if score > 0:
                source_scores[source_name] = (score, matched)

        # Sort by score and select top sources
        sorted_sources = sorted(source_scores.items(), key=lambda x: x[1][0], reverse=True)
        selected = [name for name, (_, _) in sorted_sources[:5]]  # Top 5 sources

        # Always include search engines if no sources matched
        # Priority: Bing -> Baidu -> Google -> DuckDuckGo (parallel search, ignore failures)
        if not selected:
            selected = ["bing", "baidu", "google", "duckduckgo"]
            confidence = "low"
        elif len(selected) < 3:
            confidence = "medium"
        else:
            confidence = "high"

        # Build matching keywords dict
        for name, (_, matched) in sorted_sources:
            if matched:
                matching_keywords[name] = matched

        return SourceSelection(
            selected_sources=selected,
            matching_keywords=matching_keywords,
            language_detected=detected_lang,
            confidence=confidence,
        )

    def get_available_sources(self) -> List[str]:
        """Get list of all available source names."""
        return list(self.configs.keys())

    def get_source_config(self, name: str) -> Optional[SourceConfig]:
        """Get configuration for a specific source."""
        return self.configs.get(name)
