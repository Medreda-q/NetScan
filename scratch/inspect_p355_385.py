import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
for idx in range(355, 385):
    p = doc.paragraphs[idx]
    has_img = "w:drawing" in p._element.xml
    print(f"P{idx:04d} [IMG={has_img}] (style={p.style.name if p.style else ''}): '{p.text}'")
