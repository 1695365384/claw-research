#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# Import collectors
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collectors import (
    CollectorRegistry,
    HackerNewsCollector,
    HackerNewsCommentsCollector,
    RSSCollector,
    SearchCollector,
    load_source_configs,
    load_api_keys,
)


USER_AGENT = "market-demand-research/1.0"


def default_config():
    return {
        "project_name": "market-demand-research",
        "output_dir": "./data",
        "report_dir": "./reports",
        "state_file": "./data/state.json",
        "charter_file": "./config/research-charter.json",
        "max_items_per_source": 20,
        "lookback_hours": 48,
        "cluster_window_hours": 168,
        "input": {
            "mode": "external_file",
            "name": "external_input",
            "path": "",
        },
        "keywords": {
            "include_any": [],
            "exclude_any": [],
        },
        "sources": [],
    }


def setup_registry():
    """Set up collector registry with all available collectors."""
    registry = CollectorRegistry()
    registry.register("api", HackerNewsCollector)
    registry.register("rss", RSSCollector)
    registry.register("search", SearchCollector)
    return registry


def load_research_charter(charter_path):
    """Load research charter if exists, return None otherwise."""
    if not charter_path or not os.path.exists(charter_path):
        return None
    with open(charter_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_text(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def now_iso():
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_ws(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def fingerprint(text):
    return hashlib.sha256(normalize_ws(text).lower().encode("utf-8")).hexdigest()


def within_lookback(iso_value, lookback_hours):
    if not iso_value:
        return True
    try:
        value = dt.datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
    except ValueError:
        return True
    cutoff = utc_now() - dt.timedelta(hours=lookback_hours)
    return value >= cutoff


def parse_iso(iso_value):
    if not iso_value:
        return None
    try:
        return dt.datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
    except ValueError:
        return None


def keyword_match(text, include_any, exclude_any):
    hay = (text or "").lower()
    include = any(k.lower() in hay for k in include_any) if include_any else True
    exclude = any(k.lower() in hay for k in exclude_any) if exclude_any else False
    return include and not exclude


def parse_rss(url, source_name, max_items):
    xml_text = http_text(url)
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item")[:max_items]:
        title = normalize_ws(item.findtext("title"))
        link = normalize_ws(item.findtext("link"))
        description = normalize_ws(item.findtext("description"))
        pub_date = normalize_ws(item.findtext("pubDate"))
        items.append({
            "source": source_name,
            "source_type": "rss",
            "title": title,
            "url": link,
            "text": f"{title}\n{description}",
            "captured_at": now_iso(),
            "published_at": pub_date,
        })
    return items


def fetch_hn_algolia(query, source_name, max_items):
    encoded = urllib.parse.quote(query)
    url = f"https://hn.algolia.com/api/v1/search_by_date?query={encoded}&tags=story"
    data = http_json(url)
    rows = []
    for hit in data.get("hits", [])[:max_items]:
        title = normalize_ws(hit.get("title") or hit.get("story_title") or "")
        item_url = normalize_ws(hit.get("url") or hit.get("story_url") or "")
        story_text = normalize_ws(hit.get("story_text") or "")
        rows.append({
            "source": source_name,
            "source_type": "hn_algolia",
            "title": title,
            "url": item_url,
            "text": f"{title}\n{story_text}",
            "captured_at": now_iso(),
            "published_at": hit.get("created_at"),
        })
    return rows


def normalize_external_item(item, fallback_source):
    title = normalize_ws(item.get("title") or item.get("summary") or "")
    text = normalize_ws(item.get("text") or item.get("content") or item.get("body") or title)
    return {
        "source": item.get("source") or fallback_source,
        "source_type": item.get("source_type") or "external_items",
        "title": title,
        "url": item.get("url") or "",
        "text": text,
        "captured_at": item.get("captured_at") or now_iso(),
        "published_at": item.get("published_at") or item.get("created_at") or "",
    }


def load_external_items(path, fallback_source, max_items):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".jsonl":
        raw_rows = read_jsonl(path)
    else:
        raw_rows = load_json(path, [])
        if isinstance(raw_rows, dict):
            raw_rows = raw_rows.get("items", [])
    return [normalize_external_item(item, fallback_source) for item in raw_rows[:max_items]]


def collect_items(config, registry, source_configs, api_keys):
    """
    Collect items from configured sources in config/sources.json.

    Args:
        config: Pipeline configuration dict
        registry: CollectorRegistry instance
        source_configs: Dict of SourceConfig objects from config/sources.json
        api_keys: Dict of API keys from config/keys.json

    Returns:
        Tuple of (items, source_stats)
    """
    rows = []
    max_items = config.get("max_items_per_source", 20)
    source_stats = {}

    query = config.get("query", config.get("project_name", ""))
    enabled_sources = config.get("sources", [])

    if not enabled_sources:
        print("⚠️ No sources configured. Add sources in config/sources.json", file=sys.stderr)
        return rows, source_stats

    for source_name in enabled_sources:
        source_config = source_configs.get(source_name)
        if not source_config:
            print(f"skip unknown source: {source_name}", file=sys.stderr)
            continue

        if not source_config.enabled:
            continue

        source_stats[source_name] = {
            "type": source_config.type,
            "fetched": 0,
            "failed": False,
            "error": "",
        }

        try:
            collector = registry.create(source_config.type, source_config, api_keys)
            if not collector:
                print(f"skip unsupported source type: {source_config.type}", file=sys.stderr)
                continue

            if not collector.is_available():
                msg = collector.get_missing_auth_message()
                print(f"skip source {source_name}: {msg}", file=sys.stderr)
                source_stats[source_name]["failed"] = True
                source_stats[source_name]["error"] = msg or "Authentication required"
                continue

            result = collector.collect(query, max_items)

            if result.error:
                source_stats[source_name]["failed"] = True
                source_stats[source_name]["error"] = result.error
                print(f"source {source_name} failed: {result.error}", file=sys.stderr)
            else:
                for item in result.items:
                    rows.append(normalize_external_item(item, source_name))
                source_stats[source_name]["fetched"] = len(result.items)

        except Exception as exc:
            print(f"source failed: {source_name}: {exc}", file=sys.stderr)
            source_stats[source_name]["failed"] = True
            source_stats[source_name]["error"] = str(exc)

    return rows, source_stats


def build_analysis_brief(config, items, filter_stats, source_stats, charter=None):
    top_titles = [item.get("title", "") for item in items[:20]]
    brief = {
        "generated_at": now_iso(),
        "project_name": config.get("project_name", ""),
        "instructions": {
            "goal": "Use the filtered items to identify repeated pain points, user scenarios, workarounds, payment signals, and candidate opportunity clusters.",
            "expected_outputs": [
                "top pain points",
                "repeated scenarios",
                "current workarounds",
                "payment signals",
                "candidate clusters",
                "next interview targets",
                "bayesian probability scores",
                "strategic analysis (SWOT, competitor landscape, user journey)",
                "actionable insights with evidence basis",
                "hypothesis validation results",
            ],
        },
        "source_stats": source_stats,
        "filter_stats": filter_stats,
        "item_count": len(items),
        "top_titles": top_titles,
    }
    if charter:
        brief["research_charter"] = charter
    return brief


def filter_and_dedupe(config, state, items):
    include_any = config.get("keywords", {}).get("include_any", [])
    exclude_any = config.get("keywords", {}).get("exclude_any", [])
    lookback = config.get("lookback_hours", 48)
    kept = []
    seen_urls = set(state.get("seen_urls", []))
    seen_fingerprints = set(state.get("seen_fingerprints", []))
    stats = {
        "input_items": len(items),
        "filtered_keyword": 0,
        "filtered_lookback": 0,
        "filtered_duplicate_url": 0,
        "filtered_duplicate_fingerprint": 0,
        "kept": 0,
    }
    for item in items:
        blob = f"{item.get('title', '')}\n{item.get('text', '')}"
        if not keyword_match(blob, include_any, exclude_any):
            stats["filtered_keyword"] += 1
            continue
        if not within_lookback(item.get("published_at"), lookback):
            stats["filtered_lookback"] += 1
            continue
        url = item.get("url")
        fp = fingerprint(blob)
        if url and url in seen_urls:
            stats["filtered_duplicate_url"] += 1
            continue
        if fp in seen_fingerprints:
            stats["filtered_duplicate_fingerprint"] += 1
            continue
        item["fingerprint"] = fp
        kept.append(item)
        if url:
            seen_urls.add(url)
        seen_fingerprints.add(fp)
    stats["kept"] = len(kept)
    state["seen_urls"] = list(seen_urls)[-5000:]
    state["seen_fingerprints"] = list(seen_fingerprints)[-5000:]
    return kept, stats


def recent_items(items, hours):
    cutoff = utc_now() - dt.timedelta(hours=hours)
    result = []
    for item in items:
        captured = parse_iso(item.get("captured_at"))
        if not captured:
            continue
        if captured >= cutoff:
            result.append(item)
    return result


def build_weekly_report(config, items, path):
    weekly = recent_items(items, 24 * 7)
    lines = [
        f"# Weekly Demand Report - {config.get('project_name', 'untitled')}",
        "",
        f"- generated_at: {now_iso()}",
        f"- items_last_7d: {len(weekly)}",
        "",
        "## Review Guidance",
        "",
    ]
    for item in weekly[:10]:
        lines.append(f"### {item.get('title', 'Untitled')}")
        lines.append(f"- source: {item.get('source', '')}")
        lines.append(f"- url: {item.get('url', '')}")
        lines.append(f"- published_at: {item.get('published_at', '')}")
        lines.append("")
    lines.extend([
        "## Next Step",
        "",
        "- Use OpenClaw to review `data/analysis_input.json` and `data/candidate_items.jsonl`.",
        "- Ask the agent to cluster repeated pains, workarounds, and payment signals from the weekly set.",
    ])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def build_report(config, items, path):
    lines = [
        f"# Demand Report - {config.get('project_name', 'untitled')}",
        "",
        f"- generated_at: {now_iso()}",
        f"- new_items: {len(items)}",
        "",
        "## Candidate Items",
        "",
    ]
    for item in items[:20]:
        lines.append(f"### {item.get('title', 'Untitled')}")
        lines.append(f"- source: {item.get('source', '')}")
        lines.append(f"- published_at: {item.get('published_at', '')}")
        lines.append(f"- url: {item.get('url', '')}")
        lines.append("")
    lines.extend([
        "## Agent Step",
        "",
        "- Use OpenClaw to analyze `data/candidate_items.jsonl`.",
        "- Extract repeated pain points, scenarios, workarounds, and likely payment signals.",
        "- Produce a structured summary before deciding whether to continue validation.",
    ])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def sanitize_project_name(name):
    """Convert a string to a safe project directory name."""
    if not name:
        return "untitled-project"
    # Replace spaces and special chars with hyphens
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", name.strip().lower())
    # Remove consecutive hyphens
    safe = re.sub(r"-+", "-", safe)
    # Remove leading/trailing hyphens
    safe = safe.strip("-")
    return safe or "untitled-project"


def main():
    parser = argparse.ArgumentParser(description="Claw Research Pipeline - Market Research Automation")
    parser.add_argument("--project-name", required=True, help="Unique identifier for this research project")
    parser.add_argument("--sources", help="Comma-separated list of data sources to use (default: all enabled in config/sources.json)")
    parser.add_argument("--query", required=True, help="Search query for data collection")
    parser.add_argument("--workspace", help="Project workspace directory (default: workspace/projects/{project_name}/)")
    parser.add_argument("--lookback-hours", type=int, default=720, help="Only include items from the last N hours (default: 720, 30 days)")
    parser.add_argument("--max-items-per-source", type=int, default=20, help="Maximum items per source")
    parser.add_argument("--include-keyword", action="append", default=[], help="Only include items containing this keyword")
    parser.add_argument("--exclude-keyword", action="append", default=[], help="Exclude items containing this keyword")
    args = parser.parse_args()

    config = default_config()
    base_dir = os.getcwd()
    if args.config:
        config_path = os.path.abspath(args.config)
        with open(config_path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        config.update({k: v for k, v in loaded.items() if k not in {"input", "keywords"}})
        config["input"].update(loaded.get("input", {}))
        config["keywords"].update(loaded.get("keywords", {}))
        if "sources" in loaded:
            config["sources"] = loaded["sources"]
        base_dir = os.path.dirname(config_path)

    # Set project name (required)
    config["project_name"] = args.project_name
    safe_name = sanitize_project_name(args.project_name)

    # Determine workspace - auto-generate if not specified
    if args.workspace:
        workspace_dir = args.workspace
    else:
        workspace_dir = f"workspace/projects/{safe_name}"
    workspace_path = os.path.abspath(os.path.join(base_dir, workspace_dir))

    # Derive all paths from workspace
    output_dir = os.path.join(workspace_path, "data")
    report_dir = os.path.join(workspace_path, "reports")
    state_path = os.path.join(workspace_path, "data", "state.json")
    charter_path = os.path.join(workspace_path, "config", "research-charter.json")

    # Fallback to global charter if project-specific not found
    if not os.path.exists(charter_path):
        global_charter = os.path.abspath(os.path.join(base_dir, "config/research-charter.json"))
        if os.path.exists(global_charter):
            charter_path = global_charter
    # Handle remaining config overrides
    if args.lookback_hours is not None:
        config["lookback_hours"] = args.lookback_hours
    if args.cluster_window_hours is not None:
        config["cluster_window_hours"] = args.cluster_window_hours
    if args.max_items_per_source is not None:
        config["max_items_per_source"] = args.max_items_per_source
    if args.include_keyword:
        config["keywords"]["include_any"] = args.include_keyword
    if args.exclude_keyword:
        config["keywords"]["exclude_any"] = args.exclude_keyword
    if args.input_jsonl:
        config["input"]["path"] = args.input_jsonl

    # Data collection options
    if args.collect:
        config["collect"] = True
    if args.sources:
        config["enabled_sources"] = [s.strip() for s in args.sources.split(",")]
    if args.query:
        config["query"] = args.query

    # Load data source configurations and API keys
    sources_json_path = os.path.join(base_dir, "config", "sources.json")
    keys_json_path = os.path.join(base_dir, "config", "keys.json")

    source_configs = load_source_configs(sources_json_path)
    api_keys = load_api_keys(keys_json_path)

    # Set up collector registry
    registry = setup_registry()

    # Enable sources based on config or CLI args
    if config.get("enabled_sources"):
        config["sources"] = config["enabled_sources"]
    elif not config.get("sources"):
        # Default to enabled sources from sources.json
        config["sources"] = [
            name for name, cfg in source_configs.items()
            if cfg.enabled
        ][:5]  # Limit to 5 sources by default

    # Create project directory structure
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(os.path.dirname(charter_path), exist_ok=True)

    print(f"📁 Project workspace: {workspace_path}")

    # Load research charter if exists
    charter = load_research_charter(charter_path)
    if charter:
        print(f"loaded research charter: {charter.get('project_id', 'unknown')}")

    state = load_json(state_path, {"seen_urls": [], "seen_fingerprints": [], "last_run_at": None})
    collected, source_stats = collect_items(config, registry, source_configs, api_keys)
    append_jsonl(os.path.join(output_dir, "raw.jsonl"), collected)

    filtered, filter_stats = filter_and_dedupe(config, state, collected)
    if not filtered:
        run_metrics = {
            "generated_at": now_iso(),
            "project_name": config.get("project_name", ""),
            "source_stats": source_stats,
            "filter_stats": filter_stats,
            "new_items": 0,
        }
        save_json(os.path.join(output_dir, "run_metrics.json"), run_metrics)
        state["last_run_at"] = now_iso()
        save_json(state_path, state)
        print("no new matching items")
        return

    append_jsonl(os.path.join(output_dir, "candidate_items.jsonl"), filtered)

    report_name = f"{dt.datetime.utcnow().strftime('%Y-%m-%d')}.md"
    build_report(config, filtered, os.path.join(report_dir, report_name))
    weekly_name = f"weekly-{utc_now().strftime('%Y-%W')}.md"
    all_candidates = read_jsonl(os.path.join(output_dir, "candidate_items.jsonl"))
    build_weekly_report(config, all_candidates, os.path.join(report_dir, weekly_name))

    run_metrics = {
        "generated_at": now_iso(),
        "project_name": config.get("project_name", ""),
        "source_stats": source_stats,
        "filter_stats": filter_stats,
        "new_items": len(filtered),
    }
    save_json(os.path.join(output_dir, "run_metrics.json"), run_metrics)
    save_json(os.path.join(output_dir, "analysis_input.json"), build_analysis_brief(config, filtered, filter_stats, source_stats, charter))
    state["last_run_at"] = now_iso()
    save_json(state_path, state)
    print(f"prepared {len(filtered)} items for agent analysis")


if __name__ == "__main__":
    main()
