import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")

with open("scratch/chap4_5_text.txt", "w", encoding="utf-8") as out:
    for i in range(315, 461):
        p = doc.paragraphs[i]
        style = p.style.name if p.style else ""
        txt = p.text.strip()
        if txt:
            out.write(f"P{i:04d} [{style}]: {txt}\n")

print("Dumped Chapter 4 & 5 text to scratch/chap4_5_text.txt")
