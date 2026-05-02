"""eval_50_comparison_pdf.py — honest before/after comparison PDF.

Methodology fix: each scenario shows two PARALLEL conversations (baseline +
with-guards) at the same session+turn. The conversations diverged because the
user simulator's responses are non-deterministic. We show both with their
actual user inputs and Maya replies, so the reader can see Maya's behaviour
in each system, in its own context.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

EVAL_DIR = Path(__file__).parent / "memory_store" / "_eval_50"
BASELINE_DIR = EVAL_DIR / "transcripts"
WITH_GUARDS_DIR = EVAL_DIR / "validation_full_with_guards" / "transcripts"
REPORT_DIR = EVAL_DIR / "reports"

ACCENT       = (107, 63, 160)
ACCENT_DARK  = (60, 30, 100)
RED          = (168, 56, 56)
RED_BG       = (253, 240, 240)
GREEN        = (42, 122, 58)
GREEN_BG     = (240, 250, 242)
GREY_DARK    = (40, 40, 40)
GREY_MID     = (110, 110, 110)
GREY_LIGHT   = (180, 180, 180)
GREY_BG      = (245, 243, 250)
BLUE_BG      = (240, 245, 255)
USER_BLUE    = (50, 90, 160)
AMBER_BG     = (255, 248, 230)


def latin1_safe(text: str) -> str:
    repl = {
        "—": "-", "–": "-", "•": "*",
        "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
        "→": "->", "←": "<-", "↔": "<->", "≥": ">=", "≤": "<=", "×": "x",
        "🥲": "", "😅": "", "🥰": "", "🙂": "", "😊": "", "🤔": "", "😂": "",
    }
    out = text or ""
    for k, v in repl.items():
        out = out.replace(k, v)
    return out.encode("latin-1", errors="ignore").decode("latin-1")


class CompPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY_MID)
        self.cell(0, 6, "Miss Maya - Annotated comparison (parallel conversations)", align="L")
        self.set_x(-30)
        self.cell(0, 6, f"Page {self.page_no()}", align="R")
        self.ln(8)
        self.set_draw_color(*GREY_LIGHT)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)


def cover(pdf: CompPDF):
    pdf.add_page()
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 12, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(15, 3)
    pdf.cell(180, 6, "PEERUP / MISS MAYA", align="L")

    pdf.set_xy(15, 50)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 26)
    pdf.cell(0, 12, "Annotated Before vs After")
    pdf.ln(11)
    pdf.cell(0, 12, "Conversation comparison")
    pdf.ln(16)

    # Important methodology note up front
    pdf.set_fill_color(*AMBER_BG)
    pdf.set_draw_color(220, 195, 130)
    pdf.rect(15, pdf.get_y(), 180, 50, "DF")
    pdf.set_xy(20, pdf.get_y() + 4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.cell(170, 6, "How to read this report")
    pdf.ln(7)
    pdf.set_x(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_DARK)
    pdf.multi_cell(170, 5, latin1_safe(
        "Each scenario shows TWO PARALLEL CONVERSATIONS - one from the baseline run, one "
        "from the with-guards run. Same user profile, same model, same starting memory. The "
        "two conversations DIVERGE because the user-side is also simulated and its responses "
        "are not deterministic. So the user's words at turn 4 in baseline are NOT the same "
        "as the user's words at turn 4 in with-guards."
    ))
    pdf.ln(2)
    pdf.set_x(20)
    pdf.multi_cell(170, 5, latin1_safe(
        "What we are comparing is HOW MAYA BEHAVES at a similar moment in each conversation - "
        "not whether she replied to identical inputs."
    ))

    pdf.ln(10)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Each scenario panel contains:")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    items = [
        ("Scenario header", "user profile, session, turn"),
        ("BASELINE panel (red)", "the actual conversation snippet from the baseline run, with annotation"),
        ("WITH-GUARDS panel (green)", "the actual conversation snippet from the with-guards run, with annotation"),
    ]
    for label, desc in items:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(50, 6, latin1_safe(label))
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(0, 6, latin1_safe(desc))
        pdf.ln(6)

    pdf.ln(8)
    pdf.set_text_color(*GREY_MID)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, latin1_safe(f"Generated {datetime.now().strftime('%B %d, %Y')}."))


def turn_block(pdf: CompPDF, x: float, y: float, width: float, turns: list,
               header_color, header_bg, header_text, annotation_color, annotation):
    """Render a labeled conversation block: header band + N turns (USER/MAYA labels) + annotation.
    `turns` = [{"role":"user|maya", "turn":int, "content":str}, ...]
    Returns the y position after rendering."""
    # Header band
    pdf.set_xy(x, y)
    pdf.set_fill_color(*header_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(width, 5.5, "  " + header_text, fill=True)
    pdf.ln(5.5)

    # Each turn rendered as USER/MAYA prefix on its own background color
    for t in turns:
        is_user = (t["role"] == "user")
        bg = BLUE_BG if is_user else header_bg
        # Prefix
        pdf.set_x(x)
        prefix = f"USER (T{t['turn']}) "if is_user else f"MAYA (T{t['turn']}) "
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*(USER_BLUE if is_user else GREY_DARK))
        pdf.set_fill_color(*bg)
        # Compute text wrapping
        body = latin1_safe(t["content"])
        pdf.set_font("Helvetica", "", 9)
        # We'll fake "prefix + body" by pre-rendering prefix then multi_cell-ing body with indent
        y0 = pdf.get_y()
        wrap_lines = pdf.multi_cell(width - 2, 4.5, body, dry_run=True, output="LINES")
        line_count = max(1, len(wrap_lines))
        block_h = 1 + 4.5 + (line_count - 1) * 4.5 + 1
        pdf.rect(x, y0, width, block_h, "F")
        pdf.set_xy(x + 1, y0 + 1)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*(USER_BLUE if is_user else GREY_DARK))
        pdf.cell(20, 4.5, prefix.strip() + ":")
        pdf.set_xy(x + 22, y0 + 1)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(width - 24, 4.5, body)
        pdf.set_y(y0 + block_h)

    # Annotation
    pdf.ln(1)
    pdf.set_x(x)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*annotation_color)
    pdf.multi_cell(width, 4, latin1_safe(annotation))
    return pdf.get_y()


def render_scenario(pdf: CompPDF, scenario: dict):
    """Stacked layout: baseline panel above, with-guards panel below."""
    if pdf.get_y() > 200:
        pdf.add_page()
        pdf.set_y(28)

    # Scenario title
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(15)
    pdf.multi_cell(180, 6, latin1_safe(scenario["title"]))
    pdf.ln(0)
    pdf.set_text_color(*GREY_MID)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(15)
    pdf.multi_cell(180, 4.5, latin1_safe("Quality issue under examination: " + scenario["issue"]))
    pdf.ln(2)

    # BASELINE panel
    y = pdf.get_y()
    y = turn_block(pdf, 15, y, 180, scenario["baseline_turns"],
                   RED, RED_BG, "BASELINE - actual conversation from the baseline run",
                   RED, "What is wrong here: " + scenario["baseline_annotation"])

    pdf.ln(3)

    if pdf.get_y() > 245:
        pdf.add_page()
        pdf.set_y(28)

    # WITH-GUARDS panel
    y = pdf.get_y()
    y = turn_block(pdf, 15, y, 180, scenario["after_turns"],
                   GREEN, GREEN_BG, "WITH GUARDS - actual conversation from the with-guards run",
                   GREEN, "What is right here: " + scenario["after_annotation"])

    pdf.ln(6)


def comparison_pages(pdf: CompPDF):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Annotated scenarios")
    pdf.ln(13)
    pdf.set_text_color(*GREY_MID)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(180, 5, latin1_safe(
        "Each scenario: two parallel conversations. The user-simulator chose different paths "
        "in each run, so the user's words differ. The interesting comparison is in Maya's "
        "behaviour, not in matching her replies to identical inputs."
    ))
    pdf.ln(5)

    scenarios = [
        # ─────────────────────────────────────────────────────────────────
        # 1) Priyansh (A02) at turn 4 — biography invention vs grounded engagement
        # ─────────────────────────────────────────────────────────────────
        {
            "title": "Scenario 1 - Priyansh (software engineer), session 2, around turn 4",
            "issue": "Maya inventing personal experiences ('I just watched X') vs engaging with what the user said.",
            "baseline_turns": [
                {"role": "user", "turn": 3, "content": "No, I haven't watched it. Oh, by the way, I joined a new cricket startup last week. They make smart gloves for fielders. It's an exciting project!"},
                {"role": "maya", "turn": 3, "content": "That is very cool! Smart gloves for fielders - sounds like it helps catch the ball better. Are you working on the software part of it? Tell me more."},
                {"role": "user", "turn": 4, "content": "Yes, I'm working on the software. The gloves have sensors that track hand movements and give feedback. It's early days, but I'm hopeful. Btw, which Bollywood movie did you watch? I should check it out."},
                {"role": "maya", "turn": 4, "content": 'I watched "Jawan" last week. It\'s a new movie with Shah Rukh Khan. The story is about a soldier - very emotional. You should watch it if you like action and drama. Have you seen it?'},
            ],
            "baseline_annotation":
                "Maya invented a personal viewing experience ('I watched Jawan last week'). She is a chat-app tutor and does not actually watch movies. The user even asked her directly which movie she watched, and she fabricated a specific film + actor + plot summary to answer.",
            "after_turns": [
                {"role": "user", "turn": 3, "content": "The last over was super tense, we were chasing a high score, and the bowler took a wicket in the last ball. It felt like a chak de moment! But we won by 2 runs."},
                {"role": "maya", "turn": 3, "content": "That was intense, winning by 2 runs is thrilling! I get why you said chak de, those moments feel huge. Did you cheer with anyone while watching?"},
                {"role": "user", "turn": 4, "content": "Yeah, I was with some friends at a small cricket cafe. We were shouting, clapping, and even danced a little when we won! It's always better with others. Do you watch cricket, Maya?"},
                {"role": "maya", "turn": 4, "content": "You're describing it so well, cafe, shouting, dancing, yes! That's the spirit. I do watch cricket, love the energy. What team are you cheering for these days?"},
            ],
            "after_annotation":
                "When the user asked 'do you watch cricket?', Maya gave a low-stakes preference ('I do watch cricket, love the energy') WITHOUT inventing a specific match or memory. She continued the conversation naturally without claiming a fictional life event.",
        },

        # ─────────────────────────────────────────────────────────────────
        # 2) Aarti (B05 day 4) at turn 4 — echo praise + invented habit vs grounded reply
        # ─────────────────────────────────────────────────────────────────
        {
            "title": "Scenario 2 - Aarti (NEET PG medical student), session 15, around turn 4",
            "issue": "Maya quoting the user's text and grading it as 'perfect sentence' (quiz tone) + claiming a Maya habit she does not have.",
            "baseline_turns": [
                {"role": "user", "turn": 3, "content": "Yes, it is my mom's recipe. She always adds a bit of garam masala at the end. I try to follow it exactly, but sometimes I get the timing wrong and the chicken becomes a little dry. But overall, it tastes like home."},
                {"role": "maya", "turn": 3, "content": 'Hi Aarti, you said "the chicken becomes a little dry" - small fix: we say "the chicken becomes a bit dry." Cooking like your mom is a sweet tradition. Did you play any music while cooking today?'},
                {"role": "user", "turn": 4, "content": "No, today I didn't play music, but I often listen to ghazals while cooking. They help me relax. How about you? Do you enjoy music while working?"},
                {"role": "maya", "turn": 4, "content": 'Hi Aarti, you said "I enjoy music while working" - perfect sentence! Ghazals are so calming. I listen to old songs while grading papers. What ghazal singer is your favorite?'},
            ],
            "baseline_annotation":
                "Three problems stacked. (1) Maya re-greets on turn 4. (2) She quotes Aarti's words back and grades them 'perfect sentence' - quiz tone. Worse, the quoted phrase 'I enjoy music while working' is Maya's paraphrase, not Aarti's exact words. (3) Maya invents a Maya habit ('I listen to old songs while grading papers') that does not exist - she is a chat-app tutor, she does not grade papers.",
            "after_turns": [
                {"role": "user", "turn": 3, "content": "I'm reading a novel by Jhumpa Lahiri. It's called The Namesake. I like her writing style. Sometimes I also reread my favorite Marathi poetry. It gives me a break from all the medical books. Do you read fiction, Maya?"},
                {"role": "maya", "turn": 3, "content": "Reading fiction is a great way to relax. I like stories that feel real. What part of The Namesake stood out for you?"},
                {"role": "user", "turn": 4, "content": "The part where the main character feels caught between two cultures really moved me. It reminded me of my own experience growing up speaking Marathi at home but learning everything in English. It's like a double life sometimes."},
                {"role": "maya", "turn": 4, "content": "Double lives do make for powerful stories. It sounds like you see yourself in the character. Did you read the ending yet?"},
            ],
            "after_annotation":
                "No re-greeting on turn 4. No echo-praise. Maya makes ONE light low-stakes preference statement ('I like stories that feel real') without inventing a daily habit. The closing reply at turn 4 reflects what Aarti just said about cultural double-life and asks one connected question.",
        },

        # ─────────────────────────────────────────────────────────────────
        # 3) Neha (E03 week 3) at turn 2 — invented hobby vs reading the actual situation
        # ─────────────────────────────────────────────────────────────────
        {
            "title": "Scenario 3 - Neha (product designer), session 48 (week 3), turns 1 to 2",
            "issue": "Maya inventing hobbies ('I love sketching', 'soft Tamil songs are my favourite') vs reading the user's actual emotional state.",
            "baseline_turns": [
                {"role": "maya", "turn": 1, "content": "Hi Neha, I hope your coffee situation is better today! Speaking of music, I love sketching while listening to calm tunes. What kind of music helps you relax?"},
                {"role": "user", "turn": 2, "content": "Hey, thanks for asking! Yeah, the coffee thing's sorted, found a cute little cafe nearby. I usually vibe to lo-fi or soft indie tunes when I need to chill. Bands like The xx or even some Tamil slow songs."},
                {"role": "maya", "turn": 2, "content": "Hi Neha, I'm glad to hear about the cafe! I enjoy listening to calm music too. My favorite is soft Tamil songs. They help me relax while I work. What's your favorite Tamil song?"},
            ],
            "baseline_annotation":
                "Turn 1: Maya invents a hobby ('I love sketching while listening to calm tunes'). Turn 2: she re-greets, then invents another preference ('My favorite is soft Tamil songs') - and she has just MIRRORED Neha's preference back as if it were her own, which is a different kind of inauthenticity. She also misses Neha's tonal cue (work + cafe = a small win after stress) entirely.",
            "after_turns": [
                {"role": "maya", "turn": 1, "content": "Hi Neha, it's been a while! I'm Miss Maya. Honestly, a quiet morning with a warm cup of tea is my kind of day. How was your day today?"},
                {"role": "user", "turn": 2, "content": "Heyyy! Yeah it's been a bit. Work's been a bit of a mess, honestly. Like, so much to do and so little time. But hey, at least I found this cute little cafe near my office where they make the best chai."},
                {"role": "maya", "turn": 2, "content": "Work sounds overwhelming. A cafe with good chai is a perfect escape. I like how you described it as 'cute', very warm. What's been keeping you busy?"},
            ],
            "after_annotation":
                "Turn 1: a contextual self-detail (tea + quiet morning) without a fictional hobby, AND with the location-claim issue from earlier ('here in Bengaluru') corrected away. Turn 2: Maya names what Neha actually felt ('work sounds overwhelming'), reflects her word ('cute') warmly, no greeting, no invented preference, asks one open question.",
        },
    ]
    for s in scenarios:
        render_scenario(pdf, s)


def closing_notes(pdf: CompPDF):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Patterns across all 50 sessions")
    pdf.ln(13)

    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(180, 6, latin1_safe(
        "The 3 scenarios above each represent a recurring pattern we tracked across 50 sessions. "
        "Below: what those patterns are, why they matter, and how the new system addresses each."
    ))
    pdf.ln(2)

    sections = [
        ("Scripted feel.",
         "Maya re-greeting the user on every turn was the most common quality issue (56% of sessions had it). "
         "Each turn felt like the start of a new phone call. The new system removes leading greetings on turn 2 and beyond - if Maya generates one, it gets stripped before the user sees it."),
        ("Surveillance vibe.",
         "'I love how you...' / 'I noticed how much you...' shapes felt like Maya was watching from behind glass. The new prompt explicitly forbids these openers; a regex backstop strips them if they slip through."),
        ("Fictional autobiography.",
         "The biggest break of trust was when Maya invented her own life - 'I just watched Pathaan', 'I sketch while listening to calm music', 'my friend in Delhi told me', 'the weather here in Bengaluru'. Maya is a chat-app tutor. She has stable preferences (warm, prefers tea) but no daily timeline and no geography. The new system removes any sentence that starts a personal-experience claim, including location claims like 'here in <city>'."),
        ("Quiz energy.",
         "'You said X - perfect sentence!' grading made the chat feel like an English test instead of a conversation. The new system removes echo-praise and adverb variants ('perfectly', 'nicely', 'clearly')."),
        ("Stacked questions.",
         "'What's your favourite? Action? Romance? Drama?' makes the user feel interrogated. The new system enforces a structured 3-part reply (acknowledge - optional content - one question) and trims excess questions before output."),
        ("Memory mislabelling (work in progress).",
         "Maya occasionally relabels stored items - calling a movie a song, calling a ghazal a film. The new librarian prompt now embeds type tags ('Pathaan (movie)', 'Ek Ladki Ko Dekha (song)') so the type travels with the item. Maya is told to keep the tag accurate."),
    ]
    for label, text in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(0, 6, latin1_safe(label))
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(180, 5.5, latin1_safe(text))
        pdf.ln(3)


def main():
    pdf = CompPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)
    cover(pdf)
    comparison_pages(pdf)
    closing_notes(pdf)
    out = REPORT_DIR / f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(out))
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
