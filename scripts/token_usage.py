#!/usr/bin/env python3
"""Aggregate Antigravity (agy) token usage for an orchestrated session.

Antigravity writes session transcripts to:
  ~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl

Subagent threads spawned via `invoke_subagent` carry their own transcripts in
the brain directory. This tool aggregates token consumption (input tokens,
cache read tokens, and output tokens) across the root orchestrator and all
spawned subagents, split by role and model.

Usage:
  scripts/token_usage.py --list [--date YYYY-MM-DD]
  scripts/token_usage.py --root <root-conversation-id-or-prefix> [--format md|json]
  scripts/token_usage.py --latest [--format md|json]

Standard library only. Read-only: never modifies any session files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"

USAGE_KEYS = (
    "input_tokens",
    "cache_read_tokens",
    "output_tokens",
    "total_tokens",
)


def empty_usage() -> dict[str, int]:
    return {k: 0 for k in USAGE_KEYS}


def add_usage(target: dict[str, int], usage: dict) -> None:
    inp = int(usage.get("input_tokens") or 0)
    cache = int(usage.get("cache_read_tokens") or 0)
    out = int(usage.get("output_tokens") or 0)
    target["input_tokens"] += inp
    target["cache_read_tokens"] += cache
    target["output_tokens"] += out
    target["total_tokens"] += inp + out


def parse_transcript(transcript_path: Path) -> dict:
    usage = empty_usage()
    title = ""
    created_at = None
    subagents_spawned: list[dict] = []
    subagent_ids: set[str] = set()
    model_counts: dict[str, int] = defaultdict(int)

    if not transcript_path.is_file():
        return {
            "title": title,
            "created_at": created_at,
            "usage": usage,
            "subagents": subagents_spawned,
            "subagent_ids": list(subagent_ids),
            "models": dict(model_counts),
        }

    try:
        with transcript_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if not created_at and obj.get("created_at"):
                    created_at = obj.get("created_at")

                source = obj.get("source")
                step_type = obj.get("type")

                if source == "USER_EXPLICIT" and not title:
                    content = obj.get("content") or ""
                    # strip tags if any
                    clean_content = re.sub(r"<[^>]+>", "", content).strip()
                    first_line = clean_content.splitlines()[0] if clean_content else ""
                    title = first_line[:80]

                if source == "MODEL":
                    step_usage = {
                        "input_tokens": obj.get("input_tokens", 0),
                        "cache_read_tokens": obj.get("cache_read_tokens", 0),
                        "output_tokens": obj.get("output_tokens", 0),
                    }
                    add_usage(usage, step_usage)

                    # Extract tool calls for subagents
                    tool_calls = obj.get("tool_calls") or []
                    for call in tool_calls:
                        if call.get("name") == "invoke_subagent":
                            args = call.get("args") or {}
                            if isinstance(args, str):
                                try:
                                    args = json.loads(args)
                                except json.JSONDecodeError:
                                    args = {}
                            sub_list = args.get("Subagents") or []
                            for sub in sub_list:
                                if isinstance(sub, dict):
                                    subagents_spawned.append(sub)

                # Look for conversation IDs in system responses or content
                content_str = json.dumps(obj)
                found_uuids = re.findall(
                    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
                    content_str,
                )
                for uid in found_uuids:
                    # Ignore the current file's own conversation ID
                    if uid not in str(transcript_path):
                        subagent_ids.add(uid)

    except OSError:
        pass

    return {
        "title": title or "Untitled Session",
        "created_at": created_at,
        "usage": usage,
        "subagents": subagents_spawned,
        "subagent_ids": list(subagent_ids),
        "models": dict(model_counts),
    }


def find_session_dir(brain_dir: Path, session_prefix: str) -> Path | None:
    if not brain_dir.is_dir():
        return None

    # Check exact match first
    exact = brain_dir / session_prefix
    if exact.is_dir():
        return exact

    # Check prefix matches
    matches = [
        d
        for d in brain_dir.iterdir()
        if d.is_dir() and d.name.startswith(session_prefix)
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def get_latest_session_dir(brain_dir: Path) -> Path | None:
    if not brain_dir.is_dir():
        return None

    candidates = []
    for d in brain_dir.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        transcript = d / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.is_file():
            candidates.append((transcript.stat().st_mtime, d))

    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def list_sessions(brain_dir: Path, date: str | None = None):
    if not brain_dir.is_dir():
        return

    sessions = []
    for d in brain_dir.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        transcript = d / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript.is_file():
            continue

        info = parse_transcript(transcript)
        created_str = info.get("created_at") or ""
        if date and not created_str.startswith(date):
            continue

        mtime = transcript.stat().st_mtime
        sessions.append(
            {
                "id": d.name,
                "title": info["title"],
                "created_at": created_str,
                "mtime": mtime,
                "total_tokens": info["usage"]["total_tokens"],
                "input_tokens": info["usage"]["input_tokens"],
                "cache_read_tokens": info["usage"]["cache_read_tokens"],
                "output_tokens": info["usage"]["output_tokens"],
            }
        )

    sessions.sort(key=lambda s: s["mtime"], reverse=True)
    yield from sessions


def analyze_session(conv_id: str, brain_dir: Path) -> dict:
    session_dir = find_session_dir(brain_dir, conv_id)
    if not session_dir:
        raise ValueError(f"Session not found: {conv_id} in {brain_dir}")

    resolved_id = session_dir.name
    root_transcript = session_dir / ".system_generated" / "logs" / "transcript.jsonl"
    root_info = parse_transcript(root_transcript)

    total_usage = empty_usage()
    add_usage(total_usage, root_info["usage"])

    threads = []
    threads.append(
        {
            "id": resolved_id,
            "role": "root",
            "type": "orchestrator",
            "usage": root_info["usage"],
        }
    )

    roles = {"root": dict(root_info["usage"])}

    # Link subagents
    sub_configs = root_info.get("subagents") or []
    sub_ids = root_info.get("subagent_ids") or []

    for i, sub_id in enumerate(sub_ids):
        sub_dir = brain_dir / sub_id
        sub_transcript = sub_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if sub_transcript.is_file():
            sub_info = parse_transcript(sub_transcript)
            sub_role = (
                sub_configs[i].get("Role", f"subagent-{i+1}")
                if i < len(sub_configs)
                else f"subagent-{i+1}"
            )
            sub_type = (
                sub_configs[i].get("TypeName", "self")
                if i < len(sub_configs)
                else "subagent"
            )

            threads.append(
                {
                    "id": sub_id,
                    "role": sub_role,
                    "type": sub_type,
                    "usage": sub_info["usage"],
                }
            )

            add_usage(total_usage, sub_info["usage"])
            if sub_role not in roles:
                roles[sub_role] = empty_usage()
            add_usage(roles[sub_role], sub_info["usage"])

    return {
        "id": resolved_id,
        "title": root_info["title"],
        "created_at": root_info["created_at"],
        "total": total_usage,
        "threads": threads,
        "roles": roles,
    }


def format_markdown(data: dict) -> str:
    lines = [
        f"# Antigravity Token Usage Report",
        f"",
        f"- **Session ID:** `{data['id']}`",
        f"- **Title:** {data['title']}",
        f"- **Created At:** {data.get('created_at') or 'Unknown'}",
        f"",
        f"## Overall Consumption",
        f"",
        f"| Metric | Tokens |",
        f"| :--- | :--- |",
        f"| Input Tokens | {data['total']['input_tokens']:,} |",
        f"| Cache Read Tokens | {data['total']['cache_read_tokens']:,} |",
        f"| Output Tokens | {data['total']['output_tokens']:,} |",
        f"| **Total Tokens** | **{data['total']['total_tokens']:,}** |",
        f"",
        f"## Threads and Subagents Breakdown",
        f"",
        f"| Thread ID | Role | Type | Input | Cache Read | Output | Total |",
        f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for t in data["threads"]:
        lines.append(
            f"| `{t['id'][:8]}...` | {t['role']} | {t['type']} | {t['usage']['input_tokens']:,} | {t['usage']['cache_read_tokens']:,} | {t['usage']['output_tokens']:,} | **{t['usage']['total_tokens']:,}** |"
        )

    return "\n".join(lines)


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate Antigravity token usage for orchestrated sessions."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List discovered sessions")
    group.add_argument(
        "--root", type=str, help="Root conversation ID or prefix to analyze"
    )
    group.add_argument(
        "--latest", action="store_true", help="Analyze the most recent session"
    )

    parser.add_argument(
        "--date", type=str, default=None, help="Filter list by date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--format",
        choices=["md", "json"],
        default="md",
        help="Output format (default: md)",
    )
    parser.add_argument(
        "--brain-dir",
        type=Path,
        default=DEFAULT_BRAIN_DIR,
        help="Path to Antigravity brain directory",
    )

    args = parser.parse_args()

    brain_dir = args.brain_dir.expanduser().resolve()
    if not brain_dir.is_dir():
        print(f"Error: Brain directory not found: {brain_dir}", file=sys.stderr)
        return 1

    if args.list:
        sessions = list(list_sessions(brain_dir, args.date))
        if not sessions:
            print("No sessions found.", file=sys.stderr)
            return 0

        print(
            f"{'Conversation ID':<38} {'Date':<20} {'Total Tokens':<14} {'Prompt Title'}"
        )
        print("-" * 100)
        for s in sessions:
            date_display = (s["created_at"] or "")[:19].replace("T", " ")
            print(
                f"{s['id']:<38} {date_display:<20} {s['total_tokens']:<14,} {s['title'][:40]}"
            )
        return 0

    target_id = None
    if args.latest:
        latest_dir = get_latest_session_dir(brain_dir)
        if not latest_dir:
            print("Error: No sessions found in brain directory.", file=sys.stderr)
            return 1
        target_id = latest_dir.name
    elif args.root:
        target_id = args.root

    try:
        data = analyze_session(target_id, brain_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(format_json(data))
    else:
        print(format_markdown(data))

    return 0


if __name__ == "__main__":
    sys.exit(main())
