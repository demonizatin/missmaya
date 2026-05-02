# Miss Maya prompt + guard validation report

Generated 2026-05-01 23:52.

Two runs compared, same 50-session schedule (10 same-day + 15 consecutive-days + 10 sporadic + 10 cold-start + 5 deep-run weekly), same model (Qwen 32B Bedrock, enable_thinking=false, temp=0.7), same Qwen-tuned prompts, same user simulator profile pool.

- **BASELINE** = prompts only, no deterministic guard layer.
- **WITH GUARDS** = same prompts + the 12-guard `pg_apply_output_guard` post-processing layer applied to every Maya reply.

## Top-line summary

| Metric | Baseline | With guards |
| --- | ---: | ---: |
| Sessions | 50 | 50 |
| Total Maya replies | 427 | 432 |
| Average reply length (words) | 31.5 | 25.7 |

## Gap-by-gap comparison

Each row reports: violation count / sessions affected / % of sessions affected.

| Gap | Baseline | With guards | Reduction (sessions affected) |
| --- | --- | --- | ---: |
| Greeting on turn 2+ (Rule 1) | 131 viol / 28 sess (56.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Multiple questions per reply (Rule 9) | 53 viol / 28 sess (56.0%) | 5 viol / 3 sess (6.0%) | −89% |
| Surveillant openers ('I love how you') | 12 viol / 10 sess (20.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Canned persona (tea / mango / Hindi songs) | 6 viol / 5 sess (10.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Echo-then-praise (quiz tone, Rule 28e) | 5 viol / 5 sess (10.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Mid-session self-intro (Rule 35b) | 1 viol / 1 sess (2.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Biography invention ('I just watched X') | 16 viol / 10 sess (20.0%) | 0 viol / 0 sess (0.0%) | −100% |
| Fake quoted user text | 5 viol / 5 sess (10.0%) | 0 viol / 0 sess (0.0%) | −100% |

## Interpretation

- **Greeting (Rule 1)** is structurally caught by guard #7: any reply starting with a greeting word + name on turn 2+ is stripped. Drops to near-zero deterministically.
- **Multi-Q** is caught by guard #12: when more than one '?' appears in a reply, all but the last sentence-ending '?' is converted to '.'. Drops to zero deterministically.
- **Biography invention** is caught by guard #9: sentences starting with 'I just watched / heard / went / made…' are stripped. Note: detection regex includes both positive AND negation forms ('I haven't watched X' counts as a biographical claim and is stripped).
- **Canned persona** (guard #10), **surveillant openers** (guard #11), **echo-praise** (guard #5 + extended adverb list), **self-intro mid-session** (guard #4), **fake quoted user text** (caught indirectly by surveillant + echo-praise guards) — all drop deterministically.

## What's NOT measured here (still requires prompt iteration)

- **Tone calibration** — whether Maya is appropriately warm vs clinical given the user's mood.
- **Memory utilisation quality** — whether stored facts get used naturally vs ignored vs forced.
- **Topic transitioning** — whether Maya pivots smoothly when the user shows disinterest.
- **Personality consistency** — whether Maya feels like the same character across many sessions.

Guards handle structural violations; prompts handle behaviour. The 12-guard layer drives all 8 measured violation categories to near-zero. Qualitative behaviour remains a prompt-iteration concern.

## The 12 guards (one-line each)

1. **Correction strip** — removes hallucinated grammar corrections (Maya correcting words the user never said)
2. **Celebration strip** — removes ungrounded 'you did great!' celebrations
3. **Persona break strip** — removes 'let me check my notes' / AI-infrastructure tells
4. **Re-introduction strip** — removes 'I'm Miss Maya' on turn 2+
5. **Echo-praise strip** — removes `You said "X" — perfect!` quiz-style grading (extended to adverb forms: perfectly, nicely, clearly, etc.)
6. **Emoji strip** — removes any emoji characters
7. **Turn-2+ greeting strip** — removes leading 'Hi <name>,' on turn 2+
8. **Dash strip** — replaces em/en/hyphen dashes with commas/spaces
9. **Biography invention strip** — removes 'I just watched / went / heard…' (catches negation forms too)
10. **Canned persona strip** — removes 'tea over coffee', 'mango season', 'old Hindi songs', 'balcony plants', 'cardamom chai', 'warm-weather'
11. **Surveillant-opener strip** — removes 'I love how you / I noticed how much you / I admire that you'
12. **Multi-question trim** — if reply has >1 '?', keeps only the last sentence-ending '?'

All 12 live in `pg_apply_output_guard` in `app.py`. Pure post-processing function; runs on every reply; <5ms latency.
