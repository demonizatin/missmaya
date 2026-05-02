"""eval_50_judge_report.py — honest comparison report for the judge-only eval.

Compares the WITH-GUARDS (12 regex post-processors) baseline against the
JUDGE-ONLY (single Qwen LLM-as-judge) replacement. Surfaces the wins, the
regressions (notably: em-dashes), and the unrelated finding that the
librarian still routes through Haiku via the `claude` CLI.
"""

import json
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

ROOT = Path(__file__).parent / "memory_store" / "_eval_50"
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)
SCORE_PATH = ROOT / "validation_judge_only" / "score_summary.json"

ACCENT       = (107, 63, 160)
ACCENT_DARK  = (60, 30, 100)
RED          = (168, 56, 56)
RED_BG       = (253, 240, 240)
GREEN        = (42, 122, 58)
GREEN_BG     = (240, 250, 242)
ORANGE       = (200, 110, 30)
ORANGE_BG    = (253, 245, 230)
GREY_DARK    = (40, 40, 40)
GREY_MID     = (110, 110, 110)
GREY_LIGHT   = (180, 180, 180)
GREY_BG      = (245, 243, 250)
AMBER_BG     = (255, 248, 230)


def latin1(text: str) -> str:
    repl = {
        "—": "-", "–": "-", "•": "*", "“": '"', "”": '"',
        "‘": "'", "’": "'", "…": "...",
        "→": "->", "←": "<-", "≥": ">=", "≤": "<=", "×": "x",
    }
    out = text or ""
    for k, v in repl.items():
        out = out.replace(k, v)
    return out.encode("latin-1", errors="ignore").decode("latin-1")


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY_MID)
        self.cell(0, 6, "Miss Maya - Judge-vs-regex evaluation report", align="L")
        self.set_x(-30)
        self.cell(0, 6, f"Page {self.page_no()}", align="R")
        self.ln(8)
        self.set_draw_color(*GREY_LIGHT)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)


def cover(pdf: PDF):
    pdf.add_page()
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 70, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(22)
    pdf.cell(0, 12, "Miss Maya - Honest comparison", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_y(40)
    pdf.cell(0, 7, "Replacing 12 regex output guards with one Qwen LLM-as-judge", align="C")
    pdf.set_y(50)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, datetime.now().strftime("Generated %Y-%m-%d %H:%M IST"), align="C")

    pdf.set_text_color(*GREY_DARK)
    pdf.set_y(85)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Bottom line up front")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10.5)
    body = (
        "Across 50 synthetic Maya sessions per arm (~435 Maya turns each), the LLM judge replaced "
        "all 12 deterministic regex guards. Conceptual rules - greetings, self-intros, fabricated "
        "biography, canned persona phrases - are caught BETTER by the judge: greeting-on-turn-2 "
        "regressions dropped from 32 to 15 sessions, mid-session self-intros went from 18 sessions "
        "to ZERO, and bio/soft-bio fabrications fell from 5 turns to ZERO. Mechanical rules - "
        "specifically the em-dash ban - regressed badly: the regex caught 100% of em-dashes "
        "(0 leaks), the judge let 363 turns through across all 50 sessions (82.9%). The "
        "two-question oscillation also regressed (3.2% -> 9.1%). Net: judge wins on intent, "
        "regex wins on punctuation. After 4 prompt iterations, the explicit decision was to "
        "ACCEPT the dash + multi-q regression rather than introduce any code dependency - "
        "mechanical-rule enforcement via prompt has a hard ceiling on Qwen 32B that further "
        "iteration will not break. The librarian was also moved off the Haiku CLI to Qwen "
        "in the same change set."
    )
    pdf.multi_cell(0, 5.4, latin1(body))

    pdf.ln(6)
    pdf.set_fill_color(*GREY_BG)
    pdf.rect(15, pdf.get_y(), 180, 56, "F")
    pdf.set_xy(20, pdf.get_y() + 4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "What changed in code")
    pdf.ln(7)
    pdf.set_font("Helvetica", "", 10)
    bullets = [
        "Removed: pg_apply_output_guard + 8 _PG_GUARD_* pattern lists (360 lines deleted from app.py)",
        "Added: judge_guard.py (~190 lines: prompt + adapter + JSON parser)",
        "Wired judge_review() into 5 call sites: chat(), pg_chat(), eval_50.call_maya()",
        "Pre-flight gate: 30 violations + 10 benign cases. Required >=90% recall, <=10% FP",
        "Pre-flight result: 100% recall (30/30), 10% FP (1/10 - and that 'FP' was a real soft-bio violation)",
    ]
    for b in bullets:
        pdf.set_x(22)
        pdf.cell(3, 5, "*")
        pdf.set_x(26)
        pdf.multi_cell(165, 5, latin1(b))


def category_table(pdf: PDF, score: dict):
    pdf.add_page()
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Per-category violation rates")
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5.2, latin1(
        "Each row counts the number of Maya turns containing the violation, "
        "the number of distinct sessions affected, and the share of total "
        "Maya turns. Counts are run in the same scoring harness on both arms."
    ))
    pdf.ln(3)

    a = score["baseline"]
    b = score["judge_only"]
    rows = [
        ("greeting_t2", "Turn 2+ starts with 'Hi/Hello' + name"),
        ("self_intro_t2", "'I'm Miss Maya' on returning user"),
        ("multi_q", "More than one '?' in a single reply"),
        ("bio_hard", "'I watched/listened/cooked X' fabrications"),
        ("soft_bio", "'I follow cricket', 'I'm a tea person', etc."),
        ("location_claim", "'here in Bengaluru', 'I grew up in Pune'"),
        ("love_how_you", "Surveillant openers"),
        ("echo_praise", "'You said X - perfect!'"),
        ("canned_persona", "'cardamom chai', 'old Hindi songs'"),
        ("fake_quote", "Quoting words user did not say"),
        ("emoji", "Any emoji codepoint"),
        ("dashes", "em/en-dash or hyphen between words"),
    ]
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_fill_color(*GREY_BG)
    pdf.set_text_color(*GREY_DARK)
    pdf.cell(38, 7, " Category", border=0, fill=True)
    pdf.cell(60, 7, " Description", border=0, fill=True)
    pdf.cell(38, 7, "  Before (regex)", border=0, fill=True, align="C")
    pdf.cell(38, 7, "  After (judge)", border=0, fill=True, align="C")
    pdf.cell(8, 7, "")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 9)
    for cat, desc in rows:
        a_t = a["counts"].get(cat, 0)
        b_t = b["counts"].get(cat, 0)
        a_s = len(a["sessions_with"].get(cat, []))
        b_s = len(b["sessions_with"].get(cat, []))
        a_pct = a_t / max(1, a["n_maya_turns"]) * 100
        b_pct = b_t / max(1, b["n_maya_turns"]) * 100

        # Verdict color
        if b_t == a_t == 0:
            verdict_color = GREY_LIGHT
            verdict = "stable"
        elif b_t < a_t:
            verdict_color = GREEN
            verdict = "win"
        elif b_t > a_t:
            verdict_color = RED
            verdict = "regression"
        else:
            verdict_color = GREY_LIGHT
            verdict = "tie"

        pdf.set_text_color(*GREY_DARK)
        pdf.cell(38, 6, " " + latin1(cat))
        pdf.set_text_color(*GREY_MID)
        pdf.cell(60, 6, " " + latin1(desc[:36]))

        pdf.set_text_color(*GREY_DARK)
        pdf.cell(38, 6, f"  {a_t:>3} t / {a_s:>2} s ({a_pct:>4.1f}%)", align="C")
        pdf.cell(38, 6, f"  {b_t:>3} t / {b_s:>2} s ({b_pct:>4.1f}%)", align="C")

        pdf.set_text_color(*verdict_color)
        pdf.cell(8, 6, " " + latin1({"win": "v", "regression": "x", "stable": "=", "tie": "="}[verdict]))
        pdf.ln(6)

    pdf.ln(5)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*GREY_MID)
    totals = (
        f"Total Maya turns scored: baseline {a['n_maya_turns']}, judge-only {b['n_maya_turns']}. "
        f"50 sessions per arm. Same scoring regex applied to both runs (consistent measurement)."
    )
    pdf.multi_cell(0, 4.8, latin1(totals))


def wins_section(pdf: PDF, score: dict):
    pdf.add_page()
    pdf.set_text_color(*GREEN)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Wins - where the judge beats the regex")
    pdf.ln(11)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5.2, latin1(
        "These are categories where understanding intent matters more than pattern-matching. "
        "Regex catches what it was written for; the judge catches the family of variations "
        "the writer didn't anticipate."
    ))
    pdf.ln(4)

    wins = [
        ("self_intro_t2", "From 18 sessions to ZERO",
         "The regex hit 'I'm Miss Maya' literally. The judge understands the rule "
         "('don't reintroduce yourself to a returning user') and catches paraphrases "
         "like 'I am your English chat partner' the regex missed."),
        ("greeting_t2", "32 sessions -> 15 sessions (~53% drop)",
         "The judge understands 'don't greet on turn 2+'. The regex was strict about "
         "'Hi/Hello' but missed greeting-shaped openers ('Good to hear from you again, "
         "Aarti!'). Judge cleans both."),
        ("bio_hard", "1 session -> 0 sessions",
         "Judge eliminated all 'I watched/listened/cooked X' fabrications. Marginal "
         "delta because baseline regex was already strong here, but verifies no regression."),
        ("soft_bio", "3 sessions -> 0 sessions",
         "The 'I follow cricket / I'm a morning person' family of soft fabrications "
         "is gone. This was the category most likely to leak through the regex - "
         "the judge handles it cleanly after one prompt iteration."),
    ]
    for cat, headline, body in wins:
        pdf.set_fill_color(*GREEN_BG)
        pdf.set_draw_color(*GREEN)
        y0 = pdf.get_y()
        pdf.set_xy(15, y0)
        pdf.cell(180, 6, "")
        pdf.set_xy(15, y0)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*GREEN)
        pdf.cell(60, 6, " " + latin1(cat))
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*GREY_DARK)
        pdf.cell(0, 6, latin1(headline))
        pdf.ln(7)
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*GREY_MID)
        pdf.multi_cell(180, 4.8, "  " + latin1(body))
        pdf.ln(3)


def regressions_section(pdf: PDF, score: dict):
    pdf.add_page()
    pdf.set_text_color(*RED)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Regressions - where the judge under-performs")
    pdf.ln(11)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5.2, latin1(
        "Mechanical / surface-level rules don't need understanding. A regex catches them "
        "100% of the time and zero false positives. The judge has to weigh them against "
        "every other rule in the prompt and tends to prioritize 'the reply still reads naturally' "
        "over 'punctuation is exactly right'."
    ))
    pdf.ln(4)

    b = score["judge_only"]
    samples_dashes = b["samples"].get("dashes", [])
    samples_multiq = b["samples"].get("multi_q", [])

    # Em-dashes
    pdf.set_fill_color(*RED_BG)
    pdf.set_draw_color(*RED)
    pdf.rect(15, pdf.get_y(), 180, 6, "F")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*RED)
    pdf.cell(60, 6, "  dashes (em/en-dash)")
    pdf.set_text_color(*GREY_DARK)
    pdf.cell(0, 6, latin1("0 turns -> 363 turns (50/50 sessions, 82.9% of all Maya turns)"))
    pdf.ln(8)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 4.8, latin1(
        "  This is the headline regression. The regex stripped every em-dash by "
        "definition (a one-liner). The judge enumerates rule_10 in its violation list "
        "occasionally but doesn't actually rewrite the dashes out - the cost-benefit "
        "of rewriting a whole reply just to swap a dash for a comma is unfavorable to it. "
        "Fix: a single non-LLM substitution at the end (cleaned.replace(chr(8212), ',')) "
        "would close this gap entirely without resurrecting the regex layer."
    ))
    if samples_dashes:
        pdf.ln(2)
        for s in samples_dashes[:2]:
            pdf.set_x(20)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(*GREY_MID)
            pdf.multi_cell(170, 4.2, "  " + latin1(f"{s[0]} T{s[1]}: {s[2]}"))
    pdf.ln(4)

    # Multi-q
    pdf.set_fill_color(*RED_BG)
    pdf.set_draw_color(*RED)
    pdf.rect(15, pdf.get_y(), 180, 6, "F")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*RED)
    pdf.cell(60, 6, "  multi_q (>1 question mark)")
    pdf.set_text_color(*GREY_DARK)
    pdf.cell(0, 6, latin1("14 turns / 8 sessions -> 40 turns / 21 sessions (3.2% -> 9.1%)"))
    pdf.ln(8)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(180, 4.8, latin1(
        "  The regex used to strip extra '?' characters mechanically. The judge sees "
        "two questions and decides the reply still reads coherently, so it leaves them. "
        "This is the rule the judge weighs least aggressively because the prose flow "
        "argument competes with the rule. Same fix as dashes: a tiny mechanical post-step "
        "(if reply.count('?') > 1: keep only the last) would restore parity."
    ))
    if samples_multiq:
        pdf.ln(2)
        for s in samples_multiq[:2]:
            pdf.set_x(20)
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(*GREY_MID)
            pdf.multi_cell(170, 4.2, "  " + latin1(f"{s[0]} T{s[1]}: {s[2]}"))


def architectural_finding(pdf: PDF):
    pdf.add_page()
    pdf.set_text_color(*ORANGE)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Architectural finding - librarian routing")
    pdf.ln(11)
    pdf.set_fill_color(*ORANGE_BG)
    pdf.rect(15, pdf.get_y(), 180, 26, "F")
    pdf.set_xy(20, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*ORANGE)
    pdf.cell(0, 6, latin1("The librarian is on Anthropic Haiku via the `claude` CLI - not Qwen."))
    pdf.ln(7)
    pdf.set_x(20)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*GREY_DARK)
    pdf.multi_cell(170, 4.8, latin1(
        "  call_llm_oneshot() in app.py prefers the Anthropic API client (Sonnet 4.6) "
        "if AnthropicAPIKey is set, otherwise falls back to: claude -p --model haiku. "
        "This is the function the librarian uses to merge each session into long-term memory."
    ))

    pdf.ln(6)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Why this matters")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(0, 5.2, latin1(
        "Your stated preference was: keep everything on Qwen, including the librarian. "
        "The current code does NOT match that - the librarian falls through to the Haiku "
        "CLI on every session-end. During this 50-session run, the run log shows 10 "
        "'[pg-memory] LLM call FAILED' entries (the Haiku CLI failing transiently). The "
        "judge-only chat path works fine; the librarian background task is a separate "
        "concern that pre-dates today's changes."
    ))
    pdf.ln(2)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Fix")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(0, 5.2, latin1(
        "Replace call_llm_oneshot() body with a Qwen-via-Bedrock call (same shape as "
        "the judge - one prompt in, one full string out). ~25 lines. Removes the Haiku "
        "dependency entirely and consolidates the model split to: Qwen for everything."
    ))


def recommendations(pdf: PDF):
    pdf.add_page()
    pdf.set_text_color(*ACCENT)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Recommendations")
    pdf.ln(11)

    items = [
        ("1. Live with the dash + multi-q regression for now",
         "Decision after 4 prompt iterations: prompt-only enforcement of mechanical "
         "rules has a hard ceiling on Qwen 32B. Variants tried: (a) inline rule, (b) "
         "explicit STEP A/B framing, (c) MANDATORY PRE-CHECK section, (d) few-shot "
         "worked example. Best-case 233 of 363 dash turns fixed (still 49/50 sessions "
         "affected); multi-q-only cases stayed at 0/3 in pre-flight regardless. The "
         "stronger the mechanical-rule emphasis, the worse the semantic-rule recall "
         "(greeting_t2 regressed back to baseline, canned_persona / echo_praise / emoji "
         "started leaking). Chosen path: keep v1 prompt, accept the residuals."),

        ("2. Librarian moved to Qwen (DONE this run)",
         "call_llm_oneshot() now routes through stream_via_bedrock_qwen with model "
         "qwen.qwen3-32b-v1:0. The Anthropic Haiku CLI fallback is gone. Smoke test "
         "returned 'READY'. Run #1 logged 10 librarian failures from the old Haiku "
         "path; Qwen librarian path so far has 0 failures."),

        ("3. Track judge confidence in production",
         "judge_guard.py already returns confidence in its JSON. Log the confidence per "
         "Maya reply so we can spot drift if Qwen's behavior changes after a model update. "
         "If avg confidence drops below 0.85 over a rolling window, page someone."),

        ("4. Iterate the judge prompt only when SEMANTIC regressions appear",
         "Empirical lesson: prompt iterations work for semantic rules ('don't fabricate "
         "biography', 'don't reintroduce yourself') and break down for mechanical rules "
         "('exactly one ?', 'no em-dash'). When future evals surface new SEMANTIC failure "
         "modes, add a rule to JUDGE_PROMPT_TEMPLATE and re-run pre-flight. For "
         "mechanical regressions, the honest answer is either accept them or add a "
         "1-line post-strip - prompt iteration alone won't close the gap."),
    ]
    for title, body in items:
        pdf.set_fill_color(*GREY_BG)
        y0 = pdf.get_y()
        pdf.rect(15, y0, 180, 6, "F")
        pdf.set_xy(15, y0)
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(0, 6, "  " + latin1(title))
        pdf.ln(8)
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*GREY_MID)
        pdf.multi_cell(180, 4.8, "  " + latin1(body))
        pdf.ln(4)


def methodology(pdf: PDF):
    pdf.add_page()
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Methodology")
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5.4, latin1(
        "Two arms, both running the same QWEN-tuned prompt set. Same 50-session schedule:"
    ))
    pdf.ln(2)
    bullets = [
        ("Tier A", "10 same-day sessions on one user (Priyansh)"),
        ("Tier B", "15 consecutive-day sessions on one user (Aarti)"),
        ("Tier C", "10 sporadic-gap sessions on one user (Rohan)"),
        ("Tier D", "10 cold-start sessions on 10 distinct fresh users"),
        ("Tier E", "5 deep-run weekly sessions on one user (Neha)"),
    ]
    for tier, desc in bullets:
        pdf.set_x(20)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*ACCENT_DARK)
        pdf.cell(20, 5, latin1(tier))
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*GREY_DARK)
        pdf.multi_cell(160, 5, latin1(desc))

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_DARK)
    pdf.multi_cell(0, 5.4, latin1(
        "User responses are simulated by a separate model (Sonnet) playing each profile. "
        "Maya replies via Bedrock-Qwen. Both arms wrote into isolated memory directories "
        "so neither arm contaminated the other."
    ))
    pdf.ln(3)
    pdf.set_text_color(*GREY_DARK)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "What we are not measuring")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GREY_MID)
    pdf.multi_cell(0, 5.2, latin1(
        "These rate-based numbers say nothing about whether Maya's replies feel WARM. "
        "The judge can be 100% correct on every rule and still produce stiff, transactional "
        "prose. Tone fidelity is a human-eval problem and would need a separate read-through. "
        "We also did not measure latency impact - the judge adds one extra Qwen round-trip "
        "(~0.7s observed in pre-flight) per Maya reply."
    ))


def main():
    score = json.loads(SCORE_PATH.read_text(encoding="utf-8"))
    pdf = PDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)

    cover(pdf)
    category_table(pdf, score)
    wins_section(pdf, score)
    regressions_section(pdf, score)
    architectural_finding(pdf)
    recommendations(pdf)
    methodology(pdf)

    out = OUT_DIR / f"judge_vs_regex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(out))
    print(f"PDF -> {out}  ({out.stat().st_size/1024:.1f} KB, {pdf.page_no()} pages)")


if __name__ == "__main__":
    main()
