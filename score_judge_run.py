"""score_judge_run.py — count violations in two transcript folders side-by-side.

Compares the judge-only run against the with-guards-v2 baseline. Per-session,
per-turn categorical scoring + qualitative samples for the report.

Categories (one regex/check each):
  greeting_t2   — turn 2+ Maya reply starts with "Hi|Hey|Hello|Good X" + name
  multi_q       — Maya reply contains >1 '?' character
  bio_hard      — Maya claims "I watched/listened/read/cooked/visited/went to"
  love_how_you  — Maya reply starts with "I love how you / I noticed how / I admire that you / I see that"
  echo_praise   — `you said "X" — (perfect|nicely|great)` pattern
  canned_persona— banned persona phrases ("cardamom chai", "old hindi songs", etc.)
  self_intro_t2 — "I'm Miss Maya" / "I am Miss Maya" / "I am your English chat partner" on turn 2+
  location_claim— "here in Bengaluru / Mumbai memory / I grew up in Pune" patterns
  soft_bio      — "I follow X / I cook / I'm a X person" (sport-following, hobby, persona-trait)
  emoji         — any emoji codepoint
  dashes        — em-dash —, en-dash –, double-hyphen "--", or " - " between words
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent / "memory_store" / "_eval_50"
RUN_A = ROOT / "validation_full_with_guards_v2" / "transcripts"   # before
RUN_B = ROOT / "validation_judge_only" / "transcripts"            # after

NAME_PATTERN = r"(Priyansh|Aarti|Rohan|Neha|Kabir|Diya|Shreya|Ishaan|Meera|Arjun|Riya|Vikram|Ananya|Nikhil|Tanya)"

CHECKS = {
    "greeting_t2": re.compile(rf"^\s*(Hi|Hey|Hello|Good (morning|evening|afternoon)),?\s+{NAME_PATTERN}\b", re.I),
    "multi_q": None,   # custom: count('?') > 1
    "bio_hard": re.compile(r"\bI\s+(just\s+)?(watched|listened to|read|cooked|visited|went to|grew up in|made|baked|saw)\b", re.I),
    "love_how_you": re.compile(r"^\s*I\s+(love how you|noticed how|admire that you|see that you|see how)\b", re.I),
    "echo_praise": re.compile(r"\byou said [\"'][^\"']+[\"']\s*[-—,!.]?\s*(perfect|nicely|great|nice|good|well done)", re.I),
    "canned_persona": re.compile(r"(cardamom chai|chai over coffee|tea over coffee|old hindi (film )?songs|hindi film songs|loves mango|mango season|balcony plants|balcony garden|warm.weather over cold|chai.in.the.evening|i'?m a tea person)", re.I),
    "self_intro_t2": re.compile(r"\bI(?:'| a)?m\s+Miss\s+Maya\b|I am your English chat partner\b", re.I),
    "location_claim": re.compile(r"\b(here in Bengaluru|here in Bangalore|here in Mumbai|here in Delhi|here in Pune|here in Kolkata|Mumbai memory|Bengaluru memory|I grew up in (Bengaluru|Mumbai|Delhi|Pune|Kolkata|Chennai))\b", re.I),
    "soft_bio": re.compile(r"\b(I follow (cricket|football|tennis|hockey|the IPL|MS Dhoni|Mohun Bagan)|I cook \w+|I'?m a (morning|evening|tea|coffee|night|chai) person|I'?m a big fan of (comforting|spicy|street))", re.I),
    "emoji": re.compile(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F600-\U0001F64F]"),
    "dashes": re.compile(r"\w\s*[—–]\s*\w|\w\s+--\s+\w|\w\s+-\s+\w"),
}

def is_violation(category: str, text: str, turn_idx: int, session_label: str, has_memory: bool = False) -> bool:
    if not text or not isinstance(text, str):
        return False
    if category == "multi_q":
        return text.count("?") > 1
    if category == "greeting_t2" and turn_idx == 0 and not has_memory:
        return False   # brand-new user turn 1: greeting allowed
    if category == "self_intro_t2" and turn_idx == 0 and not has_memory:
        return False   # brand-new user turn 1: self-intro allowed
    if category == "love_how_you":
        # Strip a leading "Hi <name>, " before checking the pattern
        stripped = re.sub(rf"^\s*(Hi|Hey|Hello|Good (morning|evening|afternoon)),?\s+{NAME_PATTERN}[,.\s]+", "", text, flags=re.I)
        return bool(CHECKS[category].search(stripped))
    pat = CHECKS[category]
    return bool(pat.search(text))


def score_run(folder: Path, label: str):
    sessions = sorted(folder.glob("*.json"))
    counts = defaultdict(int)             # category → number of MAYA TURNS with at least one hit
    sessions_with = defaultdict(set)      # category → set of session labels
    samples = defaultdict(list)           # category → up to 3 example (session, turn_idx, text)
    total_maya_turns = 0
    total_sessions = 0
    for p in sessions:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        sess_label = p.stem
        total_sessions += 1
        mem_before = data.get("memory_before", {}) if isinstance(data, dict) else {}
        has_memory = bool(
            (mem_before.get("facts") or {}) or
            (mem_before.get("events") or []) or
            (mem_before.get("moments") or [])
        )
        transcript = data.get("transcript", []) if isinstance(data, dict) else []
        # Pull Maya turns + the immediately-prior user message for fake-quote checks
        maya_with_context = []
        for i, msg in enumerate(transcript):
            if isinstance(msg, dict) and msg.get("role") == "maya":
                turn_no = msg.get("turn", 0)
                content = msg.get("content", "")
                user_prev = ""
                for j in range(i - 1, -1, -1):
                    if transcript[j].get("role") == "user":
                        user_prev = transcript[j].get("content", "")
                        break
                maya_with_context.append((turn_no, content, user_prev))
        for (turn_no, m, user_prev) in maya_with_context:
            total_maya_turns += 1
            # turn_no is 1-indexed: turn==1 is the opening Maya reply (greeting/intro allowed)
            turn_idx = max(0, turn_no - 1)
            for cat in CHECKS.keys():
                if is_violation(cat, m, turn_idx, sess_label, has_memory=has_memory):
                    counts[cat] += 1
                    sessions_with[cat].add(sess_label)
                    if len(samples[cat]) < 3:
                        samples[cat].append((sess_label, turn_no, m[:220]))
    return {
        "label": label,
        "folder": str(folder),
        "n_sessions": total_sessions,
        "n_maya_turns": total_maya_turns,
        "counts": dict(counts),
        "sessions_with": {k: sorted(v) for k, v in sessions_with.items()},
        "samples": dict(samples),
    }


def main():
    a = score_run(RUN_A, "WITH-GUARDS (regex, baseline)")
    b = score_run(RUN_B, "JUDGE-ONLY (Qwen judge, after)")
    print()
    print(f"{'='*86}")
    print(f"{'CATEGORY':22s}  {'BEFORE (regex)':28s}  {'AFTER (judge)':28s}")
    print(f"{'='*86}")
    for cat in CHECKS.keys():
        a_turns = a["counts"].get(cat, 0)
        b_turns = b["counts"].get(cat, 0)
        a_sess = len(a["sessions_with"].get(cat, []))
        b_sess = len(b["sessions_with"].get(cat, []))
        a_pct = a_turns / max(1, a["n_maya_turns"]) * 100
        b_pct = b_turns / max(1, b["n_maya_turns"]) * 100
        print(f"  {cat:20s}  {a_turns:3d} turns / {a_sess:2d} sess ({a_pct:4.1f}%)   {b_turns:3d} turns / {b_sess:2d} sess ({b_pct:4.1f}%)")
    print(f"{'='*86}")
    print(f"  TOTAL MAYA TURNS:    {a['n_maya_turns']:>10d}                {b['n_maya_turns']:>10d}")
    print(f"  TOTAL SESSIONS:      {a['n_sessions']:>10d}                {b['n_sessions']:>10d}")
    print()

    # Persist summary + samples
    out = {"baseline": a, "judge_only": b}
    out_path = ROOT / "validation_judge_only" / "score_summary.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Detailed counts + samples written to: {out_path}")

    print()
    print("─"*86)
    print("RESIDUAL VIOLATIONS in JUDGE-ONLY run — first 1 sample each (the things to fix next):")
    print("─"*86)
    for cat in CHECKS.keys():
        if b["counts"].get(cat, 0) > 0:
            sample = b["samples"][cat][0]
            print(f"\n  [{cat}]  ({b['counts'][cat]} turns across {len(b['sessions_with'][cat])} sessions)")
            print(f"    {sample[0]} T{sample[1]}: {sample[2]}")


if __name__ == "__main__":
    main()
