import datetime as dt
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add scripts directory to path for imports
SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SCRIPT_PATH = SCRIPTS_DIR / "run_pipeline.py"
SPEC = importlib.util.spec_from_file_location("market_demand_run_pipeline", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RunPipelineTests(unittest.TestCase):
    def test_default_config_has_external_file_mode(self):
        config = MODULE.default_config()
        self.assertEqual(config["input"]["mode"], "external_file")
        self.assertEqual(config["keywords"]["include_any"], [])

    def test_normalize_external_item_uses_text_fallbacks(self):
        item = {
            "summary": "Manual refunds are painful",
            "body": "We still do refunds in spreadsheets",
        }
        normalized = MODULE.normalize_external_item(item, "feed-a")
        self.assertEqual(normalized["source"], "feed-a")
        self.assertEqual(normalized["title"], "Manual refunds are painful")
        self.assertIn("refunds", normalized["text"])

    def test_collect_items_from_external_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = pathlib.Path(tmp) / "items.jsonl"
            input_path.write_text(
                json.dumps({
                    "source": "reddit",
                    "title": "Refunds are manual",
                    "text": "Manual workflow for every refund",
                }) + "\n",
                encoding="utf-8",
            )
            config = {
                "max_items_per_source": 20,
                "query": "refund pain points",
                "sources": ["mock_source"],
            }
            # Create mock registry and configs
            mock_registry = MagicMock()
            mock_collector = MagicMock()
            mock_collector.is_available.return_value = True

            # Import CollectorResult from collectors module
            from collectors import CollectorResult, SourceConfig
            mock_collector.collect.return_value = CollectorResult(
                items=[{
                    "source": "reddit",
                    "title": "Refunds are manual",
                    "text": "Manual workflow for every refund",
                }],
                source_name="mock_source",
                source_type="api",
            )
            mock_registry.create.return_value = mock_collector

            mock_source_configs = {
                "mock_source": SourceConfig(
                    name="mock_source",
                    type="api",
                    enabled=True,
                )
            }

            items, stats = MODULE.collect_items(
                config, mock_registry, mock_source_configs, {}
            )
            self.assertEqual(len(items), 1)
            self.assertEqual(stats["mock_source"]["fetched"], 1)
            self.assertEqual(items[0]["source"], "reddit")

    def test_filter_and_dedupe_filters_and_keeps_expected_items(self):
        config = {
            "keywords": {
                "include_any": ["refund"],
                "exclude_any": ["hiring"],
            },
            "lookback_hours": 48,
        }
        state = {"seen_urls": [], "seen_fingerprints": []}
        items = [
            {
                "title": "Manual refund handling",
                "text": "refund process is painful",
                "url": "https://a",
                "published_at": MODULE.now_iso(),
            },
            {
                "title": "We are hiring support reps",
                "text": "hiring for support",
                "url": "https://b",
                "published_at": MODULE.now_iso(),
            },
        ]
        kept, stats = MODULE.filter_and_dedupe(config, state, items)
        self.assertEqual(len(kept), 1)
        self.assertEqual(stats["filtered_keyword"], 1)
        self.assertEqual(stats["kept"], 1)

    def test_build_analysis_brief_contains_expected_summary(self):
        config = {"project_name": "refund-research"}
        items = [{"title": "Refunds are manual"}, {"title": "Chargebacks are slow"}]
        filter_stats = {"kept": 2}
        source_stats = {"external-items": {"fetched": 2}}
        brief = MODULE.build_analysis_brief(config, items, filter_stats, source_stats)
        self.assertEqual(brief["project_name"], "refund-research")
        self.assertEqual(brief["item_count"], 2)
        self.assertEqual(len(brief["top_titles"]), 2)


class TestUtilityFunctions(unittest.TestCase):
    """Tests for utility functions in run_pipeline.py"""

    def test_normalize_ws_removes_extra_whitespace(self):
        """normalize_ws should collapse whitespace."""
        result = MODULE.normalize_ws("  hello   world  \n\t")
        self.assertEqual(result, "hello world")

    def test_normalize_ws_handles_none(self):
        """normalize_ws should handle None input."""
        self.assertEqual(MODULE.normalize_ws(None), "")
        self.assertEqual(MODULE.normalize_ws(""), "")

    def test_fingerprint_is_consistent(self):
        """fingerprint should return consistent hash."""
        fp1 = MODULE.fingerprint("test content")
        fp2 = MODULE.fingerprint("test content")
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)  # SHA-256 produces 64 hex chars

    def test_fingerprint_normalizes_whitespace(self):
        """fingerprint should normalize whitespace before hashing."""
        fp1 = MODULE.fingerprint("hello  world")
        fp2 = MODULE.fingerprint("hello world")
        self.assertEqual(fp1, fp2)

    def test_keyword_match_includes_when_found(self):
        """keyword_match should include when keyword found."""
        result = MODULE.keyword_match("refund is painful", ["refund"], [])
        self.assertTrue(result)

    def test_keyword_match_excludes_when_found(self):
        """keyword_match should exclude when exclude keyword found."""
        result = MODULE.keyword_match("we are hiring", [], ["hiring"])
        self.assertFalse(result)

    def test_keyword_match_no_filters(self):
        """keyword_match should pass when no filters."""
        result = MODULE.keyword_match("any text", [], [])
        self.assertTrue(result)

    def test_within_lookback_returns_true_for_recent(self):
        """within_lookback should return True for recent dates."""
        recent = MODULE.now_iso()
        self.assertTrue(MODULE.within_lookback(recent, 48))

    def test_within_lookback_returns_false_for_old(self):
        """within_lookback should return False for old dates."""
        old = "2020-01-01T00:00:00Z"
        self.assertFalse(MODULE.within_lookback(old, 48))

    def test_within_lookback_handles_none(self):
        """within_lookback should return True for None."""
        self.assertTrue(MODULE.within_lookback(None, 48))

    def test_parse_iso_valid(self):
        """parse_iso should parse valid ISO dates."""
        result = MODULE.parse_iso("2024-01-15T10:30:00Z")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)

    def test_parse_iso_none(self):
        """parse_iso should return None for None input."""
        self.assertIsNone(MODULE.parse_iso(None))

    def test_parse_iso_invalid(self):
        """parse_iso should return None for invalid input."""
        self.assertIsNone(MODULE.parse_iso("not-a-date"))


class TestFileOperations(unittest.TestCase):
    """Tests for file I/O operations."""

    def test_load_json_existing_file(self):
        """load_json should load existing JSON file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.json")
            with open(path, "w") as f:
                json.dump({"key": "value"}, f)
            result = MODULE.load_json(path, {})
            self.assertEqual(result["key"], "value")

    def test_load_json_missing_file(self):
        """load_json should return default for missing file."""
        result = MODULE.load_json("/nonexistent/path.json", {"default": True})
        self.assertTrue(result["default"])

    def test_save_json_creates_file(self):
        """save_json should create file and directory."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "subdir", "test.json")
            MODULE.save_json(path, {"test": "data"})
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                loaded = json.load(f)
            self.assertEqual(loaded["test"], "data")

    def test_read_jsonl_existing_file(self):
        """read_jsonl should read JSONL file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.jsonl")
            with open(path, "w") as f:
                f.write('{"a": 1}\n{"b": 2}\n')
            result = MODULE.read_jsonl(path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["a"], 1)

    def test_read_jsonl_missing_file(self):
        """read_jsonl should return empty list for missing file."""
        result = MODULE.read_jsonl("/nonexistent/path.jsonl")
        self.assertEqual(result, [])

    def test_append_jsonl_appends_lines(self):
        """append_jsonl should append JSON lines."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.jsonl")
            MODULE.append_jsonl(path, [{"a": 1}, {"b": 2}])
            with open(path) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)


class TestRegistrySetup(unittest.TestCase):
    """Tests for collector registry setup."""

    def test_setup_registry_returns_registry(self):
        """setup_registry should return configured registry."""
        registry = MODULE.setup_registry()
        self.assertIsNotNone(registry)
        sources = registry.get_available_sources()
        self.assertIn("api", sources)
        self.assertIn("rss", sources)
        self.assertIn("search", sources)


class TestResearchCharter(unittest.TestCase):
    """Tests for research charter loading."""

    def test_load_research_charter_existing(self):
        """load_research_charter should load existing file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "charter.json")
            with open(path, "w") as f:
                json.dump({"project_id": "test-123"}, f)
            result = MODULE.load_research_charter(path)
            self.assertEqual(result["project_id"], "test-123")

    def test_load_research_charter_missing(self):
        """load_research_charter should return None for missing file."""
        result = MODULE.load_research_charter("/nonexistent/charter.json")
        self.assertIsNone(result)

    def test_load_research_charter_none_path(self):
        """load_research_charter should handle None path."""
        result = MODULE.load_research_charter(None)
        self.assertIsNone(result)


class TestProjectNameSanitization(unittest.TestCase):
    """Tests for project name sanitization."""

    def test_sanitize_simple_name(self):
        """sanitize_project_name should keep simple names."""
        result = MODULE.sanitize_project_name("my-project")
        self.assertEqual(result, "my-project")

    def test_sanitize_replaces_spaces(self):
        """sanitize_project_name should replace spaces with hyphens."""
        result = MODULE.sanitize_project_name("my project name")
        self.assertEqual(result, "my-project-name")

    def test_sanitize_removes_special_chars(self):
        """sanitize_project_name should remove special characters."""
        result = MODULE.sanitize_project_name("My Project@2024!")
        self.assertEqual(result, "my-project-2024")

    def test_sanitize_handles_empty(self):
        """sanitize_project_name should handle empty input."""
        result = MODULE.sanitize_project_name("")
        self.assertEqual(result, "untitled-project")

    def test_sanitize_handles_none(self):
        """sanitize_project_name should handle None input."""
        result = MODULE.sanitize_project_name(None)
        self.assertEqual(result, "untitled-project")


class TestCollectItemsEdgeCases(unittest.TestCase):
    """Tests for collect_items edge cases."""

    def test_collect_items_empty_sources(self):
        """collect_items should handle empty sources list."""
        config = {"sources": [], "query": "test", "max_items_per_source": 10}
        registry = MagicMock()
        items, stats = MODULE.collect_items(config, registry, {}, {})
        self.assertEqual(items, [])
        self.assertEqual(stats, {})

    def test_collect_items_unknown_source(self):
        """collect_items should skip unknown sources."""
        config = {"sources": ["unknown"], "query": "test", "max_items_per_source": 10}
        registry = MagicMock()
        items, stats = MODULE.collect_items(config, registry, {}, {})
        self.assertEqual(items, [])
        self.assertNotIn("unknown", stats)

    def test_collect_items_disabled_source(self):
        """collect_items should skip disabled sources."""
        from collectors import SourceConfig
        config = {"sources": ["disabled"], "query": "test", "max_items_per_source": 10}
        registry = MagicMock()
        source_configs = {
            "disabled": SourceConfig(name="disabled", type="api", enabled=False)
        }
        items, stats = MODULE.collect_items(config, registry, source_configs, {})
        self.assertEqual(items, [])

    def test_collect_items_unavailable_collector(self):
        """collect_items should handle unavailable collectors."""
        from collectors import SourceConfig
        config = {"sources": ["unavailable"], "query": "test", "max_items_per_source": 10}
        registry = MagicMock()
        mock_collector = MagicMock()
        mock_collector.is_available.return_value = False
        mock_collector.get_missing_auth_message.return_value = "Need API key"
        registry.create.return_value = mock_collector

        source_configs = {
            "unavailable": SourceConfig(name="unavailable", type="api", enabled=True)
        }
        items, stats = MODULE.collect_items(config, registry, source_configs, {})
        self.assertEqual(items, [])
        self.assertTrue(stats["unavailable"]["failed"])

    def test_collect_items_with_error(self):
        """collect_items should handle collector errors."""
        from collectors import CollectorResult, SourceConfig
        config = {"sources": ["error_source"], "query": "test", "max_items_per_source": 10}
        registry = MagicMock()
        mock_collector = MagicMock()
        mock_collector.is_available.return_value = True
        mock_collector.collect.return_value = CollectorResult(
            items=[],
            source_name="error_source",
            source_type="api",
            error="Connection failed"
        )
        registry.create.return_value = mock_collector

        source_configs = {
            "error_source": SourceConfig(name="error_source", type="api", enabled=True)
        }
        items, stats = MODULE.collect_items(config, registry, source_configs, {})
        self.assertEqual(items, [])
        self.assertTrue(stats["error_source"]["failed"])
        self.assertEqual(stats["error_source"]["error"], "Connection failed")


class TestFilterAndDedupe(unittest.TestCase):
    """Tests for filter_and_dedupe function."""

    def test_deduplicates_by_url(self):
        """filter_and_dedupe should remove duplicate URLs."""
        config = {"keywords": {}, "lookback_hours": 48}
        state = {"seen_urls": [], "seen_fingerprints": []}
        items = [
            {"title": "Test", "text": "content", "url": "https://same.com", "published_at": MODULE.now_iso()},
            {"title": "Test 2", "text": "different", "url": "https://same.com", "published_at": MODULE.now_iso()},
        ]
        kept, stats = MODULE.filter_and_dedupe(config, state, items)
        self.assertEqual(len(kept), 1)
        self.assertEqual(stats["filtered_duplicate_url"], 1)

    def test_deduplicates_by_fingerprint(self):
        """filter_and_dedupe should remove duplicate content."""
        config = {"keywords": {}, "lookback_hours": 48}
        state = {"seen_urls": [], "seen_fingerprints": []}
        items = [
            {"title": "Same", "text": "identical content", "url": "", "published_at": MODULE.now_iso()},
            {"title": "Same", "text": "identical content", "url": "", "published_at": MODULE.now_iso()},
        ]
        kept, stats = MODULE.filter_and_dedupe(config, state, items)
        self.assertEqual(len(kept), 1)
        self.assertEqual(stats["filtered_duplicate_fingerprint"], 1)

    def test_filters_by_lookback(self):
        """filter_and_dedupe should filter old items."""
        config = {"keywords": {}, "lookback_hours": 1}
        state = {"seen_urls": [], "seen_fingerprints": []}
        old_date = (MODULE.utc_now() - dt.timedelta(hours=48)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        items = [
            {"title": "Old", "text": "content", "url": "https://old.com", "published_at": old_date},
        ]
        kept, stats = MODULE.filter_and_dedupe(config, state, items)
        self.assertEqual(len(kept), 0)
        self.assertEqual(stats["filtered_lookback"], 1)


class TestBuildAnalysisBrief(unittest.TestCase):
    """Tests for build_analysis_brief function."""

    def test_includes_research_charter(self):
        """build_analysis_brief should include research charter."""
        config = {"project_name": "test"}
        charter = {"project_id": "charter-123", "hypotheses": ["h1"]}
        brief = MODULE.build_analysis_brief(config, [], {}, {}, charter)
        self.assertIn("research_charter", brief)
        self.assertEqual(brief["research_charter"]["project_id"], "charter-123")

    def test_limits_top_titles(self):
        """build_analysis_brief should limit top_titles to 20."""
        config = {"project_name": "test"}
        items = [{"title": f"Item {i}"} for i in range(30)]
        brief = MODULE.build_analysis_brief(config, items, {}, {})
        self.assertEqual(len(brief["top_titles"]), 20)


if __name__ == "__main__":
    unittest.main()
