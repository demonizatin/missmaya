# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **27.6 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **12%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **1**
- Total stale-phrase hits across all sessions: **6**
- Sessions with a clean wrap-up signal: **6**

## Ranked gaps (severity × frequency)

### 1. `opener_repetition`  · severity 5 · freq 6.7% · score 250
**Layer**: guard

1 pairs of openers across same-user sessions had >=0.65 structural similarity.

Examples:
- u04_neha sessions 47 ↔ 48 (sim 0.93): `Hi Neha, I'm Miss Maya. Honestly, the first sip of cardamom chai in monsoon mornings makes my whole week. What’s on your` ↔ `Hi Neha, I'm Miss Maya. Honestly, the first sip of cardamom chai in monsoon mornings makes my whole week. How was your d`

**Suggested fix**: Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.

### 2. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 12% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 3. `multiple_questions_per_reply`  · severity 3 · freq 40.0% · score 120
**Layer**: prompt

Maya included 2+ questions in 14 replies across 6 sessions (Rule 9 violation).

Examples:
- session 3 turn 1: `Hi Priyansh, fixed a bug today? Work wins feel great. How did it go?`
- session 7 turn 5: `Dramas with a message always stay with you, don’t they? Aamir Khan’s old films are classics for a reason. "Dil Bechara" sounds emotional — did you listen to the`
- session 10 turn 3: `"Got it — secure and fast gateways are tricky. Did the team break it into smaller parts? The movie sounds fun — who’s coming?"`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 4. `stale_phrase_hindi_songs_persona_cycle`  · severity 4 · freq 26.7% · score 107
**Layer**: prompt+guard

Maya used the stale phrase tagged 'hindi_songs_persona_cycle' in 4/15 sessions (26.7%).

Examples:
- session 2 turn 1: `Hi Priyansh, I'm Miss Maya. Honestly, old Hindi songs make my day when I'm driving. Did you have a good day?`
- session 2 turn 6: `"Got it — Arijit, Lata, and cricket make the perfect evening mix. I lean toward old Hindi songs too. What’s your go-to track when you want to just chill?"`
- session 2 turn 7: `"Lata’s 'Ye hai to yehi' is a classic for a reason — timeless peace. I like old Hindi songs too. Any old rock song you’d recommend?"`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 5. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 13.3% · score 53
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 2/15 sessions (13.3%).

Examples:
- session 46 turn 2: `"Ugh, that morning sounds rough. A bad coffee and a slow laptop — worst combo. Your walk sounds like the perfect escape. I'm a tea person, but I get how importa`
- session 49 turn 3: `That sounds rough — deadlines and revisions are heavy. At least you're pushing through. I'm a huge tea person, so I get the chai experiment. Still, better than `

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.
