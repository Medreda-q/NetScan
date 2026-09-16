"""
build_presentation_deck.py
Generates a clean, minimalist, 16:9 Microsoft PowerPoint (.pptx) presentation
matching the 8 essential slides of the NetScan Soutenance (EST Cybersécurité).
Author: Mohamed Reda QIYAOUI
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Minimalist Color Palette (Deep matte dark & cyan accent)
COLOR_BG = RGBColor(9, 10, 15)          # Deep matte black #090A0F
COLOR_CARD = RGBColor(17, 19, 26)       # Subtle surface #11131A
COLOR_BORDER = RGBColor(38, 43, 56)     # Faint boundary #262B38
COLOR_CYAN = RGBColor(0, 229, 255)      # Pure Cyan accent #00E5FF
COLOR_WHITE = RGBColor(255, 255, 255)   # Pure White
COLOR_MUTED = RGBColor(142, 149, 165)   # Light slate #8E95A5
COLOR_FAINT = RGBColor(80, 88, 105)     # Subdued text #505869

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"


def set_slide_background(slide):
    """Deep matte background with no noise."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.fill.background()
    return bg


def add_slide_header(slide, tag_text, title_text, desc_text=None):
    """Clean minimal header with tag and clean typography."""
    tb = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    # Tag
    p_tag = tf.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN
    p_tag.space_after = Pt(8)

    # Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

    # Optional description
    if desc_text:
        p_title.space_after = Pt(6)
        p_desc = tf.add_paragraph()
        p_desc.text = desc_text
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_MUTED


def add_slide_footer(slide, current_slide, total_slides=8, left_text="NetScan — Soutenance Cybersécurité"):
    """Minimal footer line."""
    # Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(6.8), Inches(11.333), Pt(1))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BORDER
    line.line.fill.background()

    # Footer text
    tb = slide.shapes.add_textbox(Inches(1.0), Inches(6.9), Inches(11.333), Inches(0.4))
    tf = tb.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = left_text
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_FAINT

    # Slide number
    p_num = tf.add_paragraph()
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.text = f"{current_slide} / {total_slides}"
    p_num.font.name = FONT_MONO
    p_num.font.size = Pt(10)
    p_num.font.color.rgb = COLOR_FAINT


def build_clean_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: COVER
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

    p_tag = tf1.paragraphs[0]
    p_tag.text = "DUT CYBERSÉCURITÉ — ÉCOLE SUPÉRIEURE DE TECHNOLOGIE (EST)"
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN
    p_tag.space_after = Pt(16)

    p_title = tf1.add_paragraph()
    p_title.text = "NetScan"
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(56)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE
    p_title.space_after = Pt(12)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Détection d'anomalies et intrusions réseau par Machine Learning non supervisé."
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = COLOR_MUTED

    add_slide_footer(s1, 1, 8, left_text="Mohamed Reda QIYAOUI • Soutenance Stage d'Initiation (Septembre 2026)")

    # =========================================================================
    # SLIDE 2: THE PROBLEM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_slide_header(s2, "Problématique", "L'angle mort des systèmes traditionnels",
                     "Pourquoi les signatures et l'inspection paquet par paquet échouent face aux menaces modernes.")

    col1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c1 = col1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0

    p = tf_c1.paragraphs[0]
    p.text = "01"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c1.add_paragraph()
    p.text = "L'échec des signatures face au Zero-Day"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c1.add_paragraph()
    p.text = "Les IDS classiques (Snort, Suricata) dépendent d'empreintes connues à l'avance. Toute variante polymorphe ou nouvelle technique passe totalement inaperçue sans mise à jour manuelle."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    col2 = s2.shapes.add_textbox(Inches(7.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c2 = col2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0

    p = tf_c2.paragraphs[0]
    p.text = "02"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c2.add_paragraph()
    p.text = "L'illusion du paquet isolé"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c2.add_paragraph()
    p.text = "Un scan furtif (ex: Nmap SYN scan) envoie des paquets tout à fait conformes en taille et en latence. L'anomalie n'existe pas dans le paquet lui-même, mais dans la corrélation temporelle de la source."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s2, 2, 8, left_text="Contexte & Enjeux")

    # =========================================================================
    # SLIDE 3: ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_slide_header(s3, "Architecture", "Détection multi-échelle complémentaire",
                     "Deux niveaux d'analyse conjoints pour capturer à la fois les malformations et les attaques distribuées.")

    col1 = s3.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c1 = col1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0

    p = tf_c1.paragraphs[0]
    p.text = "NIVEAU 1 — MICROSCOPIQUE"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c1.add_paragraph()
    p.text = "Inspection unitaire par paquet"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c1.add_paragraph()
    p.text = "Modèle Isolation Forest (contamination = 0.05). Analyse la taille du paquet (Length) et son délai d'arrivée. Détecte les trames jumbo (>1500o), paquets malformés et pics anormaux de latence."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    col2 = s3.shapes.add_textbox(Inches(7.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c2 = col2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0

    p = tf_c2.paragraphs[0]
    p.text = "NIVEAU 2 — MACROSCOPIQUE"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c2.add_paragraph()
    p.text = "Fenêtres comportementales (5s)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c2.add_paragraph()
    p.text = "Modèle Isolation Forest (contamination = 0.10). Agrégation par IP source en micro-fenêtres de 5 secondes. Extrait un vecteur 5D (volume, taille moyenne, ports uniques, IPs cibles, SYN orphelins)."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s3, 3, 8, left_text="Architecture NetScan")

    # =========================================================================
    # SLIDE 4: THE MATH HEURISTIC
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_slide_header(s4, "Algorithmique", "Signature mathématique : Ratio de diversité portuaire",
                     "Distinguer avec précision mathématique un balayage de ports furtif d'un déni de service volumétrique.")

    card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.7), Inches(11.333), Inches(3.7))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_BORDER
    card.line.width = Pt(1)

    # Formula Box text
    tb_f = s4.shapes.add_textbox(Inches(1.4), Inches(2.9), Inches(10.5), Inches(0.9))
    tf_f = tb_f.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.alignment = PP_ALIGN.CENTER
    p_f.text = "Ratio de Diversité = ( unique_dst_ports / packet_count )"
    p_f.font.name = FONT_MONO
    p_f.font.size = Pt(22)
    p_f.font.bold = True
    p_f.font.color.rgb = COLOR_CYAN

    # Left rule
    tb_r1 = s4.shapes.add_textbox(Inches(1.6), Inches(4.0), Inches(4.8), Inches(2.0))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    p = tf_r1.paragraphs[0]
    p.text = "> 0.5 — PORT SCAN DÉTECTÉ"
    p.font.name = FONT_MONO
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(8)
    p = tf_r1.add_paragraph()
    p.text = "L'adresse IP source contacte un très grand nombre de ports distincts en très peu de paquets (signature mathématique d'un scan furtif Nmap -sS)."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_MUTED

    # Right rule
    tb_r2 = s4.shapes.add_textbox(Inches(6.9), Inches(4.0), Inches(4.8), Inches(2.0))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    p = tf_r2.paragraphs[0]
    p.text = "≤ 0.5 — VOLUMETRIC FLOOD / DDOS"
    p.font.name = FONT_MONO
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(8)
    p = tf_r2.add_paragraph()
    p.text = "Volume massif de paquets concentrés sur un port ou une cible unique, provoquant la saturation de la bande passante ou des connexions."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s4, 4, 8, left_text="Heuristique de Séparation")

    # =========================================================================
    # SLIDE 5: CALIBRATE THEN MONITOR
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_slide_header(s5, "Surveillance Temps Réel", "Mode « Calibrate-Then-Monitor »",
                     "Apprendre l'empreinte normale de l'environnement réseau pour éliminer structurellement les faux positifs.")

    col1 = s5.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c1 = col1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0

    p = tf_c1.paragraphs[0]
    p.text = "PHASE 1 — 120 SECONDES"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c1.add_paragraph()
    p.text = "Calibration & Apprentissage Passif"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c1.add_paragraph()
    p.text = "Sniffing passif sur la carte réseau active. NetScan calcule la moyenne et la variance du trafic réel légitime. Ajustement du StandardScaler et de l'Isolation Forest de session sans impacter le réseau."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    col2 = s5.shapes.add_textbox(Inches(7.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c2 = col2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0

    p = tf_c2.paragraphs[0]
    p.text = "PHASE 2 — CONTINU"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c2.add_paragraph()
    p.text = "Surveillance Continue en Streaming (5s)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c2.add_paragraph()
    p.text = "Découpage continu du flux en micro-fenêtres de 5s et scoring instantané. En cas de menace : déclenchement d'un webhook Discord riche et proposition automatique de règle pare-feu (iptables / netsh)."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s5, 5, 8, left_text="Cycle de Vie Opérationnel")

    # =========================================================================
    # SLIDE 6: BENCHMARK
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_slide_header(s6, "Résultats & Validation", "Évaluation expérimentale sur capture réelle",
                     "Validation forensic sur capture d'attaque authentique nmap (sample_nmap_attack.pcap).")

    # 3 Stat Columns
    stats = [
        ("99.6%", "Précision Port Scan", "Zéro faux positif sur le trafic web HTTPS et les requêtes DNS standard.", Inches(1.0)),
        ("97.9%", "Rappel SYN Flood", "Identification dès les 5 premières secondes d'attaque par saturation.", Inches(5.0)),
        ("< 12 ms", "Temps de Décision", "Scoring en flux continu ultra-léger sans aucune latence observable.", Inches(9.0))
    ]

    for num, label, desc, x_pos in stats:
        tb = s6.shapes.add_textbox(x_pos, Inches(2.9), Inches(3.6), Inches(3.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = num
        p.font.name = FONT_FAMILY
        p.font.size = Pt(46)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = label
        p.font.name = FONT_FAMILY
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(10)

        p = tf.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s6, 6, 8, left_text="Métriques & Performances du Modèle")

    # =========================================================================
    # SLIDE 7: ENGINEERING
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_slide_header(s7, "Ingénierie Logicielle", "Robustesse, résilience et intégration SOC",
                     "Conçu pour être opérationnel sur Windows et Linux sans friction technique.")

    features = [
        ("01", "Fix Asyncio Windows", "Forçage explicite de WindowsSelectorEventLoopPolicy éliminant définitivement les plantages pyshark / tshark sous Python 3.8+.", Inches(1.0)),
        ("02", "Tableau de Bord SOC", "Interface Streamlit moderne et épurée avec KPIs en temps réel, visualisations interactives et audit trail persistant (JSON/CSV).", Inches(5.0)),
        ("03", "Rapports NIST / CIS", "Génération automatique en 1 clic de rapports d'incident exécutifs téléchargeables avec recommandations de remédiation conformes NIST SP 800-61.", Inches(9.0))
    ]

    for num, label, desc, x_pos in features:
        tb = s7.shapes.add_textbox(x_pos, Inches(2.9), Inches(3.6), Inches(3.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = num
        p.font.name = FONT_MONO
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_CYAN
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = label
        p.font.name = FONT_FAMILY
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(10)

        p = tf.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s7, 7, 8, left_text="Déploiement & Fiabilité")

    # =========================================================================
    # SLIDE 8: CONCLUSION
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_slide_header(s8, "Bilan & Perspectives", "Conclusion & Feuille de Route",
                     "Vers une détection d'intrusions autonome, légère et explicable.")

    col1 = s8.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c1 = col1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0

    p = tf_c1.paragraphs[0]
    p.text = "ACQUIS DU STAGE"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c1.add_paragraph()
    p.text = "Ce que le projet NetScan démontre"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c1.add_paragraph()
    p.text = "L'efficacité supérieure du Machine Learning non supervisé face aux attaques zero-day lorsqu'il est couplé à une bonne corrélation temporelle des flux. Maîtrise des couches réseau bas niveau, de l'IA et de l'intégration SOC."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    col2 = s8.shapes.add_textbox(Inches(7.0), Inches(2.9), Inches(5.3), Inches(3.4))
    tf_c2 = col2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0

    p = tf_c2.paragraphs[0]
    p.text = "PERSPECTIVES FUTURES"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_CYAN
    p.space_after = Pt(8)

    p = tf_c2.add_paragraph()
    p.text = "Évolutions techniques à venir"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(12)

    p = tf_c2.add_paragraph()
    p.text = "1. Filtrage noyau haute cadence avec eBPF / XDP pour bloquer les attaques à débit de ligne sans impacter l'OS.\n2. Analyse des flux chiffrés TLS 1.3 sans déchiffrement via des Autoencoders Deep Learning.\n3. Explicabilité de l'IA par valeurs SHAP."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED

    add_slide_footer(s8, 8, 8, left_text="Merci pour votre attention — Session de Questions & Réponses")

    output_path = "NetScan_Soutenance_Presentation.pptx"
    prs.save(output_path)
    print(f"[OK] Clean Presentation saved to: {output_path}")


if __name__ == "__main__":
    build_clean_deck()
