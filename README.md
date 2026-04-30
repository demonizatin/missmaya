# Miss Maya — PeerUp's AI English-tutor prototype

A Flask-based chat prototype for **Miss Maya**, the AI English-tutor character built by [PeerUp](https://www.peerup.com). This repo is the experimental playground where new prompts, memory-architecture changes, and model integrations are tested before they ship to the production app.

> **Status**: prototype. Not the production codebase. Use it as a reference, not a deploy target.

---

## What's in here

Three chat surfaces, each with a different purpose:

| URL | Purpose |
| --- | --- |
| **`/`** | Production-shape chat. Audio-style call surface with avatar video + TTS. The "real product" simulator. |
| **`/playground`** | Sandbox for memory experiments. Same chat flow, but isolated storage so prod data never gets touched. Where new memory buckets / merge logic / prompt edits get tested first. |
| **`/qwen-lab`** | A/B prompt comparison sandbox. Runs the same user input through two prompt sets in parallel — existing prompts on the left, Qwen-tuned rewrites on the right — both pinned to Qwen 32B on Bedrock. |

Plus admin pages: `/prompts`, `/playground/prompts`, `/playground/docs`, `/settings`, `/evals`.

---

## Quick start (0 → 1)

### 1. Clone and enter the repo

```bash
git clone <this-repo-url>
cd peerup-prototype
```

### 2. Configure secrets

```bash
cp .env.example .env
# open .env in your editor and fill in either:
#   - ANTHROPIC_API_KEY      (for Anthropic API calls), AND/OR
#   - AWS_BEARER_TOKEN_BEDROCK or AWS_ACCESS_KEY_ID + SECRET   (for Bedrock)
# At least one backend must be configured. Bedrock is the default for Qwen 32B.
```

### 3. (Optional) Install the Claude CLI

If you want a third backend option that uses your Claude subscription instead of API metering:

```bash
# macOS
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

The CLI is detected at runtime; if absent, the app falls back to API or Bedrock.

### 4. Run

```bash
./run.sh
```

This creates a Python venv, installs `requirements.txt`, and starts Flask on port 5050. Visit:

- **http://localhost:5050** — production-shape chat
- **http://localhost:5050/playground** — playground sandbox
- **http://localhost:5050/qwen-lab** — A/B prompt comparison
- **http://localhost:5050/playground/docs** — full architecture documentation

### 5. Send your first message

1. Pick a profile from the welcome screen.
2. Click **Start chat**.
3. Maya should reply within a few seconds. Stream is SSE; tokens arrive incrementally.

If Maya doesn't reply, check the browser console and the terminal running `./run.sh` — almost always a missing API key or Bedrock credential.

---

## Architecture in one paragraph

Each user has **one JSON file** on disk (`memory_store/<slug>.json`) holding 11 buckets of memory: facts, dated events, emotionally weighted moments, per-session mood log, repetition cooldown, inside jokes, pre-cooked openers, English skill patterns, Maya's revealed self, open conversational loops, and user-set preferences. On every chat turn, the file is read and rendered into a natural-language block injected into Maya's system prompt. After the user ends the session, a separate "librarian" LLM call reads the transcript + current memory and writes a JSON patch back to the file — that's how memory persists across sessions.

The model that powers Maya is selectable per-session: **Qwen 32B on AWS Bedrock** (default), Anthropic's **Sonnet 4.6** or **Haiku 4.5** via API, or Claude via the local **Claude CLI** subscription. Backend choice doesn't affect memory architecture — every backend reads from and writes to the same JSON files.

For a deep dive: open **`/playground/docs`** while the app is running.

---

## The 7 prompts

Every chat turn assembles its prompt from these constants (all in `app.py`):

| Constant | Role | Where it fires |
| --- | --- | --- |
| `SYSTEM_PROMPT_TEMPLATE` | Rules 1–28: tone, corrections, output format | Every turn (system role) |
| `PG_EXTRA_RULES` | Rules 29–37: emotional thread, mood, cooldown, lore, persona, open loops, user prefs | Every turn (spliced into system prompt) |
| `AVATAR_PROMPT` | Maya's character description | Every turn (interpolated into Rule 1) |
| `FIRST_MESSAGE_TEMPLATE` | First-turn user-message wrapper for **returning users** | Session start, returning |
| `GENERIC_FIRST_MESSAGE_TEMPLATE` | First-turn wrapper for **brand-new users** | Session start, no memory |
| `SESSION_SUMMARY_PROMPT` | Background rolling-summary compression | After ~30 messages, lazy |
| `PG_MEMORY_MERGE_PROMPT` | The librarian — returns a JSON patch | On `End chat` |

A Qwen-tuned rewrite of all 7 (named `QWEN_*`) lives alongside the originals and is served by the **`/qwen-lab`** A/B surface. Click **📋 View final Qwen prompts** on the lab welcome screen → **⬇ Download all (.zip)** to grab them with integration instructions.

---

## The 11 memory buckets

| Bucket | What it holds | Lifecycle |
| --- | --- | --- |
| `facts` | Timeless truths (name, profession, family, hometown, interests). | Forever, until contradicted. Name is overwrite-protected. |
| `events` | Dated things (exams, weddings, matches). | Auto-archive 14 days after the date. |
| `moments` | Emotionally weighted statements (no date). | Persist long-term. Dedupe + bump `mentions`. |
| `mood_log` | One mood reading per session. | Last 14 entries. FIFO. |
| `cooldown` | Topics + opener kinds + opener phrases Maya raised recently. | FIFO buffers (12 / 10 / 6). |
| `lore` | Inside jokes between Maya and the user. | Up to 30. Dormant items can resurface. |
| `anticipation_queue` | Pre-cooked openers Maya plans for next time. | Up to 5. TTL 14 days. Consumed on use. |
| `skills` | English error patterns + wins + current focus. | Up to 20 errors / 30 wins. |
| `maya_persona` | Maya's character + what she's already revealed to this user. | Decoration only. Never claims biography. |
| `open_loops` | Threads either party said they'd come back to. | Up to 12. Auto-expire 30 days unfollowed. |
| `meta_preferences` | User-set knobs (correction style, reply length, humor, off-limits). | Hard override. User's word is law. |

Open a chat and click **📦 My memory** in the header for the live, in-app version with all buckets and lifecycle tables.

---

## Routes

### Public

```
GET  /                         Production-shape chat
GET  /playground               Memory-experiments sandbox
GET  /qwen-lab                 Qwen A/B prompt comparison

POST /chat                     Streaming chat (prod path)
POST /playground/chat          Streaming chat (playground path)
POST /qwen-lab/chat            Dual-stream chat (left = old prompts, right = Qwen-tuned)

POST /end_session              Run librarian + save memory (prod)
POST /playground/end_session   Same, playground
POST /qwen-lab/end_session     Run librarian on BOTH sides

GET  /memory                   Memory inspector (prod)
GET  /playground/memory        Memory inspector (playground)
GET  /qwen-lab/memory          Memory inspector (lab)
```

### Admin

```
GET  /prompts                  Edit production prompt overrides (password-protected)
GET  /playground/prompts       Edit playground prompt overrides
GET  /playground/docs          Full architecture documentation
GET  /settings                 Backend / API key configuration
GET  /evals                    Multi-profile, multi-backend eval runner
GET  /qwen-lab/api/prompts     JSON dump of every QWEN_* prompt
GET  /qwen-lab/api/prompts/download   Bundle all QWEN_* prompts + INSTRUCTIONS.md as .zip
POST /playground/api/ask       Opus-powered Q&A bot for the integrating dev
```

---

## Sharing the running app publicly

For demos / showing testers, the app is wired to be exposable via [ngrok](https://ngrok.com):

```bash
brew install ngrok            # one-time
ngrok config add-authtoken <your-token>
./run.sh                      # in one terminal
ngrok http 5050               # in another — gives you a public URL
```

The Werkzeug debugger is automatically disabled (`debug=False`) when `PEERUP_DEBUG` is unset, so the public URL is safe to share with a few testers. **Do not** post the URL widely — there is no auth.

---

## Project structure

```
.
├── app.py                       # The whole Flask app — ~5,000 lines, all backends
├── requirements.txt             # 4 deps: anthropic[bedrock], boto3, flask, edge-tts
├── run.sh                       # venv setup + launch
├── .env.example                 # template for secrets (copy to .env)
├── templates/
│   ├── index.html               # Prod chat surface (audio-call style)
│   ├── playground.html          # Playground chat surface
│   ├── qwen_lab.html            # A/B comparison surface
│   ├── playground_docs.html     # In-app architecture docs
│   ├── prompts.html             # Prompt admin (prod)
│   ├── playground_prompts.html  # Prompt admin (playground)
│   ├── settings.html            # Backend / API config
│   ├── evals.html               # Eval runner
│   └── ...
├── static/peerup/               # Avatar video + UI assets
├── voices/                      # Pre-rendered TTS samples (gitignored — 121MB)
└── memory_store/                # Per-user JSON memory + session summaries
    ├── <user>.json              # Prod memory (one file per user)
    ├── _playground/             # Playground sandbox (isolated)
    │   └── <user>.json
    └── _qwen_lab/               # A/B lab (split per side)
        ├── old/<user>.json
        └── new/<user>.json
```

---

## Backend selection

The app supports four backends. Selection happens per-session via the dropdown on the welcome screen:

| Backend | When to use |
| --- | --- |
| **Bedrock — Qwen 32B** (default) | Fastest TTFT; cheapest with `enable_thinking: false`; the model the prod app uses. |
| **Bedrock — Anthropic Claude** (Sonnet 4.5, Haiku 4.5, with `apac.` / `us.` / `global.` regional prefixes) | When you want tighter rule-following than Qwen offers. |
| **Bedrock — NVIDIA Nemotron Nano 3 30B** | Experimental. Routed via the same Converse API path as Qwen. |
| **Anthropic API** (Sonnet 4.6, Haiku 4.5) | If you don't have AWS Bedrock set up. Pay-per-token. |
| **Claude CLI** (local subscription) | Free if you have a paid Claude subscription. Slower than API. |

---

## Contributing

This is a prototype that lives next to the production app. Two things to know:

1. **Don't change the prompts directly.** Use `/playground/prompts` (or the in-memory `QWEN_*` constants for the lab) so changes are scoped to one sandbox at a time.
2. **The librarian merge prompt is the highest-leverage thing in the codebase.** Tweaks here ripple across every user's stored memory. Test in the playground for a few sessions before promoting.

For a deeper dive into the memory system, prompt internals, and the experimental V4 → V6 roadmap: open `/playground/docs` while the app is running.

---

## License

No license file. Default copyright applies. Treat this as reference code, not as something to fork-and-deploy without explicit permission.
