"""eval_50_hallucinations.py — focused hallucination scan over saved transcripts.

Categories detected (pattern-based, conservative — surfaces candidates the
user can sanity-check, doesn't auto-condemn):

  A. Specific film / book / song titles in quotes or *italics* that the USER
     never mentioned in the session AND aren't in stored memory.
  B. Real-person proper-noun mentions (Virat Kohli, Shahrukh Khan, M.S. Dhoni,
     Shreya Ghoshal, etc. — using a curated list of Indian-culture entities)
     that the user didn't surface and aren't in memory.
  C. Maya claiming personal experience: "I just watched / listened / read /
     was just / saw / went to / made yesterday" — first-person present/past
     experience claims (Rule 25 / Rule 35 — biography fabrication).
  D. Fake quoted user text: 'You said "X"' where X is not in any of the
     user's prior messages this session.
  E. Specific dates / events Maya brings up that aren't in stored memory
     (e.g. "May 5", "last Tuesday" with concrete anchor).
  F. "Notes / records / files" — server-guard regex (already covered).

Output: per-session list of suspected hallucinations + cross-session totals.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

EVAL_DIR = Path(__file__).parent / "memory_store" / "_eval_50"
TRANSCRIPTS_DIR = EVAL_DIR / "transcripts"
REPORT_DIR = EVAL_DIR / "reports"


# ─────────────────────────────────────────────────────────────────────────────
# Curated entity lists — Indian-culture domain. Used for category B detection.
# ─────────────────────────────────────────────────────────────────────────────

CRICKETERS = [
    "Virat Kohli", "Rohit Sharma", "MS Dhoni", "M.S. Dhoni", "Sachin Tendulkar",
    "Yuvraj Singh", "Sourav Ganguly", "Hardik Pandya", "KL Rahul", "Jasprit Bumrah",
    "Rishabh Pant", "Bumrah", "Pant", "Kohli", "Sharma", "Dhoni", "Tendulkar",
    "Smith", "Steve Smith", "Joe Root", "Babar Azam", "Glenn Maxwell", "Ben Stokes",
    "Ravindra Jadeja", "Jadeja", "Shubman Gill", "Gill", "Shreyas Iyer",
]

ACTORS_SINGERS = [
    "Shahrukh Khan", "Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Ranbir Kapoor",
    "Ranveer Singh", "Hrithik Roshan", "Akshay Kumar", "Deepika Padukone",
    "Alia Bhatt", "Priyanka Chopra", "Kareena Kapoor", "Vidya Balan",
    "Nawazuddin Siddiqui", "Manoj Bajpayee", "Pankaj Tripathi", "Irrfan Khan",
    "Shreya Ghoshal", "Arijit Singh", "AR Rahman", "A.R. Rahman", "Lata Mangeshkar",
    "Asha Bhosle", "Kishore Kumar", "Diljit Dosanjh", "Pankaj Udhas",
    "Karan Johar", "Sanjay Leela Bhansali", "Yash Chopra",
]

FILMS_SHOWS = [
    "Pathaan", "Tiger 3", "Tiger Zinda Hai", "Jawan", "Animal", "Dunki",
    "Rock On", "Rock On!!", "Dilwale Dulhania Le Jayenge", "DDLJ",
    "Kabhi Khushi Kabhie Gham", "K3G", "Zindagi Na Milegi Dobara", "ZNMD",
    "Dil Chahta Hai", "Lagaan", "Sholay", "3 Idiots", "PK", "Dangal",
    "Bahubali", "RRR", "KGF", "Pushpa", "Drishyam", "Andhadhun",
    "Jab Tak Hai Jaan", "Veer-Zaara", "Mohabbatein", "Kuch Kuch Hota Hai",
    "Friends", "Game of Thrones", "Sacred Games", "Mirzapur", "Panchayat",
]

SPECIFIC_BIRYANI_PLACES = [
    "Paradise Biryani", "Paradise", "Bawarchi", "Pista House",
    "Behrouz Biryani", "Behrouz",
]

ALL_NAMED_ENTITIES = CRICKETERS + ACTORS_SINGERS + FILMS_SHOWS + SPECIFIC_BIRYANI_PLACES


# ─────────────────────────────────────────────────────────────────────────────
# Category C: first-person experience claims by Maya (suspect for biography)
# ─────────────────────────────────────────────────────────────────────────────

PERSONAL_EXPERIENCE_CLAIMS = [
    re.compile(r"\bi (?:just |recently |yesterday |last (?:week|night|sunday|monday|tuesday|wednesday|thursday|friday|saturday) )?(?:watched|saw|finished watching|caught|streamed)\b", re.I),
    re.compile(r"\bi (?:just |recently |yesterday |last (?:week|night|sunday|monday|tuesday|wednesday|thursday|friday|saturday) )?(?:listened to|heard|put on)\b", re.I),
    re.compile(r"\bi (?:just |recently )?(?:read|finished reading|started reading)\b", re.I),
    re.compile(r"\bi (?:just |recently |yesterday )?(?:made|cooked|baked|tried|tasted)\b", re.I),
    re.compile(r"\bi (?:just |recently |yesterday )?(?:went|visited|traveled|trekked)\b", re.I),
    re.compile(r"\b(?:my|i went to my) (?:friend|cousin|brother|sister|aunt|uncle|nani|dadi|mother|mom|dad) (?:in|from|told me)\b", re.I),
    re.compile(r"\b(?:i was|i'?ve been) (?:just |recently )?(?:thinking about|wondering about|reading about)\b", re.I),
    re.compile(r"\bi try to\b", re.I),
    re.compile(r"\b(?:my favorite|my favourite) (?:song|movie|book|recipe|food|dish|drink|place|spot)\b", re.I),
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def collect_user_corpus(transcript: list, mem_before: dict) -> str:
    """Concatenate everything the user said + all stored memory text. Maya is
    allowed to reference anything in this corpus."""
    parts = []
    for m in transcript:
        if m.get("role") == "user":
            parts.append((m.get("content") or "").lower())
    # Memory: facts (values), events.what, moments.text
    facts = mem_before.get("facts") or {}
    for v in facts.values():
        if isinstance(v, list):
            parts.extend([str(x).lower() for x in v])
        elif isinstance(v, str):
            parts.append(v.lower())
        elif v is not None:
            parts.append(str(v).lower())
    for ev in (mem_before.get("events") or []):
        parts.append(str(ev.get("what") or "").lower())
    for mo in (mem_before.get("moments") or []):
        parts.append(str(mo.get("text") or "").lower())
    return " ".join(parts)


def find_quoted_titles(text: str) -> list:
    """Pull strings inside *...* (markdown italics) or "..." that look like
    titles (capitalised, multi-word, or known long film titles)."""
    out = []
    # *italic* — common Maya choice for film titles
    for m in re.finditer(r"\*([^*\n]{3,80})\*", text):
        out.append(m.group(1).strip())
    # "double-quoted"
    for m in re.finditer(r"[\"“]([A-Z][A-Za-z0-9 ,&!\-:'\.]{2,80})[\"”]", text):
        out.append(m.group(1).strip())
    return out


def find_known_entities(text: str) -> list:
    """Find any ALL_NAMED_ENTITIES present in `text`."""
    found = []
    text_l = text.lower()
    for ent in ALL_NAMED_ENTITIES:
        if ent.lower() in text_l:
            found.append(ent)
    return found


def find_personal_experience_claims(text: str) -> list:
    matches = []
    for pat in PERSONAL_EXPERIENCE_CLAIMS:
        for m in pat.finditer(text):
            # Capture ~30 chars of context after the match
            start = m.start()
            end = min(len(text), m.end() + 60)
            matches.append(text[start:end].strip())
    return matches


def find_quoted_user_claims(text: str) -> list:
    """Find phrases like 'You said "X"' or 'You mentioned "X"' — captures X."""
    out = []
    for m in re.finditer(r"\byou (?:said|mentioned|told me|told us)[,:]?\s*[\"“]([^\"”]{3,100})[\"”]", text, re.I):
        out.append(m.group(1).strip())
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Per-session scan
# ─────────────────────────────────────────────────────────────────────────────

def scan_session(session: dict) -> dict:
    transcript = session.get("transcript", [])
    mem_before = session.get("memory_before", {}) or {}
    user_corpus = collect_user_corpus(transcript, mem_before)

    suspect = {
        "A_titles": [],            # film/book/song titles ungrounded
        "B_named_entities": [],    # cricketers/actors ungrounded
        "C_personal_claims": [],   # Maya biography fabrication
        "D_fake_quotes": [],       # 'You said "X"' where X not in user corpus
    }

    for m in transcript:
        if m.get("role") != "maya":
            continue
        text = m.get("content") or ""
        turn = m.get("turn")

        # A: Quoted/italicised titles
        for title in find_quoted_titles(text):
            if title.lower() not in user_corpus:
                suspect["A_titles"].append({"turn": turn, "title": title, "snippet": text[:200]})

        # B: Named entities
        for ent in find_known_entities(text):
            if ent.lower() not in user_corpus:
                suspect["B_named_entities"].append({"turn": turn, "entity": ent, "snippet": text[:200]})

        # C: First-person experience claims
        for claim in find_personal_experience_claims(text):
            suspect["C_personal_claims"].append({"turn": turn, "claim": claim, "snippet": text[:200]})

        # D: Fake quoted user text
        for q in find_quoted_user_claims(text):
            if q.lower() not in user_corpus:
                suspect["D_fake_quotes"].append({"turn": turn, "fake_quote": q, "snippet": text[:200]})

    return {
        "session_idx": session["spec"]["idx"],
        "label": session["spec"]["label"],
        "user_name": session["profile"]["user_name"],
        "suspect": suspect,
        "totals": {k: len(v) for k, v in suspect.items()},
    }


def summarise(per_session: list) -> dict:
    n = len(per_session)
    cat_totals = defaultdict(int)
    sessions_with_any = defaultdict(set)
    examples = defaultdict(list)
    for ps in per_session:
        for cat, items in ps["suspect"].items():
            cat_totals[cat] += len(items)
            if items:
                sessions_with_any[cat].add(ps["session_idx"])
            for it in items[:2]:
                examples[cat].append({
                    "session_idx": ps["session_idx"], "label": ps["label"],
                    "user": ps["user_name"], **it,
                })
    return {
        "session_count": n,
        "category_totals": dict(cat_totals),
        "category_session_counts": {k: len(v) for k, v in sessions_with_any.items()},
        "examples": {k: v[:8] for k, v in examples.items()},
    }


def render_report_md(summary: dict, per_session: list) -> str:
    n = summary["session_count"]
    lines = []
    lines.append("# Eval-50 hallucination scan")
    lines.append("")
    lines.append(f"**Sessions analysed**: {n}")
    lines.append("")
    lines.append("## Detection categories")
    lines.append("")
    lines.append("- **A. Ungrounded titles** — film/book/song names Maya put in *italics* or \"quotes\" that the user never mentioned and aren't in stored memory.")
    lines.append("- **B. Ungrounded named entities** — celebrities/cricketers/actors mentioned without user introducing them and not in memory.")
    lines.append("- **C. Personal-experience claims** — first-person statements (\"I just watched X\", \"I went to my nani's\") that risk Rule 35 biography fabrication. Note: Rule 35a allows low-stakes preferences (\"I'm a tea person\"), so each claim needs human review — this is a pattern flag, not a confirmed violation.")
    lines.append("- **D. Fake quoted user text** — `You said \"X\"` where X doesn't appear in the user's actual messages.")
    lines.append("")
    lines.append("## Top-line counts")
    lines.append("")
    lines.append("| Category | Total hits | Sessions affected |")
    lines.append("| --- | ---: | ---: |")
    for cat in ["A_titles", "B_named_entities", "C_personal_claims", "D_fake_quotes"]:
        t = summary["category_totals"].get(cat, 0)
        s = summary["category_session_counts"].get(cat, 0)
        lines.append(f"| {cat} | {t} | {s} / {n} |")
    lines.append("")

    for cat, label in [
        ("A_titles", "A. Ungrounded titles"),
        ("B_named_entities", "B. Ungrounded named entities"),
        ("C_personal_claims", "C. Personal-experience claims (review carefully — some are legit per Rule 35a)"),
        ("D_fake_quotes", "D. Fake quoted user text"),
    ]:
        lines.append(f"## {label}")
        lines.append("")
        examples = summary["examples"].get(cat, [])
        if not examples:
            lines.append("_No instances detected._")
            lines.append("")
            continue
        for ex in examples:
            sid = ex.get("session_idx", "?")
            user = ex.get("user", "?")
            turn = ex.get("turn", "?")
            label_text = ex.get("title") or ex.get("entity") or ex.get("claim") or ex.get("fake_quote") or ""
            snippet = ex.get("snippet", "")[:250]
            lines.append(f"- **session {sid}** ({user}) turn {turn} — `{label_text}`")
            lines.append(f"  > {snippet}")
        lines.append("")
    return "\n".join(lines)


def main():
    sessions = []
    for p in sorted(TRANSCRIPTS_DIR.glob("*.json")):
        try:
            sessions.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  skipping {p.name}: {e}", file=sys.stderr)
    if not sessions:
        print(f"No sessions in {TRANSCRIPTS_DIR}", file=sys.stderr)
        sys.exit(1)

    per_session = [scan_session(s) for s in sessions]
    summary = summarise(per_session)
    md = render_report_md(summary, per_session)

    from datetime import datetime
    out_md = REPORT_DIR / f"hallucination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_md.write_text(md, encoding="utf-8")
    out_json = REPORT_DIR / f"hallucination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_json.write_text(json.dumps({"summary": summary, "per_session": per_session}, indent=2, ensure_ascii=False), encoding="utf-8")

    print(md)
    print(f"\nSaved: {out_md}")
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
