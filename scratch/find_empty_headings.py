import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
empty_headings = []
for i, p in enumerate(doc.paragraphs):
    style = p.style.name if p.style else ""
    if ("Heading" in style or "Titre" in style) and not p.text.strip():
        empty_headings.append((i, style))

print("All empty Heading/Titre paragraphs in docx:")
for idx, st in empty_headings:
    print(f"P{idx:04d} [{st}]")
