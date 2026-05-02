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
| A_titles | 0 | 0 / 15 |
| B_named_entities | 1 | 1 / 15 |
| C_personal_claims | 1 | 1 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

_No instances detected._

## B. Ungrounded named entities

- **session 5** (Priyansh) turn 6 — `MS Dhoni`
  > Virat Kohli is a fantastic choice — I agree, he plays with heart and speaks with clarity too. I enjoy watching MS Dhoni’s calm style. What’s your take on his leadership?

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 5** (Priyansh) turn 1 — `I heard the song from Sui Dhaaga, I hummed it for days — it felt so`
  > Hi Priyansh, I'm Miss Maya. Honestly, the first time I heard the song from Sui Dhaaga, I hummed it for days — it felt so warm and honest. How was your movie night with your sister?

## D. Fake quoted user text

_No instances detected._
