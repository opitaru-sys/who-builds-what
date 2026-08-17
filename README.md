# who-builds-what

**Ever had two people build the same AI project without their manager knowing?**

Most companies have more AI projects than anyone can name. People build agents,
automations, and tools inside their teams; nobody registers anything, work gets
duplicated, and managers find out about projects by accident. Forms don't fix
it because nobody fills forms.

who-builds-what is a free kit that fixes the reporting half of the problem:

- **A Monday.com board** is the registry: one item per AI project, visible to
  everyone who should see it, in the tool your company already uses.
- **A 3-minute AI interview** replaces the registration form. People talk to
  the AI assistant they already use; it asks six questions and files the
  answers. There is also an optional "grill": ten minutes of harder questions
  that stress-test a project before a manager sees it.
- **A small script** flags projects that look like duplicates and writes a
  manager digest at whatever cadence you choose: what's new, what has no
  manager sign-off, what went quiet.

No servers, no accounts, no vendor. You own everything.

## Deploy in three steps

1. **Create the registry board.** Duplicate the template board
   <!-- TEMPLATE LINK: Omri --> or build it yourself in ten minutes from the
   column list in [docs/board-setup.md](docs/board-setup.md). Turn on the
   board's form (WorkForms) and keep the field order as listed.
2. **Share two links** with your company: the form link (for registering) and
   the board link (for browsing). Board permissions are your call; the
   registry maps your internal projects, so share it as widely as the
   portfolio should be seen, and no wider.
3. **Tell people the magic sentence:** "ask your AI to interview you, then
   paste the answers into the form." Send them
   [prompts/interview.md](prompts/interview.md). Claude Code users can skip
   the form entirely: install the skill from
   [skill/register-ai-project](skill/register-ai-project) and say "register
   my AI project"; it files the item directly.

## The digest

`wbw.py` is one Python file, standard library only, nothing to install.

```bash
python wbw.py digest --board YOUR_BOARD_ID
python wbw.py dedup --board YOUR_BOARD_ID
```

Set `MONDAY_API_TOKEN` in your environment (Monday: avatar menu, Developers,
My access tokens). Three knobs, nothing else:

| Flag | Default | Meaning |
|---|---|---|
| `--cadence daily\|weekly` | weekly | the "new since" window of the digest |
| `--stale-days N` | 60 | when a quiet project counts as stale |
| `--dedup-threshold F` | 0.35 | how similar two projects must be to get flagged |

Run it by hand, from cron, from Make, or from the included GitHub Action
example, and paste the output into Slack or mail. Stale-project nudges can
also be done with Monday's own automations if you prefer clicks to scripts.

A sample of what the digest looks like: [examples/sample-digest.md](examples/sample-digest.md).

## Where your data goes

- Entries live in your Monday account. Nowhere else.
- The interview runs on your own AI accounts, under your existing terms with
  that provider. This kit adds no new AI dependency.
- The script calls only Monday's API with your token. It has zero other
  network I/O; the file is short, read it yourself.
- No telemetry, no phone-home. Nothing reaches the author of this kit.
- The interview records data categories, never actual data, keys, or personal
  details, and is instructed to refuse them if offered.

## Honest scope

This solves the self-reporting half of the problem: the interview makes
reporting cost three minutes instead of a form nobody fills. It does not scan
your network, read your repos, or discover projects nobody mentions. That half
belongs to your culture; this kit just makes the honest path the easy one.

## Other platforms

Monday-first, by design. Want this for Notion, Google Sheets, or something
else? Open an issue: adapters get built by demand, and the schema is six
fields, so ports are small.

MIT licensed. Built by [Omri Pitaru](https://www.linkedin.com/in/omripitaru).
