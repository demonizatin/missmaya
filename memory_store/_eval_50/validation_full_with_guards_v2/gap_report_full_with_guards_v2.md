# Eval-50 gap report

**Sessions analysed**: 50

## Top-line metrics
- Average reply length: **23.7 words**
- Replies over 120 words: **0**
- Replies under 8 words: **1**
- Avg memory-reference rate (returning-user sessions): **13%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **11**
- Total stale-phrase hits across all sessions: **0**
- Sessions with a clean wrap-up signal: **22**

## Ranked gaps (severity × frequency)

### 1. `opener_repetition`  · severity 5 · freq 22.0% · score 250
**Layer**: guard

11 pairs of openers across same-user sessions had >=0.65 structural similarity.

Examples:
- u01_priyansh sessions 2 ↔ 5 (sim 0.71): `Hi Priyansh, the India vs Australia match today is on, what's your call on who wins?` ↔ `Hi Priyansh, the India vs Australia match is today, are you watching it?`
- u04_neha sessions 46 ↔ 47 (sim 1.0): `[maya error: [bedrock-qwen] An error occurred (AccessDeniedException) when calling the ConverseStream operation: Bearer ` ↔ `[maya error: [bedrock-qwen] An error occurred (AccessDeniedException) when calling the ConverseStream operation: Bearer `
- u04_neha sessions 46 ↔ 48 (sim 1.0): `[maya error: [bedrock-qwen] An error occurred (AccessDeniedException) when calling the ConverseStream operation: Bearer ` ↔ `[maya error: [bedrock-qwen] An error occurred (AccessDeniedException) when calling the ConverseStream operation: Bearer `

**Suggested fix**: Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.

### 2. `low_memory_utilization`  · severity 4 · freq 100.0% · score 200
**Layer**: prompt+renderer

On returning-user sessions, average memory-reference rate is 13% — too low. Maya is ignoring stored facts/events.

**Suggested fix**: Renderer: surface the highest-priority anticipation_queue item more prominently. Prompt: tighten Rule 31 to require referencing one stored item every 3rd turn at minimum.

### 3. `multiple_questions_per_reply`  · severity 3 · freq 16.0% · score 48
**Layer**: prompt

Maya included 2+ questions in 14 replies across 8 sessions (Rule 9 violation).

Examples:
- session 9 turn 2: `"Got it, 2020 was another wild one. Virat’s 100 was epic, wasn’t it? What’s your most unforgettable cricket moment, a game, a run, or a catch?"`
- session 16 turn 3: `"Right, onions are the base, cook them well and the whole dish lifts. Aapke matlb. is 'what do you mean?' in Hindi, right? What's on your mind?"`
- session 18 turn 6: `"सारखे उदाहरण काय करायचे?", your Marathi example is clever, and the silly image makes it stick. What’s a third side effect you want to pair with a story like th`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.
