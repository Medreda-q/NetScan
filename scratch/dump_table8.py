import docx

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
table = doc.tables[8]

with open("scratch/table8_dump.txt", "w", encoding="utf-8") as f:
    f.write(f"Table 8 (Tableau 4.1): {len(table.rows)} rows x {len(table.columns)} cols\n")
    for r_idx, row in enumerate(table.rows):
        cells = [c.text.strip().replace("\n", " ") for c in row.cells]
        f.write(f"R{r_idx:02d}: {' | '.join(cells)}\n")

print("Dumped table 8 to scratch/table8_dump.txt")
