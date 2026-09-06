"""
generate_final_docx.py — Populates the target PDFgear docx with Mohamed Reda QIYAOUI's complete academic report.
"""

import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="B0C4DE", sz="6", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def create_report_docx(md_path, target_docx_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    doc = Document()

    # Standard A4 Page Setup
    for section in doc.sections:
        section.top_margin = Inches(0.98)
        section.bottom_margin = Inches(0.98)
        section.left_margin = Inches(0.98)
        section.right_margin = Inches(0.98)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(4)

    NAVY = RGBColor(0x1B, 0x36, 0x5D)
    SLATE = RGBColor(0x2E, 0x5B, 0x88)
    DARK_GRAY = RGBColor(0x33, 0x33, 0x33)

    lines = md_content.split("\n")
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        rows_data = []
        for l in tbl_lines:
            if re.match(r'^\s*\|?\s*[-:]+[-| :]*\|?\s*$', l):
                continue
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if cells and any(cells):
                rows_data.append(cells)
        if not rows_data:
            return

        num_cols = max(len(r) for r in rows_data)
        for r in rows_data:
            while len(r) < num_cols:
                r.append("")

        table = doc.add_table(rows=len(rows_data), cols=num_cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(table, color="B0C4DE", sz="6")

        for row_idx, row_data in enumerate(rows_data):
            row = table.rows[row_idx]
            is_header = (row_idx == 0)
            for col_idx, cell_text in enumerate(row_data):
                cell = row.cells[col_idx]
                cell.text = cell_text
                set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05

                if is_header:
                    set_cell_background(cell, "1B365D")
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        run.font.size = Pt(10)
                else:
                    bg = "F4F7FA" if row_idx % 2 == 1 else "FFFFFF"
                    set_cell_background(cell, bg)
                    for run in p.runs:
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = DARK_GRAY

        doc.add_paragraph()

    def flush_code(c_lines):
        if not c_lines:
            return
        code_text = "\n".join(c_lines)
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F3F4F6")
        set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
        set_table_borders(tbl, color="D1D5DB", sz="8")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(code_text)
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
        doc.add_paragraph()

    i = 0
    while i < len(lines):
        line = lines[i]

        # Page Breaks
        if "\\newpage" in line or line.strip() == "---":
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False
            if len(doc.paragraphs) > 1 and "\\newpage" in line:
                doc.add_page_break()
            i += 1
            continue

        # Code Blocks
        if line.strip().startswith("```"):
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False

            if in_code_block:
                flush_code(code_lines)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Tables
        if "|" in line and (line.strip().startswith("|") or line.strip().endswith("|")):
            in_table = True
            table_lines.append(line)
            i += 1
            continue
        else:
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False

        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        # Blockquotes / Dédicace
        if stripped.startswith(">"):
            quote_text = re.sub(r"^>\s*", "", stripped).replace("*", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(f"« {quote_text} »" if not quote_text.startswith("«") else quote_text)
            run.font.italic = True
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            h_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(20)
            run.font.color.rgb = NAVY
            i += 1
            continue

        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(15)
            run.font.color.rgb = SLATE
            i += 1
            continue

        if stripped.startswith("### "):
            h_text = stripped[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(12.5)
            run.font.color.rgb = DARK_GRAY
            i += 1
            continue

        if stripped.startswith("#### "):
            h_text = stripped[5:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(11.5)
            run.font.color.rgb = DARK_GRAY
            i += 1
            continue

        # Bullet Lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = stripped[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*.*?\*\*)', item_text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    run.font.bold = True
                else:
                    p.add_run(part)
            i += 1
            continue

        # Numbered Lists
        if re.match(r'^\d+\.\s', stripped):
            item_text = re.sub(r'^\d+\.\s*', '', stripped)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*.*?\*\*)', item_text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    run.font.bold = True
                else:
                    p.add_run(part)
            i += 1
            continue

        # Standard Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.2

        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped[1:-1])
            run.font.italic = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
            i += 1
            continue

        parts = re.split(r'(\*\*.*?\*\*|`.*?`|\$.*?\$)', stripped)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run(part[2:-2])
                run.font.bold = True
            elif part.startswith("`") and part.endswith("`"):
                run = p.add_run(part[1:-1])
                run.font.name = "Consolas"
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)
            elif part.startswith("$") and part.endswith("$"):
                run = p.add_run(part[1:-1])
                run.font.italic = True
            else:
                p.add_run(part)

        i += 1

    if in_table:
        flush_table(table_lines)
    if in_code_block:
        flush_code(code_lines)

    # Save directly to destination
    doc.save(target_docx_path)
    print(f"SUCCESS: Report saved to {target_docx_path}")

if __name__ == "__main__":
    src_md = r"c:\Users\DevLab\Documents\ProjectSoutenance\Wireshark-Capture-Anomaly-Detection-main\RAPPORT_SOUTENANCE_CYBERSECURITE.md"
    dst_docx = r"C:\Users\DevLab\Documents\PDFgear\1782378057669 conv.docx"
    create_report_docx(src_md, dst_docx)
