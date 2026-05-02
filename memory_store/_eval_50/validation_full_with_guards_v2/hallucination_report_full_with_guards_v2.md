# Eval-50 hallucination scan

**Sessions analysed**: 50

## Detection categories

- **A. Ungrounded titles** — film/book/song names Maya put in *italics* or "quotes" that the user never mentioned and aren't in stored memory.
- **B. Ungrounded named entities** — celebrities/cricketers/actors mentioned without user introducing them and not in memory.
- **C. Personal-experience claims** — first-person statements ("I just watched X", "I went to my nani's") that risk Rule 35 biography fabrication. Note: Rule 35a allows low-stakes preferences ("I'm a tea person"), so each claim needs human review — this is a pattern flag, not a confirmed violation.
- **D. Fake quoted user text** — `You said "X"` where X doesn't appear in the user's actual messages.

## Top-line counts

| Category | Total hits | Sessions affected |
| --- | ---: | ---: |
| A_titles | 13 | 5 / 50 |
| B_named_entities | 0 | 0 / 50 |
| C_personal_claims | 1 | 1 / 50 |
| D_fake_quotes | 3 | 1 / 50 |

## A. Ungrounded titles

- **session 21** (Aarti) turn 5 — `PP Means Prevent and Palliate`
  > Got it, and that sounds like a smart plan. Acronyms are fun. What if you go with *PP Means Prevent and Palliate*. What’s next on your list?
- **session 22** (Aarti) turn 2 — `Good to hear it's getting better, Marathi notes are clever!`
  > "Good to hear it's getting better, Marathi notes are clever!" Cooking helps me too. What kind of cookies do you bake when you're stressed?
- **session 22** (Aarti) turn 5 — `completes`
  > Cumin is such a kitchen staple for me too. What’s one dish where you feel cumin just *completes* it for you?
- **session 29** (Rohan) turn 4 — `You said 'Ekti photo dekhe jodi lagay ki`
  > "You said 'Ekti photo dekhe jodi lagay ki "wow, this is something!"', got it. You said it almost perfectly!" Bengali cinema sounds interesting, do you take photos of that too?
- **session 38** (Rohan) turn 2 — `Right, okay first, you did great to point it out yourself!`
  > "Right, okay first, you did great to point it out yourself!" "Second, the mistake is a tiny tweak: we say 'I can transfer' when offering help. 'I'll transfer' sounds like a promise, not an offer." "Wh
- **session 38** (Rohan) turn 3 — `Same, those little slips happen to everyone.`
  > "Same, those little slips happen to everyone." "You handled it bravely, and being better next time is what learning is." "Yes, practice with me anytime. What part feels trickiest for you?"
- **session 39** (Neha) turn 3 — `Foam attack latte`
  > "Foam attack latte", that sounds creative! I get that, mornings can be tricky. Do you usually have a specific song or playlist to start your day?
- **session 39** (Neha) turn 4 — `actually`
  > Got it, cringe avoidance is real after a foam attack. Do you have a go to breakfast that makes you feel like you’ve *actually* started the day?

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 35** (Rohan) turn 1 — `I saw you watched the East Bengal Mohun Bagan match, what stood o`
  > Hi Rohan, I saw you watched the East Bengal Mohun Bagan match, what stood out for you in that comeback win?

## D. Fake quoted user text

- **session 31** (Rohan) turn 6 — `my brain is all foggy,`
  > You said "my brain is all foggy," yes, that sounds rough. Sleep loss hits hard, doesn’t it. What part of your revision feels the heaviest right now?
- **session 31** (Rohan) turn 7 — `gur in my coffee,`
  > You said "gur in my coffee," yes, that’s a funny way to describe it! A movie sounds like a good escape. Action, comedy, or something old school Bengali?
