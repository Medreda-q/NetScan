import docx
import os

doc = docx.Document(r"C:\Users\DevLab\Documents\Rapport_NetScan_corrige (1).docx")
out_dir = r"scratch/extracted_images"
os.makedirs(out_dir, exist_ok=True)

# Map rId to target part
rel_map = {}
for rId, rel in doc.part.rels.items():
    if "image" in rel.target_ref:
        rel_map[rId] = rel.target_part

print(f"Total image rels: {len(rel_map)}")

# Extract images per paragraph
img_idx = 0
for p_idx, p in enumerate(doc.paragraphs):
    xml = p._element.xml
    if "w:drawing" in xml:
        # find blip r:embed
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        for elem in root.iter():
            if elem.tag.endswith("blip"):
                embed_id = elem.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                if embed_id and embed_id in rel_map:
                    part = rel_map[embed_id]
                    ext = part.content_type.split("/")[-1]
                    if ext == "jpeg": ext = "jpg"
                    fname = f"p{p_idx:04d}_img{img_idx:02d}_{embed_id}.{ext}"
                    fpath = os.path.join(out_dir, fname)
                    with open(fpath, "wb") as f_out:
                        f_out.write(part.blob)
                    print(f"Saved P{p_idx:04d} -> {fname} ({len(part.blob)} bytes)")
                    img_idx += 1
