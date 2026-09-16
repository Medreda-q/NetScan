# -*- coding: utf-8 -*-
"""
Reconstruit la présentation enrichie avec TOUTES les fonctionnalités demandées :
- Les Deux Modes d'Opération (Mode 1 Forensique PCAP vs Mode 2 Live Sniffing)
- Les Fonctionnalités Clés du Dashboard SOC Streamlit
- Le Moteur Forensique & Génération de Rapports NIST
- La Traçabilité et la Génération de Commandes de Blocage Pare-Feu
Le tout en conservant scrupuleusement le design, la disposition et le template de l'utilisateur.
"""

import sys, os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

SRC = r"C:\Users\DevLab\Desktop\Soutenance\Conception-et-developpement-dun-systeme-intelligent-de-detection-danomalies-reseau (1).pptx"
DST = r"C:\Users\DevLab\Desktop\Soutenance\Soutenance_NetScan_Version_Finale.pptx"

prs = pptx.Presentation(SRC)
layout = prs.slide_layouts[0]

LEFT_STD   = 719814
TOP_TIT_STD= 800000
WIDTH_STD  = 10752067
H_TIT_STD  = 642739
TOP_TXT_STD= 1600000
H_TXT_STD  = 4800000

def ajouter_slide_texte(titre, paragraphes):
    s = prs.slides.add_slide(layout)
    tb_t = s.shapes.add_textbox(LEFT_STD, TOP_TIT_STD, WIDTH_STD, H_TIT_STD)
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = titre
    p_t.font.bold = True
    p_t.font.size = Pt(28)
    
    tb_c = s.shapes.add_textbox(LEFT_STD, TOP_TXT_STD, WIDTH_STD, H_TXT_STD)
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    for i, p_info in enumerate(paragraphes):
        p = tf_c.add_paragraph() if i > 0 else tf_c.paragraphs[0]
        txt, bold, size, space_after, space_before = p_info
        p.text = txt
        p.font.bold = bold
        p.font.size = Pt(size)
        if space_after:
            p.space_after = Pt(space_after)
        if space_before:
            p.space_before = Pt(space_before)
    return s

def ajouter_slide_tableau(titre, headers, rows):
    s = prs.slides.add_slide(layout)
    tb_t = s.shapes.add_textbox(LEFT_STD, TOP_TIT_STD, WIDTH_STD, H_TIT_STD)
    tf_t = tb_t.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = titre
    p_t.font.bold = True
    p_t.font.size = Pt(28)
    
    num_rows = len(rows) + 1
    num_cols = len(headers)
    tbl_shp = s.shapes.add_table(num_rows, num_cols, LEFT_STD, TOP_TXT_STD, WIDTH_STD, 4500000)
    tbl = tbl_shp.table
    col_w = WIDTH_STD // num_cols
    for c in range(num_cols):
        tbl.columns[c].width = col_w
    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(14)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(12)
            if c == 1 or c == num_cols - 1:
                p.font.bold = True
    return s

print(f"Présentation originale : {len(prs.slides)} diapositives.")

# -------------------------------------------------------------
# 1. SOMMAIRE GÉNÉRAL
# -------------------------------------------------------------
ajouter_slide_texte("Plan de la Présentation (Sommaire)", [
    ("01. Cadre Académique & Problématique Opérationnelle", True, 18, 4, 6),
    ("Contexte institutionnel à la Commune de Tétouan et cécité des NIDS traditionnels face aux scans furtifs.", False, 14, 10, 0),
    ("02. Fondements Théoriques & Algorithme Isolation Forest", True, 18, 4, 6),
    ("Principes des iTrees, modélisation mathématique du score s(x,n) et benchmark comparatif vs SVM/K-Means.", False, 14, 10, 0),
    ("03. Architecture Système, Modes d'Opération & Dual-Layer", True, 18, 4, 6),
    ("Les deux modes d'ingestion (PCAP vs Live), Couche 1 unitaire, Couche 2 macroscopique et Ratio de dispersion R.", False, 14, 10, 0),
    ("04. Implémentation Logicielle & Fonctionnalités Avancées", True, 18, 4, 6),
    ("Dashboard SOC Streamlit, matrice 2D de dispersion, moteur forensique PDF et commandes de blocage actif.", False, 14, 10, 0),
    ("05. Expérimentation, Résultats Chiffrés & Benchmark", True, 18, 4, 6),
    ("Banc d'essai Kali vs Windows, 100% de détection, division par 10 des faux positifs et vitesse x2.5.", False, 14, 10, 0),
    ("06. Démonstration Live, Bilan & Perspectives d'Évolution", True, 18, 4, 6),
    ("Scénarios opérationnels en direct, bilan des compétences acquises et perspectives (NIPS eBPF, SIEM).", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 2. CONTEXTE COMMUNE DE TÉTOUAN
# -------------------------------------------------------------
ajouter_slide_texte("Contexte Opérationnel : Commune de Tétouan", [
    ("Organisme d'Accueil :", True, 18, 4, 4),
    ("Division des Systèmes d'Information et de la Transformation Numérique de la Commune de Tétouan.", False, 15, 10, 0),
    ("Missions & Environnement Réseau Municipal :", True, 18, 4, 4),
    ("- Gestion de l'infrastructure réseau reliant l'ensemble des divisions communales.", False, 14, 4, 0),
    ("- Hébergement des applications métier administratives et des portails de services aux citoyens.", False, 14, 4, 0),
    ("- Trafic hétérogène et bruité mêlant navigation web, flux de bases de données et accès distants.", False, 14, 12, 0),
    ("Enjeux de Sécurité Défensive :", True, 18, 4, 4),
    ("- Recrudescence des scans de reconnaissance silencieux cartographiant les failles du parc sans alerte.", False, 14, 4, 0),
    ("- Risque de paralysie des services communaux par inondation volumétrique (SYN Flood / DDoS).", False, 14, 4, 0),
    ("- Nécessité absolue d'une solution souveraine, temps réel, légère et sans surcoût de licence logicielle.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 3. FORMULATION MATHÉMATIQUE IFOREST
# -------------------------------------------------------------
ajouter_slide_texte("Modélisation Mathématique & Scoring d'Anomalie", [
    ("Formulation du Score d'Anomalie (Liu et al., 2008) :", True, 18, 6, 4),
    ("s(x, n) = 2 ^ ( - E(h(x)) / c(n) )", True, 20, 10, 0),
    ("- E(h(x)) : Espérance de la profondeur moyenne de l'échantillon x à travers l'ensemble des arbres d'isolation.", False, 14, 4, 0),
    ("- c(n) : Facteur de normalisation représentant la longueur moyenne d'un échec de recherche dans un arbre binaire pour n paquets :", False, 14, 4, 0),
    ("  c(n) = 2 * ln(n - 1) + 0.5772156649 - (2 * (n - 1) / n)", False, 13, 14, 0),
    ("Interprétation Décisionnelle :", True, 18, 6, 4),
    ("- Si s(x, n) -> 1 : Profondeur très courte -> L'instance est isolée quasi-instantanément -> ANOMALIE HOSTILE AVÉRÉE.", False, 14, 4, 0),
    ("- Si s(x, n) -> 0.5 : Profondeur moyenne -> Comportement homogène -> TRAFIC NOMINAL SAIN.", False, 14, 4, 0),
    ("- Seuil Décisionnel Opérationnel fixé à tau = 0.60 pour un équilibre optimal sensibilité / faux positifs.", True, 14, 8, 0)
])

# -------------------------------------------------------------
# 4. BENCHMARK ALGORITHMIQUE (TABLEAU)
# -------------------------------------------------------------
ajouter_slide_tableau(
    "Benchmark Algorithmique : Pourquoi Isolation Forest ?",
    ["Critère d'Évaluation", "Isolation Forest (NetScan)", "One-Class SVM", "k-Means Anomaly"],
    [
        ["Complexité Temporelle", "O(n · log n) — Ultra-rapide", "O(n² à n³) — Lourd", "O(n · k · i) — Moyen"],
        ["Sensibilité à la Dimension", "Faible (sélection aléatoire)", "Élevée (fléau dimensionnel)", "Élevée (distances déformées)"],
        ["Hypothèse de Distribution", "Aucune hypothèse préalable", "Nécessite réglage noyau gaussien", "Suppose clusters sphériques"],
        ["Adaptation au Temps Réel", "Optimale (faible mémoire)", "Faible (inversion matricielle)", "Faible (sensible aux centres)"]
    ]
)

# -------------------------------------------------------------
# 5. LES DEUX MODES D'OPÉRATION (LA SLIDE DES MODES DEMANDÉE !)
# -------------------------------------------------------------
ajouter_slide_texte("Les Deux Modes d'Opération de NetScan", [
    ("NetScan implémente une stratégie d'ingestion bimodale pour s'adapter à tous les besoins :", True, 16, 10, 4),
    ("Mode 1 : Analyse Forensique Hors-Ligne (.pcap / .pcapng)", True, 18, 4, 4),
    ("- Finalité : Audit post-incident, investigation forensique et rejeu d'attaques enregistrées sans toucher à la production.", False, 14, 4, 0),
    ("- Moteur Hybride : Parsing séquentiel via Pyshark (analyseur natif Wireshark/TShark).", False, 14, 4, 0),
    ("- Mécanisme de Secours (Fallback) : Basculement transparent et automatique sous Scapy si TShark est indisponible.", False, 14, 14, 0),
    ("Mode 2 : Surveillance Directe en Temps Réel (Live Sniffing)", True, 18, 4, 4),
    ("- Finalité : Détection active et protection continue du réseau municipal in situ.", False, 14, 4, 0),
    ("- Capture Passive Promiscuous : Écoute bas niveau sur interfaces locales via sockets bruts et driver Npcap.", False, 14, 4, 0),
    ("- Protocole Calibrate-Then-Monitor : Phase passive de 120s pour apprendre l'empreinte locale, puis surveillance active.", False, 14, 4, 0),
    ("- Alerting Instantané : Notification immédiate sous Discord en moins de 5 secondes dès dépassement du seuil tau = 0.60.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 6. FONCTIONNALITÉS CLÉS DU DASHBOARD SOC (STREAMLIT)
# -------------------------------------------------------------
ajouter_slide_texte("Fonctionnalités Clés du Tableau de Bord SOC (Streamlit)", [
    ("Une console d'analyse interactive pensée pour les analystes de sécurité du SOC :", True, 16, 10, 4),
    ("1. Sélecteur de Mode Supérieur :", True, 17, 3, 3),
    ("Basculement instantané d'un clic entre l'analyse forensique d'un fichier .pcap et la surveillance Live en direct.", False, 14, 8, 0),
    ("2. Cartes de Synthèse KPI en Temps Réel :", True, 17, 3, 3),
    ("Affichage dynamique du volume total de paquets examinés, trames saines, paquets suspects et ratio moyen de dispersion.", False, 14, 8, 0),
    ("3. Matrice de Dispersion Comportementale 2D (Volume vs Ports) :", True, 17, 3, 3),
    ("Scatter plot bidimensionnel révélant immédiatement les anomalies : les scans Nmap se projettent en haut à droite (dispersion maximale), les DDoS en haut à gauche (volume extrême sur port unique) et le trafic sain en bas.", False, 14, 8, 0),
    ("4. Inspecteur Forensique de Trames & Chronologie :", True, 17, 3, 3),
    ("Tableau filtrable par adresse IP, port et drapeau TCP avec horodatage précis à la milliseconde pour analyse microscopique.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 7. FORENSICS, TRAÇABILITÉ & COMMANDES DE BLOCAGE
# -------------------------------------------------------------
ajouter_slide_texte("Moteur Forensique, Traçabilité & Blocage Pare-Feu", [
    ("Moteur Exécutif de Rapports d'Incident (report_generator.py) :", True, 18, 4, 4),
    ("- Génération automatisée d'un rapport complet d'incident conforme aux standards de gouvernance documentaire.", False, 14, 4, 0),
    ("- Synthèse Managériale : Résumé exécutif non technique destiné à la direction et au RSSI.", False, 14, 4, 0),
    ("- Fiche Technique d'Audit : Top 30 des fenêtres compromises, horodatage UTC, adresses IP sources et ports ciblés.", False, 14, 4, 0),
    ("- Recommandations de Durcissement calquées sur les guides NIST SP 800-61 et CIS Controls.", False, 14, 12, 0),
    ("Journalisation Sécurisée & Génération de Commandes de Blocage :", True, 18, 4, 4),
    ("- Persistance locale atomique de chaque alerte dans un journal d'audit sécurisé (alerts_history.json).", False, 14, 4, 0),
    ("- Génération Automatique des Commandes de Blocage Pare-Feu à la volée :", True, 14, 4, 0),
    ("  * Sous Linux : iptables -A INPUT -s <IP_Attaquant> -j DROP", False, 13, 3, 0),
    ("  * Sous Windows : netsh advfirewall firewall add rule name='NetScan_Block' dir=in action=block remoteip=<IP_Attaquant>", False, 13, 8, 0)
])

# -------------------------------------------------------------
# 8. STACK TECHNOLOGIQUE COMPLÈTE
# -------------------------------------------------------------
ajouter_slide_texte("Stack Technologique & Écosystème Logiciel", [
    ("Architecture Modulaire 100% Python :", True, 18, 6, 4),
    ("- Python 3.11 : Cœur du système garantissant modularité, rapidité de prototypage et maintenance aisée.", False, 14, 6, 0),
    ("- Scapy 2.5 & Driver Npcap : Ingestion réseau bas niveau, écoute passive Promiscuous et décodage précis des trames.", False, 14, 6, 0),
    ("- Pyshark / TShark : Moteur forensique haute fidélité pour l'analyse rétroactive de gros volumes PCAP/PCAPNG.", False, 14, 6, 0),
    ("- Scikit-learn : Implémentation optimisée de l'algorithme Isolation Forest pour l'inférence non supervisée.", False, 14, 6, 0),
    ("- Pandas & NumPy : Vectorisation haute performance des calculs statistiques sur les fenêtres glissantes de 5 secondes.", False, 14, 6, 0),
    ("- Streamlit & Webhooks Discord : Console SOC interactive et notification instantanée des équipes d'astreinte.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 9. LES 4 BRIQUES LOGICIELLES DU PROJET
# -------------------------------------------------------------
ajouter_slide_texte("Suite Logicielle NetScan : 4 Briques Développées", [
    ("1. Orchestrateur CLI (netscan.py) :", True, 17, 3, 3),
    ("Cœur exécutable console (Linux Kali / Windows). Supporte le mode Démo synthétique, l'analyse PCAP et le Live Sniffing avec phase passive d'auto-calibration (120 secondes).", False, 13, 10, 0),
    ("2. Console de Supervision SOC Web (dashboard.py) :", True, 17, 3, 3),
    ("Interface graphique Streamlit offrant les vues KPIs, matrices de dispersion comportementale 2D et historique d'audit.", False, 13, 10, 0),
    ("3. Moteur Forensique & Générateur PDF (report_generator.py) :", True, 17, 3, 3),
    ("Module automatisant l'édition des rapports d'incident au format PDF certifié avec recommandations NIST SP 800-61.", False, 13, 10, 0),
    ("4. Suite d'Assurance Qualité Logicielle (test_smoke.py) :", True, 17, 3, 3),
    ("Banc de tests automatisés (CI/CD) validant la conformité mathématique de l'IA et l'intégrité mémoire avant déploiement.", False, 13, 8, 0)
])

# -------------------------------------------------------------
# 10. BANC D'ESSAI EXPÉRIMENTAL
# -------------------------------------------------------------
ajouter_slide_texte("Banc d'Essai Expérimental & Topologie de Test", [
    ("Topologie Virtualisée & Physique :", True, 18, 4, 4),
    ("- Poste 1 : Attaquant / Audit (Kali Linux, IP : 192.168.1.50) équipé de Nmap (-sS) et Hping3 (--flood -S).", False, 14, 4, 0),
    ("- Poste 2 : Sonde & Supervision (Windows, IP : 192.168.1.100) exécutant NetScan en écoute passive directe (Npcap).", False, 14, 4, 0),
    ("- Poste 3 : Serveur Cible Metasploitable hébergeant des services applicatifs (HTTP, SSH, MySQL, FTP).", False, 14, 12, 0),
    ("Protocole Rigoureux de Test :", True, 18, 4, 4),
    ("- Double validation : sur captures PCAP certifiées d'attaques et in situ en temps réel sur les flux de la Commune de Tétouan.", False, 14, 4, 0),
    ("- Injection d'attaques au milieu d'un trafic d'arrière-plan réel et bruité pour prouver la résistance aux faux positifs.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 11. RÉSULTATS CHIFFRÉS & BENCHMARK (TABLEAU 5.2)
# -------------------------------------------------------------
ajouter_slide_tableau(
    "Résultats Expérimentaux & Analyse Comparative (Tableau 5.2)",
    ["Critère d'Évaluation", "Modèle Baseline (Unitaire)", "NetScan (Architecture Bicouche)", "Gain Opérationnel"],
    [
        ["Détection Scan Nmap (-sS)", "0% (Angle mort total)", "100% (Fenêtres isolées avec succès)", "Élimination totale de l'angle mort"],
        ["Détection SYN Flood (DDoS)", "Partielle (selon la taille)", "100% (Volume exceptionnel détecté)", "Identification immédiate de l'attaque"],
        ["Taux de Faux Positifs", "12.4% (Trafic web bruité)", "< 1.2% (Grâce au ratio de dispersion R)", "Divisé par 10 (Fin fatigue d'alerte)"],
        ["Temps d'Analyse (4 100 trames)", "4.8 secondes", "1.9 seconde (Optimisation Pandas)", "Vitesse multipliée par 2.5"],
        ["Explicabilité de l'Anomalie", "Simple label 'Anormal'", "Précise (Port Scan furtif ou DDoS)", "Gain décisionnel majeur pour le SOC"]
    ]
)

# -------------------------------------------------------------
# 12. DÉROULEMENT DE LA DÉMO LIVE
# -------------------------------------------------------------
ajouter_slide_texte("Démonstration Pratique : Déroulement Opérationnel", [
    ("Scénario 1 : Lancement & Calibration Passive", True, 17, 3, 3),
    ("Démarrage de netscan.py en mode écoute directe (--live). Observation de la phase d'apprentissage passif (120 s).", False, 13, 10, 0),
    ("Scénario 2 : Injection d'un Scan TCP SYN Furtif", True, 17, 3, 3),
    ("Exécution de nmap -sS depuis Kali Linux. Détection en moins de 5 secondes, ratio R > 0.90 et notification Discord immédiate.", False, 13, 10, 0),
    ("Scénario 3 : Inondation Volumétrique SYN Flood", True, 17, 3, 3),
    ("Lancement d'une salve hping3 --flood -S. Détection macroscopique instantanée avec score d'anomalie culminant à 0.92.", False, 13, 10, 0),
    ("Scénario 4 : Supervision SOC, Forensics & Rapport", True, 17, 3, 3),
    ("Exploration sur le Dashboard Streamlit, affichage des règles de blocage pare-feu et génération du rapport PDF certifié.", False, 13, 8, 0)
])

# -------------------------------------------------------------
# 13. BILAN DU STAGE & COMPÉTENCES
# -------------------------------------------------------------
ajouter_slide_texte("Bilan du Stage & Compétences Consolidées", [
    ("Compétences en Réseaux & Cyberdéfense :", True, 18, 4, 4),
    ("- Analyse avancée du cycle TCP (Handshake, flags de contrôle, gestion des files d'attente SYN).", False, 14, 4, 0),
    ("- Pratique des outils offensifs d'audit (Nmap, Hping3) et des méthodes de détection défensive (NIDS / SOC).", False, 14, 4, 0),
    ("- Conception d'une chaîne complète d'ingestion de paquets, de scoring et de journalisation forensique.", False, 14, 12, 0),
    ("Compétences en Data Science & Génie Logiciel :", True, 18, 4, 4),
    ("- Conception et réglage fin d'algorithmes de Machine Learning non supervisé appliqués à la sécurité.", False, 14, 4, 0),
    ("- Vectorisation haute performance de pipelines de traitement de flux continus sous Python.", False, 14, 4, 0),
    ("- Développement d'une suite logicielle complète de bout en bout (CLI, Web Streamlit, Alertes, PDF).", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 14. DIFFICULTÉS & SOLUTIONS
# -------------------------------------------------------------
ajouter_slide_texte("Difficultés Rencontrées & Solutions Apportées", [
    ("1. Bruit Réseau & Absence de Données Étiquetées :", True, 17, 3, 3),
    ("Défi : Comment calibrer un modèle d'IA sans données pré-étiquetées sur le réseau municipal ?\nSolution : Conception du protocole Calibrate-Then-Monitor (120 s d'auto-apprentissage passif in situ).", False, 13, 12, 0),
    ("2. Traitement Haute Fréquence sans Perte de Trames :", True, 17, 3, 3),
    ("Défi : Risque de latence et d'engorgement lors du traitement paquet par paquet avec Scapy.\nSolution : Vectorisation des calculs statistiques par micro-fenêtres de 5s sous Pandas (gain de vitesse x2.5).", False, 13, 12, 0),
    ("3. Élimination des Faux Positifs Liés au Trafic Web :", True, 17, 3, 3),
    ("Défi : La navigation Web simultanée ouvre de multiples flux pouvant ressembler à un balayage.\nSolution : Création du Ratio de Dispersion R séparant nettement les flux légitimes des scans hostiles.", False, 13, 8, 0)
])

# -------------------------------------------------------------
# 15. PERSPECTIVES D'ÉVOLUTION
# -------------------------------------------------------------
ajouter_slide_texte("Perspectives d'Évolution du Système", [
    ("1. Évolution vers la Prévention Active (NIPS Automatisé) :", True, 18, 4, 4),
    ("Passer de la détection à l'action en injectant dynamiquement des règles de blocage pare-feu sur Windows Defender Firewall ou eBPF/iptables sous Linux.", False, 14, 12, 0),
    ("2. Intégration dans l'Écosystème SOC & SIEM :", True, 18, 4, 4),
    ("Développer des connecteurs normalisés (Syslog / API REST) pour exporter les flux et alertes vers des plateformes de supervision d'entreprise (Wazuh, Elastic SIEM, Splunk).", False, 14, 12, 0),
    ("3. Inspection Avancée des Flux Chiffrés (TLS Fingerprinting) :", True, 18, 4, 4),
    ("Intégrer l'empreinte TLS (JA3 / JA3S) pour identifier les menaces et logiciels malveillants dissimulés dans le trafic chiffré HTTPS sans déchiffrement.", False, 14, 8, 0)
])

# -------------------------------------------------------------
# 16. CONCLUSION GÉNÉRALE & REMERCIEMENTS
# -------------------------------------------------------------
ajouter_slide_texte("Conclusion Générale & Questions / Réponses", [
    ("Synthèse des Apports du Projet NetScan :", True, 18, 6, 4),
    ("- NetScan démontre la puissance du Machine Learning Non Supervisé pour combler les failles critiques des NIDS traditionnels face aux attaques furtives et volumétriques sans signatures.", False, 14, 6, 0),
    ("- Une solution souveraine, légère, opérationnelle et immédiatement déployable sur du matériel standard sans surcoût de licence logicielle.", False, 14, 16, 0),
    ("Merci pour votre aimable attention !", True, 22, 8, 4),
    ("Je suis à votre entière disposition pour répondre à toutes vos questions.", True, 16, 8, 0),
    ("Mohamed Reda QIYAOUI | EST Tétouan - Commune de Tétouan | 2025/2026", False, 13, 0, 0)
])

prs.save(DST)
print(f"Total diapositives après enrichissement : {len(prs.slides)}")
print(f"[OK] Fichier sauvegardé : {DST}")
