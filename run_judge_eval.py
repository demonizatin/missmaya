"""run_judge_eval.py — wrapper that runs eval_50.run_all() into an isolated
output directory so the judge-only run doesn't clobber the existing
with-guards baseline transcripts.
"""

import sys
from pathlib import Path

import eval_50 as E

ISOLATED_ROOT = E.EVAL_DIR / "validation_judge_only"
ISOLATED_ROOT.mkdir(exist_ok=True)
ISOLATED_TRANSCRIPTS = ISOLATED_ROOT / "transcripts"
ISOLATED_TRANSCRIPTS.mkdir(exist_ok=True)
ISOLATED_MEMORY = ISOLATED_ROOT / "memory"
ISOLATED_MEMORY.mkdir(exist_ok=True)

E.EVAL_TRANSCRIPTS_DIR = ISOLATED_TRANSCRIPTS
E.EVAL_MEMORY_DIR = ISOLATED_MEMORY
E.EVAL_RUN_LOG = ISOLATED_ROOT / "run_log.jsonl"

print(f"=== judge-only eval driver ===")
print(f"  transcripts → {ISOLATED_TRANSCRIPTS}")
print(f"  memory      → {ISOLATED_MEMORY}")
print()

E.run_all(skip_done=True)
