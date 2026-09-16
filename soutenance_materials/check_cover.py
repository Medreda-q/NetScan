import sys
import docx

sys.stdout.reconfigure(encoding='utf-8')
doc_path = r"C:\Users\DevLab\Desktop\Soutenance\Avec Commune\Rapport_MohamedRedaQIYAOUI.docx"
doc = docx.Document(doc_path)

print("=== COVER PAGE (P00 to P23) ===")
for i in range(24):
    p = doc.paragraphs[i]
    runs_info = [(r.text.strip(), r.font.name, r.font.size.pt if r.font.size else None, r.bold) for r in p.runs if r.text.strip()]
    print(f"P{i:02d} [{p.style.name}] (align={p.alignment}): '{p.text}'")
    if runs_info:
        print(f"     runs: {runs_info}")
