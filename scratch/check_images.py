import docx

doc = docx.Document(r"C:\Users\DevLab\Desktop\Rapport_Soutenance_QIYAOUI.docx")

print("Checking images/drawings in doc:")
for i, p in enumerate(doc.paragraphs[:20]):
    xml = p._p.xml
    if "drawing" in xml or "blip" in xml or "shape" in xml:
        print(f"P{i:02d} has drawing/image! XML: {xml[:300]}")
    elif p.text.strip():
        print(f"P{i:02d}: text='{p.text}'")
    else:
        # Check empty spacing paragraphs
        print(f"P{i:02d}: [empty paragraph]")
