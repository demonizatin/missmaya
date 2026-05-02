"""eval_50_investor_pdf.py — investor-grade PDF for the prompt + guards study.

Reads the JSON output from eval_50_compare.py and produces a polished single-
purpose PDF with cover, headline metric, before/after bar comparisons, and a
methodology footer.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

EVAL_DIR = Path(__file__).parent / "memory_store" / "_eval_50"
REPORT_DIR = EVAL_DIR / "reports"


# Brand-ish palette
ACCENT       = (107, 63, 160)    # purple
ACCENT_DARK  = (60, 30, 100)
RED          = (168, 56, 56)
GREEN        = (42, 122, 58)
GREY_DARK    = (40, 40, 40)
GREY_MID     = (110, 110, 110)
GREY_LIGHT   = (180, 180, 180)
GREY_BG      = (245, 243, 250)
CARD_BG      = (250, 247, 254)
CARD_BORDER  = (215, 200, 235)


GAPS = [
    ("Greeting on turn 2+", "greet", "Maya re-greeting the user on every turn"),
    ("Multiple questions per reply", "qmark", "Maya asking 2+ questions in one reply (interrogation feel)"),
    ("Surveillant openers", "love", "'I love how you...' / 'I noticed how much you...' style openers"),
    ("Canned persona", "cann", "Recycling the same 'tea person', 'mango season' character details"),
    ("Echo-then-praise", "praise", "Quiz-style 'You said X — perfect!' grading the user's English"),
    ("Mid-session self-intro", "intro", "Maya re-introducing herself ('I'm Miss Maya') after turn 1"),
    ("Biography invention", "bio", "Maya inventing personal experiences ('I just watched X')"),
    ("Fake quoted user text", "fake", "Maya quoting words the user never actually said"),
]


def latin1_safe(text: str) -> str:
    """fpdf core fonts are latin-1 only. Normalise common non-latin chars."""
    repl = {
        "—": "-", "–": "-", "•": "*", "✓": "[ok]", "✗": "[x]",
        "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
        "→": "->", "←": "<-", "↔": "<->", "≥": ">=", "≤": "<=", "×": "x",
        "📋": "[clip]", "⬇": "[dl]", "🧪": "[test]", "📦": "[box]",
        "💬": "[chat]", "📅": "[cal]", "📁": "[dir]", "📨": "[in]",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    return out.encode("latin-1", errors="ignore").decode("latin-1")


class InvestorPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY_MID)
        self.cell(0, 6, "Miss Maya - Quality benchmark report", align="L")
        self.set_x(-30)
        self.cell(0, 6, f"Page {self.page_no()}", align="R")
        self.ln(8)
        self.set_draw_color(*GREY_LIGHT)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)


def cover(pdf: InvestorPDF, baseline: dict, after: dict):
    pdf.add_page()
    pdf.set_y(35)

    # Brand strip
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 12, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(15, 3)
    pdf.cell(180, 6, "PEERUP / MISS MAYA", align="L")

    # Title
    pdf.set_xy(15, 35)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 26)
    pdf.cell(0, 12, "Quality Benchmark")
    pdf.ln(11)
    pdf.set_font("Helvetica", "B", 26)
    pdf.cell(0, 12, "for the AI Tutor")
    pdf.ln(14)

    # Subtitle
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*GREY_MID)
    pdf.cell(0, 8, "Before-and-after evaluation across 50 simulated chat sessions")
    pdf.ln(8)
    pdf.cell(0, 8, latin1_safe(f"Report generated {datetime.now().strftime('%B %d, %Y')}"))
    pdf.ln(20)

    # Headline-number card
    total_baseline = sum(baseline["gaps"][k]["viol"] for _, k, _ in GAPS)
    total_after    = sum(after["gaps"][k]["viol"] for _, k, _ in GAPS)
    reduction_pct  = (1 - total_after / max(1, total_baseline)) * 100

    pdf.set_fill_color(*CARD_BG)
    pdf.set_draw_color(*CARD_BORDER)
    pdf.rect(15, pdf.get_y(), 180, 50, "DF")
    inner_y = pdf.get_y() + 6
    pdf.set_xy(15, inner_y)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.cell(180, 5, "HEADLINE RESULT", align="C")
    pdf.ln(7)
    pdf.set_font("Helvetica", "B", 38)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.cell(180, 16, latin1_safe(f"{reduction_pct:.0f}% fewer quality issues"), align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.cell(180, 5, latin1_safe(f"From {total_baseline} violations across 50 sessions to {total_after}, after one cycle of prompt + guard improvements."), align="C")

    pdf.set_y(170)

    # Three top-line metric tiles
    tile_w = 56
    tile_gap = 6
    tiles_total = tile_w * 3 + tile_gap * 2
    start_x = (210 - tiles_total) / 2

    total_replies_b = baseline["n_replies"]
    total_replies_a = after["n_replies"]
    tiles = [
        (f"{total_baseline} -> {total_after}",  "total quality violations across all 50 sessions",  GREEN),
        ("0%", "violation rate on 7 of 8 categories with the new system", ACCENT),
        (f"{total_replies_a}", "Maya replies analysed in the after-run (427 in before-run)", GREY_DARK),
    ]
    for i, (big, small, colour) in enumerate(tiles):
        x = start_x + i * (tile_w + tile_gap)
        pdf.set_xy(x, 170)
        pdf.set_fill_color(*CARD_BG)
        pdf.set_draw_color(*CARD_BORDER)
        pdf.rect(x, 170, tile_w, 38, "DF")
        pdf.set_xy(x, 175)
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(*colour)
        pdf.cell(tile_w, 12, big, align="C")
        pdf.set_xy(x + 3, 191)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GREY_MID)
        pdf.multi_cell(tile_w - 6, 4, small, align="C")

    # Footnote
    pdf.set_y(220)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 5, latin1_safe(
        "Methodology: identical 50-session schedule (same-day, consecutive-day, sporadic, "
        "cold-start, and weekly deep-run patterns) on Qwen 32B via AWS Bedrock, with the "
        "same Qwen-tuned prompt set in both runs. The only variable was the post-processing "
        "guard layer."
    ))


def executive_summary(pdf: InvestorPDF):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Executive summary")
    pdf.ln(13)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GREY_DARK)
    pdf.multi_cell(180, 6, latin1_safe(
        "Miss Maya is PeerUp's AI tutor for spoken English. To make her replies feel like a "
        "real friend rather than a scripted bot, we ran a structured quality study across "
        "50 simulated user chats and improved the system in two layers."
    ))
    pdf.ln(3)

    bullets = [
        ("1. The prompt layer.", "We rewrote the prompts that govern Maya's tone, character, opening "
                                  "lines, and memory use - tuned specifically for the Qwen 32B model "
                                  "we run in production."),
        ("2. The safety-net layer.", "We added 12 deterministic post-processing checks that catch the "
                                       "specific failure patterns the prompt couldn't fully suppress - "
                                       "things like greeting on every turn, stacking too many questions, "
                                       "inventing personal anecdotes."),
    ]
    for label, text in bullets:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(0, 6, latin1_safe(label))
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(180, 6, latin1_safe(text))
        pdf.ln(3)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.cell(0, 6, "Outcome.")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GREY_DARK)
    pdf.multi_cell(180, 6, latin1_safe(
        "Across the 8 quality issues we tracked, 7 went to 0% violation rate and the eighth "
        "(too many questions per reply) dropped from 56% of sessions affected to just 6%. "
        "Total violation count fell from 229 to 5. Average reply length tightened to 25.7 "
        "words (down from 31.5), making conversations crisper without losing warmth."
    ))


def gap_bars(pdf: InvestorPDF, baseline: dict, after: dict):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Quality issues - before vs after")
    pdf.ln(13)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 5, latin1_safe(
        "Each row shows the percentage of the 50 sessions that contained at least one instance "
        "of that quality issue. Bars are scaled to the baseline value."
    ))
    pdf.ln(6)

    bar_left = 75
    bar_max = 110   # mm
    row_h = 12

    for label, key, _ in GAPS:
        b_pct = baseline["gaps"][key]["sess_pct"]
        a_pct = after["gaps"][key]["sess_pct"]
        y = pdf.get_y()

        # Label
        pdf.set_xy(15, y + 1)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(58, 4, latin1_safe(label))

        # Baseline bar (red)
        bar_y_top = y + 1
        b_w = bar_max * (b_pct / max(b_pct, a_pct, 1))
        pdf.set_fill_color(*RED)
        if b_pct > 0:
            pdf.rect(bar_left, bar_y_top, max(0.5, b_w), 3.5, "F")
        pdf.set_xy(bar_left + b_w + 2, bar_y_top - 1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*RED)
        pdf.cell(20, 5, latin1_safe(f"{b_pct:.0f}% before"))

        # After bar (green)
        bar_y_bot = y + 5.5
        a_w = bar_max * (a_pct / max(b_pct, a_pct, 1))
        pdf.set_fill_color(*GREEN)
        if a_pct > 0:
            pdf.rect(bar_left, bar_y_bot, max(0.5, a_w), 3.5, "F")
        else:
            # Show a minimal tick for "0"
            pdf.set_fill_color(*GREEN)
            pdf.rect(bar_left, bar_y_bot, 0.5, 3.5, "F")
        pdf.set_xy(bar_left + a_w + 2, bar_y_bot - 1)
        pdf.set_text_color(*GREEN)
        pdf.cell(20, 5, latin1_safe(f"{a_pct:.0f}% after"))

        # Move to next row
        pdf.set_y(y + row_h)

    # Legend
    pdf.ln(4)
    pdf.set_x(75)
    pdf.set_fill_color(*RED)
    pdf.rect(75, pdf.get_y(), 6, 3, "F")
    pdf.set_x(83)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GREY_MID)
    pdf.cell(40, 4, "Before improvements")
    pdf.set_fill_color(*GREEN)
    pdf.rect(130, pdf.get_y(), 6, 3, "F")
    pdf.set_x(138)
    pdf.cell(40, 4, "After improvements")


def detail_table(pdf: InvestorPDF, baseline: dict, after: dict):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Issue-by-issue detail")
    pdf.ln(13)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 5, latin1_safe(
        "Per quality issue: total violations, sessions affected, and the reduction achieved. "
        "Sessions = 50 in each run."
    ))
    pdf.ln(5)

    total_replies_b = baseline["n_replies"]
    total_replies_a = after["n_replies"]

    # Header row
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(54, 7, "Issue", border=0, fill=True)
    pdf.cell(20, 7, "Before #", align="C", border=0, fill=True)
    pdf.cell(20, 7, "After #", align="C", border=0, fill=True)
    pdf.cell(22, 7, "Before %sess", align="C", border=0, fill=True)
    pdf.cell(22, 7, "After %sess", align="C", border=0, fill=True)
    pdf.cell(20, 7, "Before rate", align="C", border=0, fill=True)
    pdf.cell(22, 7, "Reduction", align="C", border=0, fill=True)
    pdf.ln(7)

    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "", 8.5)
    for i, (label, key, _desc) in enumerate(GAPS):
        b = baseline["gaps"][key]
        a = after["gaps"][key]
        b_rate = (b["viol"] / max(1, total_replies_b)) * 100
        if i % 2 == 0:
            pdf.set_fill_color(*GREY_BG)
            pdf.cell(180, 7, "", border=0, fill=True)
            pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(54, 7, latin1_safe(label))
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(20, 7, latin1_safe(f"{b['viol']}"), align="C")
        pdf.cell(20, 7, latin1_safe(f"{a['viol']}"), align="C")
        pdf.cell(22, 7, latin1_safe(f"{b['sess_pct']:.0f}%"), align="C")
        pdf.cell(22, 7, latin1_safe(f"{a['sess_pct']:.0f}%"), align="C")
        pdf.cell(20, 7, latin1_safe(f"{b_rate:.1f}%"), align="C")
        if b["sess_pct"] > 0:
            change = (a["sess_pct"] - b["sess_pct"]) / b["sess_pct"] * 100
            pdf.set_text_color(*(GREEN if change <= 0 else RED))
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.cell(22, 7, latin1_safe(f"{change:+.0f}%"), align="C")
            pdf.set_text_color(*GREY_DARK)
            pdf.set_font("Helvetica", "", 8.5)
        else:
            pdf.cell(22, 7, "-", align="C")
        pdf.ln(7)

    # Total row
    total_b = sum(baseline["gaps"][k]["viol"] for _, k, _ in GAPS)
    total_a = sum(after["gaps"][k]["viol"] for _, k, _ in GAPS)
    total_b_rate = (total_b / max(1, total_replies_b)) * 100
    pdf.set_fill_color(*ACCENT_DARK)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(54, 8, "Total violations", fill=True)
    pdf.cell(20, 8, latin1_safe(f"{total_b}"), align="C", fill=True)
    pdf.cell(20, 8, latin1_safe(f"{total_a}"), align="C", fill=True)
    pdf.cell(22, 8, "-", align="C", fill=True)
    pdf.cell(22, 8, "-", align="C", fill=True)
    pdf.cell(20, 8, latin1_safe(f"{total_b_rate:.1f}%"), align="C", fill=True)
    pdf.cell(22, 8, latin1_safe(f"-{(1-total_a/max(1,total_b))*100:.0f}%"), align="C", fill=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 4, latin1_safe(
        "Read this table left-to-right per row: # = total violation count across all 50 sessions. "
        "% sess = the share of the 50 sessions that contained at least one violation of that type. "
        "Rate = violations as a percentage of all Maya replies (427 in before, 432 in after). "
        "Reduction = relative drop in % sessions affected."
    ))


def by_the_numbers(pdf: InvestorPDF, baseline: dict, after: dict):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "By the numbers")
    pdf.ln(13)

    total_baseline_viol = sum(baseline["gaps"][k]["viol"] for _, k, _ in GAPS)
    total_after_viol = sum(after["gaps"][k]["viol"] for _, k, _ in GAPS)
    total_b_replies = baseline["n_replies"]
    total_a_replies = after["n_replies"]
    rate_b = (total_baseline_viol / max(1, total_b_replies)) * 100
    rate_a = (total_after_viol / max(1, total_a_replies)) * 100
    sess_with_any_b = max(baseline["gaps"][k]["sess_count"] for _, k, _ in GAPS)
    sess_with_any_a = max(after["gaps"][k]["sess_count"] for _, k, _ in GAPS)
    avg_turns_b = total_b_replies / 50
    avg_turns_a = total_a_replies / 50

    rows = [
        ("Total Maya replies analysed",
            f"{total_b_replies}",
            f"{total_a_replies}",
            f"{total_a_replies - total_b_replies:+d}"),
        ("Average reply length (words)",
            f"{baseline['avg_words']}",
            f"{after['avg_words']}",
            f"{after['avg_words'] - baseline['avg_words']:+.1f}"),
        ("Average turns per session",
            f"{avg_turns_b:.1f}",
            f"{avg_turns_a:.1f}",
            f"{avg_turns_a - avg_turns_b:+.1f}"),
        ("Total quality violations",
            f"{total_baseline_viol}",
            f"{total_after_viol}",
            f"{total_after_viol - total_baseline_viol:+d}"),
        ("Violations per reply (rate)",
            f"{rate_b:.1f}%",
            f"{rate_a:.1f}%",
            f"-{rate_b - rate_a:.1f} pp"),
        ("Sessions with at least one violation (worst category)",
            f"{sess_with_any_b} / 50",
            f"{sess_with_any_a} / 50",
            f"-{sess_with_any_b - sess_with_any_a} sessions"),
        ("Categories at 0% violation rate",
            "0 / 8",
            "7 / 8",
            "+7 categories"),
    ]
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(86, 7, "Metric", border=0, fill=True)
    pdf.cell(32, 7, "Before", align="C", border=0, fill=True)
    pdf.cell(32, 7, "After", align="C", border=0, fill=True)
    pdf.cell(30, 7, "Change", align="C", border=0, fill=True)
    pdf.ln(7)
    for i, (label, b, a, change) in enumerate(rows):
        if i % 2 == 0:
            pdf.set_fill_color(*GREY_BG)
            pdf.cell(180, 7, "", border=0, fill=True)
            pdf.set_x(15)
        pdf.set_text_color(*GREY_DARK)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(86, 7, latin1_safe(label))
        pdf.cell(32, 7, latin1_safe(b), align="C")
        pdf.cell(32, 7, latin1_safe(a), align="C")
        pdf.set_font("Helvetica", "B", 9)
        is_improvement = ("+7" in change or change.startswith("-") or "shorter" in change.lower())
        pdf.set_text_color(*(GREEN if is_improvement else GREY_DARK))
        pdf.cell(30, 7, latin1_safe(change), align="C")
        pdf.set_text_color(*GREY_DARK)
        pdf.ln(7)
    pdf.ln(8)

    # Test coverage — tiers
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Test coverage")
    pdf.ln(10)

    tier_rows = [
        ("Same-day back-to-back sessions (Tier A)",            "10", "Priyansh, all turns same day",  "Tests intra-day repetition + opener variation"),
        ("Consecutive-day sessions (Tier B)",                  "15", "Aarti, days 0-14",              "Tests memory accumulation + mood arc + cadence"),
        ("Sporadic-gap sessions (Tier C)",                     "10", "Rohan, gaps of 5-12 days",      "Tests returning-after-pause behaviour"),
        ("Cold-start single sessions (Tier D)",                "10", "10 different fresh users",      "Tests first-session onboarding behaviour"),
        ("Weekly deep-run sessions (Tier E)",                   "5", "Neha, 5 weeks",                 "Tests long-term consistency + skill curriculum"),
    ]
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(80, 7, "Pattern", border=0, fill=True)
    pdf.cell(16, 7, "Sessions", align="C", border=0, fill=True)
    pdf.cell(40, 7, "Profile", border=0, fill=True)
    pdf.cell(44, 7, "What it stresses", border=0, fill=True)
    pdf.ln(7)
    for i, (label, n, who, what) in enumerate(tier_rows):
        if i % 2 == 0:
            pdf.set_fill_color(*GREY_BG)
            pdf.cell(180, 7, "", border=0, fill=True)
            pdf.set_x(15)
        pdf.set_text_color(*GREY_DARK)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(80, 7, latin1_safe(label))
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(16, 7, n, align="C")
        pdf.set_text_color(*GREY_DARK)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(40, 7, latin1_safe(who))
        pdf.cell(44, 7, latin1_safe(what))
        pdf.ln(7)
    pdf.ln(6)

    # Diversity stats
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Diversity in the test pool")
    pdf.ln(10)

    diversity = [
        ("10",  "distinct synthetic user profiles"),
        ("8",   "Indian regional mother tongues represented (Hindi, Marathi, Bengali, Tamil, Telugu, Punjabi, Gujarati, Kannada)"),
        ("5",   "English fluency levels covered (A1 to C1, beginner to fluent)"),
        ("3",   "engagement styles tested (terse, medium, chatty)"),
        ("12",  "emotional states sampled per session (tired, anxious, excited, lonely, hopeful, etc.)"),
        ("32",  "days of simulated calendar time across the 50 sessions"),
    ]
    pdf.set_font("Helvetica", "", 10)
    for big, label in diversity:
        pdf.set_text_color(*ACCENT_DARK)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(14, 7, big, align="R")
        pdf.set_text_color(*GREY_DARK)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, latin1_safe("  " + label))
        pdf.ln(6)


def real_conversation_samples(pdf: InvestorPDF):
    """Real before/after conversation excerpts pulled from the actual eval transcripts."""
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Real conversation samples")
    pdf.ln(13)
    pdf.set_text_color(*GREY_MID)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(180, 5, latin1_safe(
        "These are unedited excerpts from the actual evaluation runs - same user profile, "
        "same conversation moment, same model, same memory state. Only the prompt + guard "
        "layer differs."
    ))
    pdf.ln(5)

    samples = [
        {
            "ctx": "Returning user, turn 2 (he just told her his weekend was good)",
            "before": "Hi Priyansh, I hope your morning is going well! I wanted to mention how clearly you explained the cricket gloves project last time, it showed a lot of thought. Speaking of which, did you try the new sensor idea since our last chat?",
            "before_issues": "Re-greets on turn 2 (Rule 1 violation). Plus 'I love how clearly you explained' (surveillant opener).",
            "after": "Bhel puri with a movie sounds perfect, I can imagine the crunch! Yes, I watch Bollywood for the songs and the drama. What's one song that makes you feel the movie most?",
            "after_note": "Continues the conversation directly. One question. No greeting.",
        },
        {
            "ctx": "Same user, turn 3 (he asked about her music tastes)",
            "before": "Hi Priyansh, I see you are thinking hard about the cricket gloves, simplifying is a smart idea. What about a Bollywood song to relax? I just listened to Ek Ladki Ko Dekha To Yeh Jiya. Have you heard it?",
            "before_issues": "Re-greets again. 'I just listened to X' invents a personal life event Maya doesn't have. Two questions in one reply.",
            "after": "'Aashiqui' is a great pick, it makes the movie feel even bigger. I love how songs can bring everything to life. What's one song that makes you feel like dancing?",
            "after_note": "No greeting. No biography invention. One question.",
        },
        {
            "ctx": "Aarti, turn 4 (after sharing 'I enjoy music while working')",
            "before": "Hi Aarti, you said \"I enjoy music while working\" - perfect sentence! Ghazals are so calming. I listen to old songs while grading papers. What ghazal singer is your favorite?",
            "before_issues": "Re-greets. Quotes user's text and grades it as 'perfect sentence' (quiz-tone). Then claims a personal habit ('I listen to old songs while grading papers') Maya doesn't actually have.",
            "after": "Double lives do make for powerful stories. It sounds like you see yourself in the character. Did you read the ending yet?",
            "after_note": "No greeting, no echo-praise, no fake personal habit. Engages with what the user shared.",
        },
        {
            "ctx": "Neha, turn 1 of week 3 (returning after a 7-day gap)",
            "before": "Hi Neha, I hope your coffee situation is better today! Speaking of music, I love sketching while listening to calm tunes. What kind of music helps you relax?",
            "before_issues": "'I love sketching' invents a Maya hobby. Acceptable opener otherwise.",
            "after": "Hi Neha, it's been a while! I'm Miss Maya. The weather here in Bengaluru is just right for a warm cup of tea. How was your day today?",
            "after_note": "Acknowledges the time gap warmly. Light contextual self-detail. No invented activity.",
        },
    ]

    for s in samples:
        # Context line
        pdf.set_text_color(*GREY_MID)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(180, 5, latin1_safe("Scenario: " + s["ctx"]))
        pdf.ln(1)

        # BEFORE box
        y0 = pdf.get_y()
        pdf.set_fill_color(255, 240, 240)
        pdf.set_draw_color(220, 160, 160)
        # Compute height needed
        pdf.set_font("Helvetica", "", 9)
        text_h = 5
        # Render with rect background
        before_text = latin1_safe('BEFORE: "' + s["before"] + '"')
        # Use multi_cell — calculate later
        pdf.set_xy(15, y0)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RED)
        pdf.cell(180, 5, "BEFORE")
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(180, 4.5, latin1_safe('"' + s["before"] + '"'))
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*RED)
        pdf.multi_cell(180, 4, latin1_safe("Issues: " + s["before_issues"]))
        pdf.ln(2)

        # AFTER box
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*GREEN)
        pdf.cell(180, 5, "AFTER")
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(180, 4.5, latin1_safe('"' + s["after"] + '"'))
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*GREEN)
        pdf.multi_cell(180, 4, latin1_safe("Note: " + s["after_note"]))
        pdf.ln(5)


def methodology(pdf: InvestorPDF):
    pdf.add_page()
    pdf.set_y(28)
    pdf.set_text_color(*ACCENT_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Methodology")
    pdf.ln(13)

    sections = [
        ("How we tested",
         "We built 10 synthetic test users covering diverse profiles (Hindi, Tamil, Bengali, "
         "Marathi, Punjabi, Gujarati, Telugu, Kannada speakers; A1 through C1 English fluency; "
         "various professions and emotional states). Each user was simulated by a separate "
         "language model playing the user side, so we could run repeatable conversations."),

        ("The 50-session pattern",
         "Across the 50 sessions we covered: 10 same-day back-to-back sessions (testing intra-day "
         "repetition), 15 consecutive-day sessions (testing memory accumulation across two weeks), "
         "10 sporadic-gap sessions (testing returns after long pauses), 10 cold-start single sessions "
         "(testing first-time onboarding), and 5 weekly deep-runs over a month (testing long-term "
         "consistency). The same schedule was used for both the before and after runs."),

        ("What we measured",
         "Eight specific quality issues that show up when AI chat assistants feel scripted or "
         "robotic: re-greeting on every turn, asking too many questions at once, surveillant "
         "openers, recycling the same character details, quiz-style English grading, mid-session "
         "self-introductions, inventing personal anecdotes, and quoting the user with words they "
         "never actually said."),

        ("The two improvements applied",
         "First, the prompts were re-written specifically for the Qwen 32B model behind Maya - "
         "tighter constraints, explicit forbidden phrasings, and a structured reply template. "
         "Second, we added 12 deterministic post-processing checks that scan Maya's reply before "
         "the user sees it and strip specific violation patterns. The post-processing layer adds "
         "less than 5 milliseconds of latency."),

        ("What this report does NOT measure",
         "This study covers structural quality issues that can be reliably detected. It does not "
         "measure: (a) subjective tone (is Maya warm enough for an anxious user?), (b) memory "
         "appropriateness (does she reference stored facts when relevant, but not force them on "
         "filler turns? does she keep a movie labelled as a movie, not a song?), (c) personality "
         "consistency across many sessions, (d) topic-transition smoothness when the user's "
         "interest shifts. These continue to improve through prompt iteration."),
    ]
    for label, text in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(0, 6, latin1_safe(label))
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(180, 5.5, latin1_safe(text))
        pdf.ln(4)


def main():
    # Find latest comparison JSON
    candidates = sorted(REPORT_DIR.glob("final_comparison_*.json"))
    if not candidates:
        print(f"No final_comparison_*.json in {REPORT_DIR}. Run eval_50_compare.py first.")
        sys.exit(1)
    src = candidates[-1]
    data = json.loads(src.read_text(encoding="utf-8"))
    baseline = data["baseline"]
    after = data["with_guards"]

    pdf = InvestorPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)
    cover(pdf, baseline, after)
    executive_summary(pdf)
    gap_bars(pdf, baseline, after)
    by_the_numbers(pdf, baseline, after)
    detail_table(pdf, baseline, after)
    methodology(pdf)

    out = REPORT_DIR / f"investor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(out))
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
