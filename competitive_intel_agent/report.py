"""
CLI report generator for the Competitive Intelligence Agent.

Generates both a Markdown file and a styled PDF from a single run.

Usage:
    python3 -m competitive_intel_agent.report "ProsperOps" "Archera"
    python3 -m competitive_intel_agent.report "Cast AI" "Archera" --context "..." --output reports/cast_ai
    python3 -m competitive_intel_agent.report "Spot.io" "Archera" --update

Outputs (given --output reports/foo):
    reports/foo.md   — full markdown battlecard
    reports/foo.pdf  — styled PDF ready to share or print
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import anyio
from dotenv import load_dotenv

# ── Load env from project root ───────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env", override=True)

from .agent import build_battlecard, update_battlecard_from_file  # noqa: E402
from .battlecard import Battlecard                                 # noqa: E402
from .formatter import to_markdown                                 # noqa: E402


# ── PDF generation ───────────────────────────────────────────────────────────

# Colour palette
PURPLE      = (124, 58, 237)
DARK_BG     = (15, 15, 17)
LIGHT_TEXT  = (226, 226, 229)
MUTED       = (136, 136, 136)
WHITE       = (255, 255, 255)
NEAR_WHITE  = (240, 240, 243)
BORDER      = (42, 42, 48)
CONFIRMED_C = (74, 222, 128)   # green
REPORTED_C  = (251, 191, 36)   # amber
INFERRED_C  = (167, 139, 250)  # purple

CONF_LABELS = {"confirmed": "OK", "reported": "~", "inferred": "?"}
CONF_COLORS = {
    "confirmed": CONFIRMED_C,
    "reported":  REPORTED_C,
    "inferred":  INFERRED_C,
}

# Emoji → ASCII for PDF (fpdf2's core fonts don't support emoji)
EMOJI_MAP = {
    "✅": "[OK]", "⚠️": "[~]", "🔮": "[?]",
    "🆕": "[NEW]", "📝": "[UPD]", "🕰️": "[OLD]",
    "⬆️": "[UP]", "⬇️": "[DN]", "🔄": ">>",
    "⚠": "[!]",
}

def _strip_emoji(text: str) -> str:
    for emoji, repl in EMOJI_MAP.items():
        text = text.replace(emoji, repl)
    # Remove any remaining non-latin1 characters safely
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _md_to_pdf_lines(md: str) -> list[tuple[str, str]]:
    """
    Convert markdown to a list of (tag, text) tuples.
    Tags: h1, h2, h3, body, bullet, table_header, table_row, hr, blank, badge
    """
    result = []
    for raw in md.splitlines():
        line = _strip_emoji(raw)
        if line.startswith("# "):
            result.append(("h1", line[2:]))
        elif line.startswith("## "):
            result.append(("h2", line[3:]))
        elif line.startswith("### "):
            result.append(("h3", line[4:]))
        elif line.startswith("---"):
            result.append(("hr", ""))
        elif re.match(r"^\|[-| ]+\|$", line):
            pass  # skip separator rows
        elif line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(c == c.upper() and len(c) < 30 for c in cells[:1]):
                result.append(("table_header", cells))
            else:
                result.append(("table_row", cells))
        elif re.match(r"^- \[.\]", line):
            result.append(("bullet", "□ " + line[6:]))
        elif line.startswith("- "):
            result.append(("bullet", line[2:]))
        elif line.strip() == "":
            result.append(("blank", ""))
        else:
            result.append(("body", line))
    return result


def _inline_strip(text: str) -> str:
    """Remove markdown inline formatting for plain PDF text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) → label
    text = re.sub(r"\[\[src\]\]\([^)]+\)", "[src]", text)
    text = re.sub(r"\[\[source\]\]\([^)]+\)", "[src]", text)
    return text.strip()


def build_pdf(card: Battlecard, md: str, out_path: Path) -> None:
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(*DARK_BG)
            self.rect(0, 0, 210, 14, "F")
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*PURPLE)
            self.set_xy(8, 4)
            self.cell(0, 6, f"COMPETITIVE BATTLECARD  //  {card.competitor.upper()}  vs  {card.your_company.upper()}", ln=0)
            self.set_text_color(*MUTED)
            self.set_font("Helvetica", "", 7)
            self.set_xy(0, 4)
            self.cell(200, 6, f"Generated {datetime.utcnow().strftime('%Y-%m-%d')}", align="R")

        def footer(self):
            self.set_y(-10)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*MUTED)
            self.cell(0, 6, f"Page {self.page_no()} — Archera Competitive Intel", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(14, 18, 14)
    pdf.add_page()
    pdf.set_fill_color(*WHITE)

    lines = _md_to_pdf_lines(md)
    i = 0
    table_cols: list[str] = []

    while i < len(lines):
        tag, content = lines[i]

        if tag == "blank":
            pdf.ln(2)

        elif tag == "hr":
            pdf.set_draw_color(*BORDER)
            pdf.set_line_width(0.3)
            pdf.line(14, pdf.get_y(), 196, pdf.get_y())
            pdf.ln(4)

        elif tag == "h1":
            pdf.ln(2)
            # Purple accent bar
            pdf.set_fill_color(*PURPLE)
            pdf.rect(14, pdf.get_y(), 4, 10, "F")
            pdf.set_x(20)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*DARK_BG)
            pdf.multi_cell(0, 10, _inline_strip(content), ln=1)
            pdf.ln(2)

        elif tag == "h2":
            pdf.ln(3)
            pdf.set_fill_color(*DARK_BG)
            pdf.rect(14, pdf.get_y(), 182, 8, "F")
            pdf.set_x(14)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*PURPLE)
            pdf.cell(0, 8, _inline_strip(content).upper(), ln=1)
            pdf.ln(1)

        elif tag == "h3":
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*DARK_BG)
            txt = _inline_strip(content)
            # Check for confidence badge at end
            for conf, color in CONF_COLORS.items():
                badge = {"confirmed": "[OK]", "reported": "[~]", "inferred": "[?]"}[conf]
                if txt.endswith(badge):
                    txt = txt[: -len(badge)].strip()
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 7, txt, ln=0)
                    pdf.set_font("Helvetica", "B", 7)
                    pdf.set_fill_color(*color)
                    pdf.set_text_color(*WHITE)
                    pdf.cell(10, 5, conf.upper(), fill=True, ln=1)
                    pdf.set_text_color(*DARK_BG)
                    break
            else:
                pdf.cell(0, 7, txt, ln=1)
            pdf.ln(0)

        elif tag == "bullet":
            txt = _inline_strip(content)
            # Detect confidence prefix
            conf_color = None
            for label, color in CONF_COLORS.items():
                badge = {"confirmed": "[OK]", "reported": "[~]", "inferred": "[?]"}[label]
                if txt.startswith(badge):
                    txt = txt[len(badge):].strip()
                    conf_color = color
                    break

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*DARK_BG)
            x0 = pdf.get_x()

            if conf_color:
                pdf.set_fill_color(*conf_color)
                pdf.set_text_color(*WHITE)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_x(14)
                pdf.cell(8, 5, CONF_LABELS[label], fill=True, align="C")
                pdf.set_text_color(*DARK_BG)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_x(24)
                pdf.multi_cell(168, 5, txt, ln=1)
            else:
                pdf.set_x(14)
                pdf.cell(4, 5, "-")
                pdf.set_x(19)
                pdf.multi_cell(173, 5, txt, ln=1)
            pdf.ln(0.5)

        elif tag == "table_header":
            table_cols = [_inline_strip(c) for c in content]
            pdf.ln(2)
            pdf.set_fill_color(*DARK_BG)
            col_w = 182 / max(len(table_cols), 1)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*PURPLE)
            pdf.set_x(14)
            for col in table_cols:
                pdf.cell(col_w, 6, col[:20], border=0, fill=True)
            pdf.ln(6)

        elif tag == "table_row":
            cells = [_inline_strip(c) for c in content]
            col_w = 182 / max(len(table_cols) or len(cells), 1)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*DARK_BG)
            pdf.set_x(14)
            # Light alternating row
            row_h = 6
            for j, cell in enumerate(cells):
                txt = cell[:40]
                # Colour confidence cells
                if txt in ("[OK]", "[~]", "[?]", "[src]"):
                    label = {"[OK]": "confirmed", "[~]": "reported", "[?]": "inferred"}.get(txt, "")
                    if label:
                        pdf.set_fill_color(*CONF_COLORS[label])
                        pdf.set_text_color(*WHITE)
                        pdf.set_font("Helvetica", "B", 7)
                        pdf.cell(col_w, row_h, CONF_LABELS.get(label, txt), border=0, fill=True)
                        pdf.set_text_color(*DARK_BG)
                        pdf.set_font("Helvetica", "", 8)
                    else:
                        pdf.cell(col_w, row_h, txt, border=0)
                else:
                    pdf.cell(col_w, row_h, txt, border=0)
            pdf.ln(row_h)
            pdf.set_draw_color(*BORDER)
            pdf.set_line_width(0.1)
            pdf.line(14, pdf.get_y(), 196, pdf.get_y())

        else:  # body / blockquote
            txt = _inline_strip(content)
            if not txt:
                pass
            elif txt.startswith(">"):
                txt = txt.lstrip("> ").strip()
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(*MUTED)
                pdf.set_x(18)
                pdf.multi_cell(174, 5, txt, ln=1)
                pdf.set_text_color(*DARK_BG)
            else:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*DARK_BG)
                pdf.multi_cell(0, 5, txt, ln=1)
            pdf.ln(0.5)

        i += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))


# ── CLI ──────────────────────────────────────────────────────────────────────

def _default_output(competitor: str) -> Path:
    slug = competitor.lower().replace(" ", "_")
    return ROOT / "reports" / slug


async def _run(args: argparse.Namespace) -> None:
    mode = "update" if args.update else "first run"
    print(f"🔍  Researching {args.competitor!r} for {args.your_company!r} ({mode})...", file=sys.stderr)
    print("     Running 3 research agents in parallel (G2 · website · news)...", file=sys.stderr)

    out_base = Path(args.output) if args.output else _default_output(args.competitor)
    json_path = out_base.with_suffix(".json")
    md_path   = out_base.with_suffix(".md")
    pdf_path  = out_base.with_suffix(".pdf")

    try:
        if args.update:
            card, saved_json = await update_battlecard_from_file(
                json_path=json_path,
                competitor=args.competitor,
                your_company=args.your_company,
                your_context=args.context or None,
            )
        else:
            card, saved_json = await build_battlecard(
                competitor=args.competitor,
                your_company=args.your_company,
                your_context=args.context or None,
            )
    except ValueError as exc:
        print(f"\n❌  Schema validation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = card.confidence_summary()
    print(f"\n✅  Research complete!", file=sys.stderr)
    print(f"     Sources     : {len(card.sources_consulted)}", file=sys.stderr)
    print(f"     Claims      : {summary['confirmed']} confirmed · {summary['reported']} reported · {summary['inferred']} inferred", file=sys.stderr)
    if card.intel_gaps:
        print(f"     ⚠️  Intel gaps : {len(card.intel_gaps)} need verification", file=sys.stderr)

    md = to_markdown(card)

    # Save JSON (source of truth for --update)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(saved_json, encoding="utf-8")
    print(f"\n💾  JSON     → {json_path}", file=sys.stderr)

    # Save Markdown
    md_path.write_text(md, encoding="utf-8")
    print(f"📄  Markdown → {md_path}", file=sys.stderr)

    # Save PDF
    print("🖨️   Building PDF...", file=sys.stderr)
    build_pdf(card, md, pdf_path)
    print(f"📑  PDF      → {pdf_path}", file=sys.stderr)

    print("\nDone.", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a competitive battlecard as Markdown + PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("competitor",   help="Competitor name  (e.g. 'ProsperOps')")
    parser.add_argument("your_company", help="Your company name (e.g. 'Archera')")
    parser.add_argument("--context", "-c", default="", help="Optional product/ICP context.")
    parser.add_argument(
        "--output", "-o",
        help="Base output path without extension (default: reports/<slug>). "
             "Generates <path>.md, <path>.pdf, and <path>.json.",
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Merge new research into an existing battlecard JSON (weekly update mode).",
    )
    args = parser.parse_args()
    anyio.run(_run, args)


if __name__ == "__main__":
    main()
