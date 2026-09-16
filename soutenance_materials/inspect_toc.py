import docx

doc = docx.Document(r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_FIXED.docx")
for i in range(58, 107):
    p = doc.paragraphs[i]
    print(f"P[{i}] [Style: {p.style.name}] (runs: {len(p.runs)}): {repr(p.text)}")
