import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc_path = r"C:\Users\DevLab\Desktop\Soutenance\Avec Commune\Rapport_MohamedRedaQIYAOUI.docx"
doc = docx.Document(doc_path)

# Let's inspect P20 to P26
for i in range(20, 27):
    print(f"P{i}: {doc.paragraphs[i].text}")

# Re-order cleanly:
# P21: Réalisé par : Mohamed Reda QIYAOUI
# P22: Organisme d'accueil : Commune de Tétouan (Service du SIG, des Systèmes Informatiques et de la Numérisation)
# P23: Encadrants
# P24: Année Universitaire : 2025/2026
doc.paragraphs[21].text = "Réalisé par :"
doc.paragraphs[21].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[21].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True

doc.paragraphs[22].text = "Mohamed Reda QIYAOUI\nÉtudiant en DUT Cybersécurité (EST Tétouan)"
doc.paragraphs[22].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[22].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = RGBColor(10, 37, 64)

doc.paragraphs[23].text = "Organisme d'accueil : Commune de Tétouan\nService du SIG, des Systèmes Informatiques et de la Numérisation"
doc.paragraphs[23].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[23].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(24, 76, 120)

doc.paragraphs[24].text = "Encadrant Pédagogique : Corps Enseignant — EST Tétouan\nEncadrant Professionnel : Responsable Informatique & SIG — Commune de Tétouan"
doc.paragraphs[24].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[24].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)

doc.paragraphs[25].text = "Année Universitaire : 2025/2026"
doc.paragraphs[25].alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in doc.paragraphs[25].runs:
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True

doc.save(doc_path)
print("Cover page paragraphs cleanly ordered!")
