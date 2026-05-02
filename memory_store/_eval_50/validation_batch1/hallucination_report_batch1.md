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
| A_titles | 8 | 5 / 15 |
| B_named_entities | 0 | 0 / 15 |
| C_personal_claims | 2 | 2 / 15 |
| D_fake_quotes | 0 | 0 / 15 |

## A. Ungrounded titles

- **session 2** (Priyansh) turn 8 — `Thanks for chatting with you, Maya!`
  > You're doing great, just a tiny tweak — we say "Thanks for the chat, Maya!" as "Thanks for chatting with you, Maya!" — but I get it, time and fear are real. Let’s leave it at "fun" for now. What movie
- **session 4** (Priyansh) turn 9 — `PK,`
  > You're doing great! "Dangal," "PK," and "Lagaan" are all amazing choices — they show Aamir Khan’s hard work and talent. What made you pick those ones?
- **session 4** (Priyansh) turn 10 — `PK,`
  > You said that perfectly! "Dangal," "PK," and "Lagaan" each have something special — whether it’s emotion, comedy, or cricket. I’ve seen all three, and they’re all timeless. What’s your favorite part o
- **session 5** (Priyansh) turn 7 — `papa`
  > You're doing great, just a tiny tweak — we say "the *papa* of coolness" or "the ultimate coolness" in English. And yes, that six was legendary! I follow matches live when I can — nothing beats the ten
- **session 7** (Priyansh) turn 7 — `your`
  > You said it beautifully — that song really does feel raw and real. I love how music connects generations. What’s one old song from *your* childhood that still means something to you?
- **session 50** (Neha) turn 3 — `I see everything, even the chaos.`
  > Right, the 11-eye doodles — that’s your brain saying “I see everything, even the chaos.” People-watching is a quiet escape. I do that while sipping tea. What’s the most interesting person you saw late
- **session 50** (Neha) turn 7 — `you’re`
  > Right — cats *are* the quiet judges of the world. You picked a good one for the scene. I wonder what *you’re* sketching these days — something chaotic, or something with a quiet soul like that woman’s

## B. Ungrounded named entities

_No instances detected._

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 2** (Priyansh) turn 4 — `I tried. What’s one stunt you’d love to try?`
  > Got it, "Bang Bang" is a great choice! Hrithik Roshan's stunts are top-notch. I enjoy watching them, though I’d probably trip if I tried. What’s one stunt you’d love to try?
- **session 47** (Neha) turn 1 — `I heard about your coffee spill on the sketchbook — did you turn it`
  > Hi Neha, I heard about your coffee spill on the sketchbook — did you turn it into one of your famous 'coffee abstracts'?

## D. Fake quoted user text

_No instances detected._
