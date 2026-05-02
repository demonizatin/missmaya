# Eval-50 gap report

**Sessions analysed**: 15

## Top-line metrics
- Average reply length: **29.0 words**
- Replies over 120 words: **0**
- Replies under 8 words: **0**
- Avg memory-reference rate (returning-user sessions): **20%**
- Opener-repetition pairs (≥0.65 similarity, same user, different sessions): **0**
- Total stale-phrase hits across all sessions: **0**
- Sessions with a clean wrap-up signal: **7**

## Ranked gaps (severity × frequency)

### 1. `multiple_questions_per_reply`  · severity 3 · freq 53.3% · score 160
**Layer**: prompt

Maya included 2+ questions in 21 replies across 8 sessions (Rule 9 violation).

Examples:
- session 1 turn 3: `"Jugjugg Jeeyo — I remember that one, it’s fun! Catchy songs stick around, right? AI tools can be tricky at first — what part feels confusing? Take care, and ha`
- session 7 turn 1: `Hi Priyansh, Sui Dhaaga’s music stuck with you, right? Your sister must know every lyric by heart. What did you hum most?`
- session 8 turn 1: `Hi Priyansh, you mentioned an API issue — how's the wait going? I enjoy solving tech hiccups with a hot cup of tea. What's your go-to drink?`

**Suggested fix**: Sharpen Rule 9 with 'NEVER more than ONE question mark per reply'. Optionally a guard that drops trailing questions when count>1.
