"""eval_50.py — 50-call simulation harness for the Qwen-tuned prompts.

Runs synthetic chat sessions against the playground (which now serves the
QWEN_* prompts as overrides) using Qwen-32B Bedrock for BOTH Maya and the
user simulator. Mixes same-day, consecutive-day, sporadic, and cold-start
patterns. Saves transcripts + memory snapshots, then generates a ranked
gap report.

Usage:
    python eval_50.py info        # show schedule and profile pool
    python eval_50.py run         # execute all 50 sessions
    python eval_50.py analyze     # generate ranked gap report from saved runs
    python eval_50.py report      # alias for analyze; prints to stdout

Storage isolated under memory_store/_eval_50/ so prod / playground / qwen-lab
are untouched.
"""

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

# We import the app module to reuse its backends, prompt-builders, librarian,
# memory loaders, and renderer. The app loads .env so Bedrock creds resolve.
import app as A

# ─────────────────────────────────────────────────────────────────────────────
# Storage
# ─────────────────────────────────────────────────────────────────────────────

EVAL_DIR = A.MEMORY_DIR / "_eval_50"
EVAL_DIR.mkdir(exist_ok=True)
EVAL_MEMORY_DIR = EVAL_DIR / "memory"
EVAL_MEMORY_DIR.mkdir(exist_ok=True)
EVAL_TRANSCRIPTS_DIR = EVAL_DIR / "transcripts"
EVAL_TRANSCRIPTS_DIR.mkdir(exist_ok=True)
EVAL_REPORT_DIR = EVAL_DIR / "reports"
EVAL_REPORT_DIR.mkdir(exist_ok=True)
EVAL_RUN_LOG = EVAL_DIR / "run_log.jsonl"

# Use the playground prompt-overrides path so the eval uses the QWEN-tuned
# prompts that were pushed to the playground.
EVAL_PROMPTS_PATH = A.PG_PROMPTS_OVERRIDE_PATH


# ─────────────────────────────────────────────────────────────────────────────
# Profiles — 10 synthetic learners. Variety in profession, mother tongue,
# interests, and engagement style. Engagement style drives how chatty the user
# simulator will be (terse / medium / chatty).
# ─────────────────────────────────────────────────────────────────────────────

PROFILES = [
    {
        "id": "u01_priyansh", "user_name": "Priyansh",
        "profession": "Software engineer at a fintech",
        "mother_tongue": "Hindi",
        "interests": "Cricket, Bollywood movies, Startups",
        "engagement": "medium", "english_level": "B1",
        "personality": "curious but reserved; thinks before replying; warms up after a few turns",
    },
    {
        "id": "u02_aarti", "user_name": "Aarti",
        "profession": "Medical student preparing for NEET PG",
        "mother_tongue": "Marathi",
        "interests": "Cooking, classical music, books",
        "engagement": "medium", "english_level": "B1",
        "personality": "earnest, slightly anxious about exams, opens up about study stress",
    },
    {
        "id": "u03_rohan", "user_name": "Rohan",
        "profession": "Bank PO aspirant",
        "mother_tongue": "Bengali",
        "interests": "Football, Bengali cinema, photography",
        "engagement": "chatty", "english_level": "A2",
        "personality": "enthusiastic, makes more grammar slips, talks about football a lot",
    },
    {
        "id": "u04_neha", "user_name": "Neha",
        "profession": "Product designer at a startup",
        "mother_tongue": "Tamil",
        "interests": "Indie music, travel, cafes",
        "engagement": "chatty", "english_level": "B2",
        "personality": "expressive, witty, fluent — uses contractions and casual idioms",
    },
    {
        "id": "u05_vikram", "user_name": "Vikram",
        "profession": "Sales manager at a textile firm",
        "mother_tongue": "Gujarati",
        "interests": "Cricket, family, Gujarati food",
        "engagement": "terse", "english_level": "A2",
        "personality": "polite but short; busy man; replies in 5-8 words; rarely asks questions back",
    },
    {
        "id": "u06_anu", "user_name": "Anu",
        "profession": "Recent commerce graduate looking for first job",
        "mother_tongue": "Telugu",
        "interests": "K-dramas, fitness, Instagram reels",
        "engagement": "medium", "english_level": "B1",
        "personality": "uncertain about career direction; somewhat self-doubting; opens up gradually",
    },
    {
        "id": "u07_aman", "user_name": "Aman",
        "profession": "Professional fooseball player",
        "mother_tongue": "Punjabi",
        "interests": "Fooseball, marriage, office gossip",
        "engagement": "chatty", "english_level": "A2",
        "personality": "informal, jokes around, switches topics quickly",
    },
    {
        "id": "u08_diya", "user_name": "Diya",
        "profession": "Marketing manager at a fintech",
        "mother_tongue": "Hindi",
        "interests": "Travel, books, indie podcasts",
        "engagement": "medium", "english_level": "B2",
        "personality": "thoughtful, asks back, sometimes shares heavier feelings about work-life balance",
    },
    {
        "id": "u09_kabir", "user_name": "Kabir",
        "profession": "Sales associate at a retail chain",
        "mother_tongue": "Kannada",
        "interests": "Wrestling, Kannada films, biryani",
        "engagement": "terse", "english_level": "A1",
        "personality": "very simple English; uses one or two-word replies often; warm but minimal",
    },
    {
        "id": "u10_shreya", "user_name": "Shreya",
        "profession": "MBA student at IIM",
        "mother_tongue": "Hindi",
        "interests": "Strategy consulting, books, F1",
        "engagement": "medium", "english_level": "C1",
        "personality": "fluent, articulate, occasional grammar slip; treats the chat as banter",
    },
]

PROFILE_BY_ID = {p["id"]: p for p in PROFILES}


# ─────────────────────────────────────────────────────────────────────────────
# Emotional-state pool. Each session draws one. Steers the user simulator.
# ─────────────────────────────────────────────────────────────────────────────

EMOTIONAL_STATES = [
    "neutral, ordinary day",
    "tired, slept badly",
    "anxious, exam stress",
    "content, decent day at work",
    "frustrated about a small thing today",
    "excited about a weekend plan",
    "low energy, monosyllabic mood",
    "chatty, in a good mood",
    "preoccupied, half-distracted",
    "lonely, wanting to talk",
    "embarrassed about a recent mistake",
    "hopeful, made some progress on a goal",
]


# ─────────────────────────────────────────────────────────────────────────────
# Schedule — 50 sessions across 10 profiles + several time patterns.
#
# Layout (matches the plan we agreed on):
#   10 sessions: same user, same day, back-to-back   → user u01, day 0, 10x
#   15 sessions: same user, consecutive days         → user u02, days 0-14
#   10 sessions: same user, sporadic days            → user u03, gaps 5-12 days
#   10 sessions: 10 different new users each         → cold-start coverage (u04-u10 + u01-u03 fresh)
#    5 sessions: deep run on one user                → user u04, weeks 4-8
#
# For the "10 cold-start" tier, we use a separate logical user-id so the
# memory file stays empty — those sessions test brand-new behavior.
# ─────────────────────────────────────────────────────────────────────────────

# Anchor "today" for the schedule. All session dates are computed as offsets
# from this. The eval runner advances today_override per session.
EVAL_ANCHOR = datetime(2026, 5, 1)   # arbitrary; eval transcripts dated from here.


def build_schedule() -> list:
    """Returns 50 session specs. Each: {idx, profile_id, eval_user_key, today, turns_target,
    emotional_state, label}. eval_user_key is what we use as the memory key — for cold-start
    we use a fresh key per session so memory stays empty."""
    rng = random.Random(20260501)
    schedule = []
    idx = 1

    # Tier A: 10 same-day back-to-back sessions on u01.
    for i in range(10):
        schedule.append({
            "idx": idx,
            "profile_id": "u01_priyansh",
            "eval_user_key": "u01_priyansh",   # same memory file across all 10
            "today": (EVAL_ANCHOR).strftime("%Y-%m-%d"),
            "turns_target": rng.choice([6, 8, 10, 12]),
            "emotional_state": rng.choice(EMOTIONAL_STATES),
            "label": f"A{i+1:02d}_same_day",
        })
        idx += 1

    # Tier B: 15 consecutive-day sessions on u02.
    for i in range(15):
        schedule.append({
            "idx": idx,
            "profile_id": "u02_aarti",
            "eval_user_key": "u02_aarti",
            "today": (EVAL_ANCHOR + timedelta(days=i)).strftime("%Y-%m-%d"),
            "turns_target": rng.choice([6, 8, 10, 12, 14]),
            "emotional_state": rng.choice(EMOTIONAL_STATES),
            "label": f"B{i+1:02d}_consec_d{i}",
        })
        idx += 1

    # Tier C: 10 sporadic-gap sessions on u03.
    day_offset = 0
    for i in range(10):
        schedule.append({
            "idx": idx,
            "profile_id": "u03_rohan",
            "eval_user_key": "u03_rohan",
            "today": (EVAL_ANCHOR + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
            "turns_target": rng.choice([6, 8, 10, 12]),
            "emotional_state": rng.choice(EMOTIONAL_STATES),
            "label": f"C{i+1:02d}_sporadic_d{day_offset}",
        })
        day_offset += rng.randint(5, 12)
        idx += 1

    # Tier D: 10 cold-start, each a different fresh memory key (one-shot first sessions).
    cold_profiles = [p["id"] for p in PROFILES]   # cycle through all 10 profiles
    for i, pid in enumerate(cold_profiles):
        schedule.append({
            "idx": idx,
            "profile_id": pid,
            # Distinct eval_user_key suffix so memory file is fresh, even for users we used in tiers above.
            "eval_user_key": f"{pid}_cold",
            "today": (EVAL_ANCHOR + timedelta(days=rng.randint(0, 30))).strftime("%Y-%m-%d"),
            "turns_target": rng.choice([5, 6, 8, 10]),
            "emotional_state": rng.choice(EMOTIONAL_STATES),
            "label": f"D{i+1:02d}_coldstart_{pid[:6]}",
        })
        idx += 1

    # Tier E: 5 deep-run sessions on u04 (Neha) — weekly cadence over a month.
    for i in range(5):
        schedule.append({
            "idx": idx,
            "profile_id": "u04_neha",
            "eval_user_key": "u04_neha",
            "today": (EVAL_ANCHOR + timedelta(days=7 * i)).strftime("%Y-%m-%d"),
            "turns_target": rng.choice([10, 12, 14]),
            "emotional_state": rng.choice(EMOTIONAL_STATES),
            "label": f"E{i+1:02d}_deeprun_w{i}",
        })
        idx += 1

    assert len(schedule) == 50, f"expected 50 sessions, got {len(schedule)}"
    return schedule


# ─────────────────────────────────────────────────────────────────────────────
# User simulator — a Qwen call that plays the user side. Single-shot per turn.
# We keep its system prompt aggressive about staying in learner role and not
# leaking the meta context (it knows it's a simulator; reply must NOT).
# ─────────────────────────────────────────────────────────────────────────────

USER_SIMULATOR_SYSTEM_PROMPT = """You are simulating a real person chatting with an English-tutor app called Miss Maya. The PROFILE below describes who you are. Stay completely in character. NEVER mention you are a simulator, an AI, an LLM, or anything meta — the chat partner must believe you are a real human user.

YOUR PROFILE:
  Name: {user_name}
  Profession: {profession}
  Mother tongue: {mother_tongue}
  Interests: {interests}
  English level: {english_level}  (A1 = very basic; A2 = basic; B1 = ok; B2 = good; C1 = fluent)
  Personality: {personality}
  TODAY'S MOOD: {emotional_state}

OUTPUT FORMAT:
- Plain text. ONE message. No JSON, no markdown, no quotes around your reply.
- Length scales with engagement style:
    {engagement} engagement → {length_hint}
- Match your English level. A1 = short broken sentences, A2 = simple but mostly correct, B1/B2 = natural with occasional slip, C1 = fluent.
- Occasionally make a small grammar mistake natural for your level (drop "to", "the", wrong tense, missing article). Don't overdo it.
- One Hindi/Tamil/Marathi/etc word mixed in is fine occasionally if it fits the profile (mother tongue).

CONVERSATION FLOW DISCIPLINE:
- Vary your replies. Don't always ask questions. Don't always answer with full sentences. Sometimes "yeah ok", sometimes a paragraph, sometimes a question back.
- This is turn {turn_idx} of approximately {target_turns} turns.
  - Turn 1: respond to Maya's opener naturally. Don't dump your life story.
  - Mid turns: react to whatever Maya said. Bring up new things organically. Sometimes change topic.
  - When you're approaching turn {target_turns}: start winding down. Use phrases like "ok I should head", "talk to you later", "gotta go", "nice chatting".
- When you decide to wrap up, your reply should clearly signal the end. Maya will detect it and the session ends.

WHAT NOT TO DO:
- Do NOT ask Maya about her opinions on tutoring. Do NOT comment on her style. Do NOT meta-discuss the chat itself.
- Do NOT generate "User:" prefixes or speaker labels. Just the reply text.

Output ONLY your reply as plain text."""


def _length_hint(engagement: str) -> str:
    return {
        "terse": "5-15 words most turns; very short answers; rarely a full sentence",
        "medium": "15-40 words on average; some turns shorter, occasional turn longer if topic interests you",
        "chatty": "20-60 words on average; willing to ramble a bit; ask questions back",
    }.get(engagement, "15-40 words")


def _format_chat_history_for_user_sim(history: list) -> str:
    """Render the running chat history as plain text the simulator can read."""
    lines = []
    for m in history:
        role = m.get("role", "?")
        tag = "Maya" if role == "assistant" else "You"
        lines.append(f"{tag}: {m.get('content', '').strip()}")
    return "\n".join(lines) if lines else "(start of conversation)"


def simulate_user_reply(profile: dict, history: list, emotional_state: str,
                        turn_idx: int, target_turns: int) -> str:
    """One turn of the user simulator. Returns plain-text user message."""
    sys_prompt = USER_SIMULATOR_SYSTEM_PROMPT.format(
        user_name=profile["user_name"],
        profession=profile["profession"],
        mother_tongue=profile["mother_tongue"],
        interests=profile["interests"],
        english_level=profile["english_level"],
        personality=profile["personality"],
        emotional_state=emotional_state,
        engagement=profile["engagement"],
        length_hint=_length_hint(profile["engagement"]),
        turn_idx=turn_idx,
        target_turns=target_turns,
    )
    chat_so_far = _format_chat_history_for_user_sim(history)
    user_msg = (
        f"CONVERSATION SO FAR:\n{chat_so_far}\n\n"
        f"Now write your next reply (just the text, nothing else). "
        f"This is turn {turn_idx} out of approximately {target_turns} turns."
    )
    full_text = ""
    for evt in A.stream_via_bedrock_qwen(
        sys_prompt,
        [{"role": "user", "content": user_msg}],
        model=A.QWEN_LAB_MODEL_ID,
    ):
        if isinstance(evt, str) and evt.startswith("data: "):
            try:
                d = json.loads(evt[6:].rstrip("\n"))
                if d.get("type") == "delta":
                    full_text += d.get("text", "")
                elif d.get("type") == "done":
                    full_text = d.get("full", full_text) or full_text
                    break
                elif d.get("type") == "error":
                    return f"[user-sim error: {d.get('message')}]"
            except Exception:
                pass
    return full_text.strip().strip('"').strip("'")


# ─────────────────────────────────────────────────────────────────────────────
# Maya call — wraps the playground chat-side logic but uses our isolated
# memory dir + the eval-locked anchor date. We do NOT run the librarian per
# turn; only at session end.
# ─────────────────────────────────────────────────────────────────────────────

def call_maya(profile: dict, history: list, user_message: str, today: str,
              eval_user_key: str) -> str:
    """One Maya reply. Pulls memory from EVAL_MEMORY_DIR. Uses the playground
    prompt overrides (which contain the QWEN_* set). Returns the reply text
    (unwrapped from JSON if Maya wrapped it)."""
    memory = A.pg_format_memory_for_prompt(
        A.pg_load_user_memory(eval_user_key, mem_root=EVAL_MEMORY_DIR),
        today, is_opening_turn=(len(history) == 0),
    )
    is_first_ever_session = (not memory) and (not history)
    if is_first_ever_session:
        first_msg = A.build_generic_first_message_prompt(
            profile["user_name"], profile["profession"],
            profile["mother_tongue"], profile["interests"],
            today_override=today,
            prompts_path=EVAL_PROMPTS_PATH,
        )
    else:
        first_msg = A.build_first_message_user_prompt(
            profile["user_name"], profile["profession"],
            profile["mother_tongue"], profile["interests"],
            memory=memory, session_summary="",
            older_trimmed_count=0, today_override=today,
            prompts_path=EVAL_PROMPTS_PATH,
        )
    messages = [{"role": "user", "content": first_msg}]
    messages.extend(history)
    if history and user_message:
        messages.append({"role": "user", "content": user_message})

    system_prompt = A.pg_build_system_prompt(prompts_path=EVAL_PROMPTS_PATH)

    raw = ""
    for evt in A.stream_via_bedrock_qwen(
        system_prompt, messages, model=A.QWEN_LAB_MODEL_ID,
    ):
        if isinstance(evt, str) and evt.startswith("data: "):
            try:
                d = json.loads(evt[6:].rstrip("\n"))
                if d.get("type") == "delta":
                    raw += d.get("text", "")
                elif d.get("type") == "done":
                    raw = d.get("full", raw) or raw
                    break
                elif d.get("type") == "error":
                    return f"[maya error: {d.get('message')}]"
            except Exception:
                pass
    # Apply the judge guard (Qwen LLM-as-judge — replaces all 12 regex guards).
    user_last = ""
    if history and user_message:
        user_last = user_message
    elif history:
        for prev in reversed(history):
            if prev.get("role") == "user":
                user_last = prev.get("content", "")
                break
    mem_for_guard = A.pg_load_user_memory(eval_user_key, mem_root=EVAL_MEMORY_DIR)
    import judge_guard as JG
    cleaned, _stripped = JG.apply_judge_guard(
        raw, user_last_message=user_last, mem=mem_for_guard,
        is_first_reply=(len(history) == 0),
    )

    # Unwrap JSON-wrapped output if present.
    s = (cleaned or raw).strip()
    if s.startswith("{"):
        try:
            obj = json.loads(s)
            if isinstance(obj, dict) and isinstance(obj.get("message"), str):
                return obj["message"]
        except Exception:
            pass
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', s, re.S)
    if m:
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict) and isinstance(obj.get("message"), str):
                return obj["message"]
        except Exception:
            pass
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Wrap-up detection — the user simulator signals end-of-call. We accept either
# explicit phrases or just hit the max-turn cap.
# ─────────────────────────────────────────────────────────────────────────────

WRAPUP_PATTERNS = [
    re.compile(r"\b(?:got to|gotta|i should|i must|need to)\s+(?:go|head|run|leave|sleep|crash|sign off|catch you)\b", re.I),
    re.compile(r"\btalk to you later\b", re.I),
    re.compile(r"\bcatch you (?:later|tomorrow|soon)\b", re.I),
    re.compile(r"\bnice (?:chatting|talking)\b", re.I),
    re.compile(r"\bsee you (?:soon|tomorrow|later)\b", re.I),
    re.compile(r"\bbye\b|\bgood ?night\b|\btake care\b", re.I),
]


def looks_like_wrapup(text: str) -> bool:
    return any(p.search(text) for p in WRAPUP_PATTERNS)


# ─────────────────────────────────────────────────────────────────────────────
# Session runner
# ─────────────────────────────────────────────────────────────────────────────

def run_session(spec: dict, log_fn=print) -> dict:
    """Run one full session per spec. Returns the saved session dict."""
    profile = PROFILE_BY_ID[spec["profile_id"]]
    today = spec["today"]
    target_turns = spec["turns_target"]
    eval_user_key = spec["eval_user_key"]

    log_fn(f"[{spec['idx']:02d}/50] {spec['label']:30s}  {profile['user_name']:10s}  today={today}  "
           f"turns={target_turns}  mood={spec['emotional_state']}")

    history = []
    transcript = []   # [{turn, role, content, timestamp}]
    t_start = time.time()

    # Memory snapshot before
    mem_before = A.pg_load_user_memory(eval_user_key, mem_root=EVAL_MEMORY_DIR)

    # Turn 1 is Maya's opener. After that alternate user → Maya.
    for turn_idx in range(1, target_turns + 1):
        if turn_idx == 1:
            # Maya speaks first (opening turn).
            maya_reply = call_maya(profile, history, "", today, eval_user_key)
            history.append({"role": "assistant", "content": maya_reply})
            transcript.append({"turn": turn_idx, "role": "maya", "content": maya_reply})
            log_fn(f"    T{turn_idx} maya: {maya_reply[:80]}{'…' if len(maya_reply)>80 else ''}")
            continue
        # User turn
        user_text = simulate_user_reply(profile, history, spec["emotional_state"], turn_idx, target_turns)
        history.append({"role": "user", "content": user_text})
        transcript.append({"turn": turn_idx, "role": "user", "content": user_text})
        log_fn(f"    T{turn_idx} user: {user_text[:80]}{'…' if len(user_text)>80 else ''}")
        # Maya turn (counts as same turn_idx — flow = user-then-maya)
        maya_reply = call_maya(profile, history, "", today, eval_user_key)
        history.append({"role": "assistant", "content": maya_reply})
        transcript.append({"turn": turn_idx, "role": "maya", "content": maya_reply})
        log_fn(f"    T{turn_idx} maya: {maya_reply[:80]}{'…' if len(maya_reply)>80 else ''}")
        # End if user signaled wrap-up
        if looks_like_wrapup(user_text):
            log_fn(f"    → wrap-up detected at turn {turn_idx}")
            break

    # Run the librarian on the transcript (use playground/QWEN merge prompt).
    transcript_text = "\n".join(f"{m['role'].title()}: {m['content']}" for m in transcript)
    try:
        new_mem = A.pg_merge_memory_into_dict(
            A.pg_load_user_memory(eval_user_key, mem_root=EVAL_MEMORY_DIR),
            transcript_text,
            user_name=profile["user_name"],
            session_id=f"eval_{spec['idx']}_{spec['label']}",
            today_override=today,
            prompts_path=EVAL_PROMPTS_PATH,
            pending_dir=EVAL_DIR / "_pending_merges",
        )
        A.pg_save_user_memory(eval_user_key, new_mem, mem_root=EVAL_MEMORY_DIR)
        librarian_ok = True
    except Exception as e:
        log_fn(f"    !! librarian error: {e}")
        librarian_ok = False

    mem_after = A.pg_load_user_memory(eval_user_key, mem_root=EVAL_MEMORY_DIR)

    duration_s = round(time.time() - t_start, 1)
    saved = {
        "spec": spec,
        "profile": profile,
        "transcript": transcript,
        "memory_before": mem_before,
        "memory_after": mem_after,
        "librarian_ok": librarian_ok,
        "duration_s": duration_s,
    }
    out_path = EVAL_TRANSCRIPTS_DIR / f"{spec['idx']:02d}_{spec['label']}.json"
    out_path.write_text(json.dumps(saved, indent=2, ensure_ascii=False), encoding="utf-8")
    log_fn(f"    saved → {out_path.name}  ({duration_s}s, librarian={'ok' if librarian_ok else 'FAIL'})\n")
    return saved


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator — run all 50 sessions sequentially. Sequential is intentional:
# Tier B (consecutive days) needs each session's memory to land on disk before
# the next session reads it.
# ─────────────────────────────────────────────────────────────────────────────

def run_all(skip_done: bool = True):
    schedule = build_schedule()
    log_path = EVAL_RUN_LOG
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append({"ts": datetime.now().isoformat(), "msg": msg})

    log(f"=== eval_50: starting {len(schedule)} sessions ===")
    log(f"Output: {EVAL_DIR}")
    log(f"Memory dir: {EVAL_MEMORY_DIR}")
    log(f"Prompts: {EVAL_PROMPTS_PATH}  (playground overrides — currently QWEN-tuned)\n")

    failed = []
    for spec in schedule:
        out_path = EVAL_TRANSCRIPTS_DIR / f"{spec['idx']:02d}_{spec['label']}.json"
        if skip_done and out_path.exists():
            log(f"[{spec['idx']:02d}/50] {spec['label']}  SKIP (already saved)")
            continue
        try:
            run_session(spec, log_fn=log)
        except Exception as e:
            log(f"!! session {spec['idx']} ({spec['label']}) errored: {e}")
            failed.append((spec["idx"], spec["label"], str(e)))

    # Append run log
    with open(log_path, "a", encoding="utf-8") as f:
        for ln in log_lines:
            f.write(json.dumps(ln) + "\n")

    log(f"\n=== Done. {len(schedule) - len(failed)} ok, {len(failed)} failed ===")
    if failed:
        for fid, lbl, err in failed:
            log(f"  FAIL [{fid}] {lbl}: {err}")


# ─────────────────────────────────────────────────────────────────────────────
# Analysis — runs over saved transcripts, computes metrics, builds gap report.
#
# Each gap entry has:
#   - id (short slug)
#   - severity (1-5, hand-tuned)
#   - frequency (% of sessions affected)
#   - layer (prompt | guard | renderer | memory)
#   - description
#   - examples (up to 3 verbatim from the transcripts)
#   - suggested_fix
#
# Final report is sorted by severity * frequency.
# ─────────────────────────────────────────────────────────────────────────────

def load_all_sessions() -> list:
    sessions = []
    for p in sorted(EVAL_TRANSCRIPTS_DIR.glob("*.json")):
        try:
            sessions.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  skipping {p.name}: {e}", file=sys.stderr)
    return sessions


def maya_replies(session: dict) -> list:
    return [m for m in session["transcript"] if m["role"] == "maya"]


def user_replies(session: dict) -> list:
    return [m for m in session["transcript"] if m["role"] == "user"]


def normalize_opener(text: str, user_name: str = "") -> str:
    s = (text or "").lower().strip()
    s = re.sub(r"^\s*(?:hi+|hello+|hey+|heya|good\s+(?:morning|afternoon|evening|day))\b[,!\s]+[a-z\'\-]+\s*[,]?\s*", "", s)
    if user_name:
        s = re.sub(r"\b" + re.escape(user_name.lower()) + r"\b", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Phrase blacklist — the burned-out phrases we want to flag if Qwen still uses them.
STALE_PHRASE_PATTERNS = [
    (re.compile(r"\bI noticed (?:how much|that|you|the way)\b", re.I), "surveillant_opener"),
    (re.compile(r"\b(?:tea[- ]?(?:over[- ]?)?coffee|tea person|chai[- ]?(?:in|over)[- ]?(?:the[- ]?)?(?:evening|coffee))\b", re.I), "tea_persona_cycle"),
    (re.compile(r"\b(?:mango season|mango[- ]?(?:loving|month))\b", re.I), "mango_persona_cycle"),
    (re.compile(r"\bold (?:hindi (?:film |movie )?songs|hindi songs)\b", re.I), "hindi_songs_persona_cycle"),
    (re.compile(r"\bbalcony[- ]?plants\b", re.I), "balcony_plants_cycle"),
    (re.compile(r"\bwhat english situations? (?:are|do you find) tricky\b", re.I), "clipboard_question"),
    (re.compile(r"\b(?:check|consult|look\s+at)\s+my\s+notes?\b", re.I), "notes_break"),
    (re.compile(r"\byou said[,:]?\s*[\"\'][^\"\']{1,200}[\"\']\s*[,!.]?\s*(?:very clear|perfect|good sentence|clear sentence)", re.I), "echo_praise"),
    (re.compile(r"\bI[' ]?m miss maya\b", re.I), "self_intro_in_reply"),  # ok on T1; flagged later only when T>1
    (re.compile(r"\bI'?ve been thinking about you\b", re.I), "creepy_opener"),
    (re.compile(r"\bI love how you\b", re.I), "love_how_you_opener"),
]


def analyze_session(session: dict) -> dict:
    """Per-session metrics + gap flags."""
    flags = []
    profile = session["profile"]
    user_name = profile["user_name"]
    transcript = session["transcript"]
    maya_msgs = [m for m in transcript if m["role"] == "maya"]

    # Stale-phrase scan across all Maya messages
    stale_hits = []
    for i, m in enumerate(maya_msgs):
        text = m["content"] or ""
        for pat, tag in STALE_PHRASE_PATTERNS:
            if tag == "self_intro_in_reply" and i == 0:
                continue   # first turn self-intro is allowed by Rule 35b
            if pat.search(text):
                stale_hits.append({"turn": m["turn"], "tag": tag, "snippet": text[:200]})

    # Greeting discipline — turns 2+ shouldn't start with greeting
    bad_greeting_t2 = []
    leading_greet_re = re.compile(r"^\s*(?:hi+|hello+|hey+|heya|good\s+(?:morning|afternoon|evening|day))[,!\s]", re.I)
    for i, m in enumerate(maya_msgs):
        if i == 0:
            continue
        if leading_greet_re.match((m["content"] or "").lstrip()):
            bad_greeting_t2.append({"turn": m["turn"], "snippet": m["content"][:120]})

    # Multiple-question reply — Rule 9
    multi_q = []
    for m in maya_msgs:
        text = m["content"] or ""
        # Count "?" outside of quoted segments
        q_count = text.count("?")
        if q_count >= 2:
            multi_q.append({"turn": m["turn"], "q_count": q_count, "snippet": text[:200]})

    # Reply-length stats
    word_counts = [len((m["content"] or "").split()) for m in maya_msgs]

    # Wrap-up rate
    user_msgs = [m for m in transcript if m["role"] == "user"]
    wrap_up_seen = any(looks_like_wrapup(m["content"]) for m in user_msgs)

    # Memory-ref rate (on returning users only — meaningful when memory exists)
    has_memory = bool(session["memory_before"].get("facts") or session["memory_before"].get("events"))
    memory_terms = []
    if has_memory:
        # crude: collect interest-list values + event "what" strings; flag a Maya reply as
        # referencing memory if any of those tokens appears.
        for v in (session["memory_before"].get("facts") or {}).values():
            if isinstance(v, list):
                memory_terms.extend([str(x).lower() for x in v])
            elif isinstance(v, str):
                memory_terms.append(v.lower())
        for ev in session["memory_before"].get("events") or []:
            memory_terms.append((ev.get("what") or "").lower())
    memory_terms = [t for t in memory_terms if len(t) >= 4]
    refs = 0
    for m in maya_msgs:
        if any(t and t in (m["content"] or "").lower() for t in memory_terms):
            refs += 1
    memory_ref_rate = (refs / len(maya_msgs)) if maya_msgs else 0.0

    return {
        "session_idx": session["spec"]["idx"],
        "label": session["spec"]["label"],
        "stale_hits": stale_hits,
        "bad_greeting_t2": bad_greeting_t2,
        "multi_q": multi_q,
        "word_counts": word_counts,
        "avg_words": round(sum(word_counts) / len(word_counts), 1) if word_counts else 0,
        "wrap_up_seen": wrap_up_seen,
        "memory_ref_rate": round(memory_ref_rate, 2),
        "has_memory": has_memory,
    }


def opener_repetition_across_sessions(sessions: list) -> dict:
    """Group sessions by eval_user_key, compute pairwise opener similarity within group."""
    by_user = {}
    for s in sessions:
        key = s["spec"]["eval_user_key"]
        first_maya = next((m for m in s["transcript"] if m["role"] == "maya"), None)
        if not first_maya: continue
        norm = normalize_opener(first_maya["content"], s["profile"]["user_name"])
        by_user.setdefault(key, []).append({"idx": s["spec"]["idx"], "raw": first_maya["content"], "norm": norm})

    high_sim_pairs = []
    for key, items in by_user.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i]["norm"], items[j]["norm"]
                if len(a) < 8 or len(b) < 8: continue
                ratio = SequenceMatcher(None, a, b).ratio()
                if ratio >= 0.65:
                    high_sim_pairs.append({
                        "user": key, "session_a": items[i]["idx"], "session_b": items[j]["idx"],
                        "ratio": round(ratio, 2),
                        "a_raw": items[i]["raw"][:200], "b_raw": items[j]["raw"][:200],
                    })
    return {"by_user_count": {k: len(v) for k, v in by_user.items()}, "high_sim_pairs": high_sim_pairs}


def build_gap_report(sessions: list) -> dict:
    per_session = [analyze_session(s) for s in sessions]
    n = len(per_session)
    if n == 0:
        return {"error": "no sessions"}

    # Aggregate stale hits by tag
    stale_count = {}
    stale_examples = {}
    for ps in per_session:
        for h in ps["stale_hits"]:
            stale_count[h["tag"]] = stale_count.get(h["tag"], 0) + 1
            stale_examples.setdefault(h["tag"], []).append({
                "session_idx": ps["session_idx"], "turn": h["turn"], "snippet": h["snippet"],
            })

    # Greeting-T2+ violations
    t2_greeting_total = sum(len(ps["bad_greeting_t2"]) for ps in per_session)
    t2_greeting_examples = []
    for ps in per_session:
        for h in ps["bad_greeting_t2"][:1]:
            t2_greeting_examples.append({"session_idx": ps["session_idx"], **h})

    # Multi-question violations
    multi_q_total = sum(len(ps["multi_q"]) for ps in per_session)
    multi_q_examples = []
    for ps in per_session:
        for h in ps["multi_q"][:1]:
            multi_q_examples.append({"session_idx": ps["session_idx"], **h})

    # Reply length stats
    all_lens = [w for ps in per_session for w in ps["word_counts"]]
    avg_len = round(sum(all_lens) / len(all_lens), 1) if all_lens else 0
    too_long = sum(1 for w in all_lens if w > 120)
    too_short = sum(1 for w in all_lens if w < 8)

    # Memory ref rate (only sessions with memory)
    mem_sessions = [ps for ps in per_session if ps["has_memory"]]
    avg_mem_ref = round(sum(ps["memory_ref_rate"] for ps in mem_sessions) / len(mem_sessions), 2) if mem_sessions else 0

    # Opener repetition across sessions
    rep = opener_repetition_across_sessions(sessions)

    # Build gaps list
    gaps = []
    for tag, count in sorted(stale_count.items(), key=lambda x: -x[1]):
        freq = round(count / n * 100, 1)
        sev = {
            "surveillant_opener": 5, "tea_persona_cycle": 4, "mango_persona_cycle": 4,
            "hindi_songs_persona_cycle": 4, "balcony_plants_cycle": 4,
            "clipboard_question": 4, "echo_praise": 4, "notes_break": 5,
            "self_intro_in_reply": 5, "creepy_opener": 4, "love_how_you_opener": 3,
        }.get(tag, 3)
        gaps.append({
            "id": f"stale_phrase_{tag}",
            "severity": sev,
            "frequency_pct": freq,
            "count": count,
            "layer": "prompt+guard",
            "description": f"Maya used the stale phrase tagged '{tag}' in {count}/{n} sessions ({freq}%).",
            "examples": stale_examples[tag][:3],
            "suggested_fix": "Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.",
            "score": sev * freq,
        })

    if t2_greeting_total > 0:
        freq = round(sum(1 for ps in per_session if ps["bad_greeting_t2"]) / n * 100, 1)
        gaps.append({
            "id": "greeting_on_turn_2plus",
            "severity": 4,
            "frequency_pct": freq,
            "count": t2_greeting_total,
            "layer": "prompt",
            "description": f"Maya started a turn-2+ reply with a greeting ('Hi <name>,...') in {t2_greeting_total} replies across {sum(1 for ps in per_session if ps['bad_greeting_t2'])} sessions.",
            "examples": t2_greeting_examples[:3],
            "suggested_fix": "Strengthen Rule 1 turn-2+ no-greeting clause OR add a server-side strip in pg_apply_output_guard.",
            "score": 4 * freq,
        })

    if multi_q_total > 0:
        freq = round(sum(1 for ps in per_session if ps["multi_q"]) / n * 100, 1)
        gaps.append({
            "id": "multiple_questions_per_reply",
            "severity": 3,
            "frequency_pct": freq,
            "count": multi_q_total,
            "layer": "prompt",
            "description": f"Maya included 2+ questions in {multi_q_total} replies across {sum(1 for ps in per_session if ps['multi_q'])} sessions (Rule 9 violation).",
            "examples": multi_q_examples[:3],
            "suggested_fix": "Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.",
            "score": 3 * freq,
        })

    if rep["high_sim_pairs"]:
        gaps.append({
            "id": "opener_repetition",
            "severity": 5,
            "frequency_pct": round(len(rep["high_sim_pairs"]) / max(1, n) * 100, 1),
            "count": len(rep["high_sim_pairs"]),
            "layer": "guard",
            "description": f"{len(rep['high_sim_pairs'])} pairs of openers across same-user sessions had >=0.65 structural similarity.",
            "examples": rep["high_sim_pairs"][:5],
            "suggested_fix": "Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.",
            "score": 5 * 50,  # arbitrary high since this is THE bug
        })

    if mem_sessions and avg_mem_ref < 0.20:
        gaps.append({
            "id": "low_memory_utilization",
            "severity": 4,
            "frequency_pct": 100.0,
            "count": len(mem_sessions),
            "layer": "prompt+renderer",
            "description": f"On returning-user sessions, average memory-reference rate is {avg_mem_ref:.0%} — too low. Maya is ignoring stored facts/events.",
            "examples": [],
            "suggested_fix": "Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.",
            "score": 4 * 50,
        })
    elif mem_sessions and avg_mem_ref > 0.65:
        gaps.append({
            "id": "over_personalization",
            "severity": 3,
            "frequency_pct": 100.0,
            "count": len(mem_sessions),
            "layer": "prompt",
            "description": f"On returning-user sessions, average memory-reference rate is {avg_mem_ref:.0%} — Maya may be forcing personalization on filler turns.",
            "examples": [],
            "suggested_fix": "Prompt: add explicit guidance that filler turns ('ok thanks', 'yes', 'no') get plain conversational replies without memory hooks.",
            "score": 3 * 30,
        })

    if too_long > 0:
        freq = round(too_long / max(1, len(all_lens)) * 100, 1)
        gaps.append({
            "id": "reply_too_long",
            "severity": 2,
            "frequency_pct": freq,
            "count": too_long,
            "layer": "prompt",
            "description": f"{too_long} replies exceeded 120 words (Rule 7 / OUTPUT FORMAT 20-120 words).",
            "examples": [],
            "suggested_fix": "Sharpen the word cap to MAX 100 in OUTPUT FORMAT block.",
            "score": 2 * freq,
        })
    if too_short > len(all_lens) * 0.3:
        freq = round(too_short / max(1, len(all_lens)) * 100, 1)
        gaps.append({
            "id": "reply_too_short",
            "severity": 2,
            "frequency_pct": freq,
            "count": too_short,
            "layer": "prompt",
            "description": f"{too_short} replies were under 8 words — Maya might be too terse on filler turns.",
            "examples": [],
            "suggested_fix": "Set MIN floor in OUTPUT FORMAT (e.g. 'message length: 15-100 words').",
            "score": 2 * freq,
        })

    gaps.sort(key=lambda g: -g["score"])

    return {
        "session_count": n,
        "summary_metrics": {
            "avg_reply_words": avg_len,
            "replies_over_120w": too_long,
            "replies_under_8w": too_short,
            "avg_memory_ref_rate_returning_users": avg_mem_ref,
            "opener_repetition_pairs": len(rep["high_sim_pairs"]),
            "stale_phrase_total_hits": sum(stale_count.values()),
            "wrap_up_seen_count": sum(1 for ps in per_session if ps["wrap_up_seen"]),
        },
        "ranked_gaps": gaps,
        "per_session_metrics": per_session,
    }


def render_report_md(report: dict) -> str:
    lines = []
    lines.append("# Eval-50 gap report")
    lines.append("")
    lines.append(f"**Sessions analysed**: {report['session_count']}")
    lines.append("")
    lines.append("## Top-line metrics")
    sm = report["summary_metrics"]
    lines.append(f"- Average reply length: **{sm['avg_reply_words']} words**")
    lines.append(f"- Replies over 120 words: **{sm['replies_over_120w']}**")
    lines.append(f"- Replies under 8 words: **{sm['replies_under_8w']}**")
    lines.append(f"- Avg memory-reference rate (returning-user sessions): **{sm['avg_memory_ref_rate_returning_users']:.0%}**")
    lines.append(f"- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **{sm['opener_repetition_pairs']}**")
    lines.append(f"- Total stale-phrase hits across all sessions: **{sm['stale_phrase_total_hits']}**")
    lines.append(f"- Sessions with a clean wrap-up signal: **{sm['wrap_up_seen_count']}**")
    lines.append("")
    lines.append("## Ranked gaps (severity × frequency)")
    lines.append("")
    for i, g in enumerate(report["ranked_gaps"], 1):
        lines.append(f"### {i}. `{g['id']}`  · severity {g['severity']} · freq {g['frequency_pct']}% · score {g['score']:.0f}")
        lines.append(f"**Layer**: {g['layer']}")
        lines.append("")
        lines.append(g["description"])
        lines.append("")
        if g.get("examples"):
            lines.append("Examples:")
            for ex in g["examples"][:3]:
                if "snippet" in ex:
                    lines.append(f"- session {ex.get('session_idx','?')} turn {ex.get('turn','?')}: `{ex['snippet'][:160]}`")
                elif "session_a" in ex:
                    lines.append(f"- {ex.get('user')} sessions {ex['session_a']} ↔ {ex['session_b']} (sim {ex['ratio']}): `{ex['a_raw'][:120]}` ↔ `{ex['b_raw'][:120]}`")
            lines.append("")
        lines.append(f"**Suggested fix**: {g['suggested_fix']}")
        lines.append("")
    return "\n".join(lines)


def cmd_analyze():
    sessions = load_all_sessions()
    if not sessions:
        print(f"No sessions in {EVAL_TRANSCRIPTS_DIR}. Run `python eval_50.py run` first.")
        return
    report = build_gap_report(sessions)
    md = render_report_md(report)
    out_md = EVAL_REPORT_DIR / f"gap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_md.write_text(md, encoding="utf-8")
    out_json = EVAL_REPORT_DIR / f"gap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md)
    print(f"\nSaved: {out_md}")
    print(f"Saved: {out_json}")


def cmd_info():
    schedule = build_schedule()
    print(f"Profile pool: {len(PROFILES)}")
    for p in PROFILES:
        print(f"  {p['id']:20s} {p['user_name']:10s} {p['profession'][:40]:40s} {p['mother_tongue']:10s} eng={p['english_level']} {p['engagement']}")
    print(f"\nSchedule: {len(schedule)} sessions")
    tier_counts = {}
    for s in schedule:
        tier = s['label'][0]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    for tier, c in sorted(tier_counts.items()):
        print(f"  Tier {tier}: {c} sessions")
    print(f"\nStorage:")
    print(f"  Memory dir: {EVAL_MEMORY_DIR}")
    print(f"  Transcripts: {EVAL_TRANSCRIPTS_DIR}")
    print(f"  Reports: {EVAL_REPORT_DIR}")
    print(f"\nPrompts source: {EVAL_PROMPTS_PATH}")
    print(f"Bedrock available: {A.bedrock_available()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="50-call eval harness for Qwen-tuned Maya prompts.")
    parser.add_argument("cmd", choices=["info", "run", "analyze", "report"], help="info | run | analyze")
    args = parser.parse_args()
    if args.cmd == "info":
        cmd_info()
    elif args.cmd == "run":
        run_all(skip_done=True)
    elif args.cmd in ("analyze", "report"):
        cmd_analyze()
