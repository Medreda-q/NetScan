import docx

doc_path = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI.docx"
doc = docx.Document(doc_path)

print("=== TABLE DES FIGURES ===")
for i in range(112, 126):
    t = doc.paragraphs[i].text.strip()
    if t:
        print(f"P{i}: {t}")

print("\n=== FIGURES IN BODY ===")
for i, p in enumerate(doc.paragraphs):
    if i < 150:
        continue
    t = p.text.strip()
    if t.startswith("Figure ") or "Figure " in t:
        has_img_before = 'graphicData' in doc.paragraphs[i-1]._element.xml if i > 0 else False
        has_img_after = 'graphicData' in doc.paragraphs[i+1]._element.xml if i+1 < len(doc.paragraphs) else False
        print(f"P{i}: '{t}' | Img before: {has_img_before} | Img after: {has_img_after}")

print("\n=== IMAGES IN BODY WITHOUT CAPTIONS ===")
for i, p in enumerate(doc.paragraphs):
    if i < 150:
        continue
    if 'graphicData' in p._element.xml:
        next_t = doc.paragraphs[i+1].text.strip() if i+1 < len(doc.paragraphs) else ""
        prev_t = doc.paragraphs[i-1].text.strip() if i-1 >= 0 else ""
        print(f"Image at P{i}: Prev='{prev_t[:50]}' | Next='{next_t[:60]}'")
