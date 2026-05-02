"""Render the latest gap report (.md) as a PDF using fpdf2.

Usage:
    python eval_50_pdf.py                  # picks the latest gap_report_*.md
    python eval_50_pdf.py path/to/file.md  # explicit path
"""

import re
import sys
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.errors import FPDFException

EVAL_REPORT_DIR = Path(__file__).parent / "memory_store" / "_eval_50" / "reports"


class ReportPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Eval-50 gap report — Miss Maya / Qwen-tuned prompts", align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _safe_multi_cell(pdf: FPDF, h: float, text: str, indent: float = 0.0) -> None:
    """multi_cell that can't crash on long unbreakable tokens — falls back to
    truncating per line. Always resets x to the left margin (+ optional indent)."""
    text = text or " "
    pdf.set_x(18 + indent)
    width = 210 - 18 - 18 - indent   # page - margins - indent
    try:
        pdf.multi_cell(width, h, text)
    except FPDFException:
        # Force-break long tokens by inserting spaces every 60 chars.
        chunked = " ".join(
            text[i : i + 60] if " " not in text[i : i + 60] else text[i : i + 60]
            for i in range(0, len(text), 60)
        ) if not any(len(w) > 60 for w in text.split()) else \
            "\n".join(text[i : i + 80] for i in range(0, len(text), 80))
        try:
            pdf.set_x(18 + indent)
            pdf.multi_cell(width, h, chunked)
        except FPDFException:
            pdf.set_x(18 + indent)
            pdf.cell(width, h, text[:120])
            pdf.ln(h)


def md_to_pdf(md_text: str, out_path: Path) -> None:
    """Light markdown renderer — handles #/##/###, **bold**, `code`, lists, code fences,
    horizontal rules. Doesn't fully handle tables (renders pipe-rows as plain lines)."""
    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(18, 18, 18)

    in_code_block = False
    for raw_line in md_text.splitlines():
        # Code fence toggle
        if raw_line.strip().startswith("```"):
            in_code_block = not in_code_block
            pdf.ln(2)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 9)
            pdf.set_text_color(60, 60, 60)
            pdf.set_fill_color(245, 245, 248)
            text = raw_line.replace("\t", "    ") or " "
            pdf.cell(0, 5, text[:200], fill=True)
            pdf.ln(5)
            continue

        line = raw_line.rstrip()

        # Headings
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(30, 30, 30)
            pdf.ln(3)
            _safe_multi_cell(pdf, 9, _ascii(line[2:]))
            pdf.ln(2)
            continue
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(120, 50, 30)
            pdf.ln(3)
            _safe_multi_cell(pdf, 7, _ascii(line[3:]))
            pdf.ln(1)
            continue
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(60, 60, 60)
            pdf.ln(2)
            _safe_multi_cell(pdf, 6, _ascii(line[4:]))
            continue
        if line.startswith("#### "):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(80, 80, 80)
            _safe_multi_cell(pdf, 5, _ascii(line[5:]))
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            y = pdf.get_y()
            pdf.line(18, y, 192, y)
            pdf.ln(3)
            continue

        # Bullets
        if re.match(r"^\s*[-*]\s+", line):
            text = re.sub(r"^\s*[-*]\s+", "", line)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            _safe_multi_cell(pdf, 5, "- " + _render_inline(text), indent=4)
            continue

        # Numbered list item
        if re.match(r"^\s*\d+\.\s+", line):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            _safe_multi_cell(pdf, 5, _render_inline(line.strip()))
            continue

        # Empty line
        if not line.strip():
            pdf.ln(2)
            continue

        # Default paragraph
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        _safe_multi_cell(pdf, 5, _render_inline(line))

    pdf.output(str(out_path))


def _render_inline(text: str) -> str:
    """Strip markdown inline formatting since fpdf doesn't do mixed inline styles
    cleanly without a richer renderer. Bold/italic/code markers removed but
    content preserved. Tables (pipe-rows) become plain pipe-separated text."""
    s = text
    # **bold** → BOLD MARKER kept inline as plain
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return _ascii(s)


def _ascii(text: str) -> str:
    """fpdf with built-in fonts only handles latin-1. Replace common non-latin chars."""
    replacements = {
        "—": "-", "–": "-", "•": "*", "✓": "[ok]", "✗": "[x]",
        "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
        "→": "->", "←": "<-", "↔": "<->", "↦": "->", "≥": ">=", "≤": "<=", "×": "x",
        "📋": "[clip]", "⬇": "[dl]", "🧪": "[test]", "📦": "[box]", "💬": "[chat]",
        "📅": "[cal]", "📁": "[dir]", "📨": "[in]", "🔥": "[hot]",
    }
    out = text
    for k, v in replacements.items():
        out = out.replace(k, v)
    # final fallback: strip any remaining non-latin1
    return out.encode("latin-1", errors="ignore").decode("latin-1")


def main():
    if len(sys.argv) > 1:
        md_path = Path(sys.argv[1])
    else:
        md_files = sorted(EVAL_REPORT_DIR.glob("gap_report_*.md"))
        if not md_files:
            print(f"No gap_report_*.md found in {EVAL_REPORT_DIR}. Run `python eval_50.py analyze` first.")
            sys.exit(1)
        md_path = md_files[-1]
    md_text = md_path.read_text(encoding="utf-8")
    out_path = md_path.with_suffix(".pdf")
    md_to_pdf(md_text, out_path)
    print(f"Wrote PDF: {out_path}")


if __name__ == "__main__":
    main()
