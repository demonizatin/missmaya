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
| B_named_entities | 0 | 0 / 15 |
| C_personal_claims | 1 | 1 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

- **session 12** (Aarti) turn 2 — `Got it, mixing them up is really common. Aapde kahi nahi pahuche`
  > "Got it, mixing them up is really common. Aapde kahi nahi pahuche", yes, that pressure is tough. What helps you the most when you're stuck?
- **session 14** (Aarti) turn 4 — `Beta blocks stress, heart beats less.`
  > A pharmacology rap sounds creative! Let’s start with beta blockers, how about this line: “Beta blocks stress, heart beats less.” What do you think?
- **session 14** (Aarti) turn 7 — `Medicine, medicine, memorize it right...`
  > "Medicine, medicine, memorize it right...", a great, upbeat chorus! It adds fun and rhythm. Go ahead, build your rap, I’m all ears!

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 18** (Aarti) turn 1 — `I've been thinking about your color coded drug charts, they sound like a smart way t`
  > Hi Aarti, I've been thinking about your color coded drug charts, they sound like a smart way to simplify all that information. Did you try the antidiabetic one yet?

## D. Fake quoted user text

_No instances detected._
