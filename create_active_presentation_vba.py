# -*- coding: utf-8 -*-
import sys, os

out_path = r"C:\Users\DevLab\Desktop\Soutenance\Inserer_Dans_Ma_Presentation.bas"

vba = '''Attribute VB_Name = "InsererDansMaPresentation"
' ==============================================================================
' MODULE VBA : INSERER DIRECTEMENT DANS VOTRE PRESENTATION OUVERTE
' Ce script ajoute toutes les diapositives manquantes a la fin de votre fichier
' Vous conservez votre theme, vos arrieres-plans et vous pouvez tout designer !
' ==============================================================================

Option Explicit

Public Sub InsererSlidesDansMaPresentation()
    Dim pres As Presentation
    Dim sld As Slide
    Dim totalAvant As Integer
    Dim tShp As Shape, tbl As Table
    
    ' On travaille directement sur votre presentation actuellement ouverte
    Set pres = ActivePresentation
    totalAvant = pres.Slides.Count
    
    ' -------------------------------------------------------------
    ' 1. SOMMAIRE GENERAL DE LA SOUTENANCE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Plan de la Presentation (Sommaire)"
    CreerBoite sld, 50, 100, 420, 190, "01. Cadre du Projet", _
        "- Contexte : Commune de Tetouan" & vbCrLf & _
        "- Problematique : Limites des NIDS traditionnels" & vbCrLf & _
        "- Solution NetScan : Machine Learning non supervise"
    CreerBoite sld, 490, 100, 420, 190, "02. Fondements Theoriques", _
        "- Principe d'Isolation Forest (iTrees)" & vbCrLf & _
        "- Formulation mathematique & Seuil" & vbCrLf & _
        "- Benchmark iForest vs SVM vs K-Means"
    CreerBoite sld, 50, 310, 420, 190, "03. Architecture & Outils", _
        "- Pipeline Bicouche (Couche 1 & Couche 2)" & vbCrLf & _
        "- Ratio de dispersion des ports (R)" & vbCrLf & _
        "- Stack logicielle : netscan.py, dashboard, PDF"
    CreerBoite sld, 490, 310, 420, 190, "04. Resultats & Bilan", _
        "- Banc d'essai : Kali Linux vs Windows" & vbCrLf & _
        "- Resultats chiffres & Gains operationnels" & vbCrLf & _
        "- Demonstration live, Bilan & Perspectives"

    ' -------------------------------------------------------------
    ' 2. CONTEXTE : COMMUNE DE TETOUAN
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Contexte du Projet : Commune de Tetouan"
    CreerBoite sld, 50, 100, 420, 390, "Organisme d'Accueil & Missions", _
        "Cadre Institutionnel :" & vbCrLf & _
        "- Division des Systemes d'Information de la Mairie." & vbCrLf & vbCrLf & _
        "Role de l'Infrastructure Reseau :" & vbCrLf & _
        "- Hebergement des applications metier communales." & vbCrLf & _
        "- Connectivite continue inter-services." & vbCrLf & vbCrLf & _
        "Trafic Quotidien :" & vbCrLf & _
        "- Flux heterogenes melant navigation web et bases de donnees."
    CreerBoite sld, 490, 100, 420, 390, "Enjeux Cyber & Objectifs", _
        "Menaces Identifiees :" & vbCrLf & _
        "- Scans de ports furtifs cartographiant le reseau." & vbCrLf & _
        "- Risque d'inondation DoS saturant les services publics." & vbCrLf & vbCrLf & _
        "Cahier des Charges NetScan :" & vbCrLf & _
        "- Sonde locale, legere et autonome." & vbCrLf & _
        "- Detection en temps reel sans abonnement proprietaire." & vbCrLf & _
        "- Alerting immediat pour l'equipe d'administration."

    ' -------------------------------------------------------------
    ' 3. FORMULATION MATHEMATIQUE IFOREST
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Modelisation Mathematique & Scoring d'Anomalie"
    CreerBoite sld, 50, 100, 860, 130, "Formule Fondamentale (Liu et al., 2008)", _
        "s(x, n) = 2 ^ ( - E(h(x)) / c(n) )" & vbCrLf & _
        "- E(h(x)) : Esperance de la profondeur d'isolation moyenne a travers les arbres." & vbCrLf & _
        "- c(n) : Longueur moyenne d'un echec d'arbre binaire de recherche pour n echantillons."
    CreerBoite sld, 50, 250, 275, 240, "s(x, n) -> 1", _
        "Profondeur E(h(x)) tres faible." & vbCrLf & vbCrLf & _
        "L'instance est isolee en tres peu de coupures." & vbCrLf & vbCrLf & _
        "Signature certaine d'une anomalie hostile."
    CreerBoite sld, 342, 250, 275, 240, "s(x, n) -> 0.5", _
        "Profondeur moyenne standard." & vbCrLf & vbCrLf & _
        "L'ensemble des paquets ne presente aucune anomalie notable." & vbCrLf & vbCrLf & _
        "Trafic nominal d'arriere-plan."
    CreerBoite sld, 635, 250, 275, 240, "Seuil tau = 0.60", _
        "Seuil de decision optimal fixe apres experimentation." & vbCrLf & vbCrLf & _
        "Compromis parfait entre sensibilite de detection et limitation des faux positifs."

    ' -------------------------------------------------------------
    ' 4. BENCHMARK ALGORITHMIQUE (TABLEAU)
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Benchmark Algorithmique : Pourquoi Isolation Forest ?"
    Set tShp = sld.Shapes.AddTable(5, 4, 50, 110, 860, 370)
    Set tbl = tShp.Table
    MettreEnFormeTableau tbl, _
        Array("Critere", "Isolation Forest (NetScan)", "One-Class SVM", "k-Means Anomaly"), _
        Array( _
            Array("Complexite", "O(n log n) - Ultra-rapide", "O(n^2 a n^3) - Lourd", "O(n k i) - Moyen"), _
            Array("Dimension", "Faible sensibilite (aleatoire)", "Elevee (fleau dimensionnel)", "Elevee (distances faussees)"), _
            Array("Distribution", "Aucune hypothese prealable", "Choix du noyau gaussien fin", "Suppose clusters spheriques"), _
            Array("Temps Reel", "Optimale (faible memoire)", "Faible (inversion matrice)", "Faible (sensible centres)") _
        )

    ' -------------------------------------------------------------
    ' 5. STACK TECHNOLOGIQUE
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Stack Technologique & Outils Developpes"
    CreerBoite sld, 50, 100, 275, 185, "Python 3.11", _
        "Langage coeur pour le prototypage rapide, la modularite et la richesse des bibliotheques cyber."
    CreerBoite sld, 342, 100, 275, 185, "Scapy 2.5 & Npcap", _
        "Moteur de capture passive en mode Promiscuous et dissection fine des trames reseau."
    CreerBoite sld, 635, 100, 275, 185, "Scikit-learn", _
        "Implementation hautement optimisee de l'algorithme Isolation Forest pour l'inference."
    CreerBoite sld, 50, 305, 275, 185, "Pandas & NumPy", _
        "Vectorisation rapide des calculs statistiques sur les micro-fenetres temporelles de 5s."
    CreerBoite sld, 342, 305, 275, 185, "Streamlit (Dashboard)", _
        "Console web interactive pour la supervision SOC des flux et visualisations en temps reel."
    CreerBoite sld, 635, 305, 275, 185, "ReportLab & Discord", _
        "Generation automatique des rapports d'incident PDF et alertes webhook instantanees."

    ' -------------------------------------------------------------
    ' 6. LES 4 MODULES LOGICIELS DU PROJET
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Suite Logicielle NetScan : 4 Briques Modulaires"
    CreerBoite sld, 50, 100, 420, 185, "1. netscan.py (CLI)", _
        "Orchestrateur console (Linux Kali / Windows)." & vbCrLf & _
        "Modes : Demo synthetique, analyse PCAP hors-ligne et Live Sniffing avec auto-calibration de 120s."
    CreerBoite sld, 490, 100, 420, 185, "2. dashboard.py (SOC Web)", _
        "Interface graphique sous Streamlit." & vbCrLf & _
        "Affiche les KPIs de securite, la distribution des scores d'anomalie et la chronologie des alertes."
    CreerBoite sld, 50, 305, 420, 185, "3. report_generator.py (PDF)", _
        "Moteur forensique automatisant l'edition de rapports d'incident au format PDF professionnel avec horodatage."
    CreerBoite sld, 490, 305, 420, 185, "4. test_smoke.py (Qualite)", _
        "Suite de tests automatises validant l'integrite du pipeline de traitement avant tout deploiement."

    ' -------------------------------------------------------------
    ' 7. BANC D'ESSAI EXPERIMENTAL
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Banc d'Essai Experimental & Topologie de Test"
    CreerBoite sld, 50, 100, 420, 390, "Topologie Materielle & Virtuelle", _
        "Poste 1 : Attaquant / Audit (Kali Linux) :" & vbCrLf & _
        "- IP : 192.168.1.50" & vbCrLf & _
        "- Outils : Nmap (scans furtifs -sS) et Hping3 (SYN Flood volumetrique)." & vbCrLf & vbCrLf & _
        "Poste 2 : Sonde & Supervision (Windows) :" & vbCrLf & _
        "- IP : 192.168.1.100" & vbCrLf & _
        "- NetScan en ecoute passive Promiscuous via driver Npcap." & vbCrLf & vbCrLf & _
        "Poste 3 : Cible Metasploitable (Services HTTP/SSH)."
    CreerBoite sld, 490, 100, 420, 390, "Protocole de Validation", _
        "1. Validation sur Captures PCAP Certifiees :" & vbCrLf & _
        "- Rejeu de traces d'attaques reelles et verifiees." & vbCrLf & vbCrLf & _
        "2. Validation in situ en Direct :" & vbCrLf & _
        "- Surveillance du trafic reel de la Commune de Tetouan." & vbCrLf & vbCrLf & _
        "Conditions de Realisme :" & vbCrLf & _
        "- Ingestion d'attaques melangees a un trafic normal et bruite (Web, streaming, DNS)."

    ' -------------------------------------------------------------
    ' 8. RESULTATS EXPERIMENTAUX & BENCHMARK COMPARATIF (TABLEAU 5.2)
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Resultats Experimentaux & Gains Operationnels (Tableau 5.2)"
    Set tShp = sld.Shapes.AddTable(6, 4, 50, 110, 860, 370)
    Set tbl = tShp.Table
    MettreEnFormeTableau tbl, _
        Array("Critere d'Evaluation", "Modele Baseline (Unitaire)", "NetScan (Bicouche)", "Gain Operationnel"), _
        Array( _
            Array("Detection Scan Nmap (-sS)", "0% (Angle mort total)", "100% (Isole avec succes)", "Elimination angle mort"), _
            Array("Detection SYN Flood", "Partielle (selon taille)", "100% (Volume detecte)", "Neutralisation immediate"), _
            Array("Taux de Faux Positifs", "12.4% (Trafic web bruite)", "< 1.2% (Grace au ratio R)", "Divise par 10 (Anti-fatigue)"), _
            Array("Temps d'Analyse (4 100 pkts)", "4.8 secondes", "1.9 seconde (Vectorise)", "Vitesse multipliee par 2.5"), _
            Array("Explicabilite Menace", "Simple label 'Anormal'", "Port Scan ou DDoS precis", "Gain decisionnel pour le SOC") _
        )

    ' -------------------------------------------------------------
    ' 9. BILAN DU PROJET & COMPETENCES
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Bilan du Projet & Competences Consolidees"
    CreerBoite sld, 50, 100, 420, 390, "Competences Reseaux & Cyberdefense", _
        "- Analyse approfondie du cycle TCP (Handshake, flags, retransmissions)." & vbCrLf & vbCrLf & _
        "- Pratique d'outils offensifs sous Kali Linux (Nmap, Hping3)." & vbCrLf & vbCrLf & _
        "- Conception d'une chaine complete de supervision SOC et alerting temps reel."
    CreerBoite sld, 490, 100, 420, 390, "Competences IA & Genie Logiciel", _
        "- Maitrise mathematique et reglage fin de l'algorithme Isolation Forest." & vbCrLf & vbCrLf & _
        "- Traitement et vectorisation de donnees continues en temps reel via Pandas." & vbCrLf & vbCrLf & _
        "- Developpement complet d'un outillage modulaire (CLI, Web, Forensics PDF)."

    ' -------------------------------------------------------------
    ' 10. DIFFICULTES & SOLUTIONS
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Difficultes Rencontrees & Solutions Apportees"
    CreerBoite sld, 50, 100, 860, 115, "1. Bruit Reseau & Absence de Donnees Etiquetees", _
        "Defi : Comment calibrer l'IA sans historique de trafic labellise ?" & vbCrLf & _
        "Solution : Protocole Calibrate-Then-Monitor (phase passive in situ de 120s)."
    CreerBoite sld, 50, 230, 860, 115, "2. Traitement Haute Frequence sans Perte de Trames", _
        "Defi : Risque de latence lors du decodage paquet par paquet avec Scapy." & vbCrLf & _
        "Solution : Vectorisation des calculs statistiques par micro-fenetres de 5s sous Pandas (gain x2.5)."
    CreerBoite sld, 50, 360, 860, 115, "3. Elimination des Faux Positifs de Navigation Web", _
        "Defi : La navigation Web simultanee ouvre de nombreux ports et peut imiter un scan." & vbCrLf & _
        "Solution : Ratio de Dispersion R separant nettement les flux reels des scans Nmap."

    ' -------------------------------------------------------------
    ' 11. PERSPECTIVES D'EVOLUTION
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Perspectives d'Evolution du Systeme"
    CreerBoite sld, 50, 100, 275, 390, "Reponse Active (NIPS)", _
        "Passer d'une detection passive a un blocage actif automatise." & vbCrLf & vbCrLf & _
        "Declenchement dynamique de regles d'isolement IP via l'API Pare-feu Windows ou eBPF/iptables sous Linux."
    CreerBoite sld, 342, 100, 275, 390, "Integration SIEM", _
        "Connexion standardisee (Syslog / API) vers les plateformes de supervision d'entreprise telles que Wazuh, Elastic SIEM ou Splunk."
    CreerBoite sld, 635, 100, 275, 390, "Flux Chiffres (TLS)", _
        "Integration de l'empreinte TLS (JA3 / JA3S) pour repérer les anomalies et communications suspectes sans dechiffrer le contenu."

    ' -------------------------------------------------------------
    ' 12. CONCLUSION & REMERCIEMENTS
    ' -------------------------------------------------------------
    Set sld = pres.Slides.Add(pres.Slides.Count + 1, ppLayoutBlank)
    CreerTitre sld, "Conclusion Generale & Questions / Reponses"
    CreerBoite sld, 50, 100, 860, 150, "Apport Principal de NetScan", _
        "NetScan confirme la pertinence et la robustesse du Machine Learning Non Supervise pour combler les angles morts critiques des NIDS traditionnels face aux attaques furtives et volumetriques sans signatures."
    CreerBoite sld, 50, 270, 860, 220, "Remerciements", _
        "Merci pour votre aimable attention !" & vbCrLf & vbCrLf & _
        "Avez-vous des questions ?" & vbCrLf & vbCrLf & _
        "Mohamed Reda QIYAOUI | EST Tetouan - Commune de Tetouan | 2025/2026"

    MsgBox "Succes ! " & (pres.Slides.Count - totalAvant) & " nouvelles diapositives ont ete inserees directement dans votre presentation ouverte !", vbInformation, "NetScan - EST Tetouan"
End Sub

' -----------------------------------------------------------------
' FONCTIONS UTILITAIRES POUR DESIGN MODIFIABLE
' -----------------------------------------------------------------
Private Sub CreerTitre(sld As Slide, titre As String)
    Dim tb As Shape
    Set tb = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, 50, 25, 860, 50)
    tb.TextFrame.WordWrap = msoTrue
    With tb.TextFrame.TextRange
        .Text = titre
        .Font.Name = "Segoe UI"
        .Font.Size = 22
        .Font.Bold = msoTrue
    End With
End Sub

Private Sub CreerBoite(sld As Slide, left As Single, top As Single, width As Single, height As Single, entete As String, texte As String)
    Dim shp As Shape
    Set shp = sld.Shapes.AddShape(msoShapeRoundedRectangle, left, top, width, height)
    shp.Fill.Solid
    shp.Fill.ForeColor.RGB = RGB(255, 255, 255)
    shp.Line.ForeColor.RGB = RGB(203, 213, 225)
    shp.Line.Weight = 1.2
    
    Dim tb As Shape
    Set tb = sld.Shapes.AddTextbox(msoTextOrientationHorizontal, left + 10, top + 10, width - 20, height - 20)
    tb.TextFrame.WordWrap = msoTrue
    
    With tb.TextFrame.TextRange
        .Text = entete & vbCrLf & vbCrLf & texte
        .Font.Name = "Segoe UI"
        .Font.Size = 12
        .Font.Color.RGB = RGB(15, 23, 42)
        .Paragraphs(1).Font.Size = 14
        .Paragraphs(1).Font.Bold = msoTrue
        .Paragraphs(1).Font.Color.RGB = RGB(14, 116, 144)
    End With
End Sub

Private Sub MettreEnFormeTableau(tbl As Table, headers As Variant, rowsData As Variant)
    Dim r As Integer, c As Integer
    
    For c = 0 To UBound(headers)
        tbl.Cell(1, c + 1).Shape.Fill.Solid
        tbl.Cell(1, c + 1).Shape.Fill.ForeColor.RGB = RGB(15, 23, 42)
        With tbl.Cell(1, c + 1).Shape.TextFrame.TextRange
            .Text = headers(c)
            .Font.Name = "Segoe UI"
            .Font.Size = 12
            .Font.Bold = msoTrue
            .Font.Color.RGB = RGB(255, 255, 255)
        End With
    Next c
    
    For r = 0 To UBound(rowsData)
        For c = 0 To UBound(rowsData(r))
            tbl.Cell(r + 2, c + 1).Shape.Fill.Solid
            tbl.Cell(r + 2, c + 1).Shape.Fill.ForeColor.RGB = IIf(r Mod 2 = 0, RGB(241, 245, 249), RGB(255, 255, 255))
            With tbl.Cell(r + 2, c + 1).Shape.TextFrame.TextRange
                .Text = rowsData(r)(c)
                .Font.Name = "Segoe UI"
                .Font.Size = 11
                .Font.Color.RGB = RGB(15, 23, 42)
                If c = 1 Or c = 3 Then .Font.Bold = msoTrue
            End With
        Next c
    Next r
End Sub
'''

with open(out_path, "w", encoding="cp1252", errors="replace") as f:
    f.write(vba)

print(f"[OK] Fichier VBA Inserer_Dans_Ma_Presentation.bas généré : {out_path}")
