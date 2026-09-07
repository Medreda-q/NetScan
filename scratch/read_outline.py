import docx

doc = docx.Document(r"C:\Users\DevLab\Desktop\Rapport_Soutenance_QIYAOUI.docx")

print("=== OUTLINE OF Rapport_Soutenance_QIYAOUI.docx ===")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if p.style.name.startswith("Heading") or any(txt.startswith(x) for x in ["Chapitre", "Table", "Figure", "1.", "2.", "3.", "4.", "5.", "6.", "Conclusion", "Rsum", "Remerciement"]):
        print(f"P{i:03d} [{p.style.name}]: {txt[:90]}")
