# Miss Maya — PeerUp's AI English-tutor prototype

A Flask chat prototype for **Miss Maya**, the AI English-tutor character built by [PeerUp](https://www.peerup.com). All chat, output review, and memory-write paths run on **Qwen 32B via AWS Bedrock** (`qwen.qwen3-32b-v1:0`). No Anthropic models, no CLI fallbacks.

> Status: prototype. Reference for the production app, not a deploy target.

---

## What's in here

| URL | Purpose |
| --- | --- |
| `/` | Production-shape chat. Audio-style call surface with avatar video + TTS. |
| `/playground` | Sandbox for memory + prompt experiments. Isolated storage. |
| `/qwen-lab` | A/B prompt comparison (left = baseline prompts, right = active Qwen-tuned set). |

Plus admin: `/prompts`, `/playground/prompts`, `/playground/docs`, `/settings`, `/evals`.

---

## Quick start

```bash
git clone <this-repo-url>
cd peerup-prototype
cp .env.example .env
# fill in AWS_BEARER_TOKEN_BEDROCK (12-hour scoped token for Bedrock)
./run.sh
```

Visit `http://localhost:5050`. Pick a profile, click **Start chat**.

---

## Architecture in one paragraph

Each user has one JSON file on disk (`memory_store/<slug>.json`) holding 11 buckets of memory: facts, dated events, emotionally weighted moments, mood log, repetition cooldown, inside jokes, pre-cooked openers, English skill patterns, Maya's revealed self, open conversational loops, user-set preferences. Every chat turn renders the file into a natural-language block injected into Maya's system prompt. Maya's reply runs through a single Qwen-based **output judge** (`judge_guard.py`) that may rewrite the reply against 10 rules. After `/end_session`, a separate **librarian** Qwen call reads the transcript + memory and writes a JSON patch back. Both judge and librarian are Qwen — there are no Anthropic models in the live path.

---

## The 8 prompts in production

All eight live in `final_prompts/` (extracted from `app.py` + `judge_guard.py` for easy reading). Source of truth is still the constants in those two files.

| File | Role | When |
| --- | --- | --- |
| `final_prompts/1_system_prompt.md` | Maya persona + rules 1-28 | Every chat turn |
| `final_prompts/2_extra_rules.md` | Rules 29-37 (emotional thread, mood, cooldown, lore, etc.) | Every chat turn |
| `final_prompts/3_avatar_prompt.md` | Maya's character description | Every chat turn |
| `final_prompts/4_first_message_returning_user.md` | Opening turn for returning users | Session start, has memory |
| `final_prompts/5_first_message_new_user.md` | Opening turn for brand-new users | Session start, no memory |
| `final_prompts/6_session_summary.md` | Rolling-summary compression | Background, > WINDOW_SIZE messages |
| `final_prompts/7_librarian_memory_merge.md` | Writes JSON patch to memory | On `/end_session` |
| `final_prompts/8_output_judge.md` | Reviews + rewrites every Maya reply | Before reply ships to user |

---

## The output judge (replaces 12 regex guards)

`judge_guard.py` runs one Qwen Bedrock call per Maya reply. Returns structured JSON: `{verdict, violations_found, rewritten_reply, confidence}`. If verdict is "rewrite" with confidence ≥ 0.7, the rewritten reply ships to the user; otherwise the original ships.

Pre-flight gating: `judge_preflight.py` runs the judge against `judge_test_set.json` (40 cases, 30 violations + 10 benign). Required ≥90% recall, ≤10% FP. The current prompt passes at 100% recall on intent rules. Mechanical rules (em-dash, multi-question) have a hard ceiling on Qwen 32B — see `memory_store/_eval_50/reports/judge_vs_regex_*.pdf` for the honest eval.

---

## Date-aware additive openers

When a returning user opens a session, `pg_select_date_trigger()` checks for:
1. Birthday today / tomorrow / yesterday (`facts.birthday`)
2. Anniversary today / tomorrow / yesterday (`facts.anniversary`)
3. Stored event with date today / tomorrow / 1-3 days ago

At most one trigger per session (priority: birthday > anniversary > event). If a trigger fires, an additive instruction is injected into the memory block — Maya wishes / acknowledges / asks-how-it-went, AND continues with her usual question. After the reply ships, `pg_mark_acknowledgement()` records the trigger in `mem.acknowledgements` so a same-day reopen doesn't repeat the wish. Birthdays/anniversaries are stored as `MM-DD` for year-rolling; events use full `YYYY-MM-DD`.

---

## The 11 memory buckets

| Bucket | Holds | Lifecycle |
| --- | --- | --- |
| `facts` | Timeless truths (name, profession, family, hometown, birthday, anniversary). | Forever. Name overwrite-protected. |
| `events` | Dated things (exams, weddings, matches). | Auto-archive 14 days after the date. |
| `moments` | Emotionally weighted statements (no date). | Persist. Dedupe + bump `mentions`. |
| `mood_log` | One mood reading per session. | Last 14 entries. |
| `cooldown` | Recent topics + opener kinds. | FIFO buffers (12 / 10 / 6). |
| `lore` | Inside jokes Maya + user share. | Up to 30. |
| `anticipation_queue` | Pre-cooked openers Maya plans for next time. | Up to 5. TTL 14 days. |
| `skills` | English error patterns + wins + current focus. | Up to 20 errors / 30 wins. |
| `maya_persona` | Maya's character + revealed self. | Decoration only. Never claims biography. |
| `open_loops` | Threads either party said they'd come back to. | Up to 12. Auto-expire 30 days. |
| `meta_preferences` | User-set knobs (correction style, reply length, humor, off-limits). | Hard override. User's word is law. |
| `acknowledgements` | Date-trigger anti-spam (per-trigger last-fired date). | Indefinite, small. |

Open a chat → `📦 My memory` for the live in-app inspector.

---

## Eval harness

The `eval_50.py` script runs a 50-session synthetic conversation suite across five tiers: same-day, consecutive-day, sporadic-gap, cold-start, deep-run. Output goes to `memory_store/_eval_50/`. Scoring + comparison reports:

```bash
./.venv/bin/python run_judge_eval.py        # run 50 sessions into validation_judge_only/
./.venv/bin/python score_judge_run.py       # score vs the regex baseline
./.venv/bin/python eval_50_judge_report.py  # generate the comparison PDF
```

Latest comparison: `memory_store/_eval_50/reports/judge_vs_regex_<ts>.pdf`.

---

## Project structure

```
.
├── app.py                       # Flask app; all routes + prompts + memory logic
├── judge_guard.py               # Qwen output-judge layer (replaces regex guards)
├── judge_preflight.py           # Pre-flight gate for the judge
├── judge_test_set.json          # 40 curated judge test cases
├── final_prompts/               # The 8 active prompts, one per file
├── eval_50.py                   # 50-session synthetic eval harness
├── eval_50_judge_report.py      # PDF comparison report generator
├── score_judge_run.py           # Categorical scoring of a transcript folder
├── run_judge_eval.py            # Wrapper: 50-session run into isolated dir
├── requirements.txt
├── run.sh
├── .env.example                 # Copy to .env and fill AWS_BEARER_TOKEN_BEDROCK
├── templates/
├── static/peerup/               # Avatar video + UI assets
├── voices/                      # Pre-rendered TTS samples (gitignored, ~120MB)
└── memory_store/                # Per-user JSON memory + session summaries
    ├── <user>.json              # Prod memory
    ├── _playground/             # Playground sandbox (isolated)
    ├── _qwen_lab/               # A/B lab (split per side)
    └── _eval_50/                # Eval transcripts + reports
```

---

## Sharing the running app

```bash
brew install ngrok
ngrok config add-authtoken <your-token>
./run.sh                         # one terminal
ngrok http 5050                  # another — gives a public URL
```

Werkzeug debugger is off by default. Don't post the URL widely — there's no auth.

---

## Contributing

This is a prototype that lives next to the production app. Two things to know:

1. **Don't change the prompts directly.** Use `/playground/prompts` (or the in-memory `QWEN_*` constants for the lab) so changes are scoped to one sandbox at a time.
2. **The librarian + judge prompts are the highest-leverage things in the codebase.** Tweaks here ripple across every user. Test in the playground for a few sessions, then run the 50-session eval before promoting.

For the deepest dive: open `/playground/docs` while the app is running.

---

## License

No license file. Default copyright applies. Reference code, not for fork-and-deploy.
