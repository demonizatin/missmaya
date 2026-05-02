"""judge_preflight.py — gate the judge cutover by running it against a curated test set.

Loads judge_test_set.json, runs each case through judge_review, and reports
precision/recall on each violation category + false-positive rate on benign cases.

Pass criterion: >= 90% recall on violations, <= 10% false-positive rate on benign.
"""

import json
import time
from pathlib import Path

import judge_guard as JG


TEST_SET_PATH = Path(__file__).parent / "judge_test_set.json"


def main():
    data = json.loads(TEST_SET_PATH.read_text(encoding="utf-8"))

    cat_results = {}    # category → {tp, fn, examples_missed}
    benign_fp = 0
    benign_total = 0
    benign_examples = []
    durations = []

    print(f"\n{'='*72}\nJUDGE PRE-FLIGHT — running against curated test set\n{'='*72}\n")

    # Run violation cases
    for cat, cases in data["violations"].items():
        cat_results[cat] = {"tp": 0, "fn": 0, "missed": []}
        for case in cases:
            t0 = time.monotonic()
            cleaned, violations = JG.judge_review(
                reply=case["reply"],
                user_last=case["user_last"],
                turn_number=case.get("turn", 2),
                has_memory=True,
            )
            dt = time.monotonic() - t0
            durations.append(dt)
            # We count it as a TRUE POSITIVE if (a) judge produced a rewrite OR (b) flagged at least 1 violation
            if cleaned != case["reply"] or (violations and violations != ["judge_parse_failed"]):
                cat_results[cat]["tp"] += 1
                print(f"  [{cat}] PASS ({dt:.1f}s) violations={violations}")
            else:
                cat_results[cat]["fn"] += 1
                cat_results[cat]["missed"].append({
                    "reply": case["reply"][:140],
                    "violations_returned": violations,
                })
                print(f"  [{cat}] MISS ({dt:.1f}s) — judge said OK on a known violation")

    # Run benign cases
    print()
    for case in data["benign"]:
        benign_total += 1
        t0 = time.monotonic()
        cleaned, violations = JG.judge_review(
            reply=case["reply"],
            user_last=case["user_last"],
            turn_number=case.get("turn", 3),
            has_memory=True,
        )
        dt = time.monotonic() - t0
        durations.append(dt)
        if cleaned != case["reply"]:
            benign_fp += 1
            benign_examples.append({"reply": case["reply"][:140], "rewritten": cleaned[:140]})
            print(f"  [benign] FALSE POSITIVE ({dt:.1f}s) — judge rewrote a clean reply")
        else:
            print(f"  [benign] OK ({dt:.1f}s)")

    # Summary
    print(f"\n{'='*72}\nSUMMARY\n{'='*72}\n")
    total_tp = sum(c["tp"] for c in cat_results.values())
    total_viol = sum(c["tp"] + c["fn"] for c in cat_results.values())
    overall_recall = total_tp / max(1, total_viol) * 100
    benign_fp_rate = benign_fp / max(1, benign_total) * 100
    avg_duration = sum(durations) / max(1, len(durations))

    print(f"  Overall recall on violations:  {total_tp}/{total_viol} = {overall_recall:.1f}%  (target >= 90%)")
    print(f"  False-positive rate on benign: {benign_fp}/{benign_total} = {benign_fp_rate:.1f}%  (target <= 10%)")
    print(f"  Avg judge call duration:       {avg_duration:.2f}s")
    print()
    print(f"  Per-category recall:")
    for cat in sorted(cat_results.keys()):
        r = cat_results[cat]
        n = r["tp"] + r["fn"]
        rate = r["tp"] / max(1, n) * 100
        print(f"    {cat:20s} {r['tp']}/{n} = {rate:>5.1f}%")
    print()
    if cat_results and any(r["fn"] > 0 for r in cat_results.values()):
        print(f"  Categories with misses (need prompt iteration):")
        for cat, r in cat_results.items():
            for ex in r["missed"][:2]:
                print(f"    [{cat}] reply: {ex['reply']}")
                print(f"          judge returned: {ex['violations_returned']}")
        print()
    if benign_examples:
        print(f"  False-positive details:")
        for ex in benign_examples[:3]:
            print(f"    BENIGN: {ex['reply']}")
            print(f"    REWRITTEN: {ex['rewritten']}")
        print()

    if overall_recall >= 90 and benign_fp_rate <= 10:
        print(f"  → PRE-FLIGHT PASSED. Safe to wire judge into chat endpoints.")
    else:
        print(f"  → PRE-FLIGHT FAILED. Iterate the judge prompt before proceeding.")


if __name__ == "__main__":
    main()
