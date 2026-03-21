import importlib.util
import json
import pathlib
import tempfile
import unittest


SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "run_pipeline.py"
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
                "input": {
                    "mode": "external_file",
                    "name": "external-items",
                    "path": str(input_path),
                },
            }
            items, stats = MODULE.collect_items(config)
            self.assertEqual(len(items), 1)
            self.assertEqual(stats["external-items"]["fetched"], 1)
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


if __name__ == "__main__":
    unittest.main()
