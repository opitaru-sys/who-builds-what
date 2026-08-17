#!/usr/bin/env python3
"""who-builds-what: dedup and manager digest for a Monday AI-project board.

Standard library only. fetch_board_items is the only function that touches
the network; everything else is pure and safe to test offline.
"""

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from itertools import combinations

MONDAY_API_URL = "https://api.monday.com/v2"

CADENCE_WINDOW_DAYS = {"daily": 1, "weekly": 7}

STOPWORDS = {
    "the", "a", "an", "for", "of", "and", "to", "in", "on", "with",
    "using", "bot", "agent", "ai", "tool",
}


def tokenize(text):
    """Lowercase, strip punctuation, split on whitespace, drop stopwords."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return {word for word in cleaned.split() if word not in STOPWORDS}


def similarity(a, b):
    """Jaccard similarity between two token sets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _column_text(item, title):
    for column_value in item.get("column_values", []):
        if column_value.get("column", {}).get("title") == title:
            return column_value.get("text") or ""
    return ""


def _item_tokens(item):
    name = item.get("name", "")
    description = item.get("description", "")
    tools = _column_text(item, "Tools & models")
    return tokenize(" ".join([name, description, tools]))


def find_duplicates(items, threshold=0.35):
    """Return (item_a, item_b, score) tuples for every pair scoring at or above threshold."""
    tokens_by_id = {id(item): _item_tokens(item) for item in items}
    duplicates = []
    for item_a, item_b in combinations(items, 2):
        score = similarity(tokens_by_id[id(item_a)], tokens_by_id[id(item_b)])
        if score >= threshold:
            duplicates.append((item_a, item_b, score))
    return duplicates


def _parse_updated_at(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _format_entry(item, extra=""):
    owner = _column_text(item, "Owner") or "unknown owner"
    line = "- **{0}** (owner: {1})".format(item.get("name", "Untitled project"), owner)
    if extra:
        line += " - " + extra
    return line


def build_digest(items, now, cadence="weekly", stale_days=60, threshold=0.35):
    """Render the manager digest as markdown."""
    if cadence not in CADENCE_WINDOW_DAYS:
        raise ValueError("cadence must be 'daily' or 'weekly'")

    if not items:
        return (
            "# who-builds-what digest\n\n"
            "No projects on the board yet. Once someone runs the interview, "
            "they will show up here.\n"
        )

    window_start = now - timedelta(days=CADENCE_WINDOW_DAYS[cadence])
    stale_cutoff = now - timedelta(days=stale_days)

    new_items = []
    unapproved = []
    stale_items = []
    for item in items:
        updated_at = _parse_updated_at(item["updated_at"])
        if updated_at >= window_start:
            new_items.append(item)
        if _column_text(item, "Manager aware").strip().lower() != "yes":
            unapproved.append(item)
        if updated_at < stale_cutoff:
            stale_items.append(item)

    duplicates = find_duplicates(items, threshold)

    lines = [
        "# who-builds-what digest",
        "",
        "Cadence: {0} | Stale after: {1} days | Dedup threshold: {2}".format(
            cadence, stale_days, threshold
        ),
        "Projects: {0} total, {1} new, {2} needing approval, {3} stale, {4} possible duplicate pairs".format(
            len(items), len(new_items), len(unapproved), len(stale_items), len(duplicates)
        ),
        "",
        "## New since last {0} digest".format(cadence),
        "",
    ]
    if new_items:
        lines.extend(_format_entry(item) for item in new_items)
    else:
        lines.append("Nothing new this window.")
    lines.append("")

    lines.append("## Needs approval")
    lines.append("")
    if unapproved:
        for item in unapproved:
            aware = _column_text(item, "Manager aware") or "unset"
            lines.append(_format_entry(item, "Manager aware: {0}".format(aware)))
    else:
        lines.append("Every project has manager sign-off.")
    lines.append("")

    lines.append("## Stale (no update in {0}+ days)".format(stale_days))
    lines.append("")
    if stale_items:
        for item in stale_items:
            lines.append(_format_entry(item, "last updated {0}".format(item["updated_at"])))
    else:
        lines.append("Nothing has gone stale.")
    lines.append("")

    lines.append("## Possible duplicates")
    lines.append("")
    if duplicates:
        for item_a, item_b, score in duplicates:
            owner_a = _column_text(item_a, "Owner") or "unknown owner"
            owner_b = _column_text(item_b, "Owner") or "unknown owner"
            lines.append(
                "- **{0}** (owner: {1}) and **{2}** (owner: {3}) look similar (score {4:.2f})".format(
                    item_a.get("name", "Untitled project"), owner_a,
                    item_b.get("name", "Untitled project"), owner_b, score,
                )
            )
    else:
        lines.append("No overlap above the dedup threshold.")
    lines.append("")

    return "\n".join(lines)


def fetch_board_items(board_id, token):
    """Fetch a board's items from Monday's API. The only function that touches the network."""
    query = (
        "query { boards(ids: %s) { items_page(limit: 500) { items { "
        "id name updated_at description "
        "column_values { column { title } text } } } } }" % json.dumps(str(board_id))
    )
    payload = json.dumps({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        MONDAY_API_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not reach Monday's API. Check your internet connection and try again."
        ) from exc

    if "errors" in body:
        raise RuntimeError(
            "Monday's API rejected the request. Double check your board id and API token."
        )

    boards = body.get("data", {}).get("boards") or []
    if not boards:
        raise RuntimeError(
            "No board found with id {0}. Double check the board id.".format(board_id)
        )
    return boards[0].get("items_page", {}).get("items", [])


def _read_token():
    token = os.environ.get("MONDAY_API_TOKEN")
    if not token:
        raise SystemExit(
            "Missing MONDAY_API_TOKEN. Set it to your Monday API token and try again."
        )
    return token


def _load_items(args):
    if args.fixture:
        with open(args.fixture, "r", encoding="utf-8") as f:
            return json.load(f)
    if not args.board:
        raise SystemExit(
            "Missing --board. Pass your Monday board id, or use --fixture for a local file."
        )
    token = _read_token()
    return fetch_board_items(args.board, token)


def _cmd_digest(args):
    items = _load_items(args)
    now = datetime.now(timezone.utc)
    digest = build_digest(
        items, now, cadence=args.cadence, stale_days=args.stale_days, threshold=args.dedup_threshold
    )
    print(digest)


def _cmd_dedup(args):
    items = _load_items(args)
    if not items:
        print("No projects on the board yet.")
        return
    duplicates = find_duplicates(items, args.dedup_threshold)
    if not duplicates:
        print("No possible duplicates above the dedup threshold.")
        return
    for item_a, item_b, score in duplicates:
        print("{0} <-> {1} (score {2:.2f})".format(item_a["name"], item_b["name"], score))


def _add_common_args(subparser):
    subparser.add_argument("--board", help="Monday board id")
    subparser.add_argument(
        "--dedup-threshold", type=float, default=0.35,
        help="Similarity threshold for flagging duplicates (default 0.35)",
    )
    # Hidden: lets tests and demos run fully offline against a JSON file
    # shaped like fetch_board_items' return value, instead of --board.
    subparser.add_argument("--fixture", help=argparse.SUPPRESS)


def build_parser():
    parser = argparse.ArgumentParser(prog="wbw.py", description="who-builds-what registry tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    digest_parser = subparsers.add_parser("digest", help="Render the manager digest as markdown")
    _add_common_args(digest_parser)
    digest_parser.add_argument(
        "--cadence", choices=["daily", "weekly"], default="weekly", help="Digest cadence (default weekly)"
    )
    digest_parser.add_argument(
        "--stale-days", type=int, default=60,
        help="Days without an update before a project counts as stale (default 60)",
    )
    digest_parser.set_defaults(func=_cmd_digest)

    dedup_parser = subparsers.add_parser("dedup", help="List possible duplicate projects")
    _add_common_args(dedup_parser)
    dedup_parser.set_defaults(func=_cmd_dedup)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except RuntimeError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
