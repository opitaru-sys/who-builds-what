#!/usr/bin/env python3
"""Build the who-builds-what registry board on Monday.com in one command.

Standard library only. Creates a board with the registry columns, and with
--demo also loads five fictional example projects so the board demos itself.

Usage:
    python scripts/setup_board.py --name "AI Project Registry" --private
    python scripts/setup_board.py --demo --dry-run

Requires MONDAY_API_TOKEN in the environment (Monday: avatar menu, Developers,
My access tokens). The token never leaves your machine except to Monday's API.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

MONDAY_API_URL = "https://api.monday.com/v2"

STATUS_LABELS = {"1": "idea", "2": "building", "3": "in use", "4": "retired"}
AWARE_LABELS = {"1": "yes", "2": "no", "3": "pending"}

COLUMNS = [
    ("Owner", "text", None),
    ("Team", "text", None),
    ("Status", "status", {"labels": STATUS_LABELS}),
    ("Tools & models", "dropdown", None),
    ("Data it touches", "dropdown", None),
    ("Manager aware", "status", {"labels": AWARE_LABELS}),
    ("Last updated", "last_updated", None),
]

DEMO_ITEMS = [
    {
        "name": "Churn summary bot",
        "Owner": "Alice Chen",
        "Team": "Customer Success",
        "Status": "in use",
        "Tools & models": ["Claude", "Make"],
        "Data it touches": ["customer emails", "support tickets"],
        "Manager aware": "yes",
    },
    {
        "name": "Customer churn digest agent",
        "Owner": "Marcus Webb",
        "Team": "Sales Ops",
        "Status": "building",
        "Tools & models": ["GPT", "Zapier"],
        "Data it touches": ["sales pipeline", "customer emails"],
        "Manager aware": "yes",
    },
    {
        "name": "Meeting notes summarizer",
        "Owner": "Priya Patel",
        "Team": "Product",
        "Status": "in use",
        "Tools & models": ["Claude"],
        "Data it touches": ["internal docs"],
        "Manager aware": "no",
    },
    {
        "name": "Support ticket triager",
        "Owner": "Jordan Lee",
        "Team": "Support",
        "Status": "idea",
        "Tools & models": ["GPT"],
        "Data it touches": ["support tickets"],
        "Manager aware": "pending",
    },
    {
        "name": "Sales call transcriber",
        "Owner": "Sam Okafor",
        "Team": "Sales Ops",
        "Status": "in use",
        "Tools & models": ["Whisper", "Claude"],
        "Data it touches": ["call recordings"],
        "Manager aware": "yes",
    },
]


def api(query, token, dry_run=False):
    if dry_run:
        print("DRY RUN:", query)
        return {}
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
        raise SystemExit(
            "Could not reach Monday's API. Check your internet connection."
        ) from exc
    if "errors" in body:
        raise SystemExit(
            "Monday's API rejected a request: {0}".format(
                body["errors"][0].get("message", "unknown error")
            )
        )
    return body.get("data", {})


def gq_string(value):
    return json.dumps(value)


def create_board(name, private, token, dry_run):
    kind = "private" if private else "public"
    data = api(
        "mutation {{ create_board (board_name: {0}, board_kind: {1}) {{ id }} }}".format(
            gq_string(name), kind
        ),
        token,
        dry_run,
    )
    if dry_run:
        return "DRY_BOARD_ID"
    return data["create_board"]["id"]


def create_columns(board_id, token, dry_run):
    ids = {}
    for title, column_type, defaults in COLUMNS:
        defaults_part = ""
        if defaults:
            defaults_part = ", defaults: {0}".format(gq_string(json.dumps(defaults)))
        data = api(
            "mutation {{ create_column (board_id: {0}, title: {1}, column_type: {2}{3}) {{ id }} }}".format(
                board_id, gq_string(title), column_type, defaults_part
            ),
            token,
            dry_run,
        )
        if dry_run:
            ids[title] = "DRY_" + title.lower().replace(" ", "_").replace("&", "and")
        else:
            ids[title] = data["create_column"]["id"]
    return ids


def create_demo_items(board_id, column_ids, token, dry_run):
    for item in DEMO_ITEMS:
        values = {
            column_ids["Owner"]: item["Owner"],
            column_ids["Team"]: item["Team"],
            column_ids["Status"]: {"label": item["Status"]},
            column_ids["Tools & models"]: {"labels": item["Tools & models"]},
            column_ids["Data it touches"]: {"labels": item["Data it touches"]},
            column_ids["Manager aware"]: {"label": item["Manager aware"]},
        }
        api(
            "mutation {{ create_item (board_id: {0}, item_name: {1}, column_values: {2}, create_labels_if_missing: true) {{ id }} }}".format(
                board_id, gq_string(item["name"]), gq_string(json.dumps(values))
            ),
            token,
            dry_run,
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the registry board on Monday")
    parser.add_argument("--name", default="AI Project Registry", help="Board name")
    parser.add_argument(
        "--private", action="store_true",
        help="Create as a private board (visible only to you) instead of public",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Load five fictional example projects after creating the board",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the API calls without sending anything",
    )
    args = parser.parse_args(argv)

    token = os.environ.get("MONDAY_API_TOKEN", "")
    if not token and not args.dry_run:
        raise SystemExit(
            "Missing MONDAY_API_TOKEN. Set it to your Monday API token and rerun."
        )

    board_id = create_board(args.name, args.private, token, args.dry_run)
    print("Board created: id {0}".format(board_id))
    column_ids = create_columns(board_id, token, args.dry_run)
    print("Columns created: {0}".format(", ".join(title for title, _, _ in COLUMNS)))
    if args.demo:
        create_demo_items(board_id, column_ids, token, args.dry_run)
        print("Demo projects loaded: {0}".format(len(DEMO_ITEMS)))
    print(
        "Done. Open the board in Monday, add a Form view (WorkForms) if you "
        "want form registrations, and you are live."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
