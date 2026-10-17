import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
for i in range(8, 22):
    p = doc.paragraphs[i]
    style = p.style.name if p.style else "NoStyle"
    xml = p._element.xml
    has_page_break = "w:br" in xml and 'type="page"' in xml
    has_sect_break = "w:sectPr" in xml
    print(f"P{i:04d} [{style}]: text='{p.text}' | pageBreak={has_page_break} | sectBreak={has_sect_break}")
