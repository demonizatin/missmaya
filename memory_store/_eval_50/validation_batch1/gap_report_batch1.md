# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **30.3 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **7%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **1**
- Total stale-phrase hits across all sessions: **6**
- Sessions with a clean wrap-up signal: **9**

## Ranked gaps (severity × frequency)

### 1. `opener_repetition`  · severity 5 · freq 6.7% · score 250
**Layer**: guard

1 pairs of openers across same-user sessions had >=0.65 structural similarity.

Examples:
- u01_priyansh sessions 5 ↔ 6 (sim 0.88): `Hi Priyansh, I hope your weekend plans went well! Speaking of which, did you get a chance to walk in the park while list` ↔ `Hi Priyansh, I hope your weekend plans went well. Did you get a chance to try walking in the park while listening to som`

**Suggested fix**: Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.

### 2. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 7% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 3. `multiple_questions_per_reply`  · severity 3 · freq 40.0% · score 120
**Layer**: prompt

Maya included 2+ questions in 15 replies across 6 sessions (Rule 9 violation).

Examples:
- session 2 turn 6: `Right, that scene was incredible! Parkour sounds fun — you’d start slow, of course. What made you want to try it? The thrill?`
- session 4 turn 6: `You're doing great, just a small tweak — we say "do you like action movies?" instead of "by the way, do you like action movies?" 😊  
Miss Maya here — I enjoy ac`
- session 5 turn 9: `I get that — Bollywood dramas are the best way to switch off. Work stress needs *big* drama to melt away, right? I’m all for simple comforts — a film, some quie`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 4. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 20.0% · score 80
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 3/15 sessions (20.0%).

Examples:
- session 8 turn 2: `That sounds lovely! Watching an emotional movie can be so comforting. I'm a tea person, but I understand the need for drama — it helps unwind. Did you enjoy the`
- session 46 turn 7: `You love masala chai for sketching — nice! I’m a tea person, but I get needing coffee for long days. Do you mostly drink black tea, or do you prefer it with mil`
- session 49 turn 4: `That part sounds tricky — I totally understand the *thud*. I'm a tea person, honestly, but even I'd need a strong cup right now. What's the one thing about acce`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 5. `stale_phrase_love_how_you_opener`  · severity 3 · freq 13.3% · score 40
**Layer**: prompt+guard

Maya used the stale phrase tagged 'love_how_you_opener' in 2/15 sessions (13.3%).

Examples:
- session 7 turn 10: `You said *khubsurat* perfectly — I love how you used it! Gulab jamuns are hard to beat, really. Take care, and tell me how your meeting goes!`
- session 9 turn 1: `Hi Priyansh, I'm Miss Maya. You know, I love how you said 'hit a six' so naturally — it made the story vivid! Did your meeting go smoothly today?`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 6. `stale_phrase_echo_praise`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt+guard

Maya used the stale phrase tagged 'echo_praise' in 1/15 sessions (6.7%).

Examples:
- session 10 turn 9: `That’s a fantastic choice — Virat’s mindset is something to admire! You said "inspiring" perfectly. I might watch it now. What made his training stand out to yo`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 7. `greeting_on_turn_2plus`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt

Maya started a turn-2+ reply with a greeting ('Hi <name>,...') in 1 replies across 1 sessions.

Examples:
- session 48 turn 9: `Hi Neha, I love that — walking in the rain sounds like a little reset. I’m more of a "carry an umbrella" person, but I g`

**Suggested fix**: Strengthen Rule 1 turn-2+ no-greeting clause OR add a server-side strip in pg_apply_output_guard.
