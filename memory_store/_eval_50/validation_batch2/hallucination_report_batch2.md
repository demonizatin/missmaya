# Eval-50 hallucination scan

**Sessions analysed**: 15

## Detection categories

- **A. Ungrounded titles** — film/book/song names Maya put in *italics* or "quotes" that the user never mentioned and aren't in stored memory.
- **B. Ungrounded named entities** — celebrities/cricketers/actors mentioned without user introducing them and not in memory.
- **C. Personal-experience claims** — first-person statements ("I just watched X", "I went to my nani's") that risk Rule 35 biography fabrication. Note: Rule 35a allows low-stakes preferences ("I'm a tea person"), so each claim needs human review — this is a pattern flag, not a confirmed violation.
- **D. Fake quoted user text** — `You said "X"` where X doesn't appear in the user's actual messages.

## Top-line counts

| Category | Total hits | Sessions affected |
| --- | ---: | ---: |
| A_titles | 6 | 2 / 15 |
| B_named_entities | 0 | 0 / 15 |
| C_personal_claims | 1 | 1 / 15 |
| D_fake_quotes | 1 | 1 / 15 |

## A. Ungrounded titles

- **session 48** (Neha) turn 9 — `Quiet corners of the brain`
  > "Quiet corners of the brain" — that's a lovely way to put it. *Holocene* is a classic for a reason — I get that. Do you often find yourself returning to old favourites when you need something to lean 
- **session 49** (Neha) turn 4 — `I can't wait for this phase to pass`
  > You're doing great, just a tiny tweak — we say "I can't wait for this phase to pass" without the "for" after "wait." Kerala sounds lovely — I'd love to hear what makes it so calming for you. What do y
- **session 49** (Neha) turn 6 — `Have you ever felt like`
  > I get that — staring at notes and wondering why you said yes is part of the process. You're doing great, just a tiny tweak: "You ever feel like" should be "Have you ever felt like" for tense consisten

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 47** (Neha) turn 1 — `I've been thinking about your design work — it sounds creative. Did something feel o`
  > Hi Neha, I've been thinking about your design work — it sounds creative. Did something feel off lately that you'd like to talk through?

## D. Fake quoted user text

- **session 49** (Neha) turn 5 — `stress over exams now`
  > That sounds like a perfect escape — slow beaches and relaxed air are just what’s needed. Exams are tough, I get that. You said "stress over exams now" — small fix: we'd say "stressing over exams now" 
