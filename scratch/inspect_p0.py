import docx

doc = docx.Document(r"C:\Users\DevLab\Desktop\Rapport_Soutenance_QIYAOUI.docx")

p0 = doc.paragraphs[0]
print("P0 text:", p0.text)
print("P0 xml:\n", p0._p.xml[:800])
