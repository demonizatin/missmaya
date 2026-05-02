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
| A_titles | 21 | 11 / 50 |
| B_named_entities | 1 | 1 / 50 |
| C_personal_claims | 3 | 3 / 50 |
| D_fake_quotes | 0 | 0 / 50 |

## A. Ungrounded titles

- **session 4** (Priyansh) turn 4 — `Mere Meri Pehli Baarish`
  > Got it, DDLJ is a true classic. The song "Mere Meri Pehli Baarish" always stands out. Do you prefer old Bollywood or the newer ones?
- **session 6** (Priyansh) turn 4 — `Barish.`
  > You said it perfectly that time, "I have two left feet", and I love the spirit! I’m more of a *Lag Ja Gale* slow sway person, but I get the energy of "Barish." What do you and your friends end up danc
- **session 9** (Priyansh) turn 4 — `Tricky but got it working`
  > That’s a productive and colorful day, full of work, Bollywood, and cricket. “Tricky but got it working”, I like that phrase, it sounds confident. What kind of movie are you in the mood for now, action
- **session 16** (Aarti) turn 3 — `Right, ginger tea is a great pick, very grounding.`
  > "Right, ginger tea is a great pick, very grounding." "Turmeric and honey are perfect for focus. What kind of namkeen do you prefer?"
- **session 22** (Aarti) turn 6 — `Diuretics flush out potassium, like a banana losing its peel.`
  > Got it, low potassium with diuretics is tricky. A banana reminder is smart! Maybe add a tiny story: "Diuretics flush out potassium, like a banana losing its peel." What’s another side effect you’d lik
- **session 22** (Aarti) turn 14 — `Stories and dinner, both important! Talk to you later, Aarti. Enjoy your meal!`
  > "Stories and dinner, both important! Talk to you later, Aarti. Enjoy your meal!"
- **session 25** (Aarti) turn 2 — `Pharmacology is my weakest area`
  > "Pharmacology is my weakest area" is clear. A slightly smoother phrasing: "Pharmacology is the subject I find most challenging." What part feels tricky?
- **session 25** (Aarti) turn 2 — `Pharmacology is the subject I find most challenging.`
  > "Pharmacology is my weakest area" is clear. A slightly smoother phrasing: "Pharmacology is the subject I find most challenging." What part feels tricky?

## B. Ungrounded named entities

- **session 4** (Priyansh) turn 4 — `DDLJ`
  > Got it, DDLJ is a true classic. The song "Mere Meri Pehli Baarish" always stands out. Do you prefer old Bollywood or the newer ones?

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 27** (Rohan) turn 7 — `I try to focus", got it, that’s a good way to put it. Horror comedy`
  > You said "I try to focus", got it, that’s a good way to put it. Horror comedy is fun. Do you like scary movies more than funny ones, or the other way around?
- **session 29** (Rohan) turn 8 — `I try to use burst mode", and that’s clear. That sounds like a perfe`
  > You said "I try to use burst mode", and that’s clear. That sounds like a perfect moment to freeze, fans, goals, and emotions all in one frame! Talk to you soon, and good luck with your reading. Keep c
- **session 30** (Rohan) turn 1 — `I just saw their latest match. How was your day?`
  > Hi Rohan, Manchester United's doing well this season, I just saw their latest match. How was your day?

## D. Fake quoted user text

_No instances detected._
