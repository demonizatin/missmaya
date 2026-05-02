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
| A_titles | 2 | 1 / 15 |
| B_named_entities | 0 | 0 / 15 |
| C_personal_claims | 0 | 0 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

- **session 8** (Priyansh) turn 5 — `We aim to expand to other cities`
  > Got it — "We plan to launch next month" sounds confident and natural. For future growth, you could say, "We aim to expand to other cities" or "We’re looking to grow to other cities." Both sound profes
- **session 8** (Priyansh) turn 6 — `We plan to expand after the app is stable and running smoothly.`
  > Yes, that flows well. It shows thoughtfulness. You could also say, "We plan to expand after the app is stable and running smoothly." Both versions work. How do you want to describe the app’s stability

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

_No instances detected._

## D. Fake quoted user text

_No instances detected._
