# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **29.2 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **7%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **0**
- Total stale-phrase hits across all sessions: **1**
- Sessions with a clean wrap-up signal: **11**

## Ranked gaps (severity × frequency)

### 1. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 7% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 2. `multiple_questions_per_reply`  · severity 3 · freq 33.3% · score 100
**Layer**: prompt

Maya included 2+ questions in 7 replies across 5 sessions (Rule 9 violation).

Examples:
- session 4 turn 4: `Actors bringing raw emotion to screen — that’s powerful. Cricket matches and good films both carry that energy, don’t they? I follow cricket — the drama of a ti`
- session 7 turn 5: `It’s okay to feel stuck sometimes — no need to fix it right away. If you did pick something new, what would it be? Something tiny, just to shift the rhythm?`
- session 8 turn 4: `You said that clearly — I get it, long stories can drag. Sometimes a lighter film helps. What about *Raees*? It has some nice drama and action balance. Or a com`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 3. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 1/15 sessions (6.7%).

Examples:
- session 50 turn 1: `Hi Neha, your laptop survived the coffee spill? I'm a tea person myself — no drama, just hot leaves.`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.
