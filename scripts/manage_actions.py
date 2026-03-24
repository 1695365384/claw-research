#!/usr/bin/env python3
"""
Action Item Management CLI for claw-research.

Usage:
    # With project isolation (recommended)
    python3 scripts/manage_actions.py --project pm-pain-points --list-pending
    python3 scripts/manage_actions.py --project pm-pain-points --complete ACTION-001 --note "Completed"
    python3 scripts/manage_actions.py --project pm-pain-points --add "Interview 5 sellers" --due 2026-04-15

    # Legacy mode (uses global tracker)
    python3 scripts/manage_actions.py --list-pending
    python3 scripts/manage_actions.py --stats
"""

import argparse
import datetime as dt
import json
import os
import re
import sys


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def now_iso():
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sanitize_project_name(name):
    """Convert a string to a safe project directory name."""
    if not name:
        return "untitled-project"
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", name.strip().lower())
    safe = re.sub(r"-+", "-", safe)
    safe = safe.strip("-")
    return safe or "untitled-project"


def load_tracker(path):
    if not os.path.exists(path):
        return {
            "project_id": "default",
            "last_updated": now_iso(),
            "action_items": [],
            "learnings": []
        }
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_tracker(path, tracker):
    tracker["last_updated"] = now_iso()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(tracker, fh, ensure_ascii=False, indent=2)


def list_pending(tracker):
    """List all pending action items."""
    pending = [a for a in tracker.get("action_items", []) if a.get("status") == "pending"]
    if not pending:
        print("No pending action items.")
        return

    print(f"Pending Action Items ({len(pending)}):\n")
    for item in pending:
        print(f"  [{item['id']}] {item['action']}")
        print(f"      Due: {item.get('due_date', 'N/A')}")
        print(f"      Insight: {item.get('linked_insight', 'N/A')}")
        print(f"      Validation: {item.get('validation_criteria', 'N/A')}")
        print()


def list_all(tracker):
    """List all action items regardless of status."""
    items = tracker.get("action_items", [])
    if not items:
        print("No action items found.")
        return

    print(f"All Action Items ({len(items)}):\n")
    for item in items:
        status_icon = {"pending": "[ ]", "completed": "[x]", "blocked": "[!]"}.get(item.get("status"), "[?]")
        print(f"  {status_icon} [{item['id']}] {item['action']}")
        print(f"      Status: {item.get('status', 'unknown')}")
        print(f"      Due: {item.get('due_date', 'N/A')}")
        print()


def complete_action(tracker, action_id, note=""):
    """Mark an action item as completed."""
    for item in tracker.get("action_items", []):
        if item["id"] == action_id:
            item["status"] = "completed"
            item["completed_at"] = now_iso()
            if note:
                item["completion_note"] = note
            print(f"Marked {action_id} as completed.")
            return tracker
    print(f"Action {action_id} not found.")
    return tracker


def add_action(tracker, action, due_date=None, linked_insight="", validation_criteria=""):
    """Add a new action item."""
    existing_ids = [a["id"] for a in tracker.get("action_items", [])]
    next_num = 1
    while f"ACTION-{next_num:03d}" in existing_ids:
        next_num += 1

    new_id = f"ACTION-{next_num:03d}"
    new_item = {
        "id": new_id,
        "action": action,
        "due_date": due_date or "",
        "owner": "user",
        "status": "pending",
        "linked_insight": linked_insight,
        "validation_criteria": validation_criteria,
        "created_at": now_iso()
    }
    tracker.setdefault("action_items", []).append(new_item)
    print(f"Added {new_id}: {action}")
    return tracker


def add_learning(tracker, learning, evidence_strength="medium", next_questions=None):
    """Add a learning to the tracker."""
    new_learning = {
        "date": now_iso(),
        "learning": learning,
        "evidence_strength": evidence_strength,
        "next_questions": next_questions or []
    }
    tracker.setdefault("learnings", []).append(new_learning)
    print(f"Added learning: {learning}")
    return tracker


def show_stats(tracker):
    """Show statistics about action items."""
    items = tracker.get("action_items", [])
    pending = len([a for a in items if a.get("status") == "pending"])
    completed = len([a for a in items if a.get("status") == "completed"])
    blocked = len([a for a in items if a.get("status") == "blocked"])
    learnings = len(tracker.get("learnings", []))

    print("Action Tracker Statistics:\n")
    print(f"  Total Actions: {len(items)}")
    print(f"  Pending: {pending}")
    print(f"  Completed: {completed}")
    print(f"  Blocked: {blocked}")
    print(f"  Learnings: {learnings}")
    print(f"  Last Updated: {tracker.get('last_updated', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Manage action items for claw-research")
    parser.add_argument("--project", help="Project name for project-isolated workspace")
    parser.add_argument("--workspace", help="Explicit workspace directory (overrides --project)")
    parser.add_argument("--tracker-file", default=None,
                        help="Path to action tracker JSON file (legacy mode, ignored if --project is set)")
    parser.add_argument("--list-pending", action="store_true", help="List all pending action items")
    parser.add_argument("--list-all", action="store_true", help="List all action items")
    parser.add_argument("--complete", metavar="ACTION_ID", help="Mark action as completed")
    parser.add_argument("--note", default="", help="Note to add when completing an action")
    parser.add_argument("--add", metavar="ACTION", help="Add a new action item")
    parser.add_argument("--due", metavar="DATE", help="Due date for new action (YYYY-MM-DD)")
    parser.add_argument("--insight", metavar="TEXT", help="Linked insight for new action")
    parser.add_argument("--validation", metavar="CRITERIA", help="Validation criteria for new action")
    parser.add_argument("--add-learning", metavar="LEARNING", help="Add a learning")
    parser.add_argument("--evidence", default="medium", help="Evidence strength for learning")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    # Resolve tracker path based on project isolation
    base_dir = os.getcwd()
    if args.workspace:
        tracker_path = os.path.join(args.workspace, "data", "action-tracker.json")
    elif args.project:
        safe_name = sanitize_project_name(args.project)
        workspace_path = os.path.join(base_dir, "workspace", "projects", safe_name)
        tracker_path = os.path.join(workspace_path, "data", "action-tracker.json")
    elif args.tracker_file:
        tracker_path = os.path.abspath(os.path.join(base_dir, args.tracker_file))
    else:
        # Default to legacy location
        tracker_path = os.path.abspath(os.path.join(base_dir, "workspace/data/action-tracker.json"))

    tracker_path = os.path.abspath(tracker_path)
    print(f"Using tracker: {tracker_path}")

    tracker = load_tracker(tracker_path)

    if args.list_pending:
        list_pending(tracker)
    elif args.list_all:
        list_all(tracker)
    elif args.complete:
        tracker = complete_action(tracker, args.complete, args.note)
        save_tracker(tracker_path, tracker)
    elif args.add:
        tracker = add_action(tracker, args.add, args.due, args.insight or "", args.validation or "")
        save_tracker(tracker_path, tracker)
    elif args.add_learning:
        tracker = add_learning(tracker, args.add_learning, args.evidence)
        save_tracker(tracker_path, tracker)
    elif args.stats:
        show_stats(tracker)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
