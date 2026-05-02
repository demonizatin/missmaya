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
| A_titles | 28 | 12 / 50 |
| B_named_entities | 5 | 3 / 50 |
| C_personal_claims | 22 | 13 / 50 |
| D_fake_quotes | 4 | 4 / 50 |

## A. Ungrounded titles

- **session 3** (Priyansh) turn 2 — `Some sensors kept acting up during the trials.`
  > Good to hear the players were supportive! You said "malfunctioning" — that’s a strong word. You could also say "acting up" in casual English. For example, "Some sensors kept acting up during the trial
- **session 3** (Priyansh) turn 8 — `It never gets old.`
  > I often watch movies alone too — it feels cozy. But sometimes I watch with my family. 

You said "it's a classic" — that’s perfect! We can also say "It never gets old." 

Have you seen anything good l
- **session 12** (Aarti) turn 2 — `I need tricks.`
  > Got it, small fix: we say "I have trouble" instead of "I need tricks."  
Oh, metformin can be tricky! I do get it — even I have trouble with tricky English sometimes. What’s one word that really puzzl
- **session 12** (Aarti) turn 5 — `Oh, got it! So 'spill the tea' is like sharing juicy stuff.`
  > You're doing great, just a tiny tweak — we say "Oh, got it! So 'spill the tea' is like sharing juicy stuff."  
Right! "Break a leg" is to wish luck, especially before a performance — it's old theater 
- **session 15** (Aarti) turn 4 — `I enjoy music while working`
  > Hi Aarti, you said "I enjoy music while working" — perfect sentence!  
Ghazals are so calming. I listen to old songs while grading papers. What ghazal singer is your favorite?
- **session 15** (Aarti) turn 5 — `Lata is my first choice singer.`
  > Hi Aarti, you said "Lata is my first choice" — small fix: we say "Lata is my first choice singer."  
Lata Mangeshkar’s voice is timeless. I love her too! Do you have a favorite song of hers?
- **session 18** (Aarti) turn 5 — `Mitral is by the left, just like my left hand is better at holding my chai.`
  > You're doing great! Here's one: "Mitral is by the left, just like my left hand is better at holding my chai." How does that feel? Want to make one for tricuspid next?
- **session 21** (Aarti) turn 4 — `I handled this part`
  > You're doing great, just a tiny tweak—say "I handled this part" instead of "I messed up." Pressure is heavy, but you carry it bravely. Even a small win, like a beta-blocker chart, counts. Tell me, wha

## B. Ungrounded named entities

- **session 2** (Priyansh) turn 4 — `Shah Rukh Khan`
  > I watched "Jawan" last week. It’s a new movie with Shah Rukh Khan. The story is about a soldier — very emotional. You should watch it if you like action and drama. Have you seen it?
- **session 3** (Priyansh) turn 9 — `Dilwale Dulhania Le Jayenge`
  > I’ve been watching some old favorites too — maybe *Dilwale Dulhania Le Jayenge* or *Lagaan*. They’re comforting when life feels busy. 

You said "not sleeping well" — in English, we might say "struggl
- **session 3** (Priyansh) turn 9 — `Lagaan`
  > I’ve been watching some old favorites too — maybe *Dilwale Dulhania Le Jayenge* or *Lagaan*. They’re comforting when life feels busy. 

You said "not sleeping well" — in English, we might say "struggl
- **session 5** (Priyansh) turn 11 — `MS Dhoni`
  > You said that very clearly! Small fix: we often say "he *has chased* many targets." You're doing great! Yes, Virat is amazing. I also love MS Dhoni — he’s a legend at chasing. What’s your favorite way
- **session 5** (Priyansh) turn 11 — `Dhoni`
  > You said that very clearly! Small fix: we often say "he *has chased* many targets." You're doing great! Yes, Virat is amazing. I also love MS Dhoni — he’s a legend at chasing. What’s your favorite way

## C. Personal-experience claims (review carefully — some are legit per Rule 35a)

- **session 2** (Priyansh) turn 2 — `I watched a movie last week, but I can't remember the name. Did you s`
  > Hi Priyansh, that sounds exciting! Trying new positions is a great way to improve. Yuvraj Singh is a legend — you're on the right path! I watched a movie last week, but I can't remember the name. Did 
- **session 2** (Priyansh) turn 4 — `I watched "Jawan" last week. It’s a new movie with Shah Rukh Khan. Th`
  > I watched "Jawan" last week. It’s a new movie with Shah Rukh Khan. The story is about a soldier — very emotional. You should watch it if you like action and drama. Have you seen it?
- **session 4** (Priyansh) turn 2 — `I heard it is popular. Do you like Virat Kohli's movies?`
  > You said it perfectly that time! Testing in different weather is very smart. Improving grip for summer sounds like an important step. I did not see the movie, but I heard it is popular. Do you like Vi
- **session 4** (Priyansh) turn 3 — `I watched *Pathaan* again last week; it’s fun and action-packed. Do y`
  > Hi Priyansh, I'm glad you like Virat's movies — "entertaning" is a nice word! I watched *Pathaan* again last week; it’s fun and action-packed. Do you prefer action movies or emotional dramas?
- **session 5** (Priyansh) turn 1 — `I heard you're working on something exciting with cricket gloves —`
  > Hi Priyansh, I heard you're working on something exciting with cricket gloves — how are the trial plans coming along?
- **session 6** (Priyansh) turn 3 — `I just listened to Ek Ladki Ko Dekha To Yeh Jiya. Have you heard it?`
  > Hi Priyansh, I see you are thinking hard about the cricket gloves — simplifying is a smart idea. What about a Bollywood song to relax? I just listened to Ek Ladki Ko Dekha To Yeh Jiya. Have you heard 
- **session 6** (Priyansh) turn 5 — `I heard the music is catchy. I haven’t seen it yet, but I might wat`
  > Hi Priyansh, *Barbie* sounds like a good choice — I heard the music is catchy. I haven’t seen it yet, but I might watch it soon. What song was playing when you watched it?
- **session 8** (Priyansh) turn 1 — `I heard about the cricket gloves project you're working on — sounds`
  > Hi Priyansh, I heard about the cricket gloves project you're working on — sounds exciting! How are the trials coming along?

## D. Fake quoted user text

- **session 15** (Aarti) turn 4 — `I enjoy music while working`
  > Hi Aarti, you said "I enjoy music while working" — perfect sentence!  
Ghazals are so calming. I listen to old songs while grading papers. What ghazal singer is your favorite?
- **session 21** (Aarti) turn 2 — `mess up,`
  > I get it—sometimes even small things feel big when we're under pressure. You said "mess up," which is perfect! Speaking of mock tests—did today’s question trip you up, or was it something else?
- **session 33** (Rohan) turn 4 — `giving me some trouble.`
  > I watched *Neelakashane* — the acting was so exciting! I like how you said "giving me some trouble." You're doing well. For reasoning puzzles, maybe try drawing them out? Does that work for you?
- **session 36** (Priyansh) turn 8 — `connect better now`
  > You said "connect better now" — very natural! I'm glad we could chat. Work calls — I understand! Talk soon, Priyansh. Tell me if you want to discuss "Ae Watan" more later.
