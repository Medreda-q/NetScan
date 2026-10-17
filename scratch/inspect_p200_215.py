import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
for idx in range(200, 215):
    p = doc.paragraphs[idx]
    print(f"P{idx:04d} [{p.style.name if p.style else ''}]: '{p.text[:90]}'")
