# Board setup guide

Ten minutes in Monday, once, by whoever keeps the registry. Or thirty seconds:

```bash
MONDAY_API_TOKEN=your_token python scripts/setup_board.py --private --demo
```

builds the whole board for you (`--demo` adds five fictional projects so it
demos itself; `--dry-run` shows the API calls without sending; drop
`--private` for a workspace-visible board). The script uses Dropdown columns
where the manual list says Tags; both work, dropdowns are what the API can
seed with values.

## Columns

Create a board named "AI Project Registry" with these columns, in this order:

| Column | Type | Values / notes |
|---|---|---|
| Project name | Item name | built-in first column |
| Owner | Person | falls back to Text if registering non-Monday users |
| Team | Text | or Dropdown with your team list |
| Status | Status | idea / building / in use / retired |
| Tools & models | Tags | free tags, e.g. Claude, GPT, Make, n8n |
| Data it touches | Tags | categories only, e.g. customer emails, internal docs, public data |
| Manager aware | Status | yes / no / pending |
| Created | Creation log | automatic |
| Last updated | Last updated | automatic |

Recommended views: main table grouped by Team; a "Needs approval" filtered view
(Manager aware is not yes); a "By status" board view.

## The form

Open the board's Form view (WorkForms), include: Project name, Owner (as text
if respondents lack Monday seats), Team, Status, Tools & models, Data it
touches, Manager aware, and one long-text question labeled Description. Enable
the shareable link. That link is what non-technical registrants use after the
interview.

## Template sharing

Board menu, Save as template (or duplicate per org). If you publish a public
template link, paste it into README.md where the placeholder marks it.

## For the Claude Code skill and the script

- API token: Monday, avatar menu, Developers, My access tokens, copy.
- Board id: the number in the board's URL after /boards/.
- Set both in the environment: `MONDAY_API_TOKEN`, `WBW_BOARD_ID`.

## Monday-native extras (no script needed)

- Automation: "When Last updated is more than 60 days ago, notify board owner"
  covers stale nudges.
- Automation: "When Manager aware changes to no, notify board owner" gives
  real-time flags between digests.
