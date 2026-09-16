# -*- coding: utf-8 -*-
"""
Générateur de la soutenance NetScan :
1. Fichier VBA (.bas) pour import direct dans PowerPoint
2. Fichier PowerPoint (.pptx) complet avec 23 diapositives professionnelles
"""

import sys, os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

PPTX_OUT = r"C:\Users\DevLab\Desktop\Soutenance\Soutenance_NetScan_Complete.pptx"
BAS_OUT  = r"C:\Users\DevLab\Desktop\Soutenance\Generer_Soutenance_NetScan.bas"

# Palette Graphique Professionnelle Cybersécurité
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A Bleu Nuit Fond Titre / En-tête
C_TEAL      = RGBColor(14, 116, 144)    # #0E7490 Cyan / Sarcelle
C_BLUE_CYBER= RGBColor(2, 132, 199)     # #0284C7 Bleu Cyber
C_BG_PAGE   = RGBColor(248, 250, 252)   # #F8FAFC Fond Épuré
C_CARD_BG   = RGBColor(255, 255, 255)   # Blanc Carte
C_BORDER    = RGBColor(203, 213, 225)   # Bordure Grise Discrète
C_TEXT_DARK = RGBColor(15, 23, 42)      # Texte Sombre
C_TEXT_MUTED= RGBColor(100, 116, 139)   # Texte Gris
C_SUCCESS   = RGBColor(16, 185, 129)    # Vert Validation
C_DANGER    = RGBColor(220, 38, 38)     # Rouge Alerte
C_WHITE     = RGBColor(255, 255, 255)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.color.rgb = color
    return bg

def add_header(slide, title_text, category_text):
    # Bandeau supérieur
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.15))
    header.fill.solid()
    header.fill.fore_color.rgb = C_NAVY_DARK
    header.line.fill.background()

    # Ligne d'accentuation cyan
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), Inches(13.333), Inches(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BLUE_CYBER
    line.line.fill.background()

    # Badge Catégorie
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
    tf_cat = tb_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_BLUE_CYBER
    p_cat.font.name = "Segoe UI"

    # Titre de la diapositive
    tb_tit = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.5), Inches(0.65))
    tf_tit = tb_tit.text_frame
    tf_tit.word_wrap = True
    p_tit = tf_tit.paragraphs[0]
    p_tit.text = title_text
    p_tit.font.size = Pt(21)
    p_tit.font.bold = True
    p_tit.font.color.rgb = C_WHITE
    p_tit.font.name = "Segoe UI"

def add_card(slide, left, top, width, height, title=None, border_color=C_BORDER, fill_color=C_CARD_BG):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    
    if title:
        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(0.45))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
        p.font.name = "Segoe UI"
    return card

def add_card_text(slide, left, top, width, height, lines, start_y_offset=0.6):
    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + start_y_offset), Inches(width - 0.5), Inches(height - start_y_offset - 0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line_info in enumerate(lines):
        txt, bold, size, color, bullet = line_info
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.text = (u"  - " if bullet else "") + txt
        p.font.bold = bold
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = "Segoe UI"
        p.space_after = Pt(6)

print("Création des 23 diapositives professionnelles...")

# ==========================================
# SLIDE 1 : TITRE & ACCUEIL
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, C_NAVY_DARK)

# Barre latérale cyan
bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.12), Inches(4.5))
bar.fill.solid()
bar.fill.fore_color.rgb = C_BLUE_CYBER
bar.line.fill.background()

tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(11.0), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "SOUTENANCE DE PROJET DE FIN D'ÉTUDES"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_BLUE_CYBER

p2 = tf.add_paragraph()
p2.text = "Conception et Développement d'un Système Intelligent de Détection d'Anomalies Réseau"
p2.font.size = Pt(25)
p2.font.bold = True
p2.font.color.rgb = C_WHITE
p2.space_before = Pt(8)

p3 = tf.add_paragraph()
p3.text = "NetScan : Détection Précoce d'Intrusions par Machine Learning Non Supervisé (Isolation Forest)"
p3.font.size = Pt(16)
p3.font.color.rgb = RGBColor(148, 163, 184)
p3.space_before = Pt(6)

# Carte Candidat & Encadrement
card_info = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.2), Inches(10.8), Inches(2.2))
card_info.fill.solid()
card_info.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_info.line.color.rgb = C_BLUE_CYBER

tb_cand = s1.shapes.add_textbox(Inches(1.5), Inches(4.35), Inches(5.0), Inches(1.8))
tf_c = tb_cand.text_frame
p = tf_c.paragraphs[0]
p.text = "Réalisé par :"
p.font.size = Pt(12)
p.font.color.rgb = C_BLUE_CYBER
p.font.bold = True
p2 = tf_c.add_paragraph()
p2.text = "Mohamed Reda QIYAOUI"
p2.font.size = Pt(18)
p2.font.color.rgb = C_WHITE
p2.font.bold = True
p3 = tf_c.add_paragraph()
p3.text = "Filière Génie Informatique\nEST Tétouan - Université Abdelmalek Essaâdi"
p3.font.size = Pt(12)
p3.font.color.rgb = RGBColor(203, 213, 225)

tb_enc = s1.shapes.add_textbox(Inches(7.0), Inches(4.35), Inches(4.8), Inches(1.8))
tf_e = tb_enc.text_frame
p = tf_e.paragraphs[0]
p.text = "Encadrement & Soutenance :"
p.font.size = Pt(12)
p.font.color.rgb = C_BLUE_CYBER
p.font.bold = True
p2 = tf_e.add_paragraph()
p2.text = "Encadrantes :\n- Mme Asmae LAAZIZ\n- Mme Najia OTHMANI\n- Mme Salwa DOKALLI\nLieu : Commune de Tétouan | Année 2025/2026"
p2.font.size = Pt(12)
p2.font.color.rgb = RGBColor(226, 232, 240)

# ==========================================
# SLIDE 2 : SOMMAIRE GÉNÉRAL
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, C_BG_PAGE)
add_header(s2, "Plan de la Présentation", "Structure de la Soutenance")

agenda_items = [
    ("01", "Contexte Opérationnel & Problématique", "Commune de Tétouan, cécité des NIDS traditionnels (Snort, Suricata)."),
    ("02", "Fondements Théoriques & Algorithme iForest", "Principe des iTrees, formulation mathématique et justification du choix IA."),
    ("03", "Architecture Système : Approche Bicouche", "Pipeline global, analyse unitaire (Couche 1) et macroscopique (Couche 2)."),
    ("04", "Implémentation Logicielle & Outils Développés", "Orchestrateur CLI, Dashboard SOC Streamlit, Rapports Forensiques PDF."),
    ("05", "Banc d'Essai Expérimental & Résultats", "Topologie Kali vs Windows, élimination des angles morts, benchmark chiffré."),
    ("06", "Démonstration Pratique & Bilan", "Scénarios d'attaque en direct, compétences acquises et perspectives d'avenir.")
]

for i, item in enumerate(agenda_items):
    col = i % 2
    row = i // 2
    x = 0.8 + col * 6.0
    y = 1.6 + row * 1.8
    add_card(s2, x, y, 5.7, 1.6, None, C_BORDER, C_CARD_BG)
    
    # Badge numéro
    num_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.2), Inches(y + 0.25), Inches(0.9), Inches(0.9))
    num_box.fill.solid()
    num_box.fill.fore_color.rgb = C_NAVY_DARK
    num_box.line.fill.background()
    p = num_box.text_frame.paragraphs[0]
    p.text = item[0]
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_CYBER
    p.alignment = PP_ALIGN.CENTER
    
    # Textes
    tb = s2.shapes.add_textbox(Inches(x + 1.25), Inches(y + 0.15), Inches(4.2), Inches(1.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = item[1]
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = C_NAVY_DARK
    p2 = tf.add_paragraph()
    p2.text = item[2]
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_MUTED
    p2.space_before = Pt(3)

# ==========================================
# SLIDE 3 : CONTEXTE OPÉRATIONNEL & ORGANISME
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, C_BG_PAGE)
add_header(s3, "Contexte Opérationnel & Organisme d'Accueil", "01. Cadre du Projet")

add_card(s3, 0.8, 1.6, 5.6, 5.2, "Commune de Tétouan")
add_card_text(s3, 0.8, 1.6, 5.6, 5.2, [
    ("Cadre Institutionnel :", True, 13, C_TEAL, False),
    ("Division des Systèmes d'Information et de la Transformation Numérique.", False, 12, C_TEXT_DARK, True),
    ("Rôle & Missions Critiques :", True, 13, C_TEAL, False),
    ("Gestion du parc informatique, hébergement d'applications métier communales et connectivité inter-services.", False, 12, C_TEXT_DARK, True),
    ("Trafic Réseau Quotidien :", True, 13, C_TEAL, False),
    ("Flux hétérogènes mêlant navigation Web administrative, transferts de bases de données et accès distants.", False, 12, C_TEXT_DARK, True)
])

add_card(s3, 6.8, 1.6, 5.7, 5.2, "Enjeux de Sécurité & Motivation du Projet")
add_card_text(s3, 6.8, 1.6, 5.7, 5.2, [
    ("Vulnérabilité face aux Scans Furtifs :", True, 13, C_DANGER, False),
    ("Multiplication des reconnaissances silencieuses cartographiant les faiblesses du réseau sans déclencher d'alerte.", False, 12, C_TEXT_DARK, True),
    ("Risque de Déni de Service (DDoS) :", True, 13, C_DANGER, False),
    ("Menace de paralysie des services aux citoyens par saturation de la bande passante et des serveurs internes.", False, 12, C_TEXT_DARK, True),
    ("Besoin d'Autonomie & Légèreté :", True, 13, C_SUCCESS, False),
    ("Déployer une solution souveraine, rapide, sans abonnement onéreux ni surcharge matérielle.", False, 12, C_TEXT_DARK, True)
])

# ==========================================
# SLIDE 4 : PROBLÉMATIQUE : LIMITES DES NIDS
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, C_BG_PAGE)
add_header(s4, "Problématique : Les Angles Morts des NIDS Traditionnels", "01. Cadre du Projet")

add_card(s4, 0.8, 1.6, 3.6, 5.2, "Modèle à Signatures (Snort / Suricata)")
add_card_text(s4, 0.8, 1.6, 3.6, 5.2, [
    ("Principe Déterministe :", True, 13, C_NAVY_DARK, False),
    ("Recherche exacte de motifs textuels ou d'octets dans chaque trame.", False, 12, C_TEXT_DARK, True),
    ("Limite Majeure :", True, 13, C_DANGER, False),
    ("Totalement inefficace face à une menace nouvelle (Zero-Day) ou non documentée.", False, 12, C_TEXT_DARK, True),
    ("Maintenance Lourde :", True, 13, C_TEXT_MUTED, False),
    ("Nécessite des mises à jour constantes de règles complexes par des analystes.", False, 12, C_TEXT_DARK, True)
])

add_card(s4, 4.8, 1.6, 3.6, 5.2, "L'Angle Mort du SYN Stealth Scan")
add_card_text(s4, 4.8, 1.6, 3.6, 5.2, [
    ("Absence de Connexion :", True, 13, C_NAVY_DARK, False),
    ("Un scan SYN furtif n'établit jamais la connexion complète (Three-Way Handshake avorté).", False, 12, C_TEXT_DARK, True),
    ("Aucun Payload Malveillant :", True, 13, C_DANGER, False),
    ("Le paquet ne contient aucune charge utile suspecte : il s'agit d'une trame TCP standard.", False, 12, C_TEXT_DARK, True),
    ("Cécité Totale :", True, 13, C_DANGER, False),
    ("Les NIDS traditionnels laissent passer ce trafic sans déclencher la moindre alerte.", False, 12, C_TEXT_DARK, True)
])

add_card(s4, 8.8, 1.6, 3.7, 5.2, "Le Dilemme des Faux Positifs")
add_card_text(s4, 8.8, 1.6, 3.7, 5.2, [
    ("Règles Trop Sensibles :", True, 13, C_NAVY_DARK, False),
    ("Génèrent des milliers d'alertes injustifiées pour du trafic Web classique.", False, 12, C_TEXT_DARK, True),
    ("Fatigue d'Alerte :", True, 13, C_DANGER, False),
    ("Les analystes du SOC saturent et finissent par ignorer les alertes critiques réelles.", False, 12, C_TEXT_DARK, True),
    ("Nécessité de l'IA :", True, 13, C_SUCCESS, False),
    ("Apprendre la normalité statistique pour ne signaler que les réelles déviances comportementales.", False, 12, C_TEXT_DARK, True)
])

# ==========================================
# SLIDE 5 : LA SOLUTION NETSCAN
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, C_BG_PAGE)
add_header(s5, "La Solution NetScan : Détection Non Supervisée", "01. Cadre du Projet")

add_card(s5, 0.8, 1.6, 11.7, 1.4, "Changement de Paradigme")
add_card_text(s5, 0.8, 1.6, 11.7, 1.4, [
    ("Au lieu de chercher une signature connue (approche réactive dépassée), NetScan modélise la 'normalité' du réseau local et détecte géométriquement toute déviance anormale (approche proactive et autonome).", False, 13, C_TEXT_DARK, False)
], start_y_offset=0.55)

cards_s5 = [
    ("100% Non Supervisé", "Aucune dépendance envers des jeux de données pré-étiquetés ou des benchmarks historiques obsolètes.", C_TEAL),
    ("Calibrate-Then-Monitor", "Phase d'apprentissage passif (120 s) sur le trafic réel local avant d'activer la surveillance temps réel.", C_BLUE_CYBER),
    ("Architecture Bicouche", "Couche 1 unitaire (par paquet) + Couche 2 comportementale (fenêtres glissantes de 5 secondes).", C_SUCCESS)
]

for i, c in enumerate(cards_s5):
    x = 0.8 + i * 4.0
    add_card(s5, x, 3.3, 3.7, 3.5, c[0])
    add_card_text(s5, x, 3.3, 3.7, 3.5, [
        (c[1], False, 12, C_TEXT_DARK, False),
        ("Objectif :", True, 12, c[2], False),
        ("Neutraliser les Zero-Days sans intervention humaine quotidienne.", False, 11, C_TEXT_MUTED, True)
    ])

# ==========================================
# SLIDE 6 : ALGORITHME ISOLATION FOREST
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, C_BG_PAGE)
add_header(s6, "Fondements Théoriques : Algorithme Isolation Forest", "02. Fondements Théoriques")

add_card(s6, 0.8, 1.6, 5.6, 5.2, "Principe des Arbres d'Isolation (iTrees)")
add_card_text(s6, 0.8, 1.6, 5.6, 5.2, [
    ("Partitionnement Géométrique :", True, 13, C_TEAL, False),
    ("L'algorithme découpe l'espace des données de manière récursive en choisissant un attribut aléatoire et un seuil de coupure aléatoire.", False, 12, C_TEXT_DARK, True),
    ("Axiome Fondamental d'Isolation :", True, 13, C_NAVY_DARK, False),
    ("Les instances normales sont nombreuses et regroupées en clusters denses. Il faut un grand nombre de découpes pour les isoler.", False, 12, C_TEXT_DARK, True),
    ("Les anomalies sont rares et éloignées géométriquement. Elles sont isolées dès les premières coupures (faible profondeur).", False, 12, C_SUCCESS, True)
])

add_card(s6, 6.8, 1.6, 5.7, 5.2, "Pourquoi Isolation Forest en Cyberdéfense ?")
add_card_text(s6, 6.8, 1.6, 5.7, 5.2, [
    ("Complexité Linéaire Optimale :", True, 13, C_TEAL, False),
    ("Complexité en O(n log n), idéale pour analyser des flux réseau intenses en temps réel sans latence.", False, 12, C_TEXT_DARK, True),
    ("Sensibilité Nulle à la Forme des Données :", True, 13, C_NAVY_DARK, False),
    ("Ne fait aucune hypothèse préalable sur la distribution statistique des paquets réseau.", False, 12, C_TEXT_DARK, True),
    ("Faible Empreinte Mémoire :", True, 13, C_SUCCESS, False),
    ("Exécution possible sur une machine d'administration modeste sans équipement GPU dédié.", False, 12, C_TEXT_DARK, True)
])

# ==========================================
# SLIDE 7 : FORMULATION MATHÉMATIQUE
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, C_BG_PAGE)
add_header(s7, "Modélisation Mathématique & Scoring d'Anomalie", "02. Fondements Théoriques")

add_card(s7, 0.8, 1.6, 11.7, 2.0, "Formule Fondamentale du Score d'Anomalie (Liu et al., 2008)")
add_card_text(s7, 0.8, 1.6, 11.7, 2.0, [
    ("s(x, n) = 2 ^ ( - E(h(x)) / c(n) )", True, 16, C_BLUE_CYBER, False),
    ("E(h(x)) : Espérance de la profondeur de l'instance x à travers l'ensemble des iTrees de la forêt.", False, 12, C_TEXT_DARK, True),
    ("c(n) = 2 * ln(n - 1) + 0.5772156649 - (2 * (n - 1) / n) : Facteur de normalisation représentant la longueur moyenne d'un échec de recherche binaire pour n échantillons.", False, 12, C_TEXT_DARK, True)
], start_y_offset=0.5)

add_card(s7, 0.8, 3.8, 3.6, 3.0, "s(x, n) -> 1 (Anomalie Aisée)")
add_card_text(s7, 0.8, 3.8, 3.6, 3.0, [
    ("Profondeur E(h(x)) très faible.", True, 12, C_DANGER, False),
    ("L'échantillon est isolé instantanément.", False, 11, C_TEXT_DARK, True),
    ("Signature évidente d'un comportement d'attaque.", False, 11, C_DANGER, True)
])

add_card(s7, 4.8, 3.8, 3.6, 3.0, "s(x, n) -> 0.5 (Incertitude)")
add_card_text(s7, 4.8, 3.8, 3.6, 3.0, [
    ("Profondeur moyenne standard.", True, 12, C_TEXT_MUTED, False),
    ("L'ensemble des données ne présente pas d'anomalie marquée.", False, 11, C_TEXT_DARK, True),
    ("Trafic typique d'arrière-plan.", False, 11, C_TEXT_MUTED, True)
])

add_card(s7, 8.8, 3.8, 3.7, 3.0, "Seuil Décisionnel : Seuil = 0.60")
add_card_text(s7, 8.8, 3.8, 3.7, 3.0, [
    ("Fixé après benchmark empirique.", True, 12, C_SUCCESS, False),
    ("Garantit un taux de détection maximal.", False, 11, C_TEXT_DARK, True),
    ("Maintient les faux positifs à moins de 1.2%.", False, 11, C_SUCCESS, True)
])

# ==========================================
# SLIDE 8 : BENCHMARK ALGORITHMIQUE (TABLEAU)
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, C_BG_PAGE)
add_header(s8, "Benchmark Algorithmique : Pourquoi Isolation Forest ?", "02. Fondements Théoriques")

# Tableau comparatif (Tableau 2.3 du rapport)
tbl_s8 = s8.shapes.add_table(5, 4, Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.8))
tbl = tbl_s8.table
tbl.columns[0].width = Inches(2.7)
tbl.columns[1].width = Inches(3.0)
tbl.columns[2].width = Inches(3.0)
tbl.columns[3].width = Inches(3.0)

headers_s8 = ["Critère d'Évaluation", "Isolation Forest (NetScan)", "One-Class SVM", "k-Means Anomaly"]
data_s8 = [
    ["Complexité Temporelle", "O(n · log n) — Ultra-rapide", "O(n² à n³) — Lourd", "O(n · k · i) — Moyen"],
    ["Sensibilité à la Dimension", "Faible (sélection aléatoire)", "Élevée (fléau dimensionnel)", "Élevée (distances déformées)"],
    ["Hypothèse de Distribution", "Aucune hypothèse préalable", "Nécessite réglage noyau fin", "Suppose clusters sphériques"],
    ["Adaptation Temps Réel", "Optimale (faible mémoire)", "Faible (inversion matricielle)", "Faible (sensible centres init.)"]
]

for col_idx, h in enumerate(headers_s8):
    cell = tbl.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK if col_idx != 1 else C_BLUE_CYBER
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = C_WHITE

for row_idx, row_data in enumerate(data_s8):
    for col_idx, text in enumerate(row_data):
        cell = tbl.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 0 else C_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(12)
        p.font.name = "Segoe UI"
        if col_idx == 1:
            p.font.bold = True
            p.font.color.rgb = C_TEAL
        else:
            p.font.color.rgb = C_TEXT_DARK

# ==========================================
# SLIDE 9 : MENACE 1 : SYN STEALTH SCAN
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, C_BG_PAGE)
add_header(s9, "Attaque Cible 1 : TCP SYN Stealth Scan (Nmap -sS)", "02. Fondements Théoriques")

add_card(s9, 0.8, 1.6, 5.6, 5.2, "Mécanisme Technique de l'Attaque")
add_card_text(s9, 0.8, 1.6, 5.6, 5.2, [
    ("1. Émission du paquet SYN :", True, 13, C_NAVY_DARK, False),
    ("L'attaquant envoie un paquet TCP avec le flag SYN activé vers chaque port de la cible.", False, 12, C_TEXT_DARK, True),
    ("2. Réponse du Serveur Cible :", True, 13, C_TEAL, False),
    ("Si le port est ouvert, le serveur répond par un paquet SYN-ACK.", False, 12, C_TEXT_DARK, True),
    ("3. Interruption Brutale (Flag RST) :", True, 13, C_DANGER, False),
    ("Au lieu de renvoyer le ACK final, l'attaquant envoie immédiatement un paquet RST pour réinitialiser la connexion.", False, 12, C_DANGER, True)
])

add_card(s9, 6.8, 1.6, 5.7, 5.2, "Conséquences Opérationnelles pour le SOC")
add_card_text(s9, 6.8, 1.6, 5.7, 5.2, [
    ("Connexion Jamais Complétée :", True, 13, C_DANGER, False),
    ("Le Three-Way Handshake n'est jamais terminé par le client.", False, 12, C_TEXT_DARK, True),
    ("Absence de Logs Applicatifs :", True, 13, C_DANGER, False),
    ("Les serveurs Web (Apache, Nginx) ou de bases de données ne consignent RIEN dans leurs fichiers de journaux.", False, 12, C_TEXT_DARK, True),
    ("Cartographie Furtive Réussie :", True, 13, C_NAVY_DARK, False),
    ("L'attaquant dresse la liste exacte des ports ouverts sans éveiller les pare-feux applicatifs.", False, 12, C_TEXT_MUTED, True)
])

# ==========================================
# SLIDE 10 : MENACE 2 : SYN FLOOD (DDOS)
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, C_BG_PAGE)
add_header(s10, "Attaque Cible 2 : SYN Flood (DDoS Volumétrique)", "02. Fondements Théoriques")

add_card(s10, 0.8, 1.6, 5.6, 5.2, "Mécanisme d'Inondation TCP")
add_card_text(s10, 0.8, 1.6, 5.6, 5.2, [
    ("Inondation Massive :", True, 13, C_DANGER, False),
    ("L'attaquant injecte des milliers de requêtes SYN par seconde avec des adresses IP sources forgées (Spoofing).", False, 12, C_TEXT_DARK, True),
    ("Allocation Mémoire Cible :", True, 13, C_NAVY_DARK, False),
    ("Le serveur alloue une structure Transmission Control Block (TCB) pour chaque requête et passe en état SYN_RECEIVED.", False, 12, C_TEXT_DARK, True),
    ("Attente sans Fin :", True, 13, C_TEXT_MUTED, False),
    ("Le serveur attend le ACK de validation jusqu'à expiration du délai de garde (Timeout).", False, 12, C_TEXT_DARK, True)
])

add_card(s10, 6.8, 1.6, 5.7, 5.2, "Impact Critique sur l'Infrastructure")
add_card_text(s10, 6.8, 1.6, 5.7, 5.2, [
    ("Saturation de la Backlog Queue :", True, 13, C_DANGER, False),
    ("La file d'attente des connexions demi-ouvertes est saturée en quelques secondes.", False, 12, C_DANGER, True),
    ("Rejet des Utilisateurs Légitimes :", True, 13, C_DANGER, False),
    ("Toute nouvelle demande de connexion valide est rejetée immédiatement (Déni de Service total).", False, 12, C_DANGER, True),
    ("Paralysie des Services Municipaux :", True, 13, C_NAVY_DARK, False),
    ("Indisponibilité des serveurs de la mairie et interruption du service aux citoyens.", False, 12, C_TEXT_MUTED, True)
])

# ==========================================
# SLIDE 11 : ARCHITECTURE SYSTÈME GLOBALE
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, C_BG_PAGE)
add_header(s11, "Architecture Globale : Le Pipeline Bicouche (Dual-Layer)", "03. Architecture Système")

steps_s11 = [
    ("Étape 1 : Ingestion", "Capture passive Promiscuous via Scapy & Npcap en temps réel.", C_NAVY_DARK),
    ("Étape 2 : Extraction", "Génération des features Couche 1 (unitaire) et Couche 2 (macro 5s).", C_TEAL),
    ("Étape 3 : IA iForest", "Calcul récursif des profondeurs moyennes d'isolation et des scores.", C_BLUE_CYBER),
    ("Étape 4 : Qualification", "Matrice de décision : Normal, Port Scan furtif ou Flood volumétrique.", C_SUCCESS),
    ("Étape 5 : Réponse", "Alertes Discord en temps réel, Dashboard Streamlit et Rapport PDF.", C_NAVY_DARK)
]

for i, step in enumerate(steps_s11):
    x = 0.8 + i * 2.4
    card = add_card(s11, x, 1.8, 2.25, 4.8, step[0], C_BORDER, C_CARD_BG)
    add_card_text(s11, x, 1.8, 2.25, 4.8, [
        (step[1], False, 12, C_TEXT_DARK, False),
        ("Rôle clé :", True, 12, step[2], False),
        ("Fiabilité opérationnelle garantie.", False, 11, C_TEXT_MUTED, True)
    ], start_y_offset=0.7)

# ==========================================
# SLIDE 12 : COUCHE 1 - ANALYSE UNITAIRE
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, C_BG_PAGE)
add_header(s12, "Couche 1 : Analyse Microscopique Unitaire (Par Paquet)", "03. Architecture Système")

add_card(s12, 0.8, 1.6, 5.6, 5.2, "Attributs Extraits au Niveau Trame")
add_card_text(s12, 0.8, 1.6, 5.6, 5.2, [
    ("Protocole de Transport :", True, 13, C_TEAL, False),
    ("Encodage numérique (TCP = 6, UDP = 17, ICMP = 1).", False, 12, C_TEXT_DARK, True),
    ("Longueur Totale du Paquet :", True, 13, C_TEAL, False),
    ("Taille de la trame en octets (repère les trames anormalement courtes ou longues).", False, 12, C_TEXT_DARK, True),
    ("Drapeaux de Contrôle TCP :", True, 13, C_NAVY_DARK, False),
    ("Indicateurs binaires pour les flags SYN, ACK, RST et FIN.", False, 12, C_TEXT_DARK, True),
    ("Intervalle Inter-Paquets :", True, 13, C_NAVY_DARK, False),
    ("Temps écoulé depuis la dernière trame capturée (Delta t).", False, 12, C_TEXT_DARK, True)
])

add_card(s12, 6.8, 1.6, 5.7, 5.2, "Pourquoi la Couche 1 est-elle Insuffisante Seule ?")
add_card_text(s12, 6.8, 1.6, 5.7, 5.2, [
    ("La Faille Fondamentale de l'Analyse Unitaire :", True, 13, C_DANGER, False),
    ("Pris isolément, un paquet émis par un scan Nmap possède toutes les caractéristiques d'une trame légitime (taille standard ~60 octets, entêtes valides).", False, 12, C_TEXT_DARK, True),
    ("Résultat Expérimental :", True, 13, C_DANGER, False),
    ("Le modèle unitaire baseline rate 100% des scans de ports SYN furtifs (taux de détection de 0%) !", False, 12, C_DANGER, True),
    ("Nécessité de Corrélation :", True, 13, C_SUCCESS, False),
    ("L'anomalie n'est pas dans le contenu de la trame, mais dans son comportement temporel global.", False, 12, C_SUCCESS, True)
])

# ==========================================
# SLIDE 13 : COUCHE 2 - ANALYSE COMPORTEMENTALE
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13, C_BG_PAGE)
add_header(s13, "Couche 2 : Analyse Comportementale par Micro-Fenêtres (5s)", "03. Architecture Système")

add_card(s13, 0.8, 1.6, 5.6, 5.2, "Agrégation Temporelle & Features Clés")
add_card_text(s13, 0.8, 1.6, 5.6, 5.2, [
    ("Fenêtre Glissante de 5 Secondes :", True, 13, C_TEAL, False),
    ("Compromis optimal entre réactivité opérationnelle et consistance statistique.", False, 12, C_TEXT_DARK, True),
    ("Volume de Paquets par Fenêtre :", True, 13, C_NAVY_DARK, False),
    ("Détecte immédiatement les hausses brutales de débit (inondations).", False, 12, C_TEXT_DARK, True),
    ("Nombre de Ports Uniques Contactés :", True, 13, C_BLUE_CYBER, False),
    ("Révèle les comportements d'exploration horizontale ou verticale.", False, 12, C_TEXT_DARK, True)
])

add_card(s13, 6.8, 1.6, 5.7, 5.2, "Le Ratio de Dispersion des Ports (R)")
add_card_text(s13, 6.8, 1.6, 5.7, 5.2, [
    ("Formule Mathématique du Ratio :", True, 13, C_BLUE_CYBER, False),
    ("R = Nombre de Ports Uniques Contactés / Nombre Total de Paquets", True, 13, C_NAVY_DARK, False),
    ("Signature du Port Scan : R -> 1", True, 13, C_DANGER, False),
    ("Une grande variété de ports contactés pour un nombre réduit de paquets par port (R proche de 1.0).", False, 12, C_TEXT_DARK, True),
    ("Signature du Flood / DDoS : R -> 0", True, 13, C_DANGER, False),
    ("Un volume gigantesque de trames concentrées vers un seul port cible (ex: port 80/443).", False, 12, C_TEXT_DARK, True),
    ("Trafic Normal : R stable et modéré", True, 13, C_SUCCESS, False),
    ("Moins de 4 ports cibles réguliers pour du trafic applicatif usuel.", False, 12, C_TEXT_MUTED, True)
])

# ==========================================
# SLIDE 14 : MATRICE DE DÉCISION
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14, C_BG_PAGE)
add_header(s14, "Matrice de Décision & Qualification des Menaces", "03. Architecture Système")

tbl_s14 = s14.shapes.add_table(4, 4, Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.8))
tbl = tbl_s14.table
tbl.columns[0].width = Inches(2.7)
tbl.columns[1].width = Inches(3.0)
tbl.columns[2].width = Inches(3.0)
tbl.columns[3].width = Inches(3.0)

headers_s14 = ["Séquence de Trafic", "Comportement Niveau 1", "Comportement Niveau 2 (5s)", "Décision & Qualification"]
data_s14 = [
    ["Trafic Sain (Arrière-plan)", "Trames TCP/UDP régulières", "<= 4 ports, < 30 pkts / 5s", "Trafic Normal (s ~ 0.44)"],
    ["Scan Nmap (-sS)", "Paquets SYN de taille légitime (60 B) -> Non détecté", "330+ ports cibles uniques, Ratio R > 0.90", "ALERTE CRITIQUE : Port Scan (s = 0.88)"],
    ["SYN Flood (DDoS)", "Trame par trame : paquets SYN identiques", "800+ paquets / 5s concentrés sur 1 port", "ALERTE CRITIQUE : Flood / DDoS (s = 0.92)"]
]

for col_idx, h in enumerate(headers_s14):
    cell = tbl.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK if col_idx != 3 else C_BLUE_CYBER
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = C_WHITE

for row_idx, row_data in enumerate(data_s14):
    for col_idx, text in enumerate(row_data):
        cell = tbl.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 0 else C_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(12)
        p.font.name = "Segoe UI"
        if col_idx == 3:
            p.font.bold = True
            p.font.color.rgb = C_SUCCESS if row_idx == 0 else C_DANGER
        else:
            p.font.color.rgb = C_TEXT_DARK

# ==========================================
# SLIDE 15 : STACK TECHNOLOGIQUE
# ==========================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15, C_BG_PAGE)
add_header(s15, "Stack Technologique & Écosystème Logiciel", "04. Implémentation Logicielle")

stack_s15 = [
    ("Python 3.11", "Langage principal de développement : prototypage rapide, syntaxe claire et richesse des bibliothèques.", C_TEAL),
    ("Scapy 2.5 & Npcap", "Moteur d'ingestion et de dissection réseau bas niveau en temps réel sur interface physique.", C_NAVY_DARK),
    ("Scikit-learn", "Implémentation hautement optimisée de l'algorithme Isolation Forest pour l'inférence.", C_BLUE_CYBER),
    ("Pandas & NumPy", "Vectorisation haute performance des calculs statistiques sur les fenêtres glissantes.", C_TEAL),
    ("Streamlit", "Interface utilisateur web interactive pour la console de supervision SOC en temps réel.", C_SUCCESS),
    ("ReportLab & Webhooks", "Génération automatique de rapports forensiques PDF et alertes Discord instantanées.", C_NAVY_DARK)
]

for i, st in enumerate(stack_s15):
    col = i % 3
    row = i // 3
    x = 0.8 + col * 4.0
    y = 1.6 + row * 2.7
    add_card(s15, x, y, 3.7, 2.4, st[0], C_BORDER, C_CARD_BG)
    add_card_text(s15, x, y, 3.7, 2.4, [
        (st[1], False, 12, C_TEXT_DARK, False),
        ("Rôle Clé :", True, 12, st[2], False),
        ("Intégration transparente dans la chaîne d'alerte.", False, 11, C_TEXT_MUTED, True)
    ], start_y_offset=0.6)

# ==========================================
# SLIDE 16 : LES 4 BRIQUES LOGICIELLES
# ==========================================
s16 = prs.slides.add_slide(blank_layout)
set_slide_background(s16, C_BG_PAGE)
add_header(s16, "Les 4 Briques Logicielles Développées", "04. Implémentation Logicielle")

modules_s16 = [
    ("netscan.py (Orchestrateur CLI)", "Cœur d'exécution exécutable sous Linux Kali ou Windows. Gère les modes Démo, PCAP statique et Live Sniffing avec phase de calibration passive (120 s).", C_NAVY_DARK),
    ("dashboard.py (Console SOC Web)", "Tableau de bord interactif sous Streamlit affichant les indicateurs clés (KPI), les distributions de scores, l'historique des alertes et les flux en direct.", C_BLUE_CYBER),
    ("report_generator.py (Forensics PDF)", "Moteur d'audit générant des synthèses d'incident prêtes pour l'équipe RSSI avec horodatage certifié, adresses IP sources et préconisations de mitigation.", C_TEAL),
    ("test_smoke.py (Assurance Qualité)", "Suite de tests automatisés validant la conformité des flux de capture, la non-régression de l'inférence iForest et l'absence de saturation mémoire.", C_SUCCESS)
]

for i, mod in enumerate(modules_s16):
    col = i % 2
    row = i // 2
    x = 0.8 + col * 6.0
    y = 1.6 + row * 2.7
    add_card(s16, x, y, 5.7, 2.4, mod[0], C_BORDER, C_CARD_BG)
    add_card_text(s16, x, y, 5.7, 2.4, [
        (mod[1], False, 12, C_TEXT_DARK, False),
        ("Impact Opérationnel :", True, 12, mod[2], False),
        ("Autonomie complète et déploiement immédiat.", False, 11, C_TEXT_MUTED, True)
    ], start_y_offset=0.6)

# ==========================================
# SLIDE 17 : BANC D'ESSAI EXPÉRIMENTAL
# ==========================================
s17 = prs.slides.add_slide(blank_layout)
set_slide_background(s17, C_BG_PAGE)
add_header(s17, "Banc d'Essai Expérimental & Topologie de Test", "05. Expérimentation & Résultats")

add_card(s17, 0.8, 1.6, 5.6, 5.2, "Topologie Virtualisée & Matérielle")
add_card_text(s17, 0.8, 1.6, 5.6, 5.2, [
    ("Poste 1 : Attaquant / Audit (Kali Linux) :", True, 13, C_DANGER, False),
    ("Adresse IP : 192.168.1.50 — Outillage : Nmap pour les scans furtifs (-sS), Hping3 pour les inondations SYN Flood massives.", False, 12, C_TEXT_DARK, True),
    ("Poste 2 : Sonde & Supervision (Windows) :", True, 13, C_NAVY_DARK, False),
    ("Adresse IP : 192.168.1.100 — NetScan exécuté en écoute Promiscuous via driver Npcap.", False, 12, C_TEXT_DARK, True),
    ("Poste 3 : Cible & Services Réseau :", True, 13, C_TEAL, False),
    ("Serveur Metasploitable / Serveur de test hébergeant des services HTTP, SSH, FTP simulés.", False, 12, C_TEXT_DARK, True)
])

add_card(s17, 6.8, 1.6, 5.7, 5.2, "Protocole Rigoureux de Test")
add_card_text(s17, 6.8, 1.6, 5.7, 5.2, [
    ("Double Environnement de Validation :", True, 13, C_BLUE_CYBER, False),
    ("1. Validation contrôlée sur des captures réelles et synthétiques (fichiers PCAP certifiés).", False, 12, C_TEXT_DARK, True),
    ("2. Validation in situ en temps réel sur le trafic réel de la Commune de Tétouan.", False, 12, C_TEXT_DARK, True),
    ("Conditions de Réalisme :", True, 13, C_NAVY_DARK, False),
    ("Injection d'attaques au milieu d'un trafic d'arrière-plan sain et bruité (navigation web, streaming, DNS).", False, 12, C_TEXT_DARK, True),
    ("Vérification Zéro-Faux-Positif :", True, 13, C_SUCCESS, False),
    ("Confirmation de la robustesse face au bruit ordinaire.", False, 12, C_SUCCESS, True)
])

# ==========================================
# SLIDE 18 : RÉSULTATS EXPÉRIMENTAUX (TABLEAU 5.2)
# ==========================================
s18 = prs.slides.add_slide(blank_layout)
set_slide_background(s18, C_BG_PAGE)
add_header(s18, "Résultats Expérimentaux & Analyse Comparative", "05. Expérimentation & Résultats")

tbl_s18 = s18.shapes.add_table(6, 4, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
tbl = tbl_s18.table
tbl.columns[0].width = Inches(2.7)
tbl.columns[1].width = Inches(2.8)
tbl.columns[2].width = Inches(3.2)
tbl.columns[3].width = Inches(3.0)

headers_s18 = ["Critère d'Évaluation", "Modèle Baseline (Unitaire)", "NetScan (Architecture Bicouche)", "Gain Opérationnel"]
data_s18 = [
    ["Détection Scans Nmap (-sS)", "0% (Angle mort total)", "100% (Fenêtres isolées)", "Élimination totale de l'angle mort"],
    ["Détection SYN Flood (DDoS)", "Partielle (selon la taille)", "100% (Volume détecté)", "Identification immédiate de l'attaquant"],
    ["Taux de Faux Positifs", "12.4% (Trafic web bruité)", "< 1.2% (Grâce au ratio R)", "Divisé par 10 (Fin fatigue d'alerte)"],
    ["Temps d'Analyse (4 100 trames)", "4.8 secondes", "1.9 seconde (Pandas vectorisé)", "Vitesse multipliée par 2.5"],
    ["Explicabilité de l'Anomalie", "Simple label 'Anormal'", "Précise (Port Scan ou DDoS)", "Gain de temps décisionnel pour le SOC"]
]

for col_idx, h in enumerate(headers_s18):
    cell = tbl.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK if col_idx != 2 else C_BLUE_CYBER
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = C_WHITE

for row_idx, row_data in enumerate(data_s18):
    for col_idx, text in enumerate(row_data):
        cell = tbl.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 0 else C_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(12)
        p.font.name = "Segoe UI"
        if col_idx == 2:
            p.font.bold = True
            p.font.color.rgb = C_TEAL
        elif col_idx == 3:
            p.font.bold = True
            p.font.color.rgb = C_SUCCESS
        else:
            p.font.color.rgb = C_TEXT_DARK

# ==========================================
# SLIDE 19 : DÉMONSTRATION PRATIQUE LIVE
# ==========================================
s19 = prs.slides.add_slide(blank_layout)
set_slide_background(s19, C_BG_PAGE)
add_header(s19, "Démonstration Pratique : Scénarios Opérationnels", "06. Démonstration Live")

demo_steps = [
    ("Étape 1 : Initialisation & Calibration", "Lancement de netscan.py --live sur l'interface réseau. Observation de la calibration passive de 120s pour apprendre l'empreinte locale.", C_NAVY_DARK),
    ("Étape 2 : Simulation Scan Furtif", "Exécution depuis Kali de nmap -sS vers la cible. Détection immédiate (< 5s), calcul du ratio R > 0.90 et notification Discord.", C_DANGER),
    ("Étape 3 : Simulation Inondation DDoS", "Lancement d'une salve hping3 --flood -S -p 80. Détection volumétrique en Couche 2 avec score d'anomalie culminant à 0.92.", C_DANGER),
    ("Étape 4 : Consultation SOC & Rapport", "Ouverture du Dashboard Streamlit : analyse des courbes en direct, consultation des logs forensiques et export du rapport d'incident PDF.", C_SUCCESS)
]

for i, step in enumerate(demo_steps):
    x = 0.8 + i * 3.0
    add_card(s19, x, 1.8, 2.7, 4.8, step[0], C_BORDER, C_CARD_BG)
    add_card_text(s19, x, 1.8, 2.7, 4.8, [
        (step[1], False, 12, C_TEXT_DARK, False),
        ("Validation attendue :", True, 12, step[2], False),
        ("Réaction en moins de 5 secondes.", False, 11, C_TEXT_MUTED, True)
    ], start_y_offset=0.8)

# ==========================================
# SLIDE 20 : BILAN DU STAGE & COMPÉTENCES
# ==========================================
s20 = prs.slides.add_slide(blank_layout)
set_slide_background(s20, C_BG_PAGE)
add_header(s20, "Bilan du Projet & Compétences Consolidées", "07. Bilan & Perspectives")

add_card(s20, 0.8, 1.6, 5.6, 5.2, "Compétences Réseaux & Cyberdéfense")
add_card_text(s20, 0.8, 1.6, 5.6, 5.2, [
    ("Analyse Protocolaire Approfondie :", True, 13, C_TEAL, False),
    ("Maîtrise du cycle TCP (Handshake, flags, teardown, fenêtrage).", False, 12, C_TEXT_DARK, True),
    ("Sécurité Offensive & Audit :", True, 13, C_NAVY_DARK, False),
    ("Pratique des outils d'audit Nmap et Hping3 sous environnement Kali Linux.", False, 12, C_TEXT_DARK, True),
    ("Architecture NIDS & SOC :", True, 13, C_BLUE_CYBER, False),
    ("Conception d'une chaîne complète d'alerte, de scoring et de journalisation forensique.", False, 12, C_TEXT_DARK, True)
])

add_card(s20, 6.8, 1.6, 5.7, 5.2, "Compétences Data Science & Génie Logiciel")
add_card_text(s20, 6.8, 1.6, 5.7, 5.2, [
    ("Intelligence Artificielle Non Supervisée :", True, 13, C_TEAL, False),
    ("Compréhension mathématique et réglage fin de l'algorithme Isolation Forest.", False, 12, C_TEXT_DARK, True),
    ("Traitement de Données Temps Réel :", True, 13, C_NAVY_DARK, False),
    ("Vectorisation performante sous Pandas/NumPy pour respecter les contraintes du live streaming.", False, 12, C_TEXT_DARK, True),
    ("Développement Full-Stack Python :", True, 13, C_SUCCESS, False),
    ("Création d'un outillage complet (CLI, Web Streamlit, Générateur PDF, API Webhooks).", False, 12, C_TEXT_DARK, True)
])

# ==========================================
# SLIDE 21 : DIFFICULTÉS & SOLUTIONS
# ==========================================
s21 = prs.slides.add_slide(blank_layout)
set_slide_background(s21, C_BG_PAGE)
add_header(s21, "Difficultés Rencontrées & Solutions Apportées", "07. Bilan & Perspectives")

diff_items = [
    ("1. Bruit Réseau & Absence de Vérité Terrain", "Défi : Comment entraîner un modèle d'IA sans données pré-étiquetées sur le réseau local ?\nSolution : Implémentation du protocole Calibrate-Then-Monitor (120 s d'auto-apprentissage passif in situ).", C_TEAL),
    ("2. Ingestion Haute Fréquence sans Perte de Trames", "Défi : Risque d'engorgement mémoire et de latence lors du décodage trame par trame avec Scapy.\nSolution : Vectorisation des calculs statistiques par micro-fenêtres de 5s via Pandas (gain de vitesse x2.5).", C_NAVY_DARK),
    ("3. Élimination des Faux Positifs Web", "Défi : La navigation Web génère de multiples connexions simultanées pouvant ressembler à un scan.\nSolution : Création du Ratio de Dispersion des Ports (R) pour distinguer le trafic légitime des attaques.", C_SUCCESS)
]

for i, item in enumerate(diff_items):
    y = 1.6 + i * 1.8
    add_card(s21, 0.8, y, 11.7, 1.6, item[0], C_BORDER, C_CARD_BG)
    add_card_text(s21, 0.8, y, 11.7, 1.6, [
        (item[1], False, 12, C_TEXT_DARK, False)
    ], start_y_offset=0.55)

# ==========================================
# SLIDE 22 : PERSPECTIVES D'ÉVOLUTION
# ==========================================
s22 = prs.slides.add_slide(blank_layout)
set_slide_background(s22, C_BG_PAGE)
add_header(s22, "Perspectives d'Évolution du Système", "07. Bilan & Perspectives")

perspectives = [
    ("Réponse Active Automatisée (NIPS)", "Évolution vers un système de prévention active en déclenchant des règles de blocage automatique sur le pare-feu (Windows Firewall / iptables / eBPF) dès confirmation d'une alerte critique.", C_DANGER),
    ("Intégration SIEM d'Entreprise", "Développement de connecteurs standardisés (Syslog, JSON) pour exporter les alertes vers des plateformes de supervision centralisées telles que Wazuh, Elastic SIEM ou Splunk.", C_BLUE_CYBER),
    ("Analyse des Flux Chiffrés (TLS)", "Intégration de techniques de fingerprinting TLS (JA3 / JA3S) pour détecter les anomalies et malwares dissimulés dans le trafic chiffré HTTPS sans déchiffrement de contenu.", C_TEAL)
]

for i, p in enumerate(perspectives):
    x = 0.8 + i * 4.0
    add_card(s22, x, 1.8, 3.7, 4.8, p[0], C_BORDER, C_CARD_BG)
    add_card_text(s22, x, 1.8, 3.7, 4.8, [
        (p[1], False, 12, C_TEXT_DARK, False),
        ("Horizon de Déploiement :", True, 12, p[2], False),
        ("Évolution logicielle à court et moyen terme.", False, 11, C_TEXT_MUTED, True)
    ], start_y_offset=0.7)

# ==========================================
# SLIDE 23 : CONCLUSION & QUESTIONS/RÉPONSES
# ==========================================
s23 = prs.slides.add_slide(blank_layout)
set_slide_background(s23, C_NAVY_DARK)

bar_end = s23.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(4.0))
bar_end.fill.solid()
bar_end.fill.fore_color.rgb = C_BLUE_CYBER
bar_end.line.fill.background()

tb_end = s23.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
tf_end = tb_end.text_frame
tf_end.word_wrap = True
p = tf_end.paragraphs[0]
p.text = "CONCLUSION GÉNÉRALE"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_BLUE_CYBER

p2 = tf_end.add_paragraph()
p2.text = "NetScan confirme la pertinence et la robustesse du Machine Learning Non Supervisé pour combler les failles critiques des systèmes traditionnels."
p2.font.size = Pt(22)
p2.font.bold = True
p2.font.color.rgb = C_WHITE
p2.space_before = Pt(10)

card_thanks = s23.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.2), Inches(10.8), Inches(2.2))
card_thanks.fill.solid()
card_thanks.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_thanks.line.color.rgb = C_BLUE_CYBER

tb_th = s23.shapes.add_textbox(Inches(1.5), Inches(4.4), Inches(10.2), Inches(1.8))
tf_th = tb_th.text_frame
p = tf_th.paragraphs[0]
p.text = "Merci pour votre attention !"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = C_WHITE
p.alignment = PP_ALIGN.CENTER

p2 = tf_th.add_paragraph()
p2.text = "Je suis à votre disposition pour répondre à toutes vos questions."
p2.font.size = Pt(15)
p2.font.color.rgb = C_BLUE_CYBER
p2.alignment = PP_ALIGN.CENTER
p2.space_before = Pt(6)

p3 = tf_th.add_paragraph()
p3.text = "Mohamed Reda QIYAOUI | EST Tétouan | Commune de Tétouan"
p3.font.size = Pt(12)
p3.font.color.rgb = RGBColor(148, 163, 184)
p3.alignment = PP_ALIGN.CENTER
p3.space_before = Pt(8)

prs.save(PPTX_OUT)
print(f"[OK] Fichier PowerPoint complet généré avec succès : {PPTX_OUT}")

# ==========================================
# GÉNÉRATION DU FICHIER VBA (.BAS)
# ==========================================
vba_code = '''Attribute VB_Name = "Module_Soutenance_NetScan"
' ==============================================================================
' MODULE VBA : GENERATEUR DE LA SOUTENANCE NETSCAN (23 SLIDES PROFESSIONNELLES)
' Projet : Conception et developpement d'un systeme intelligent de detection d'anomalies reseau
' Auteur : Mohamed Reda QIYAOUI - EST Tetouan - 2025/2026
' ==============================================================================

Option Explicit

' Palette de Couleurs Modernes Cyber
Public Const C_NAVY_DARK As Long = &H2A170F      ' RGB(15, 23, 42)
Public Const C_NAVY_HEADER As Long = &H2F190A    ' RGB(10, 25, 47)
Public Const C_BLUE_CYBER As Long = &HC78402     ' RGB(2, 132, 199)
Public Const C_TEAL As Long = &H90740E           ' RGB(14, 116, 144)
Public Const C_BG_PAGE As Long = &HFCFAF8        ' RGB(248, 250, 252)
Public Const C_CARD_BG As Long = &HFFFFFF        ' Blanc
Public Const C_BORDER As Long = &HE0D4CB         ' RGB(203, 213, 225)
Public Const C_TEXT_DARK As Long = &H2A170F      ' RGB(15, 23, 42)
Public Const C_TEXT_MUTED As Long = &H8B7464     ' RGB(100, 116, 139)
Public Const C_SUCCESS As Long = &H81B910        ' RGB(16, 185, 129)
Public Const C_DANGER As Long = &H2626DC         ' RGB(220, 38, 38)
Public Const C_WHITE As Long = &HFFFFFF

Public Sub GenererSoutenanceNetScan()
    Dim pres As Presentation
    Dim sld As Slide
    Dim i As Integer
    
    ' Creation d'une nouvelle presentation ecran large (16:9)
    Set pres = Presentations.Add
    pres.PageSetup.SlideWidth = 960
    pres.PageSetup.SlideHeight = 540
    
    ' -------------------------------------------------------------
    ' SLIDE 1 : TITRE & ACCUEIL
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(1, ppLayoutBlank)
    CreerFond sld, C_NAVY_DARK
    CreerBarreLaterale sld, 40, 90, 8, 350, C_BLUE_CYBER
    
    CreerZoneTexte sld, 60, 90, 840, 40, "SOUTENANCE DE PROJET DE FIN D'ETUDES", 14, True, C_BLUE_CYBER
    CreerZoneTexte sld, 60, 125, 840, 80, "Conception et Developpement d'un Systeme Intelligent de Detection d'Anomalies Reseau", 24, True, C_WHITE
    CreerZoneTexte sld, 60, 205, 840, 40, "NetScan : Detection Precoce d'Intrusions par Machine Learning Non Supervise (Isolation Forest)", 16, False, RGB(148, 163, 184)
    
    ' Bloc informations
    Dim c1 As Shape
    Set c1 = CreerCarte(sld, 60, 270, 840, 200, RGB(30, 41, 59), C_BLUE_CYBER)
    CreerZoneTexte sld, 80, 290, 380, 160, "Realise par :" & vbCrLf & "Mohamed Reda QIYAOUI" & vbCrLf & "Filiere Genie Informatique" & vbCrLf & "EST Tetouan - Univ. Abdelmalek Essaadi", 14, False, C_WHITE
    CreerZoneTexte sld, 480, 290, 400, 160, "Encadrantes :" & vbCrLf & "- Mme Asmae LAAZIZ" & vbCrLf & "- Mme Najia OTHMANI" & vbCrLf & "- Mme Salwa DOKALLI" & vbCrLf & "Lieu : Commune de Tetouan | 2025/2026", 14, False, C_WHITE

    ' -------------------------------------------------------------
    ' SLIDE 2 : SOMMAIRE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(2, ppLayoutBlank)
    CreerHeader sld, "Plan de la Presentation", "Structure de la Soutenance"
    
    Dim agenda(0 To 5, 0 To 1) As String
    agenda(0, 0) = "01. Contexte & Problematique": agenda(0, 1) = "Commune de Tetouan, cecite des NIDS traditionnels (Snort, Suricata)."
    agenda(1, 0) = "02. Fondements Theoriques & iForest": agenda(1, 1) = "Principe des iTrees, formulation mathematique et benchmark algorithmique."
    agenda(2, 0) = "03. Architecture Systeme Bicouche": agenda(2, 1) = "Pipeline global, Couche 1 unitaire et Couche 2 macroscopique (5s)."
    agenda(3, 0) = "04. Implementation Logicielle": agenda(3, 1) = "Orchestrateur CLI, Dashboard SOC Streamlit, Rapports Forensiques PDF."
    agenda(4, 0) = "05. Experimentation & Resultats": agenda(4, 1) = "Topologie Kali vs Windows, elimination des angles morts, benchmark chiffre."
    agenda(5, 0) = "06. Demonstration & Perspectives": agenda(5, 1) = "Scenarios live, competences consolidees et perspectives d'avenir."
    
    Dim rowIdx As Integer, colIdx As Integer, posX As Single, posY As Single
    For i = 0 To 5
        colIdx = i Mod 2
        rowIdx = i \\ 2
        posX = 50 + colIdx * 435
        posY = 110 + rowIdx * 135
        CreerCarte sld, posX, posY, 420, 120, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 15, posY + 15, 390, 30, agenda(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 15, posY + 50, 390, 60, agenda(i, 1), 11, False, C_TEXT_MUTED
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 3 : CONTEXTE OPERATIONNEL
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(3, ppLayoutBlank)
    CreerHeader sld, "Contexte Operationnel & Organisme d'Accueil", "01. Cadre du Projet"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Commune de Tetouan" & vbCrLf & vbCrLf & _
        "Cadre Institutionnel :" & vbCrLf & "- Division des Systemes d'Information de la Mairie." & vbCrLf & vbCrLf & _
        "Missions du Reseau :" & vbCrLf & "- Hebergement des applications metier administratives." & vbCrLf & _
        "- Echanges continus et connectivite inter-services." & vbCrLf & vbCrLf & _
        "Trafic Quotidien :" & vbCrLf & "- Flux heterogenes melant navigation web et bases de donnees.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Enjeux Cyber & Motivation" & vbCrLf & vbCrLf & _
        "Recrudescence des Scans Furtifs :" & vbCrLf & "- Cartographie silencieuse du parc sans declencher d'alerte." & vbCrLf & vbCrLf & _
        "Risque Critique de Deni de Service :" & vbCrLf & "- Menace de paralysie des services publics aux citoyens." & vbCrLf & vbCrLf & _
        "Besoin de Souverainete :" & vbCrLf & "- Solution legere, autonome et sans couts recurrents de licence.", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 4 : PROBLEMATIQUE NIDS
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(4, ppLayoutBlank)
    CreerHeader sld, "Problematique : Les Angles Morts des NIDS Traditionnels", "01. Cadre du Projet"
    CreerCarte sld, 50, 110, 275, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 65, 125, 245, 360, "NIDS a Signatures" & vbCrLf & vbCrLf & _
        "Exemples : Snort, Suricata." & vbCrLf & vbCrLf & _
        "Principe : Motifs exacts predefinis." & vbCrLf & vbCrLf & _
        "Faille Majeure :" & vbCrLf & "Inoperant face aux menaces Zero-Day jamais repertoriees.", 13, False, C_TEXT_DARK

    CreerCarte sld, 342, 110, 275, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 357, 125, 245, 360, "L'Angle Mort SYN Scan" & vbCrLf & vbCrLf & _
        "Le scan furtif interrompt le cycle par un paquet RST." & vbCrLf & vbCrLf & _
        "Aucune charge malveillante." & vbCrLf & vbCrLf & _
        "Resultat : Les pare-feux et NIDS restent aveugles face a l'attaque.", 13, False, C_DANGER

    CreerCarte sld, 635, 110, 275, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 650, 125, 245, 360, "Fatigue d'Alerte" & vbCrLf & vbCrLf & _
        "Seuils trop stricts = milliers de faux positifs." & vbCrLf & vbCrLf & _
        "Saturation des analystes du SOC municipal." & vbCrLf & vbCrLf & _
        "Necessite absolue d'une detection intelligente.", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 5 : SOLUTION NETSCAN
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(5, ppLayoutBlank)
    CreerHeader sld, "La Solution NetScan : Detection d'Anomalies par IA", "01. Cadre du Projet"
    CreerCarte sld, 50, 110, 860, 100, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 820, 70, "Changement de Paradigme : Au lieu de chercher des signatures connues, NetScan apprend statistiquement la normalite locale du reseau et isole mathematiquement tout profil aberrant.", 14, True, C_TEAL
    
    CreerCarte sld, 50, 230, 275, 270, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 65, 245, 245, 240, "100% Non Supervise" & vbCrLf & vbCrLf & "Aucune dependance envers des bases de donnees pre-etiquetees ou des historiques obsoletes.", 13, False, C_TEXT_DARK

    CreerCarte sld, 342, 230, 275, 270, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 357, 245, 245, 240, "Calibrate-Then-Monitor" & vbCrLf & vbCrLf & "Phase d'apprentissage passif (120 s) sur les flux reels locaux avant surveillance active.", 13, False, C_TEXT_DARK

    CreerCarte sld, 635, 230, 275, 270, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 650, 245, 245, 240, "Approche Bicouche" & vbCrLf & vbCrLf & "Couche 1 (unitaire par paquet) + Couche 2 comportementale (fenetre de 5 secondes).", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 6 : ALGORITHME ISOLATION FOREST
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(6, ppLayoutBlank)
    CreerHeader sld, "Fondements Theoriques : Algorithme Isolation Forest", "02. Fondements Theoriques"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Principe des iTrees" & vbCrLf & vbCrLf & _
        "Partitionnement recursif :" & vbCrLf & "- Decoupes orthogonales aleatoires de l'espace de donnees." & vbCrLf & vbCrLf & _
        "Axiome d'Isolation :" & vbCrLf & "- Les paquets normaux sont nombreux et regroupes (profondeur elevee)." & vbCrLf & _
        "- Les anomalies sont rares et isolees tres rapidement (faible profondeur).", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Atouts Cyberdefense" & vbCrLf & vbCrLf & _
        "Vitesse Maximale :" & vbCrLf & "- Complexite en O(n log n), ideale pour le flux continu." & vbCrLf & vbCrLf & _
        "Insensibilite a la Distribution :" & vbCrLf & "- Ne necessite aucune hypothese gaussienne." & vbCrLf & vbCrLf & _
        "Legerete Materielle :" & vbCrLf & "- S'execute sur machine standard sans GPU.", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 7 : MATHEMATIQUES IFOREST
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(7, ppLayoutBlank)
    CreerHeader sld, "Modelisation Mathematique & Scoring d'Anomalie", "02. Fondements Theoriques"
    CreerCarte sld, 50, 110, 860, 150, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 820, 120, "Formule du Score d'Anomalie (Liu et al., 2008) :" & vbCrLf & _
        "s(x, n) = 2 ^ ( - E(h(x)) / c(n) )" & vbCrLf & _
        "- E(h(x)) : Esperance de la profondeur d'isolation moyenne a travers tous les iTrees." & vbCrLf & _
        "- c(n) : Facteur de normalisation representant la longueur moyenne d'un echec d'arbre binaire.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 50, 280, 275, 220, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 65, 295, 245, 190, "s(x, n) -> 1" & vbCrLf & vbCrLf & "Profondeur E(h(x)) tres faible." & vbCrLf & "Anomalie critique averee (attaque).", 13, False, C_DANGER

    CreerCarte sld, 342, 280, 275, 220, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 357, 295, 245, 190, "s(x, n) -> 0.5" & vbCrLf & vbCrLf & "Profondeur moyenne nominale." & vbCrLf & "Trafic typique d'arriere-plan sain.", 13, False, C_TEXT_MUTED

    CreerCarte sld, 635, 280, 275, 220, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 650, 295, 245, 190, "Seuil = 0.60" & vbCrLf & vbCrLf & "Compromis optimal empirique." & vbCrLf & "Detection maximale et < 1.2% de faux positifs.", 13, False, C_SUCCESS

    ' -------------------------------------------------------------
    ' SLIDE 8 : BENCHMARK ALGORITHMIQUE (TABLEAU)
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(8, ppLayoutBlank)
    CreerHeader sld, "Benchmark Algorithmique : Pourquoi Isolation Forest ?", "02. Fondements Theoriques"
    
    Dim tblSld8 As Shape
    Set tblSld8 = sld.Shapes.AddTable(5, 4, 50, 110, 860, 380)
    RemplirTableau tblSld8, Array("Critere", "Isolation Forest (NetScan)", "One-Class SVM", "k-Means"), _
        Array( _
            Array("Complexite Temporelle", "O(n log n) - Ultra rapide", "O(n^2 a n^3) - Lourd", "O(n k i) - Moyen"), _
            Array("Sensibilite a la Dimension", "Faible (selection aleatoire)", "Elevee (fleau dimensionnel)", "Elevee (distances faussees)"), _
            Array("Hypothese de Distribution", "Aucune hypothese prealable", "Noyau gaussien complexe", "Suppose clusters spheriques"), _
            Array("Adaptation Temps Reel", "Optimale (faible memoire)", "Faible (inversion matricielle)", "Faible (sensible aux centres)") _
        )

    ' -------------------------------------------------------------
    ' SLIDE 9 : MENACE 1 - SYN STEALTH SCAN
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(9, ppLayoutBlank)
    CreerHeader sld, "Attaque Cible 1 : TCP SYN Stealth Scan (Nmap -sS)", "02. Fondements Theoriques"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Mecanisme de l'Attaque" & vbCrLf & vbCrLf & _
        "1. Emission du SYN :" & vbCrLf & "- Paquet envoye vers chaque port cible." & vbCrLf & vbCrLf & _
        "2. Reponse SYN-ACK :" & vbCrLf & "- Le serveur indique que le port est ouvert." & vbCrLf & vbCrLf & _
        "3. Rupture par Flag RST :" & vbCrLf & "- L'attaquant envoie immediatement un RST pour avorter la session.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Consequences Operationnelles" & vbCrLf & vbCrLf & _
        "Connexion Jamais Terminee :" & vbCrLf & "- Pas d'entree dans les logs applicatifs (Apache, Nginx)." & vbCrLf & vbCrLf & _
        "Cecite des Pare-feux :" & vbCrLf & "- Laisse passer le flux considere comme inoffensif." & vbCrLf & vbCrLf & _
        "Cartographie Complete :" & vbCrLf & "- Reussite de la reconnaissance adverse sans trace.", 13, False, C_DANGER

    ' -------------------------------------------------------------
    ' SLIDE 10 : MENACE 2 - SYN FLOOD
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(10, ppLayoutBlank)
    CreerHeader sld, "Attaque Cible 2 : SYN Flood (DDoS Volumetrique)", "02. Fondements Theoriques"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Mecanisme d'Inondation" & vbCrLf & vbCrLf & _
        "Inondation Massive :" & vbCrLf & "- Envoi de milliers de paquets SYN/seconde avec IP falsifiees." & vbCrLf & vbCrLf & _
        "Allocation Memoire Serveur :" & vbCrLf & "- Le serveur alloue des blocs TCB et attend en SYN_RECEIVED." & vbCrLf & vbCrLf & _
        "Attente sans Fin :" & vbCrLf & "- Le ACK final ne vient jamais.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Impact sur l'Infrastructure" & vbCrLf & vbCrLf & _
        "Saturation de la Backlog Queue :" & vbCrLf & "- La file d'attente sature en quelques secondes." & vbCrLf & vbCrLf & _
        "Deni de Service Total :" & vbCrLf & "- Rejet immediat de toutes les requetes citoyennes legitimes." & vbCrLf & vbCrLf & _
        "Paralysie Municipale :" & vbCrLf & "- Arret complet des services administratifs en ligne.", 13, False, C_DANGER

    ' -------------------------------------------------------------
    ' SLIDE 11 : ARCHITECTURE DU PIPELINE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(11, ppLayoutBlank)
    CreerHeader sld, "Architecture Globale : Le Pipeline Bicouche NetScan", "03. Architecture Systeme"
    
    Dim steps(0 To 4, 0 To 1) As String
    steps(0, 0) = "1. Ingestion": steps(0, 1) = "Capture Scapy & Npcap en mode Promiscuous."
    steps(1, 0) = "2. Extraction": steps(1, 1) = "Couche 1 (unitaire) et Couche 2 (macro 5s)."
    steps(2, 0) = "3. Inférence": steps(2, 1) = "Modèle Isolation Forest & Scoring d'anomalie."
    steps(3, 0) = "4. Décision": steps(3, 1) = "Matrice de qualification (Scan vs Flood)."
    steps(4, 0) = "5. Réponse": steps(4, 1) = "Alertes Discord, Dashboard SOC et PDF."
    
    For i = 0 To 4
        posX = 50 + i * 175
        CreerCarte sld, posX, 130, 165, 360, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 10, 145, 145, 40, steps(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 10, 195, 145, 280, steps(i, 1), 12, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 12 : COUCHE 1
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(12, ppLayoutBlank)
    CreerHeader sld, "Couche 1 : Analyse Microscopique Unitaire (Par Paquet)", "03. Architecture Systeme"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Caracteristiques Extraites" & vbCrLf & vbCrLf & _
        "- Protocole de transport (TCP = 6, UDP = 17, ICMP = 1)" & vbCrLf & _
        "- Taille du paquet (longueur de trame en octets)" & vbCrLf & _
        "- Intervalle inter-paquets (Delta t)" & vbCrLf & _
        "- Drapeaux TCP (SYN, ACK, RST, FIN)" & vbCrLf & _
        "- Indicateur de retransmission", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "La Limite de l'Analyse Unitaire" & vbCrLf & vbCrLf & _
        "Un paquet Nmap SYN pris individuellement :" & vbCrLf & _
        "- Mesure environ 60 octets (taille parfaitement legale)." & vbCrLf & _
        "- Possede des entetes valides." & vbCrLf & vbCrLf & _
        "Resultat : 0% de detection sur les scans de ports SYN furtifs !" & vbCrLf & vbCrLf & _
        "Conclusion : Il faut analyser le comportement dans le temps.", 13, False, C_DANGER

    ' -------------------------------------------------------------
    ' SLIDE 13 : COUCHE 2
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(13, ppLayoutBlank)
    CreerHeader sld, "Couche 2 : Analyse Comportementale par Micro-Fenetres (5s)", "03. Architecture Systeme"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Agregation par Fenetres de 5s" & vbCrLf & vbCrLf & _
        "- Volume global de paquets par fenetre." & vbCrLf & _
        "- Nombre de ports cibles uniques contactes." & vbCrLf & _
        "- Debit moyen et frequence d'arrivee." & vbCrLf & vbCrLf & _
        "Compromis ideal entre reactivite d'alerte et accumulation statistique.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Ratio de Dispersion des Ports (R)" & vbCrLf & vbCrLf & _
        "R = Ports Uniques / Paquets Totaux" & vbCrLf & vbCrLf & _
        "R -> 1 (Scan de Ports) :" & vbCrLf & "Beaucoup de ports contactes avec peu de paquets par port." & vbCrLf & vbCrLf & _
        "R -> 0 (SYN Flood / DDoS) :" & vbCrLf & "Enorme volume de paquets concentre sur un port unique.", 13, False, C_TEAL

    ' -------------------------------------------------------------
    ' SLIDE 14 : MATRICE DE DECISION (TABLEAU)
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(14, ppLayoutBlank)
    CreerHeader sld, "Matrice de Decision & Qualification des Menaces", "03. Architecture Systeme"
    Dim tblSld14 As Shape
    Set tblSld14 = sld.Shapes.AddTable(4, 4, 50, 110, 860, 380)
    RemplirTableau tblSld14, Array("Sequence Trafic", "Comportement Niveau 1", "Comportement Niveau 2 (5s)", "Decision NetScan"), _
        Array( _
            Array("Trafic Sain", "Trames TCP/UDP regulieres", "<= 4 ports, < 30 pkts / 5s", "Normal (s ~ 0.44)"), _
            Array("Scan Nmap (-sS)", "Taille legitime (60 B) -> Non detecte", "330+ ports uniques, Ratio R > 0.9", "ALERTE : Port Scan (s = 0.88)"), _
            Array("SYN Flood", "Paquets SYN identiques", "800+ paquets / 5s sur 1 port", "ALERTE : Flood / DDoS (s = 0.92)") _
        )

    ' -------------------------------------------------------------
    ' SLIDE 15 : STACK TECHNIQUE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(15, ppLayoutBlank)
    CreerHeader sld, "Stack Technologique & Outils", "04. Implementation Logicielle"
    Dim tools(0 To 5, 0 To 1) As String
    tools(0, 0) = "Python 3.11": tools(0, 1) = "Langage coeur pour le prototypage rapide et l'ecosysteme securite."
    tools(1, 0) = "Scapy & Npcap": tools(1, 1) = "Dissection reseau et capture bas niveau en mode Promiscuous."
    tools(2, 0) = "Scikit-learn": tools(2, 1) = "Modele Isolation Forest optimise pour l'inference non supervisee."
    tools(3, 0) = "Pandas & NumPy": tools(3, 1) = "Vectorisation rapide des calculs statistiques sur les fenetres 5s."
    tools(4, 0) = "Streamlit": tools(4, 1) = "Console SOC web interactive pour la visualisation en temps reel."
    tools(5, 0) = "ReportLab & Discord": tools(5, 1) = "Generation des rapports PDF d'incident et alertes webhook directes."
    
    For i = 0 To 5
        colIdx = i Mod 3
        rowIdx = i \\ 3
        posX = 50 + colIdx * 290
        posY = 120 + rowIdx * 190
        CreerCarte sld, posX, posY, 280, 175, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 15, posY + 15, 250, 30, tools(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 15, posY + 55, 250, 110, tools(i, 1), 12, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 16 : 4 MODULES LOGICIELS
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(16, ppLayoutBlank)
    CreerHeader sld, "Les 4 Briques Logicielles Developpees", "04. Implementation Logicielle"
    Dim mods(0 To 3, 0 To 1) As String
    mods(0, 0) = "netscan.py (Orchestrateur CLI)": mods(0, 1) = "Moteur console sous Linux/Windows. Modes Demo, PCAP et Live Sniffing avec auto-calibration de 120 secondes."
    mods(1, 0) = "dashboard.py (Console SOC Web)": mods(1, 1) = "Interface de supervision sous Streamlit : KPIs, scores d'anomalie, timeline des alertes et traffic live."
    mods(2, 0) = "report_generator.py (Forensics)": mods(2, 1) = "Exportateur automatique de syntheses d'incident au format PDF certifie avec IP suspectes et recommandations."
    mods(3, 0) = "test_smoke.py (Assurance Qualite)": mods(3, 1) = "Banc de tests automatises validant l'integrite du pipeline avant le deploiement sur site."
    
    For i = 0 To 3
        colIdx = i Mod 2
        rowIdx = i \\ 2
        posX = 50 + colIdx * 435
        posY = 120 + rowIdx * 190
        CreerCarte sld, posX, posY, 420, 175, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 15, posY + 15, 390, 30, mods(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 15, posY + 55, 390, 110, mods(i, 1), 12, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 17 : BANC D'ESSAI
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(17, ppLayoutBlank)
    CreerHeader sld, "Banc d'Essai Experimental & Topologie", "05. Experimentation & Resultats"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Postes d'Experimentation" & vbCrLf & vbCrLf & _
        "Poste 1 : Attaquant (Kali Linux)" & vbCrLf & _
        "- IP : 192.168.1.50" & vbCrLf & _
        "- Outils : Nmap (-sS) et Hping3 (--flood)" & vbCrLf & vbCrLf & _
        "Poste 2 : Sonde NetScan (Windows)" & vbCrLf & _
        "- IP : 192.168.1.100" & vbCrLf & _
        "- Ecoute passive en mode Promiscuous" & vbCrLf & vbCrLf & _
        "Poste 3 : Cible Metasploitable", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Protocole de Validation" & vbCrLf & vbCrLf & _
        "1. Validation sur Captures PCAP :" & vbCrLf & _
        "- Echantillons d'attaques certifiees et replays." & vbCrLf & vbCrLf & _
        "2. Validation in situ en direct :" & vbCrLf & _
        "- Trafic reel au sein de la Commune de Tetouan." & vbCrLf & vbCrLf & _
        "Condition de Realisme :" & vbCrLf & _
        "- Attaques injectees au milieu d'un trafic d'arriere-plan sain.", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 18 : RESULTATS EXP (TABLEAU 5.2)
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(18, ppLayoutBlank)
    CreerHeader sld, "Resultats Experimentaux & Benchmark Comparatif", "05. Experimentation & Resultats"
    Dim tblSld18 As Shape
    Set tblSld18 = sld.Shapes.AddTable(6, 4, 50, 110, 860, 380)
    RemplirTableau tblSld18, Array("Critere", "Modele Baseline (Unitaire)", "NetScan (Bicouche)", "Gain Operationnel"), _
        Array( _
            Array("Detection Scan Nmap (-sS)", "0% (Angle mort total)", "100% (Isole avec succes)", "Angle mort elimine"), _
            Array("Detection SYN Flood", "Partielle", "100% (Volume detecte)", "Neutralisation immediate"), _
            Array("Taux de Faux Positifs", "12.4% (Trafic web bruite)", "< 1.2% (Grace au ratio R)", "Divise par 10"), _
            Array("Temps Analyse (4 100 trames)", "4.8 secondes", "1.9 seconde (Vectorise)", "Vitesse multipliee par 2.5"), _
            Array("Explicabilite de Menace", "Simple 'Anormal'", "Port Scan ou Flood precis", "Gain de temps pour le SOC") _
        )

    ' -------------------------------------------------------------
    ' SLIDE 19 : DEMONSTRATION LIVE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(19, ppLayoutBlank)
    CreerHeader sld, "Demonstration Pratique : Scenarios Operationnels", "06. Demonstration Live"
    Dim demo(0 To 3, 0 To 1) As String
    demo(0, 0) = "Etape 1 : Demarrage": demo(0, 1) = "Lancement de netscan.py --live et phase passive de calibration (120 s)."
    demo(1, 0) = "Etape 2 : Scan Furtif": demo(1, 1) = "Attaque Nmap SYN furtive depuis Kali -> Alerte en < 5s et notification Discord."
    demo(2, 0) = "Etape 3 : SYN Flood": demo(2, 1) = "Attaque massive via Hping3 -> Detection volumetrique avec score s = 0.92."
    demo(3, 0) = "Etape 4 : SOC & Rapport": demo(3, 1) = "Supervision sur Streamlit et generation du rapport d'incident PDF."
    
    For i = 0 To 3
        posX = 50 + i * 220
        CreerCarte sld, posX, 130, 205, 360, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 15, 145, 175, 40, demo(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 15, 200, 175, 270, demo(i, 1), 12, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 20 : BILAN DU STAGE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(20, ppLayoutBlank)
    CreerHeader sld, "Bilan du Projet & Competences Consolidees", "07. Bilan & Perspectives"
    CreerCarte sld, 50, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 70, 125, 380, 360, "Competences Reseaux & Securite" & vbCrLf & vbCrLf & _
        "- Analyse approfondie du cycle TCP (Handshake, flags)." & vbCrLf & _
        "- Pratique d'outils offensifs sous Kali (Nmap, Hping3)." & vbCrLf & _
        "- Conception d'architectures SOC, NIDS et alerting temps reel.", 13, False, C_TEXT_DARK
        
    CreerCarte sld, 490, 110, 420, 390, C_CARD_BG, C_BORDER
    CreerZoneTexte sld, 510, 125, 380, 360, "Competences IA & Developpement" & vbCrLf & vbCrLf & _
        "- Maitrise du Machine Learning non supervise (Isolation Forest)." & vbCrLf & _
        "- Optimisation et vectorisation des flux continus via Pandas." & vbCrLf & _
        "- Developpement full-stack Python (CLI, Web Streamlit, PDF).", 13, False, C_TEXT_DARK

    ' -------------------------------------------------------------
    ' SLIDE 21 : DIFFICULTES & SOLUTIONS
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(21, ppLayoutBlank)
    CreerHeader sld, "Difficultes Rencontrees & Solutions Apportees", "07. Bilan & Perspectives"
    Dim diff(0 To 2, 0 To 1) As String
    diff(0, 0) = "1. Bruit Reseau & Absence d'Etiquetage": diff(0, 1) = "Defi : Comment calibrer un modele sans donnees pre-etiquetees ?" & vbCrLf & "Solution : Mise en place du protocole Calibrate-Then-Monitor (120 s d'auto-apprentissage in situ)."
    diff(1, 0) = "2. Capture Haute Frequence en Temps Reel": diff(1, 1) = "Defi : Risque de latence lors du traitement paquet par paquet." & vbCrLf & "Solution : Vectorisation des calculs par fenetres de 5s via Pandas (gain de vitesse x2.5)."
    diff(2, 0) = "3. Elimination des Faux Positifs Web": diff(2, 1) = "Defi : Le surf web standard ouvre plusieurs connexions simultanees." & vbCrLf & "Solution : Ratio de Dispersion des Ports (R) separant clairement trafic sain et scans."
    
    For i = 0 To 2
        posY = 115 + i * 125
        CreerCarte sld, 50, posY, 860, 115, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, 70, posY + 10, 820, 25, diff(i, 0), 13, True, C_TEAL
        CreerZoneTexte sld, 70, posY + 40, 820, 65, diff(i, 1), 11, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 22 : PERSPECTIVES
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(22, ppLayoutBlank)
    CreerHeader sld, "Perspectives d'Evolution du Systeme", "07. Bilan & Perspectives"
    Dim pers(0 To 2, 0 To 1) As String
    pers(0, 0) = "Reponse Active (NIPS)": pers(0, 1) = "Blocage dynamique automatise des IP hostiles via API Pare-feu Windows ou eBPF sous Linux."
    pers(1, 0) = "Integration SIEM": pers(1, 1) = "Connecteurs standardises pour exporter les alertes vers Wazuh, Elastic SIEM ou Splunk."
    pers(2, 0) = "Inspection Flux TLS": pers(2, 1) = "Empreinte JA3/JA3S pour detecter les flux hostiles dans le trafic chiffre HTTPS."
    
    For i = 0 To 2
        posX = 50 + i * 290
        CreerCarte sld, posX, 130, 280, 360, C_CARD_BG, C_BORDER
        CreerZoneTexte sld, posX + 15, 145, 250, 40, pers(i, 0), 14, True, C_NAVY_DARK
        CreerZoneTexte sld, posX + 15, 200, 250, 270, pers(i, 1), 12, False, C_TEXT_DARK
    Next i

    ' -------------------------------------------------------------
    ' SLIDE 23 : CONCLUSION & MERCI
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(23, ppLayoutBlank)
    CreerFond sld, C_NAVY_DARK
    CreerBarreLaterale sld, 40, 100, 8, 340, C_BLUE_CYBER
    
    CreerZoneTexte sld, 60, 100, 840, 40, "CONCLUSION GENERALE", 14, True, C_BLUE_CYBER
    CreerZoneTexte sld, 60, 145, 840, 80, "NetScan demontre la viabilite et la puissance du Machine Learning Non Supervise pour securiser les reseaux face aux menaces furtives sans signatures.", 20, True, C_WHITE
    
    CreerCarte sld, 60, 250, 840, 200, RGB(30, 41, 59), C_BLUE_CYBER
    Dim thBox As Shape
    Set thBox = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 80, 280, 800, 140)
    thBox.TextFrame.WordWrap = msoTrue
    thBox.TextFrame.TextRange.Text = "Merci pour votre aimable attention !" & vbCrLf & vbCrLf & _
                                    "Avez-vous des questions ?" & vbCrLf & vbCrLf & _
                                    "Mohamed Reda QIYAOUI | EST Tetouan | 2025/2026"
    thBox.TextFrame.TextRange.Paragraphs(1).Font.Size = 22
    thBox.TextFrame.TextRange.Paragraphs(1).Font.Bold = msoTrue
    thBox.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = C_WHITE
    thBox.TextFrame.TextRange.Paragraphs(1).ParagraphFormat.Alignment = ppAlignCenter
    thBox.TextFrame.TextRange.Paragraphs(2).Font.Size = 16
    thBox.TextFrame.TextRange.Paragraphs(2).Font.Color.RGB = C_BLUE_CYBER
    thBox.TextFrame.TextRange.Paragraphs(2).ParagraphFormat.Alignment = ppAlignCenter

    MsgBox "Presentation de Soutenance NetScan generee avec succes (23 diapositives) !", vbInformation, "NetScan - EST Tetouan"
End Sub

' -----------------------------------------------------------------
' FONCTIONS UTILITAIRES GRAPHIQUES
' -----------------------------------------------------------------
Private Sub CreerFond(sld As Slide, color As Long)
    Dim bg As Shape
    Set bg = sld.Shapes.AddShape(msoShapeRectangle, 0, 0, 960, 540)
    bg.Fill.Solid
    bg.Fill.ForeColor.RGB = color
    bg.Line.Visible = msoFalse
End Sub

Private Sub CreerBarreLaterale(sld As Slide, left As Single, top As Single, width As Single, height As Single, color As Long)
    Dim bar As Shape
    Set bar = sld.Shapes.AddShape(msoShapeRectangle, left, top, width, height)
    bar.Fill.Solid
    bar.Fill.ForeColor.RGB = color
    bar.Line.Visible = msoFalse
End Sub

Private Sub CreerHeader(sld As Slide, titre As String, categorie As String)
    Dim h As Shape, l As Shape
    Set h = sld.Shapes.AddShape(msoShapeRectangle, 0, 0, 960, 80)
    h.Fill.Solid
    h.Fill.ForeColor.RGB = C_NAVY_DARK
    h.Line.Visible = msoFalse
    
    Set l = sld.Shapes.AddShape(msoShapeRectangle, 0, 80, 960, 4)
    l.Fill.Solid
    l.Fill.ForeColor.RGB = C_BLUE_CYBER
    l.Line.Visible = msoFalse
    
    CreerZoneTexte sld, 50, 10, 860, 20, UCase(categorie), 10, True, C_BLUE_CYBER
    CreerZoneTexte sld, 50, 30, 860, 40, titre, 18, True, C_WHITE
End Sub

Private Function CreerCarte(sld As Slide, left As Single, top As Single, width As Single, height As Single, fillColor As Long, borderColor As Long) As Shape
    Dim c As Shape
    Set c = sld.Shapes.AddShape(msoShapeRoundedRectangle, left, top, width, height)
    c.Fill.Solid
    c.Fill.ForeColor.RGB = fillColor
    c.Line.ForeColor.RGB = borderColor
    c.Line.Weight = 1.2
    Set CreerCarte = c
End Function

Private Sub CreerZoneTexte(sld As Slide, left As Single, top As Single, width As Single, height As Single, texte As String, fontSize As Single, isBold As Boolean, fontColor As Long)
    Dim tb As Shape
    Set tb = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, left, top, width, height)
    tb.TextFrame.WordWrap = msoTrue
    tb.TextFrame.TextRange.Text = texte
    tb.TextFrame.TextRange.Font.Name = "Segoe UI"
    tb.TextFrame.TextRange.Font.Size = fontSize
    tb.TextFrame.TextRange.Font.Bold = IIf(isBold, msoTrue, msoFalse)
    tb.TextFrame.TextRange.Font.Color.RGB = fontColor
End Sub

Private Sub RemplirTableau(tblShp As Shape, headers As Variant, rowsData As Variant)
    Dim t As Table
    Set t = tblShp.Table
    Dim r As Integer, c As Integer
    
    ' Entetes
    For c = 0 To UBound(headers)
        t.Cell(1, c + 1).Shape.Fill.Solid
        t.Cell(1, c + 1).Shape.Fill.ForeColor.RGB = IIf(c = 1, C_BLUE_CYBER, C_NAVY_DARK)
        With t.Cell(1, c + 1).Shape.TextFrame.TextRange
            .Text = headers(c)
            .Font.Name = "Segoe UI"
            .Font.Size = 12
            .Font.Bold = msoTrue
            .Font.Color.RGB = C_WHITE
        End With
    Next c
    
    ' Donnees
    For r = 0 To UBound(rowsData)
        For c = 0 To UBound(rowsData(r))
            t.Cell(r + 2, c + 1).Shape.Fill.Solid
            t.Cell(r + 2, c + 1).Shape.Fill.ForeColor.RGB = IIf(r Mod 2 = 0, RGB(241, 245, 249), C_WHITE)
            With t.Cell(r + 2, c + 1).Shape.TextFrame.TextRange
                .Text = rowsData(r)(c)
                .Font.Name = "Segoe UI"
                .Font.Size = 11
                .Font.Color.RGB = C_TEXT_DARK
                If c = 1 Or c = 3 Then .Font.Bold = msoTrue
            End With
        Next c
    Next r
End Sub
'''

# Écriture du fichier VBA en ANSI/cp1252 pour compatibilité parfaite avec l'éditeur VBA Office
with open(BAS_OUT, "w", encoding="cp1252", errors="replace") as f:
    f.write(vba_code)

print(f"[OK] Fichier Macro VBA généré avec succès : {BAS_OUT}")
