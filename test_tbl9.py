import docx
from docx.oxml import parse_xml

doc = docx.Document(r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_FIXED.docx")
tbl = doc.tables[9]
print("Initial rows:", len(tbl.rows), "Initial cols:", len(tbl.columns))

# Remove last 2 cells from each row
for row in tbl.rows:
    tcs = row._tr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')
    if len(tcs) > 3:
        for tc in tcs[3:]:
            row._tr.remove(tc)

# Fix gridCol
tblGrid = tbl._tbl.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblGrid')
if tblGrid is not None:
    gridCols = tblGrid.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}gridCol')
    for gc in gridCols[3:]:
        tblGrid.remove(gc)
    gridCols[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w', '2500')
    gridCols[1].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w', '2800')
    gridCols[2].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w', '4400')

print("After fix, rows:", len(tbl.rows), "cols:", len(tbl.columns))
for r_idx, row in enumerate(tbl.rows):
    print(f"Row {r_idx}: len={len(row.cells)}")

doc.save("test_tbl9_fix.docx")
print("Saved test_tbl9_fix.docx successfully!")
