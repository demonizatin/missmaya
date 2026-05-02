"""eval_50_memory_fidelity.py — measure memory appropriateness on a finished run.

Three metrics:
  1. Type-tag presence in saved memory (did the librarian add (movie), (song), (exam), etc.?)
  2. Filler-turn memory hooks (did Maya force memory refs on "ok"/"thanks" turns? — should be 0)
  3. Type-fidelity violations (did Maya call a stored "X (movie)" a "song" or vice versa?)

Reads from a transcripts directory and the corresponding memory snapshots.
"""

import json
import re
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent / "memory_store" / "_eval_50"

# Filler responses — short user replies that should NOT trigger a memory hook
FILLER_RE = re.compile(r"^\s*(?:ok|okay|yes|no|sure|thanks|thank\s+you|yeah|got\s+it|hmm|right|k|nice|cool|oh|fine|good)[.!]?\s*$", re.I)

# Common "kinds" the librarian should embed
KNOWN_KINDS = {"movie", "song", "album", "book", "podcast", "show", "game",
               "sport", "exam", "project", "trip", "restaurant", "dish",
               "person", "festival", "event", "author", "place"}

# Heuristic: Maya referring to a stored named thing — extract candidate names from memory items
NAMED_RE = re.compile(r"\(([a-z]+)\)$", re.I)   # captures the kind in parentheses


def extract_tagged_items(mem: dict) -> list:
    """Pull every stored item that has a (kind) tag at the end. Returns [(name, kind, source_bucket)]."""
    tagged = []
    for ev in (mem.get("events") or []):
        what = (ev.get("what") or "").strip()
        m = NAMED_RE.search(what)
        if m:
            kind = m.group(1).lower()
            name = NAMED_RE.sub("", what).strip()
            tagged.append((name, kind, "event"))
    for mo in (mem.get("moments") or []):
        text = (mo.get("text") or "").strip()
        m = NAMED_RE.search(text)
        if m:
            kind = m.group(1).lower()
            name = NAMED_RE.sub("", text).strip()
            tagged.append((name, kind, "moment"))
    return tagged


def find_filler_violations(transcript: list, mem_items: list) -> list:
    """Find Maya turns that forced a memory reference on a filler user turn."""
    out = []
    name_lookup = [name.lower() for name, _kind, _src in mem_items if len(name) >= 4]
    for i, m in enumerate(transcript):
        if m["role"] != "user": continue
        if not FILLER_RE.match(m["content"] or ""): continue
        # Find Maya's next reply
        for j in range(i + 1, len(transcript)):
            if transcript[j]["role"] == "maya":
                maya_text = (transcript[j]["content"] or "").lower()
                refs = [name for name in name_lookup if name in maya_text]
                if refs:
                    out.append({
                        "filler_user": m["content"][:60],
                        "maya_reply": transcript[j]["content"][:200],
                        "names_referenced": refs,
                    })
                break
    return out


def find_fidelity_violations(transcript: list, mem_items: list) -> list:
    """Find Maya turns that referenced a stored item with the WRONG type label.
    Conservative: only fires if Maya uses an explicit conflicting kind word."""
    out = []
    # Build lookups: name → expected_kind
    name_to_kind = {name.lower(): kind.lower() for name, kind, _src in mem_items}
    # Aliases for common confusions
    kind_words = {
        "movie": ["movie", "film"],
        "song": ["song", "track", "tune", "number"],
        "book": ["book", "novel"],
        "show": ["show", "series"],
        "podcast": ["podcast"],
        "exam": ["exam", "test"],
        "trip": ["trip", "journey"],
        "restaurant": ["restaurant", "place to eat"],
        "dish": ["dish", "food", "recipe"],
        "festival": ["festival", "celebration"],
        "person": ["person"],
    }
    for m in transcript:
        if m["role"] != "maya": continue
        text_lower = (m["content"] or "").lower()
        for name, expected_kind in name_to_kind.items():
            if name not in text_lower: continue
            if expected_kind not in kind_words: continue
            # Look at small window around the name for kind-words
            idx = text_lower.find(name)
            window = text_lower[max(0, idx - 40): idx + len(name) + 40]
            wrong_kinds = [k for k, words in kind_words.items()
                          if k != expected_kind and any(w in window for w in words)]
            if wrong_kinds:
                out.append({
                    "name": name, "expected_kind": expected_kind,
                    "called_it": wrong_kinds, "snippet": window,
                })
    return out


def analyse(dir: Path) -> dict:
    sessions = []
    for p in sorted(dir.glob("*.json")):
        try:
            sessions.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  skip {p.name}: {e}", file=sys.stderr)

    total_tagged_items = 0
    sessions_with_any_tag = 0
    kind_counts = {}
    total_filler_violations = 0
    sessions_with_filler_viol = 0
    total_fidelity_violations = 0
    sample_filler = []
    sample_fidelity = []

    # We use memory_AFTER each session because that's where the librarian's
    # type-tag work shows up (the after-state of memory).
    for s in sessions:
        mem_after = s.get("memory_after", {}) or {}
        tagged = extract_tagged_items(mem_after)
        if tagged:
            sessions_with_any_tag += 1
            total_tagged_items += len(tagged)
            for _name, kind, _src in tagged:
                kind_counts[kind] = kind_counts.get(kind, 0) + 1

        # Run filler check using whatever was in memory BEFORE the session (Maya's working set)
        mem_before = s.get("memory_before", {}) or {}
        all_items = extract_tagged_items(mem_before)
        # Also include facts list values (interests etc.) for filler-check coverage
        for v in (mem_before.get("facts") or {}).values():
            if isinstance(v, list):
                for it in v: all_items.append((str(it), "fact_item", "fact"))
            elif isinstance(v, str) and len(v) >= 4:
                all_items.append((v, "fact_item", "fact"))

        filler_viol = find_filler_violations(s["transcript"], all_items)
        if filler_viol:
            sessions_with_filler_viol += 1
            total_filler_violations += len(filler_viol)
            for f in filler_viol[:1]:
                sample_filler.append({"label": s["spec"]["label"], **f})

        # Fidelity check
        fid_viol = find_fidelity_violations(s["transcript"], all_items)
        if fid_viol:
            total_fidelity_violations += len(fid_viol)
            for f in fid_viol[:1]:
                sample_fidelity.append({"label": s["spec"]["label"], **f})

    n = len(sessions)
    print()
    print(f"=== MEMORY APPROPRIATENESS — {dir.name} ===\n")
    print(f"Sessions analysed:                                {n}")
    print()
    print(f"-- Type tags in librarian-saved memory --")
    print(f"  Total tagged items across sessions (after librarian ran): {total_tagged_items}")
    print(f"  Sessions where ≥1 stored item has a type tag:   {sessions_with_any_tag} / {n}")
    if kind_counts:
        print(f"  Tag breakdown: " + ", ".join(f"{k}={v}" for k, v in sorted(kind_counts.items(), key=lambda x: -x[1])))
    print()
    print(f"-- Filler-turn memory hooks --")
    print(f"  Filler-turn violations (Maya forcing memory ref on 'ok'/'yes'/'thanks'): {total_filler_violations}")
    print(f"  Sessions with at least one filler-violation:    {sessions_with_filler_viol} / {n}")
    if sample_filler:
        print()
        print(f"  Sample filler violations (first 3):")
        for f in sample_filler[:3]:
            print(f"    [{f['label']}] user said {f['filler_user']!r}")
            print(f"      Maya: {f['maya_reply']}")
            print(f"      Maya referenced: {f['names_referenced']}")
    print()
    print(f"-- Type-fidelity violations --")
    print(f"  Total violations (Maya called stored 'X (movie)' a 'song' etc.): {total_fidelity_violations}")
    if sample_fidelity:
        print()
        print(f"  Sample fidelity violations (first 3):")
        for f in sample_fidelity[:3]:
            print(f"    [{f['label']}] '{f['name']}' is stored as {f['expected_kind']}, Maya called it {f['called_it']}")
            print(f"      ...{f['snippet']}...")
    print()


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        EVAL_DIR / "validation_memory_fidelity" / "transcripts"
    if not target.exists():
        print(f"Not found: {target}")
        sys.exit(1)
    analyse(target)
