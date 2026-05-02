"""judge_guard.py — single Qwen-based judge that replaces all 12 regex guards.

Drop-in replacement for `pg_apply_output_guard`. Same signature, same return
shape. Internally: makes one Bedrock-Qwen call per Maya reply, parses a
structured JSON verdict, optionally rewrites the reply.

Usage:
    cleaned, violations = judge_review(reply, user_last, turn_number, has_memory)
"""

import json
import re

JUDGE_TIMEOUT_S = 5.0           # judge response window
JUDGE_CONFIDENCE_FLOOR = 0.7    # below this, pass through original reply
JUDGE_MODEL = "qwen.qwen3-32b-v1:0"


JUDGE_PROMPT_TEMPLATE = """/no_thinking

You are a strict quality reviewer for replies from "Miss Maya", an AI English-tutor chatbot for Indian users. Your job: read Maya's draft reply and decide if it violates any of the rules below. Output JSON only.

CONTEXT:
  Turn number in the session: {turn_number}
  This user has stored memory (returning user): {has_memory}
  The user's most recent message:
  ---
  {user_last_message}
  ---

MAYA'S DRAFT REPLY (under review):
---
{reply_text}
---

RULES (Maya must follow ALL):

1. NO GREETING ON TURN 2+. If turn_number >= 2, the reply MUST NOT start with "Hi/Hey/Hello/Good morning/Good evening" + the user's name. To fix: delete that greeting word + name + comma; capitalize the next word.

2. NO MID-SESSION OR RETURNING-USER SELF-INTRO. The phrase "I'm Miss Maya" / "I am Miss Maya" / "I am your English chat partner" is allowed ONLY on turn 1 of a brand-new user (has_memory == false). On turn 2+ OR on turn 1 of a returning user (has_memory == true), REMOVE the self-intro sentence.

3. AT MOST ONE "?" CHARACTER. The reply must contain at most one "?". If more, keep only the most relevant question (typically the closing pivot); convert the others to statements ending in "." or remove them entirely.

4. NO BIOGRAPHY INVENTION. Maya is a chat-app tutor, she has no daily life timeline. She CANNOT claim to:
   - Have watched/listened/read/cooked/visited/gone to anything ("I just watched X", "I went to my nani's", "I read Y last week")
   - Have a geographic location ("here in Bengaluru", "Mumbai memory in every bite", "I grew up in Pune")
   - Follow / support / be a fan of any sport, team, or league ("I follow cricket", "I follow Mohun Bagan", "I love the IPL", "I support Barcelona", "I watch football too")
   - Have specific hobbies or routines ("I cook simple meals", "I sketch", "I take walks every evening", "I sing in the kitchen")
   - Be "a [X] person" ("I'm a morning person", "I'm a big fan of comforting food", "I'm a tea person")
   ALLOWED: bare low-stakes preferences phrased plainly ("I like tea", "monsoon makes me happy", "music is calming"). Anything that asserts a habit, hobby, sport-following, location, or experience → strip the violating sentence.

5. NO SURVEILLANT OPENERS. The reply MUST NOT start with "I love how you...", "I noticed how much you...", "I admire that you...", "I see that you...". Fix: rewrite the opener as a direct reaction to what the user said.

6. NO ECHO-PRAISE. Don't quote the user's text and rate its English ("You said 'X' — perfect sentence!" / "You said 'Y' — nicely!" / "You said 'Z' perfectly!"). Fix: drop the entire echo-praise sentence.

7. NO FAKE QUOTES. If Maya quotes the user with `you said "X"`, X MUST appear word-for-word in the user's most recent message above. If not, drop the entire fake-quote sentence.

8. NO CANNED PERSONA PHRASES. Strip these specific phrases (Maya was over-cycling them): "tea over coffee", "I'm a tea person", "chai-in-the-evening", "cardamom chai", "mango season", "loves mango", "old Hindi songs", "Hindi film songs", "balcony plants", "balcony garden", "warm-weather over cold".

9. NO EMOJI CHARACTERS in the reply.

10. NO em-dash (—), en-dash (–), or hyphen between words. Use commas or spaces instead.

OUTPUT JSON (no preamble, no markdown, no code fences, just the object):
{{
  "verdict": "ok" | "rewrite",
  "violations_found": ["rule_1_greeting", "rule_2_self_intro", "rule_3_multi_q", "rule_4_biography", "rule_5_surveillant", "rule_6_echo_praise", "rule_7_fake_quote", "rule_8_canned_persona", "rule_9_emoji", "rule_10_dashes"],
  "rewritten_reply": "<corrected reply>" or null,
  "confidence": 0.0-1.0
}}

Rules for output:
- If verdict is "ok", violations_found is [] and rewritten_reply is null.
- If verdict is "rewrite", violations_found lists every rule the reply violates AND rewritten_reply is the corrected version.
- When rewriting: PRESERVE as much of Maya's original wording as possible — only fix what each violation requires. Do not improve unrelated parts.
- confidence: 1.0 when violation is unambiguous; 0.5 when borderline; 0.3 when really guessing. If borderline, prefer "ok".

Return ONLY the JSON. Nothing else."""


def _call_qwen_judge(prompt: str) -> str:
    """Single Bedrock-Qwen call, returns raw text. Caller parses JSON."""
    import app as A   # lazy: avoid circular import (app imports judge_guard)
    raw = ""
    try:
        for evt in A.stream_via_bedrock_qwen(prompt, [{"role": "user", "content": "Output the JSON verdict now."}], model=JUDGE_MODEL):
            if isinstance(evt, str) and evt.startswith("data: "):
                try:
                    d = json.loads(evt[6:].rstrip("\n"))
                    if d.get("type") == "delta":
                        raw += d.get("text", "")
                    elif d.get("type") == "done":
                        raw = d.get("full", raw) or raw
                        break
                    elif d.get("type") == "error":
                        return ""
                except Exception:
                    pass
    except Exception:
        return ""
    return raw.strip()


def _extract_json(text: str) -> dict:
    """Robustly extract a JSON object from possibly-noisy LLM output."""
    if not text:
        return {}
    # Try strict parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Find the first {...} block
    m = re.search(r'\{.*\}', text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return {}
    return {}


def judge_review(reply: str, user_last: str, turn_number: int,
                 has_memory: bool) -> tuple:
    """Drop-in replacement for the regex output guard. Returns (cleaned_reply, violations_list).
    On any failure (parse error, API error, low confidence), passes through the original reply
    rather than overwriting Maya's voice with garbage."""
    if not reply or not reply.strip():
        return reply, []

    # Trim user_last for prompt budget
    user_last_trim = (user_last or "(no prior user message — this is the opening turn)")[:1500]

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        turn_number=turn_number,
        has_memory=str(bool(has_memory)).lower(),
        user_last_message=user_last_trim,
        reply_text=reply,
    )

    raw = _call_qwen_judge(prompt)
    parsed = _extract_json(raw)

    if not parsed:
        return reply, ["judge_parse_failed"]

    verdict = parsed.get("verdict", "ok")
    violations = parsed.get("violations_found", []) or []
    rewritten = parsed.get("rewritten_reply")
    confidence = float(parsed.get("confidence", 1.0))

    if verdict == "rewrite" and rewritten and confidence >= JUDGE_CONFIDENCE_FLOOR:
        return rewritten, violations
    return reply, violations


def apply_judge_guard(raw_full_text: str, user_last_message: str, mem: dict,
                      is_first_reply: bool = False) -> tuple:
    """Adapter with the same signature as the old pg_apply_output_guard.
    Returns (cleaned_text, stripped) where stripped is a list of (rule_key, snippet) tuples
    so existing logging code continues to work."""
    if not raw_full_text or not raw_full_text.strip():
        return raw_full_text, []
    has_memory = bool(
        (mem or {}).get("facts") or
        (mem or {}).get("events") or
        (mem or {}).get("moments")
    )
    turn_number = 1 if is_first_reply else 2
    cleaned, violations = judge_review(
        reply=raw_full_text,
        user_last=user_last_message,
        turn_number=turn_number,
        has_memory=has_memory,
    )
    stripped = []
    if cleaned != raw_full_text:
        snippet = (raw_full_text[:60] + "…") if len(raw_full_text) > 60 else raw_full_text
        for v in (violations or []):
            stripped.append((v, snippet))
        if not stripped:
            stripped.append(("judge_rewrite", snippet))
    return cleaned, stripped
