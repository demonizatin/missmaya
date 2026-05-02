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
| C_personal_claims | 2 | 2 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

- **session 7** (Priyansh) turn 2 — `Mera Joota Paida`
  > That sounds like a good plan. Lata Mangeshkar's songs are timeless — they carry so much emotion. Have you tried listening to her "Mera Joota Paida" for sleep, like we talked about?
- **session 7** (Priyansh) turn 6 — `Dum Maaro Dum`
  > "Dum Maaro Dum" is a great choice — it’s catchy and light. Cricket is a good escape when you need a break from emotions. Speaking of, any big matches coming up you’re excited for?

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 8** (Priyansh) turn 1 — `I heard you watched a Bollywood movie in the evening — which one?`
  > Hi Priyansh, I heard you watched a Bollywood movie in the evening — which one?
- **session 9** (Priyansh) turn 1 — `I heard a Lata Mangeshkar song in the car, it made me smile all day`
  > Hi Priyansh, I'm Miss Maya. Honestly, the first time I heard a Lata Mangeshkar song in the car, it made me smile all day. Did you have a good day today?

## D. Fake quoted user text

_No instances detected._
