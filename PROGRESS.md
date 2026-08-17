# who-builds-what: progress

Free public tool: AI-project registry for orgs on Monday.com. An AI interview
(3 min) replaces the registration form, optional "grill" stress-test, dedup
check, manager digest at configurable cadence. Spec: docs/spec-2026-08-17.md.
Plan: docs/plan-2026-08-17.md.

## Done (verified 17 Aug 2026)

- Interview prompt (prompts/interview.md): quick six + optional five-area
  grill, no-secrets rule. Written by hand, Dana-proof language.
- Claude Code skill (skill/register-ai-project/SKILL.md): interview + dedup
  check against board + create item via Monday API + grill.
- wbw.py: digest + dedup subcommands, 3 config flags (--cadence daily|weekly,
  --stale-days 60, --dedup-threshold 0.35), hidden --fixture for offline runs.
  8/8 tests green (python -m unittest discover tests -v), network isolated to
  fetch_board_items, stdlib only. CI action in .github/workflows/test.yml.
- scripts/setup_board.py: one-command board build (--private --demo
  --dry-run). Dry-run verified; NOT yet run against a live board.
- README.md: hook first, column-list deploy primary (template link removed
  deliberately), trust section, honest scope, platforms-on-demand v2 note.
- examples/: 5 fictional projects (Alice/Marcus churn duplicate pair, Priya's
  unapproved item, one stale) + sample-digest.md.
- All committed locally. NO remote yet.
- Demo board LIVE (17 Aug, via the Monday connector, which now exposes the
  full create toolkit): board id 18426874150, private, Overwolf Monday,
  https://theoverwolf.monday.com/boards/18426874150. 7 columns + 5 demo items
  verified by reading the board back. Connector gotcha: create_column status
  settings need {labels: [{label, color, index}]}, not the raw API's
  index-keyed map. setup_board.py stays as the self-serve door for users.

## 17 Aug, second pass: launch state

- Board approved by Omri ("looks good").
- Live smoke test of wbw.py WAIVED by Omri ("assume it works"). Unverified
  against a live board; fixture-tested only. If a user reports a digest bug,
  start here.
- Repo PUBLIC at github.com/opitaru-sys/who-builds-what (his call, 17 Aug).
- Launch order: LinkedIn first. Drafts in
  seed-agent/writing-desk/wbw-launch-posts.md; reddit sub and screenshot
  decision still open.

## Next (original plan, kept for reference)

1. Build the demo board: private, in Omri's Overwolf Monday (his call, made
   knowingly). Preferred door: the Monday CONNECTOR once it exposes create
   tools (as of 17 Aug it exposes ONLY update_column; Omri changed connector
   settings; a NEW session may see the full toolkit - check ToolSearch for
   create_board/create_item/get_board_schema first). Fallback door:
   scripts/setup_board.py --private --demo with MONDAY_API_TOKEN that Omri
   sets himself (token is NOT on disk: BP Workspace encrypts it via
   safeStorage per its ADR 0013; do not hunt for it, the classifier blocks
   .env probing and rightly).
2. Smoke-test wbw.py digest --board <new id> against the live board.
3. Screenshots of board + form. STANDING CAVEAT: screenshots from the
   Overwolf workspace are decision-material only; before public use, re-shoot
   from a personal Monday account or scrub workspace chrome. Omri decides.
4. Push repo to github.com/opitaru-sys/who-builds-what PRIVATE; Omri flips
   public after review.
5. Draft launch posts (LinkedIn + reddit), hook: "ever had two people build
   the same project without their manager knowing?" Image via Omri's ChatGPT
   pipeline. Voice per his rules; claim discipline: OWASP = "submitted, PR
   pending review".

## Decided, do not reopen

- Monday-first, NOT a GitHub-template product (his catch: non-technical
  companies have no GitHub accounts). Other platforms only on public demand.
- Quick intake + optional grill (registries die of friction).
- Config surface is exactly the three flags. No more.
- Free tool = reputation asset, not a business. Weekend scope, then stop.
- Grill questions written fresh; no employer-framework text imported.
