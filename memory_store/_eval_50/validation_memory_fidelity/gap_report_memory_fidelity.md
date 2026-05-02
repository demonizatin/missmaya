# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **25.1 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **17%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **0**
- Total stale-phrase hits across all sessions: **0**
- Sessions with a clean wrap-up signal: **6**

## Ranked gaps (severity × frequency)

### 1. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 17% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 2. `multiple_questions_per_reply`  · severity 3 · freq 20.0% · score 60
**Layer**: prompt

Maya included 2+ questions in 3 replies across 3 sessions (Rule 9 violation).

Examples:
- session 11 turn 4: `"Stress makes it worse, right. Try linking each name to a word that starts with the first letter. For example, M for metoprolol, maybe 'M for muscle relaxer'? W`
- session 18 turn 3: `"Marathi mnemonics are a brilliant touch, makes it personal, right? Flashcards with mechanisms and side effects will help a lot. What’s one key difference you w`
- session 22 turn 4: `"Autonomic drugs can muddle even the best minds, that’s normal. You mentioned color coded charts before, maybe try that with these categories? What’s one agonis`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.
