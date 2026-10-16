import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
for i in range(130, 155):
    p = doc.paragraphs[i]
    style_name = p.style.name if p.style else ""
    print(f"P{i:04d} [{style_name}]: '{p.text}'")
