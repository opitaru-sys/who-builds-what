---
name: register-ai-project
description: Register an AI project in the company's who-builds-what registry on Monday.com. Use when the user says "register my AI project", "add my project to the registry", or asks to log an AI tool, agent, or automation they are building.
---

# Register an AI project

You interview the user about the AI project they are building, check the
registry for lookalikes, and file the entry on the company's Monday board.
Three minutes for them, one board item from you.

## Step 0: config

Read two values from the environment: `MONDAY_API_TOKEN` and `WBW_BOARD_ID`.

If either is missing, stop and tell the user, in plain words: the API token
comes from Monday (avatar menu, Developers, My access tokens), and the board id
is the number in the registry board's URL. Suggest they ask their registry
keeper, then stop. Do not improvise storage anywhere else.

## Step 1: the interview

Ask these ONE at a time, waiting for each answer. Keep the user's own words for
the description. Warm and quick, a colleague asking, not an audit.

1. What are you building, in one or two sentences?
2. Who is it for, and who owns it going forward (you, your team, someone else)?
3. What tools and models does it use?
4. What data does it touch? Categories only, for example: customer emails,
   internal docs, sales pipeline, public data.
5. Does your manager know about this project? (yes / no / partially)
6. Where does it stand right now? (idea / building / in use)

Data safety rule, non-negotiable: record data CATEGORIES only, never actual
data, credentials, keys, or personal details. If the user pastes any of those,
do not repeat them; say you'll record the category, not the data itself.

Propose a short project name from their description and confirm it.

## Step 2: check for lookalikes

Before creating anything, query the board:

POST https://api.monday.com/v2 with header `Authorization: <MONDAY_API_TOKEN>`
and body:

```json
{"query": "query { boards(ids: [BOARD_ID]) { items_page(limit: 500) { items { id name column_values { column { title } text } } } } }"}
```

Compare the new project's name and description words against existing item
names and texts. If any existing item shares several meaningful words, ask the
user: "This looks close to '<item name>'. Same thing, or different?" Record
their answer at the end of the description ("Checked against <item>: different
because ..."). If they say it IS the same thing, do not create a duplicate;
suggest they talk to that item's owner, and stop.

## Step 3: create the item

Create the item with a GraphQL mutation. First fetch the board's columns
(`boards(ids:[...]) { columns { id title type } }`) and map by TITLE to find
the column ids for: Owner, Team, Status, Tools & models, Data it touches,
Manager aware. Then:

```json
{"query": "mutation { create_item (board_id: BOARD_ID, item_name: \"PROJECT NAME\", column_values: \"{ ...mapped values as JSON... }\") { id } }"}
```

Set values for every column you have an answer for; skip columns the board
does not have rather than failing. Then post the description as an update on
the created item (`create_update`), so the user's own words live on the item.

## Step 4: offer the grill

Offer exactly: "Want the full grill? Ten more minutes of harder questions that
stress-test the project. Useful before you show it to your manager. Totally
optional."

If yes: relentless but friendly, one question at a time, offer your recommended
answer with each question. Five areas, one honest follow-up each if the answer
is vague:

1. Duplication: who else in the company would plausibly have built this or
   need it? Have you checked?
2. Data exposure: what is the worst realistic mishandling of the data this
   touches? Who would care?
3. Continuity: who runs this when you are on leave? Where do the instructions
   live?
4. Kill criteria: what result or cost would make you shut it down? Would you
   notice?
5. Cost: what does this cost monthly, in tools and in your hours? Is that
   visible to anyone?

Post the five-line "Grill notes" as a second update on the item.

## Step 5: report back

Give the user the item's URL (https://COMPANY.monday.com/boards/BOARD_ID/pulses/ITEM_ID
works; if you cannot determine the company slug, give the board URL and item
name), confirm what was filed, and remind them their manager will see it in
the next digest. Done.
