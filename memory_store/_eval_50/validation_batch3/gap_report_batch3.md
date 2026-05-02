# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **29.4 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **20%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **0**
- Total stale-phrase hits across all sessions: **4**
- Sessions with a clean wrap-up signal: **6**

## Ranked gaps (severity × frequency)

### 1. `multiple_questions_per_reply`  · severity 3 · freq 33.3% · score 100
**Layer**: prompt

Maya included 2+ questions in 7 replies across 5 sessions (Rule 9 violation).

Examples:
- session 4 turn 10: `"Bollywood has that built-in shared history, so the references feel like a big group hug.  

Hollywood can be fun too — if you like twists and hidden details, m`
- session 6 turn 2: `You're doing great — 'excited' is a good word. 'Thrilled' adds extra energy. Try this: 'I'm thrilled about the new feature!' Sounds fun, right? Was your meeting`
- session 47 turn 6: `That sounds beautiful — a café owner’s smile makes all the work worth it. Freezing time in a good moment? Yes, I get that. Rain, chai, and a sketchbook… what wo`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.

### 2. `stale_phrase_love_how_you_opener`  · severity 3 · freq 13.3% · score 40
**Layer**: prompt+guard

Maya used the stale phrase tagged 'love_how_you_opener' in 2/15 sessions (13.3%).

Examples:
- session 4 turn 4: `That makes sense — Hindi movies often hide small stories in plain sight. I love how you watch for layers.  

Do you usually take notes while watching a movie, o`
- session 6 turn 1: `Hi Priyansh, I hope your project deadline is going smoothly! I love how you're working on richer ways to talk about emotions — that's a big win for your English`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 3. `stale_phrase_self_intro_in_reply`  · severity 5 · freq 6.7% · score 34
**Layer**: prompt+guard

Maya used the stale phrase tagged 'self_intro_in_reply' in 1/15 sessions (6.7%).

Examples:
- session 46 turn 2: `"Hi Neha, I'm Miss Maya." — I'm sorry to hear your day has been rough. Rainy commutes can be the worst. I hope things turn better for you soon. How about your d`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.

### 4. `stale_phrase_tea_persona_cycle`  · severity 4 · freq 6.7% · score 27
**Layer**: prompt+guard

Maya used the stale phrase tagged 'tea_persona_cycle' in 1/15 sessions (6.7%).

Examples:
- session 7 turn 1: `Hi Priyansh, the first sip of cardamom chai in the evening makes my day brighter. I heard you're planning to watch 'Chhichhore' this weekend — excited about it?`

**Suggested fix**: Add to forbidden-phrase list in QWEN_EXTRA_RULES Rule 35b; mirror as deterministic regex guard in pg_apply_output_guard.
