import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()
p1 = doc.add_paragraph("Introductory text page 1")
p2 = doc.add_paragraph("Preliminary text page 2")

# Insert a next-page section break on p2
pPr = p2._p.get_or_add_pPr()
sectPr = parse_xml(f'<w:sectPr {nsdecls("w")}><w:type w:val="nextPage"/></w:sectPr>')
pPr.append(sectPr)

p3 = doc.add_paragraph("Body starts here page 3 (Section 2)")
print("Sections detected by python-docx:", len(doc.sections))
for i, s in enumerate(doc.sections):
    print(f"Section {i}: {s.start_type}")
