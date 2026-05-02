# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **29.4 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **13%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **0**
- Total stale-phrase hits across all sessions: **4**
- Sessions with a clean wrap-up signal: **7**

## Ranked gaps (severity × frequency)

### 1. `multiple_questions_per_reply`  · severity 3 · freq 73.3% · score 220
**Layer**: prompt

Maya included 2+ questions in 18 replies across 11 sessions (Rule 9 violation).

Examples:
- session 2 turn 2: `That sounds rewarding. Cricket commentary is fun to listen to, isn't it? What team are you cheering for these days?`
- session 3 turn 1: `Hi Priyansh, the cricket final is in three days — what snacks will you have at 7:00 PM? I'm a tea person, but you?`
- session 4 turn 10: `"Movie marathon energy for the final — no breaks, no distractions. Got it. What will you do if MI wins? Any traditions?"`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 2. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 13% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 3. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 13.3% · score 53
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 2/15 sessions (13.3%).

Examples:
- session 3 turn 1: `Hi Priyansh, the cricket final is in three days — what snacks will you have at 7:00 PM? I'm a tea person, but you?`
- session 10 turn 1: `Hi Priyansh, I'm Miss Maya. I'm a tea person — it's my evening comfort. How was your day?`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 4. `stale_phrase_mango_persona_cycle`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt+guard

Maya used the stale phrase tagged 'mango_persona_cycle' in 1/15 sessions (6.7%).

Examples:
- session 2 turn 1: `Hi Priyansh, mango season is here — my favorite time of the year! What's been on your mind today?`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 5. `stale_phrase_love_how_you_opener`  · severity 3 · freq 6.7% · score 20
**Layer**: prompt+guard

Maya used the stale phrase tagged 'love_how_you_opener' in 1/15 sessions (6.7%).

Examples:
- session 48 turn 6: `You turn “color choice anxiety” into chaos — I love how you lean into the drama. Both options work: scribble the list *then* sing “Good Life” on loop. Add a dan`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.
