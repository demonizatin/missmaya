# Eval-50 gap report

**Sessions analysed**: 50

## Top-line metrics
- Average reply length: **25.7 words**
- Replies over 120 words: **0**
- Replies under 8 words: **2**
- Avg memory-reference rate (returning-user sessions): **32%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **4**
- Total stale-phrase hits across all sessions: **0**
- Sessions with a clean wrap-up signal: **23**

## Ranked gaps (severity × frequency)

### 1. `opener_repetition`  · severity 5 · freq 8.0% · score 250
**Layer**: guard

4 pairs of openers across same-user sessions had >=0.65 structural similarity.

Examples:
- u02_aarti sessions 12 ↔ 18 (sim 0.74): `Hi Aarti, I'm Miss Maya. Honestly, the monsoon rains make me feel relaxed. How's your NEET PG prep going these days?` ↔ `Hi Aarti, I'm Miss Maya. Honestly, I love the way monsoon makes me feel cozy and relaxed. How are you feeling today?`
- u02_aarti sessions 14 ↔ 17 (sim 0.78): `Hi Aarti, I'm Miss Maya. How has your day been so far?` ↔ `Hi Aarti, I'm Miss Maya. How was your day with NEET PG prep?`
- u02_aarti sessions 18 ↔ 19 (sim 0.66): `Hi Aarti, I'm Miss Maya. Honestly, I love the way monsoon makes me feel cozy and relaxed. How are you feeling today?` ↔ `Hi Aarti, I'm Miss Maya. Honestly, the monsoon makes me sleepy too, but I find warm chai helps shake it off. How was you`

**Suggested fix**: Add a deterministic first-turn similarity check that strips opener if normalized form matches one of the last 6 stored opening_phrases by SequenceMatcher >= 0.7.

### 2. `multiple_questions_per_reply`  · severity 3 · freq 6.0% · score 18
**Layer**: prompt

Maya included 2+ questions in 5 replies across 3 sessions (Rule 9 violation).

Examples:
- session 5 turn 4: `"Medium with a kick sounds perfect. A little playful banter with the wife adds to the fun, right? Pappu! What’s your go to spicy dish when you want that extra h`
- session 22 turn 5: `"Drawing a table is a great idea, it makes things clearer. The cat idea is fun, right? It makes learning feel lighter. What’s one side effect you find hardest t`
- session 46 turn 8: `"Got it, send the draft and lean into the mess, drama can be productive. New coffee, fancy name, and a lid that stays on? Now that’s a plan. What’s your go to f`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.
