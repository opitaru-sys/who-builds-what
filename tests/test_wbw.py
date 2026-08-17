"""Tests for wbw.py. All offline: no network calls are made anywhere here."""

import json
import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wbw

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "board_fixture.json")

# Matches the fixture's "now": 2026-08-17T08:00:00Z is 4 hours old, well inside
# both the daily (1 day) and weekly (7 day) windows; 2026-01-15 is far outside both.
NOW = datetime(2026, 8, 17, 12, 0, 0, tzinfo=timezone.utc)


def load_fixture():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def section(digest, heading):
    """Return the text of one '## heading' section of a digest, for scoped assertions."""
    lines = digest.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## " + heading or line.strip().startswith("## " + heading):
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end])


class TestTokenize(unittest.TestCase):
    def test_tokenize_normalizes(self):
        tokens = wbw.tokenize("The Churn-Summary Bot, using AI!")
        self.assertEqual(tokens, {"churn", "summary"})


class TestSimilarity(unittest.TestCase):
    def test_similarity_identical_is_1(self):
        a = wbw.tokenize("Sales call transcriber for the sales team")
        b = wbw.tokenize("Sales call transcriber for the sales team")
        self.assertEqual(wbw.similarity(a, b), 1.0)

    def test_similarity_disjoint_is_0(self):
        a = wbw.tokenize("Meeting notes summarizer")
        b = wbw.tokenize("Support ticket triager")
        self.assertEqual(wbw.similarity(a, b), 0.0)


class TestFindDuplicates(unittest.TestCase):
    def test_find_duplicates_flags_churn_pair_only(self):
        items = load_fixture()
        duplicates = wbw.find_duplicates(items, threshold=0.35)
        self.assertEqual(len(duplicates), 1)
        a, b, score = duplicates[0]
        names = {a["name"], b["name"]}
        self.assertEqual(names, {"Churn summary bot", "Customer churn digest agent"})
        self.assertGreaterEqual(score, 0.35)


class TestBuildDigest(unittest.TestCase):
    def setUp(self):
        self.items = load_fixture()

    def test_digest_lists_unapproved(self):
        digest = wbw.build_digest(self.items, NOW, cadence="weekly", stale_days=60, threshold=0.35)
        approval_section = section(digest, "Needs approval")
        self.assertIn("Meeting notes summarizer", approval_section)
        self.assertIn("Manager aware: no", approval_section)
        # Approved projects should not show up here.
        self.assertNotIn("Churn summary bot", approval_section)

    def test_digest_flags_stale_by_threshold(self):
        digest_default = wbw.build_digest(self.items, NOW, cadence="weekly", stale_days=60, threshold=0.35)
        stale_section = section(digest_default, "Stale")
        self.assertIn("Support ticket triager", stale_section)
        self.assertNotIn("Churn summary bot", stale_section)

        # With a much longer stale window, nothing should qualify.
        digest_lenient = wbw.build_digest(self.items, NOW, cadence="weekly", stale_days=3650, threshold=0.35)
        lenient_section = section(digest_lenient, "Stale")
        self.assertNotIn("Support ticket triager", lenient_section)

    def test_digest_cadence_window_daily_vs_weekly(self):
        daily = wbw.build_digest(self.items, NOW, cadence="daily", stale_days=60, threshold=0.35)
        weekly = wbw.build_digest(self.items, NOW, cadence="weekly", stale_days=60, threshold=0.35)

        daily_new = section(daily, "New since")
        weekly_new = section(weekly, "New since")

        # Updated ~5 days ago: inside the weekly window, outside the daily one.
        self.assertNotIn("Customer churn digest agent", daily_new)
        self.assertIn("Customer churn digest agent", weekly_new)

        # Updated a few hours ago: inside both windows.
        self.assertIn("Churn summary bot", daily_new)
        self.assertIn("Churn summary bot", weekly_new)

    def test_digest_empty_board_friendly(self):
        digest = wbw.build_digest([], NOW, cadence="weekly", stale_days=60, threshold=0.35)
        self.assertIn("No projects on the board yet", digest)


if __name__ == "__main__":
    unittest.main()
