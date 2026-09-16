import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
import shutil, os

def fix_rapport(doc_path):
    doc = docx.Document(doc_path)

    # --------------------------------------------------------------------------
    # 1. SOMMAIRE : Supprimer l'entree orpheline 2.5
    # --------------------------------------------------------------------------
    for p in doc.paragraphs[:100]:
        if "2.5 - L'Architecture Dual-Layer" in p.text:
            p._element.getparent().remove(p._element)
            print("[OK 1] Entree orpheline 2.5 supprimee du Sommaire.")
            break

    # --------------------------------------------------------------------------
    # 2. FRONT MATTER : Reconstruction propre de Liste des Figures et Tableaux
    # --------------------------------------------------------------------------
    clean_figures = [
        "Figure 5.1 : Configuration reseau du Poste 1 d'Audit (Kali Linux).",
        "Figure 5.2 : Configuration reseau du Poste 2 de Supervision NetScan (Windows).",
        "Figure 5.3 : Demarrage de la sonde NetScan en ecoute passive directe.",
        "Figure 5.4 : Simulation du balayage de reconnaissance furtif (nmap -sS).",
        "Figure 5.5 : Detection en direct et qualification de l'alerte Port Scan par NetScan.",
        "Figure 5.6 : Simulation de l'attaque par deni de service volumetrique (hping3 SYN Flood).",
        "Figure 5.7 : Detection en temps reel et qualification de l'alerte Flood / DDoS par NetScan."
    ]

    clean_tableaux = [
        "\u2022  Tableau 1.1 : Matrice des specifications fonctionnelles et contraintes techniques de NetScan.",
        "\u2022  Tableau 1.2 : Matrice d'analyse, d'evaluation et de mitigation des risques du projet.",
        "\u2022  Tableau 2.1 : Comparatif synthetique : NIDS a base de signatures (Snort/Suricata) vs NIDS non supervise (NetScan).",
        "\u2022  Tableau 2.2 : Comparaison des algorithmes d'isolation (Isolation Forest, One-Class SVM et k-Means).",
        "\u2022  Tableau 3.1 : Vecteur des caracteristiques extraites au Niveau 1 (Analyse unitaire de paquet).",
        "\u2022  Tableau 3.2 : Vecteur des caracteristiques comportementales agregees au Niveau 2 (Fenetre de 5 secondes).",
        "\u2022  Tableau 3.3 : Synthese comparative des hyperparametres des deux couches d'Isolation Forest.",
        "\u2022  Tableau 4.1 : Stack technologique, langages et bibliotheques logicielles mobilisees.",
        "\u2022  Tableau 5.1 : Synthese comparative des resultats experimentaux de detection sur capture reelle.",
        "\u2022  Tableau 5.2 : Bilan comparatif des capacites de detection : Modele Baseline vs NetScan Dual-Layer."
    ]

    start_idx = None
    end_idx = None
    for i, p in enumerate(doc.paragraphs):
        if "Figure 5.1" in p.text and start_idx is None and i < 150:
            start_idx = i
        if "Liste des Abr" in p.text and i > 120:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        paras_to_remove = [doc.paragraphs[k] for k in range(start_idx, end_idx)]
        end_p = doc.paragraphs[end_idx]

        for p in paras_to_remove:
            p._element.getparent().remove(p._element)

        for fig in clean_figures:
            new_p = doc.add_paragraph(style='List Paragraph')
            new_p.text = fig
            end_p._element.addprevious(new_p._element)

        h_tab = doc.add_paragraph(style='Heading 1')
        h_tab.text = "Liste des Tableaux"
        end_p._element.addprevious(h_tab._element)

        for tab in clean_tableaux:
            new_p = doc.add_paragraph(style='List Paragraph')
            new_p.text = tab
            end_p._element.addprevious(new_p._element)

        spacer = doc.add_paragraph(style='Normal')
        spacer.text = ""
        end_p._element.addprevious(spacer._element)
        print("[OK 2] Liste des Figures (5.1 a 5.7) et Liste des Tableaux reconstruites proprement.")

    # --------------------------------------------------------------------------
    # 3. SECTION 2.4.2 : Parentheses manquantes dans la formule c(n)
    # --------------------------------------------------------------------------
    for p in doc.paragraphs:
        if "c(n) = 2 \\ln(n - 1) + 0.5772156649" in p.text:
            p.text = "c(n) = 2 \\left( \\ln(n - 1) + 0.5772156649 \\right) - \\frac{2(n - 1)}{n}"
            p.runs[0].font.name = "Cambria Math"
            p.runs[0].italic = True
            print("[OK 3] Formule mathematique c(n) corrigee avec parentheses.")
            break

    # --------------------------------------------------------------------------
    # 4. SECTION 3.4 : Insertion de la Regle 4 (Garde-fou deterministe)
    # --------------------------------------------------------------------------
    p_r3 = None
    p_tab33 = None
    for i, p in enumerate(doc.paragraphs):
        if "Comportement Normal (Volume Insuffisant)" in p.text:
            p_r3 = p
            for k in range(i+1, min(len(doc.paragraphs), i+10)):
                if "Tableau 3.3" in doc.paragraphs[k].text:
                    p_tab33 = doc.paragraphs[k]
                    break
            break

    if p_r3 and p_tab33:
        has_r4 = any("Garde-Fou" in doc.paragraphs[k].text for k in range(i+1, i+6))
        if not has_r4:
            r4 = doc.add_paragraph(style='List Paragraph')
            r4.paragraph_format.left_indent = p_r3.paragraph_format.left_indent
            r4.paragraph_format.space_before = p_r3.paragraph_format.space_before
            r4.paragraph_format.space_after = p_r3.paragraph_format.space_after
            r4.text = "\u2022  R\u00e8gle 4 \u2014 Garde-Fou D\u00e9terministe Anti-Scan Furtif : Ind\u00e9pendamment du mod\u00e8le ML, si une fen\u00eatre pr\u00e9sente une dispersion critique avec P_{unique} \\ge 10 ET que R = \\frac{P_{unique}}{N_{pkts}} \\ge 0.7, l'incident est automatiquement qualifi\u00e9 de `Port Scan` (Niveau de s\u00e9v\u00e9rit\u00e9 : CRITICAL). Cette r\u00e8gle de s\u00fbret\u00e9 \u00e9limine l'angle mort des scans lents (nmap -sS en cadence standard T3) masqu\u00e9s par le trafic de fond volumineux."
            p_tab33._element.addprevious(r4._element)
            print("[OK 4] Regle 4 inseree dans la section 3.4 au-dessus du Tableau 3.3.")

    # --------------------------------------------------------------------------
    # 5. SECTION 4.4 : Separation du Titre 4.4 et du paragraphe de corps
    # --------------------------------------------------------------------------
    for p in doc.paragraphs:
        if p.text.startswith("4.4 Moteur de Journalisation") and "\n" in p.text:
            parts = p.text.split("\n", 1)
            p.text = parts[0]
            new_p = doc.add_paragraph(style='Normal')
            new_p.text = parts[1]
            p._element.addnext(new_p._element)
            print("[OK 5] Titre 4.4 separe proprement du texte explicatif.")
            break

    # --------------------------------------------------------------------------
    # 6. CHAPITRE V : Separation des legendes fusionnees (Figures 5.5 et 5.7)
    # --------------------------------------------------------------------------
    for p in doc.paragraphs:
        if any('blip' in r._element.xml for r in p.runs):
            for r in p.runs:
                if "Figure 5.5" in r.text:
                    cap = r.text
                    r.text = ""
                    new_p = doc.add_paragraph(style='Normal')
                    new_p.text = cap
                    new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    new_p.runs[0].italic = True
                    new_p.paragraph_format.space_before = docx.shared.Pt(4)
                    new_p.paragraph_format.space_after = docx.shared.Pt(12)
                    p._element.addnext(new_p._element)
                    print("[OK 6a] Legende Figure 5.5 separee de l'image (centree, italique).")
                elif "Figure 5.7" in r.text:
                    cap = r.text
                    r.text = ""
                    new_p = doc.add_paragraph(style='Normal')
                    new_p.text = cap
                    new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    new_p.runs[0].italic = True
                    new_p.paragraph_format.space_before = docx.shared.Pt(4)
                    new_p.paragraph_format.space_after = docx.shared.Pt(12)
                    p._element.addnext(new_p._element)
                    print("[OK 6b] Legende Figure 5.7 separee de l'image (centree, italique).")

    # --------------------------------------------------------------------------
    # 7. CHAPITRE V : Coherence des renvois et termes
    # --------------------------------------------------------------------------
    for p in doc.paragraphs:
        if "ci-dessous :" in p.text and ("Figure 5.2" in p.text or "Figure 5.3" in p.text or "Figure 5.6" in p.text):
            p.text = p.text.replace("Figure 5.2", "Figure 5.7").replace("Figure 5.3", "Figure 5.7").replace("Figure 5.6", "Figure 5.7")
            print("[OK 7a] Reference du Scenario 2 mise a jour vers la Figure 5.7.")
        if "Figure 5.3 : Demarrage de la sonde NetScan en ecoute active directe." in p.text:
            p.text = p.text.replace("ecoute active directe", "ecoute passive directe")
            print("[OK 7b] Correction 'ecoute passive directe' pour la Figure 5.3.")

    doc.save(doc_path)
    print("\n>>> SUCCES TOTAL : Toutes les corrections appliquees avec succes a :", doc_path)

if __name__ == "__main__":
    target = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedRedaQIYAOUI_TEST.docx"
    fix_rapport(target)
