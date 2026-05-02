"""eval_validate_batch.py — re-run a targeted subset of sessions to validate
a fix batch. Saves to memory_store/_eval_50/validation_<batch_name>/ so the
baseline transcripts in memory_store/_eval_50/transcripts/ are preserved for
side-by-side comparison.

Usage:
    python eval_validate_batch.py batch1
"""

import argparse
import json
import sys
import time
from pathlib import Path

import eval_50 as E
import app as A


def run_validation(batch_name: str, tiers: list):
    """Re-run all sessions whose label starts with one of the tier prefixes.
    Saves transcripts to a batch-specific subfolder + memory to a fresh isolate."""
    out_dir = E.EVAL_DIR / f"validation_{batch_name}"
    out_dir.mkdir(exist_ok=True)
    transcripts_dir = out_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    memory_dir = out_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    pending_dir = out_dir / "_pending_merges"
    pending_dir.mkdir(exist_ok=True)

    # Monkey-patch eval_50 to use the validation paths.
    E.EVAL_TRANSCRIPTS_DIR = transcripts_dir
    E.EVAL_MEMORY_DIR = memory_dir
    E.EVAL_DIR = out_dir   # so library writes pending_merges in the right place

    schedule = [s for s in E.build_schedule() if s["label"][0] in tiers]
    print(f"=== validation '{batch_name}': running {len(schedule)} sessions ===")
    print(f"  Output: {transcripts_dir}")
    print(f"  Memory: {memory_dir}")
    print(f"  Tiers:  {tiers}\n")

    failed = []
    for spec in schedule:
        try:
            E.run_session(spec, log_fn=print)
        except Exception as e:
            print(f"!! session {spec['idx']} failed: {e}")
            failed.append(spec['idx'])
    print(f"\n=== Done. {len(schedule) - len(failed)} ok, {len(failed)} failed ===")
    return transcripts_dir


def analyze_validation(transcripts_dir: Path, batch_name: str):
    """Use the same analyzers from eval_50 + the hallucination scanner against
    the validation transcripts only. Returns (gap_report, hallucination_report)."""
    sessions = []
    for p in sorted(transcripts_dir.glob("*.json")):
        try:
            sessions.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  skipping {p.name}: {e}", file=sys.stderr)

    if not sessions:
        print("No sessions to analyze.")
        return None, None

    gap_report = E.build_gap_report(sessions)
    gap_md = E.render_report_md(gap_report)

    # Hallucination scan
    import eval_50_hallucinations as H
    per_session = [H.scan_session(s) for s in sessions]
    halluc_summary = H.summarise(per_session)
    halluc_md = H.render_report_md(halluc_summary, per_session)

    # Save
    out_dir = transcripts_dir.parent
    (out_dir / f"gap_report_{batch_name}.md").write_text(gap_md, encoding="utf-8")
    (out_dir / f"gap_report_{batch_name}.json").write_text(json.dumps(gap_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / f"hallucination_report_{batch_name}.md").write_text(halluc_md, encoding="utf-8")
    (out_dir / f"hallucination_report_{batch_name}.json").write_text(json.dumps({"summary": halluc_summary, "per_session": per_session}, indent=2, ensure_ascii=False), encoding="utf-8")

    return gap_report, halluc_summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", help="batch name (e.g. batch1)")
    parser.add_argument("--tiers", default="A,E", help="comma-separated tier prefixes to include (default: A,E)")
    parser.add_argument("--analyze-only", action="store_true", help="skip run, just analyze existing")
    args = parser.parse_args()
    tiers = args.tiers.split(",")

    if not args.analyze_only:
        out = run_validation(args.batch, tiers)
    else:
        out = E.EVAL_DIR / f"validation_{args.batch}" / "transcripts"
        if not out.exists():
            print(f"No transcripts at {out}", file=sys.stderr)
            sys.exit(1)

    gap_report, halluc_summary = analyze_validation(out, args.batch)
    if gap_report is None:
        return

    print("\n" + "=" * 60)
    print(f"VALIDATION REPORT — {args.batch}")
    print("=" * 60)
    print(f"\nSessions: {gap_report['session_count']}")
    print(f"\nTop-line metrics:")
    for k, v in gap_report['summary_metrics'].items():
        print(f"  {k}: {v}")
    print(f"\nRanked gaps (top 5):")
    for g in gap_report['ranked_gaps'][:5]:
        print(f"  - {g['id']:40s} sev {g['severity']}  freq {g['frequency_pct']}%  count {g['count']}")
    print(f"\nHallucination categories:")
    for cat in ["A_titles", "B_named_entities", "C_personal_claims", "D_fake_quotes"]:
        t = halluc_summary['category_totals'].get(cat, 0)
        s = halluc_summary['category_session_counts'].get(cat, 0)
        print(f"  {cat:25s} hits={t}  sessions={s}")


if __name__ == "__main__":
    main()
