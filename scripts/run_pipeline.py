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


USER_AGENT = "market-demand-research/1.0"


def default_config():
    return {
        "project_name": "market-demand-research",
        "output_dir": "./workspace/data",
        "report_dir": "./workspace/reports",
        "state_file": "./workspace/data/state.json",
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


def collect_items(config, input_jsonl=None):
    rows = []
    max_items = config.get("max_items_per_source", 20)
    input_config = config.get("input", {})
    input_mode = input_config.get("mode", "external_file")
    source_stats = {}
    if input_jsonl:
        fetched = load_external_items(input_jsonl, "external_input", max_items)
        source_stats["external_input"] = {
            "type": "external_file",
            "fetched": len(fetched),
            "failed": False,
            "error": "",
        }
        return fetched, source_stats
    if input_mode == "external_file":
        path = input_config.get("path", "").strip()
        if not path:
            raise RuntimeError("input.path is required when input.mode=external_file")
        fetched = load_external_items(path, input_config.get("name", "external_input"), max_items)
        source_stats[input_config.get("name", "external_input")] = {
            "type": "external_file",
            "fetched": len(fetched),
            "failed": False,
            "error": "",
        }
        return fetched, source_stats
    if input_mode != "builtin_sources":
        raise RuntimeError(f"unsupported input.mode: {input_mode}")
    for source in config.get("sources", []):
        stype = source["type"]
        source_stats[source["name"]] = {
            "type": stype,
            "fetched": 0,
            "failed": False,
            "error": "",
        }
        try:
            if stype in {"rss", "reddit_rss"}:
                fetched = parse_rss(source["url"], source["name"], max_items)
            elif stype == "hn_algolia":
                fetched = fetch_hn_algolia(source["query"], source["name"], max_items)
            else:
                print(f"skip unsupported source type: {stype}", file=sys.stderr)
                fetched = []
            rows.extend(fetched)
            source_stats[source["name"]]["fetched"] = len(fetched)
        except Exception as exc:
            print(f"source failed: {source['name']}: {exc}", file=sys.stderr)
            source_stats[source["name"]]["failed"] = True
            source_stats[source["name"]]["error"] = str(exc)
    return rows, source_stats


def build_analysis_brief(config, items, filter_stats, source_stats):
    top_titles = [item.get("title", "") for item in items[:20]]
    return {
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
            ],
        },
        "source_stats": source_stats,
        "filter_stats": filter_stats,
        "item_count": len(items),
        "top_titles": top_titles,
    }


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--input-jsonl")
    parser.add_argument("--project-name")
    parser.add_argument("--output-dir")
    parser.add_argument("--report-dir")
    parser.add_argument("--state-file")
    parser.add_argument("--lookback-hours", type=int)
    parser.add_argument("--cluster-window-hours", type=int)
    parser.add_argument("--max-items-per-source", type=int)
    parser.add_argument("--include-keyword", action="append", default=[])
    parser.add_argument("--exclude-keyword", action="append", default=[])
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

    if args.project_name:
        config["project_name"] = args.project_name
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.report_dir:
        config["report_dir"] = args.report_dir
    if args.state_file:
        config["state_file"] = args.state_file
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

    output_dir = os.path.abspath(os.path.join(base_dir, config.get("output_dir", "./data")))
    report_dir = os.path.abspath(os.path.join(base_dir, config.get("report_dir", "./reports")))
    state_path = os.path.abspath(os.path.join(base_dir, config.get("state_file", "./data/state.json")))

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    state = load_json(state_path, {"seen_urls": [], "seen_fingerprints": [], "last_run_at": None})
    collected, source_stats = collect_items(config, input_jsonl=args.input_jsonl)
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
    save_json(os.path.join(output_dir, "analysis_input.json"), build_analysis_brief(config, filtered, filter_stats, source_stats))
    state["last_run_at"] = now_iso()
    save_json(state_path, state)
    print(f"prepared {len(filtered)} items for agent analysis")


if __name__ == "__main__":
    main()
