"""
Tests for the collectors module.
"""

import json
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Import collector modules
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from collectors.base import (
    BaseCollector,
    CollectorResult,
    CollectorRegistry,
    SourceConfig,
    load_api_keys,
    load_source_configs,
    now_iso,
)
from collectors.selector import (
    SourceSelector,
    SourceSelection,
    PERSONA_KEYWORDS,
    TOPIC_KEYWORDS,
)
from collectors.hacker_news import HackerNewsCollector
from collectors.rss_generic import RSSCollector, strip_html, parse_rss_date
from collectors.search_collector import (
    SearchCollector,
    google_collector,
    bing_collector,
    duckduckgo_collector,
    baidu_collector,
)


class TestBaseCollector(unittest.TestCase):
    """Tests for base collector classes."""

    def test_source_config_defaults(self):
        """SourceConfig should have sensible defaults."""
        config = SourceConfig(name="test", type="api")
        self.assertEqual(config.name, "test")
        self.assertEqual(config.type, "api")
        self.assertFalse(config.requires_auth)
        self.assertIsNone(config.auth_hint)
        self.assertTrue(config.enabled)

    def test_source_config_with_auth(self):
        """SourceConfig should handle auth requirements."""
        config = SourceConfig(
            name="reddit",
            type="api",
            requires_auth=True,
            auth_hint="Need API key",
        )
        self.assertTrue(config.requires_auth)
        self.assertEqual(config.auth_hint, "Need API key")

    def test_collector_result_defaults(self):
        """CollectorResult should have sensible defaults."""
        result = CollectorResult(items=[], source_name="test", source_type="api")
        self.assertEqual(result.items, [])
        self.assertIsNone(result.error)
        self.assertEqual(result.metadata, {})

    def test_collector_result_with_error(self):
        """CollectorResult should capture errors."""
        result = CollectorResult(
            items=[], source_name="test", source_type="api", error="Connection failed"
        )
        self.assertEqual(result.error, "Connection failed")

    def test_now_iso_returns_valid_format(self):
        """now_iso should return valid ISO format."""
        iso = now_iso()
        self.assertIn("T", iso)
        self.assertTrue(iso.endswith("Z"))


class TestCollectorRegistry(unittest.TestCase):
    """Tests for collector registry."""

    def test_registry_register_and_create(self):
        """Registry should register and create collectors."""
        registry = CollectorRegistry()

        registry.register("test_source", MagicMock)
        sources = registry.get_available_sources()
        self.assertIn("test_source", sources)

    def test_registry_get_available_sources(self):
        """Registry should list available sources."""
        registry = CollectorRegistry()
        registry.register("source_a", MagicMock)
        registry.register("source_b", MagicMock)

        sources = registry.get_available_sources()
        self.assertIn("source_a", sources)
        self.assertIn("source_b", sources)

    def test_registry_create_returns_instance(self):
        """Registry.create should return collector instance."""
        registry = CollectorRegistry()
        registry.register("test", MagicMock)

        config = SourceConfig(name="test", type="api")
        instance = registry.create("test", config)
        self.assertIsNotNone(instance)


class TestLoadSourceConfigs(unittest.TestCase):
    """Tests for loading source configurations."""

    def test_load_source_configs_from_file(self):
        """Should load source configs from JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            config_path = pathlib.Path(tmp) / "sources.json"
            config_path.write_text(
                json.dumps({
                    "sources": {
                        "test_source": {
                            "type": "api",
                            "url": "http://example.com",
                            "enabled": True,
                        }
                    }
                }),
                encoding="utf-8",
            )

            configs = load_source_configs(config_path)
            self.assertIn("test_source", configs)
            self.assertEqual(configs["test_source"].type, "api")

    def test_load_source_configs_missing_file(self):
        """Should return empty dict for missing config file."""
        configs = load_source_configs(pathlib.Path("/nonexistent/path.json"))
        self.assertEqual(configs, {})


class TestLoadApiKeys(unittest.TestCase):
    """Tests for loading API keys."""

    def test_load_api_keys_from_file(self):
        """Should load API keys from JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            keys_path = pathlib.Path(tmp) / "keys.json"
            keys_path.write_text(
                json.dumps({"reddit": {"client_id": "test123"}}),
                encoding="utf-8",
            )

            keys = load_api_keys(keys_path)
            self.assertEqual(keys["reddit"]["client_id"], "test123")

    def test_load_api_keys_missing_file(self):
        """Should return empty dict for missing keys file."""
        keys = load_api_keys(pathlib.Path("/nonexistent/keys.json"))
        self.assertEqual(keys, {})


class TestSourceSelector(unittest.TestCase):
    """Tests for intelligent source selection."""

    def test_selector_initializes_with_defaults(self):
        """Selector should initialize with default configs."""
        selector = SourceSelector()
        self.assertIsNotNone(selector.configs)
        self.assertGreater(len(selector.configs), 0)

    def test_detect_language_chinese(self):
        """Should detect Chinese language."""
        selector = SourceSelector()
        lang = selector.detect_language("产品经理痛点研究")
        self.assertEqual(lang, "chinese")

    def test_detect_language_english(self):
        """Should detect English language."""
        selector = SourceSelector()
        lang = selector.detect_language("product manager pain points")
        self.assertEqual(lang, "english")

    def test_select_pm_related_sources(self):
        """Should select PM-related sources for PM queries."""
        selector = SourceSelector()
        selection = selector.select(query="产品经理日常工作痛点")

        # Should include PM-related sources
        source_names = selection.selected_sources
        # woshipm should be high priority for Chinese PM content
        self.assertTrue(
            any("woshipm" in name or "zhihu" in name for name in source_names),
            f"Expected PM sources, got: {source_names}",
        )

    def test_select_returns_source_selection(self):
        """Should return SourceSelection with proper structure."""
        selector = SourceSelector()
        selection = selector.select(query="developer tools")

        self.assertIsInstance(selection, SourceSelection)
        self.assertIsInstance(selection.selected_sources, list)
        self.assertIsInstance(selection.matching_keywords, dict)
        self.assertGreater(len(selection.selected_sources), 0)

    def test_persona_keywords_mapping(self):
        """PERSONA_KEYWORDS should have expected mappings."""
        self.assertIn("产品经理", PERSONA_KEYWORDS)
        self.assertIn("developer", PERSONA_KEYWORDS)

    def test_topic_keywords_mapping(self):
        """TOPIC_KEYWORDS should have expected mappings."""
        self.assertIn("痛点", TOPIC_KEYWORDS)
        self.assertIn("pain point", TOPIC_KEYWORDS)


class TestHackerNewsCollector(unittest.TestCase):
    """Tests for Hacker News collector."""

    def test_collector_initialization(self):
        """HackerNewsCollector should initialize correctly."""
        config = SourceConfig(
            name="hacker_news",
            type="api",
            config={"url": "https://hn.algolia.com/api/v1/search_by_date"},
        )
        collector = HackerNewsCollector(config)
        self.assertEqual(collector.config.name, "hacker_news")

    def test_collector_is_available_without_auth(self):
        """HackerNewsCollector should be available without auth."""
        config = SourceConfig(name="hacker_news", type="api", config={})
        collector = HackerNewsCollector(config)
        self.assertTrue(collector.is_available())

    @patch("collectors.hacker_news.urllib.request.urlopen")
    def test_collect_returns_items(self, mock_urlopen):
        """HackerNewsCollector.collect should return items."""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "hits": [
                {
                    "objectID": "123",
                    "title": "Test HN Post",
                    "url": "https://example.com",
                    "author": "testuser",
                    "created_at_i": 1700000000,
                    "points": 10,
                }
            ]
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(name="hacker_news", type="api", config={})
        collector = HackerNewsCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(result.source_name, "hacker_news")
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]["title"], "Test HN Post")


class TestRSSCollector(unittest.TestCase):
    """Tests for generic RSS collector."""

    def test_strip_html_removes_tags(self):
        """strip_html should remove HTML tags."""
        html = "<p>Hello <b>world</b>!</p>"
        clean = strip_html(html)
        self.assertEqual(clean, "Hello world !")

    def test_strip_html_handles_none(self):
        """strip_html should handle None input."""
        self.assertEqual(strip_html(None), "")
        self.assertEqual(strip_html(""), "")

    def test_parse_rss_date_handles_rfc2822(self):
        """parse_rss_date should parse RFC 2822 dates."""
        iso = parse_rss_date("Mon, 15 Jan 2024 10:30:00 GMT")
        self.assertIn("2024", iso)
        self.assertIn("T", iso)

    def test_parse_rss_date_handles_empty(self):
        """parse_rss_date should return empty for empty input."""
        self.assertEqual(parse_rss_date(""), "")
        self.assertEqual(parse_rss_date(None), "")

    def test_collector_initialization(self):
        """RSSCollector should initialize with feed URL."""
        config = SourceConfig(
            name="woshipm",
            type="rss",
            config={"url": "https://www.woshipm.com/feed"},
        )
        collector = RSSCollector(config)
        self.assertEqual(collector.feed_url, "https://www.woshipm.com/feed")

    def test_collector_no_url_returns_error(self):
        """RSSCollector without URL should return error."""
        config = SourceConfig(name="test", type="rss", config={})
        collector = RSSCollector(config)
        result = collector.collect("test", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("No RSS feed URL", result.error)

    def test_collector_max_items_default(self):
        """RSSCollector should have default max_items."""
        config = SourceConfig(
            name="test",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        self.assertEqual(collector.max_items, 50)

    def test_collector_max_items_custom(self):
        """RSSCollector should accept custom max_items."""
        config = SourceConfig(
            name="test",
            type="rss",
            config={"url": "https://example.com/feed", "max_items": 100},
        )
        collector = RSSCollector(config)
        self.assertEqual(collector.max_items, 100)

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_rss_feed(self, mock_urlopen):
        """RSSCollector should parse RSS feed."""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <item>
                    <title>Test Item</title>
                    <link>https://example.com/item1</link>
                    <description>Test description</description>
                    <pubDate>Mon, 15 Jan 2024 10:30:00 GMT</pubDate>
                    <author>Test Author</author>
                </item>
            </channel>
        </rss>"""

        mock_response = MagicMock()
        mock_response.read.return_value = rss_xml.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="test_rss",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        result = collector.collect("", max_items=10)

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]["title"], "Test Item")
        self.assertIsNone(result.error)

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_atom_feed(self, mock_urlopen):
        """RSSCollector should parse Atom feed."""
        atom_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>Test Feed</title>
            <entry>
                <title>Atom Entry</title>
                <link href="https://example.com/entry1" rel="alternate"/>
                <content>Atom content here</content>
                <updated>2024-01-15T10:30:00Z</updated>
                <author><name>Atom Author</name></author>
            </entry>
        </feed>"""

        mock_response = MagicMock()
        mock_response.read.return_value = atom_xml.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="test_atom",
            type="rss",
            config={"url": "https://example.com/atom"},
        )
        collector = RSSCollector(config)
        result = collector.collect("", max_items=10)

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]["title"], "Atom Entry")
        self.assertIsNone(result.error)

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_filters_by_query(self, mock_urlopen):
        """RSSCollector should filter items by query keywords."""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Product Management Tips</title>
                    <link>https://example.com/pm</link>
                    <description>PM content</description>
                </item>
                <item>
                    <title>Developer News</title>
                    <link>https://example.com/dev</link>
                    <description>Dev content</description>
                </item>
            </channel>
        </rss>"""

        mock_response = MagicMock()
        mock_response.read.return_value = rss_xml.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="test_rss",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        result = collector.collect("product management", max_items=10)

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]["title"], "Product Management Tips")

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_handles_http_error(self, mock_urlopen):
        """RSSCollector should handle HTTP errors."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com/feed", 404, "Not Found", {}, None
        )

        config = SourceConfig(
            name="test_rss",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        result = collector.collect("", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("HTTP error", result.error)

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_handles_url_error(self, mock_urlopen):
        """RSSCollector should handle URL errors."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        config = SourceConfig(
            name="test_rss",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        result = collector.collect("", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("URL error", result.error)

    @patch("collectors.rss_generic.urllib.request.urlopen")
    def test_collect_handles_xml_error(self, mock_urlopen):
        """RSSCollector should handle XML parse errors."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"Not valid XML <broken>"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="test_rss",
            type="rss",
            config={"url": "https://example.com/feed"},
        )
        collector = RSSCollector(config)
        result = collector.collect("", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("XML parse error", result.error)


class TestRSSCollectorFactories(unittest.TestCase):
    """Tests for RSS collector factory functions."""

    def test_woshipm_collector(self):
        """woshipm_collector should set correct URL."""
        config = SourceConfig(name="woshipm", type="rss")
        collector = RSSCollector(config)
        # Import and use factory
        from collectors.rss_generic import woshipm_collector
        collector = woshipm_collector(config)
        self.assertIn("woshipm.com", collector.feed_url)

    def test_pmcaff_collector(self):
        """pmcaff_collector should set correct URL."""
        config = SourceConfig(name="pmcaff", type="rss")
        from collectors.rss_generic import pmcaff_collector
        collector = pmcaff_collector(config)
        self.assertIn("pmcaff.com", collector.feed_url)

    def test_techcrunch_collector(self):
        """techcrunch_collector should set correct URL."""
        config = SourceConfig(name="techcrunch", type="rss")
        from collectors.rss_generic import techcrunch_collector
        collector = techcrunch_collector(config)
        self.assertIn("techcrunch.com", collector.feed_url)

    def test_mindtheproduct_collector(self):
        """mindtheproduct_collector should set correct URL."""
        config = SourceConfig(name="mindtheproduct", type="rss")
        from collectors.rss_generic import mindtheproduct_collector
        collector = mindtheproduct_collector(config)
        self.assertIn("mindtheproduct.com", collector.feed_url)


class TestSearchCollector(unittest.TestCase):
    """Tests for SearchCollector."""

    def test_collector_initialization_default_duckduckgo(self):
        """SearchCollector should default to DuckDuckGo."""
        config = SourceConfig(name="search", type="search")
        collector = SearchCollector(config)
        self.assertEqual(collector.engine, "duckduckgo")
        self.assertEqual(collector.delay_seconds, 2)

    def test_collector_custom_engine(self):
        """SearchCollector should accept custom engine."""
        config = SourceConfig(
            name="bing_search",
            type="search",
            config={"engine": "bing", "delay_seconds": 1}
        )
        collector = SearchCollector(config)
        self.assertEqual(collector.engine, "bing")
        self.assertEqual(collector.delay_seconds, 1)

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_google_browser(self, mock_urlopen):
        """SearchCollector should use browser simulation for Google."""
        html_response = """
        <html>
        <div class="g">
            <a href="/url?q=https://example.com/page1&amp;sa=U">
                <h3>Google Result 1</h3>
            </a>
            <div class="VwiC3b">Snippet for result 1</div>
        </div>
        </html>
        """
        mock_response = MagicMock()
        mock_response.read.return_value = html_response.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="google",
            type="search",
            config={"engine": "google", "delay_seconds": 0}
        )
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(result.metadata.get("engine"), "google")
        self.assertEqual(result.metadata.get("method"), "browser")

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_bing_browser(self, mock_urlopen):
        """SearchCollector should use browser simulation for Bing."""
        html_response = """
        <html>
        <li class="b_algo">
            <h2><a href="https://example.com/page1">Bing Result 1</a></h2>
            <div class="b_caption"><p>Snippet for result 1</p></div>
        </li>
        </html>
        """
        mock_response = MagicMock()
        mock_response.read.return_value = html_response.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="bing",
            type="search",
            config={"engine": "bing", "delay_seconds": 0}
        )
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(result.metadata.get("engine"), "bing")
        self.assertEqual(result.metadata.get("method"), "browser")

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_baidu_browser(self, mock_urlopen):
        """SearchCollector should use browser simulation for Baidu."""
        html_response = """
        <html>
        <div class="result">
            <h3 class="t"><a href="https://baidu.com/link?url=xxx">百度结果 1</a></h3>
            <div class="c-abstract">这是摘要</div>
        </div>
        </html>
        """
        mock_response = MagicMock()
        mock_response.read.return_value = html_response.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(
            name="baidu",
            type="search",
            config={"engine": "baidu", "delay_seconds": 0}
        )
        collector = SearchCollector(config)
        result = collector.collect("测试查询", max_items=10)

        self.assertEqual(result.metadata.get("engine"), "baidu")
        self.assertEqual(result.metadata.get("method"), "browser")

    def test_collect_unknown_engine(self):
        """SearchCollector should return error for unknown engine."""
        config = SourceConfig(
            name="unknown",
            type="search",
            config={"engine": "unknown_engine"}
        )
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("Unknown search engine", result.error)

    def test_google_collector_factory(self):
        """google_collector should create Google search collector."""
        config = SourceConfig(name="google", type="search")
        collector = google_collector(config)
        self.assertEqual(collector.engine, "google")

    def test_bing_collector_factory(self):
        """bing_collector should create Bing search collector."""
        config = SourceConfig(name="bing", type="search")
        collector = bing_collector(config)
        self.assertEqual(collector.engine, "bing")

    def test_duckduckgo_collector_factory(self):
        """duckduckgo_collector should create DuckDuckGo search collector."""
        config = SourceConfig(name="duckduckgo", type="search")
        collector = duckduckgo_collector(config)
        self.assertEqual(collector.engine, "duckduckgo")

    def test_baidu_collector_factory(self):
        """baidu_collector should create Baidu search collector."""
        config = SourceConfig(name="baidu", type="search")
        collector = baidu_collector(config)
        self.assertEqual(collector.engine, "baidu")

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_duckduckgo_returns_items(self, mock_urlopen):
        """SearchCollector should return items from DuckDuckGo."""
        html_response = """
        <html>
        <div class="result__body">
            <a class="result__a" href="https://example.com/page1">Test Result 1</a>
            <a class="result__snippet">This is a snippet for result 1</a>
        </div>
        <div class="result__body">
            <a class="result__a" href="https://example.com/page2">Test Result 2</a>
            <a class="result__snippet">This is a snippet for result 2</a>
        </div>
        </html>
        """
        mock_response = MagicMock()
        mock_response.read.return_value = html_response.encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        config = SourceConfig(name="duckduckgo", type="search", config={"delay_seconds": 0})
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.items[0]["title"], "Test Result 1")
        self.assertEqual(result.metadata["engine"], "duckduckgo")

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_duckduckgo_handles_error(self, mock_urlopen):
        """SearchCollector should handle DuckDuckGo errors."""
        mock_urlopen.side_effect = Exception("Connection timeout")

        config = SourceConfig(name="duckduckgo", type="search", config={"delay_seconds": 0})
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("DuckDuckGo search error", result.error)

    @patch("collectors.search_collector.urllib.request.urlopen")
    def test_collect_google_handles_error(self, mock_urlopen):
        """SearchCollector should handle Google errors."""
        mock_urlopen.side_effect = Exception("Network error")

        config = SourceConfig(
            name="google",
            type="search",
            config={"engine": "google", "delay_seconds": 0}
        )
        collector = SearchCollector(config)
        result = collector.collect("test query", max_items=10)

        self.assertEqual(len(result.items), 0)
        self.assertIn("Google search error", result.error)

    def test_clean_html_removes_tags(self):
        """_clean_html should remove HTML tags."""
        config = SourceConfig(name="duckduckgo", type="search")
        collector = SearchCollector(config)
        clean = collector._clean_html("<b>Hello</b> <i>World</i>")
        self.assertEqual(clean, "Hello World")

    def test_clean_html_decodes_entities(self):
        """_clean_html should decode HTML entities."""
        config = SourceConfig(name="duckduckgo", type="search")
        collector = SearchCollector(config)
        clean = collector._clean_html("Hello &amp; World &lt;test&gt;")
        self.assertEqual(clean, "Hello & World <test>")

    def test_clean_html_handles_empty(self):
        """_clean_html should handle empty input."""
        config = SourceConfig(name="duckduckgo", type="search")
        collector = SearchCollector(config)
        self.assertEqual(collector._clean_html(""), "")
        self.assertEqual(collector._clean_html(None), "")


class TestIntegration(unittest.TestCase):
    """Integration tests for collector workflow."""

    def test_full_source_selection_flow(self):
        """Test complete flow from query to source selection."""
        selector = SourceSelector()

        # Chinese PM query
        selection = selector.select(query="产品经理在日常工作中遇到哪些痛点")

        # Should have selected sources
        self.assertGreater(len(selection.selected_sources), 0)
        self.assertEqual(selection.language_detected, "chinese")

        # Should have matching keywords
        self.assertIsInstance(selection.matching_keywords, dict)


if __name__ == "__main__":
    unittest.main()
