"""Build paper_draft.docx (and, via LibreOffice, paper_draft.pdf) from
paper_draft.md. Light Markdown handling: headings, **bold**, *italic*,
images, bullet lists and the results table.
Run from the project root:  python paper/build_docx.py
"""
import re
import subprocess
import sys
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC = "paper/paper_draft.md"
OUT = "paper/paper_draft.docx"


def add_rich(par, text):
    """Add runs with **bold** and *italic* spans to a paragraph."""
    tokens = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text)
    for tok in tokens:
        if tok.startswith("**") and tok.endswith("**"):
            run = par.add_run(tok[2:-2]); run.bold = True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            run = par.add_run(tok[1:-1]); run.italic = True
        else:
            par.add_run(tok)


def main():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line.strip() or line.strip() == "---":
            continue
        if line.startswith("# "):
            h = doc.add_heading(line[2:], level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=1)
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:], level=2)
            continue
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if m:  # image (path is relative to paper/)
            path = m.group(2).replace("../", "", 1)
            doc.add_picture(path, width=Inches(5.6))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        if line.startswith("|"):  # markdown table
            rows = []
            while i - 1 < len(lines) and lines[i - 1].startswith("|"):
                rows.append([c.strip() for c in lines[i - 1].strip().strip("|").split("|")])
                i += 1
                if i - 1 >= len(lines):
                    break
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            table = doc.add_table(rows=len(rows), cols=len(rows[0]))
            table.style = "Light Grid Accent 1"
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    cell = table.cell(r, c)
                    cell.text = ""
                    add_rich(cell.paragraphs[0], val)
                    if r == 0:
                        for run in cell.paragraphs[0].runs:
                            run.bold = True
            continue
        if line.startswith("- "):
            par = doc.add_paragraph(style="List Bullet")
            add_rich(par, line[2:])
            continue
        par = doc.add_paragraph()
        add_rich(par, line)

    doc.save(OUT)
    print("wrote", OUT)
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                        OUT, "--outdir", "paper"], check=True,
                       capture_output=True, timeout=180)
        print("wrote paper/paper_draft.pdf")
    except Exception as e:  # PDF is a bonus; DOCX is the deliverable
        print("PDF conversion skipped:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
