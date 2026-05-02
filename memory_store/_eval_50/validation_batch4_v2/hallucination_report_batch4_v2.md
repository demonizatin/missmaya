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
| A_titles | 3 | 2 / 15 |
| B_named_entities | 1 | 1 / 15 |
| C_personal_claims | 3 | 3 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

- **session 6** (Priyansh) turn 6 — `your`
  > Got it — that prank in *Chennai Express* is a classic loop-worthy moment. I get how *Bhool Bhulaiyaa*’s prank feels more magical. What makes it feel like *your* favorite?
- **session 49** (Neha) turn 2 — `Mad day`
  > "Mad day" sounds heavy — exams are tough. I get how music helps you through it. What exam are you preparing for?
- **session 49** (Neha) turn 6 — `Dark chocolate and pretending to meditate`
  > "Dark chocolate and pretending to meditate" — I get that. Will you try the sketching first or save it as a backup plan?

## B. Ungrounded named entities

- **session 10** (Priyansh) turn 1 — `Shah Rukh Khan`
  > Hi Priyansh, I'm Miss Maya. Honestly, the first time I watched 'Raees' made me understand why people love Shah Rukh Khan so much. How was your day?

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 4** (Priyansh) turn 2 — `I watched Dilwale Dulhania Le Jayenge again last week. What’s your go`
  > Ah, rain is the best kind of surprise — even when it’s just a drizzle. Coding and meetings sound busy. I watched Dilwale Dulhania Le Jayenge again last week. What’s your go-to Bollywood movie right no
- **session 9** (Priyansh) turn 1 — `I've been thinking about your walks — how was your 20-minute reset today?`
  > Hi Priyansh, I've been thinking about your walks — how was your 20-minute reset today?
- **session 10** (Priyansh) turn 1 — `I watched 'Raees' made me understand why people love Shah Rukh Khan s`
  > Hi Priyansh, I'm Miss Maya. Honestly, the first time I watched 'Raees' made me understand why people love Shah Rukh Khan so much. How was your day?

## D. Fake quoted user text

_No instances detected._
