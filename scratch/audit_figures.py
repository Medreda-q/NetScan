import docx
import os

doc_path = r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx"
doc = docx.Document(doc_path)

print(f"Total paragraphs: {len(doc.paragraphs)}")

# Find all images and their nearest caption
findings = []
for i, p in enumerate(doc.paragraphs):
    xml = p._element.xml
    has_img = "w:drawing" in xml
    text = p.text.strip()
    
    # check if this or next/prev paragraph is a Figure caption
    if has_img:
        # look around
        prev_text = doc.paragraphs[i-1].text.strip() if i > 0 else ""
        next_text = doc.paragraphs[i+1].text.strip() if i+1 < len(doc.paragraphs) else ""
        findings.append({
            "idx": i,
            "type": "IMAGE",
            "text": text,
            "prev": prev_text[:100],
            "next": next_text[:100]
        })
    elif text.startswith("Figure ") or text.startswith("Fig. "):
        findings.append({
            "idx": i,
            "type": "CAPTION",
            "text": text
        })

with open("scratch/figures_audit.txt", "w", encoding="utf-8") as f:
    for item in findings:
        f.write(f"P{item['idx']:04d} [{item['type']}]: text='{item.get('text', '')}'\n")
        if "prev" in item:
            f.write(f"   PREV: {item['prev']}\n")
        if "next" in item:
            f.write(f"   NEXT: {item['next']}\n")

print(f"Logged {len(findings)} image/caption items to scratch/figures_audit.txt")
