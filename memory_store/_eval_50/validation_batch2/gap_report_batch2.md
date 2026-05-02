# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **28.1 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **15%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **1**
- Total stale-phrase hits across all sessions: **5**
- Sessions with a clean wrap-up signal: **11**

## Ranked gaps (severity × frequency)

### 1. `opener_repetition`  · severity 5 · freq 6.7% · score 250
**Layer**: guard

1 pairs of openers across same-user sessions had >=0.65 structural similarity.

Examples:
- u01_priyansh sessions 4 ↔ 10 (sim 0.8): `Hi Priyansh, how did your team meeting about the new app feature go today?` ↔ `Hi Priyansh, how was the team meeting about the new app feature?`

**Suggested fix**: Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.

### 2. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 15% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 3. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 26.7% · score 107
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 4/15 sessions (26.7%).

Examples:
- session 2 turn 1: `Hi Priyansh, the monsoon is starting today — I’m a tea person, so I’ll be sipping chai by the window. How was your day at work?`
- session 5 turn 6: `I love a good chaat — spicy and tangy hits the spot! Tea pairs well with it. I’m a tea person too. What chaat do you like best?`
- session 48 turn 1: `Hi Neha, it's been a few days — how's the design work feeling these days? I'm a tea person myself, by the way. What's your take on it?`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 4. `multiple_questions_per_reply`  · severity 3 · freq 26.7% · score 80
**Layer**: prompt

Maya included 2+ questions in 8 replies across 4 sessions (Rule 9 violation).

Examples:
- session 3 turn 5: `I get that — lazy days happen, and plain dal is always there for you. Next time, maybe toss in some chopped tomatoes? It adds a nice kick. What do you think?`
- session 7 turn 2: `"Got it — meetings can be busy. Startup ideas are exciting, right? What kind of app are you thinking about?"`
- session 48 turn 1: `Hi Neha, it's been a few days — how's the design work feeling these days? I'm a tea person myself, by the way. What's your take on it?`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 5. `stale_phrase_hindi_songs_persona_cycle`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt+guard

Maya used the stale phrase tagged 'hindi_songs_persona_cycle' in 1/15 sessions (6.7%).

Examples:
- session 10 turn 6: `"Classic songs like 'Chunariyaan' stick with you for a reason — they're beautiful. I enjoy old Hindi songs too, especially when they feel timeless. What's one y`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 6. `greeting_on_turn_2plus`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt

Maya started a turn-2+ reply with a greeting ('Hi <name>,...') in 1 replies across 1 sessions.

Examples:
- session 48 turn 7: `Hi Neha, "The Winter Kids" sounds interesting. I like how you mix different styles. What's your favorite song by *Vaalee`

**Suggested fix**: Strengthen Rule 1 turn-2+ no-greeting clause OR add a server-side strip in pg_apply_output_guard.
