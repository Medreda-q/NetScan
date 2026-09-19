with open(r"C:\Users\DevLab\Desktop\Soutenance\Mettre_A_Jour_Rapport.bas", "r", encoding="latin1") as f:
    text = f.read()
import re
calls = re.findall(r'RemplacerParagrapheComplet\(\s*_\s*\n\s*"([^"]+)"', text)
for c in calls:
    print(f"Anchor: [{c}] -> Length: {len(c)}")
