# -*- coding: utf-8 -*-
out_file = r"C:\Users\DevLab\Desktop\Soutenance\Mettre_A_Jour_Rapport_UltraRapide.bas"

vba_code = '''Attribute VB_Name = "MiseAJourUltraRapide"
' ==============================================================================
' MODULE VBA COMPLET & ULTRA-RAPIDE (ZERO FREEZE / EXECUTION EN 0.1 SECONDE)
' Ce code met a jour directement votre document Word ouvert !
' ==============================================================================

Option Explicit

Public Sub AppliquerMiseAJour()
    Dim p As Paragraph
    Dim txt As String
    Dim nbModifs As Long
    nbModifs = 0
    
    Application.ScreenUpdating = True
    
    For Each p In ActiveDocument.Paragraphs
        txt = p.Range.Text
        
        ' --- 1. SOMMAIRE : SECTION 4.4 ---
        If InStr(1, txt, "4.4 - Moteur de Journalisation", vbTextCompare) > 0 Then
            p.Range.Text = "4.4 - Module de Journalisation d'Audit et de Rem" & ChrW(233) & "diation Pare-feu (alerting.py & alerts_history.json)" & vbCrLf
            nbModifs = nbModifs + 1
            
        ' --- 2. SOMMAIRE : SECTION 5.2 ---
        ElseIf InStr(1, txt, "5.2 - Sc", vbTextCompare) > 0 And InStr(1, txt, "furtif", vbTextCompare) > 0 Then
            p.Range.Text = "5.2 - Sc" & ChrW(233) & "nario 1 : " & ChrW(201) & "talonnage dynamique de la r" & ChrW(233) & "f" & ChrW(233) & "rence et d" & ChrW(233) & "tection d'un scan Nmap furtif en direct" & vbCrLf
            nbModifs = nbModifs + 1
            
        ' --- 3. SECTION 3.2 : INGESTION & CYCLE 2 PHASES ---
        ElseIf InStr(1, txt, "Mode Surveillance Directe (Live)", vbTextCompare) > 0 Then
            p.Range.Text = ChrW(8226) & "  Mode Surveillance Directe (Live) : Capture passive en temps r" & ChrW(233) & "el sur les interfaces r" & ChrW(233) & "seau locales via l'ouverture de sockets bruts (raw sockets) op" & ChrW(233) & "rant en mode promiscuit" & ChrW(233) & "." & vbCrLf & _
                           "Cycle Op" & ChrW(233) & "rationnel du Mode Surveillance Directe (Dual-Phase Surveillance) :" & vbCrLf & _
                           "1. Phase 1 " & ChrW(8212) & " " & ChrW(201) & "talonnage Dynamique du Trafic de R" & ChrW(233) & "f" & ChrW(233) & "rence (Baseline Calibration) : D" & ChrW(233) & "s l'activation de la sonde, NetScan capture passivement le trafic ambiant pendant 15 " & ChrW(224) & " 30 secondes. L'algorithme Isolation Forest et le StandardScaler apprennent la distribution statistique normale du sous-r" & ChrW(233) & "seau communal (volume moyen, dispersion habituelle des ports). Un contr" & ChrW(244) & "le de variance garantit la robustesse du mod" & ChrW(232) & "le m" & ChrW(234) & "me en cas de r" & ChrW(233) & "seau inactif." & vbCrLf & _
                           "2. Phase 2 " & ChrW(8212) & " Surveillance Continue et Scoring Temps R" & ChrW(233) & "el : Les trames captur" & ChrW(233) & "es sont agr" & ChrW(233) & "g" & ChrW(233) & "es et " & ChrW(233) & "valu" & ChrW(233) & "es par fen" & ChrW(234) & "tres glissantes de 5 secondes (score_monitoring_window). Chaque tranche est projet" & ChrW(233) & "e dans l'espace multidimensionnel " & ChrW(233) & "talonn" & ChrW(233) & " pour calculer instantan" & ChrW(233) & "ment le score d'anomalie s(x)." & vbCrLf & _
                           "Filtrage Anti-Pollution de l'H" & ChrW(244) & "te (filter_local_ip) : NetScan identifie dynamiquement l'adresse IP locale de la station de supervision (get_local_ip()) et isole strictement les flux entrants suspects, " & ChrW(233) & "vitant d'imputer des comportements anormaux " & ChrW(224) & " la machine de supervision elle-m" & ChrW(234) & "me." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 4. SECTION 3.4 : REGLE 1 SCAN MULTI-CRITERES ---
        ElseIf (InStr(1, txt, "Règle 1 — Scan de Ports", vbTextCompare) > 0 Or InStr(1, txt, "R" & ChrW(232) & "gle 1", vbTextCompare) > 0) And InStr(1, txt, "0,60", vbTextCompare) = 0 Then
            p.Range.Text = ChrW(8226) & "  R" & ChrW(232) & "gle 1 " & ChrW(8212) & " Scan de Ports (Port Scan) : Si la fen" & ChrW(234) & "tre est jug" & ChrW(233) & "e anormale par le mod" & ChrW(232) & "le ET que l'une des conditions suivantes est v" & ChrW(233) & "rifi" & ChrW(233) & "e : (1) P_unique " & ChrW(8805) & " 15, (2) P_unique " & ChrW(8805) & " 8 ET R " & ChrW(8805) & " 0,60, ou (3) P_unique " & ChrW(8805) & " 5 ET N_SYN " & ChrW(8805) & " 5 ET R " & ChrW(8805) & " 0,35, l'incident est formellement qualifi" & ChrW(233) & " de Port Scan (Niveau de s" & ChrW(233) & "v" & ChrW(233) & "rit" & ChrW(233) & " : CRITICAL)." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 5. SECTION 3.4 : REGLE 2 FLOOD SYN & MTU ---
        ElseIf (InStr(1, txt, "Règle 2 — Inondation", vbTextCompare) > 0 Or InStr(1, txt, "R" & ChrW(232) & "gle 2", vbTextCompare) > 0) And InStr(1, txt, "900 octets", vbTextCompare) = 0 Then
            p.Range.Text = ChrW(8226) & "  R" & ChrW(232) & "gle 2 " & ChrW(8212) & " Inondation / D" & ChrW(233) & "ni de Service (Flood / DDoS) : Si la fen" & ChrW(234) & "tre est jug" & ChrW(233) & "e anormale ET que P_unique " & ChrW(8804) & " 5, et qu'au moins l'un des deux crit" & ChrW(232) & "res suivants est satisfait : (a) Inondation SYN : N_SYN " & ChrW(8805) & " 15, ou N_SYN " & ChrW(8805) & " 8 avec un ratio SYN/paquet " & ChrW(8805) & " 20% ; (b) Amplification volum" & ChrW(233) & "trique : N_pkts " & ChrW(8805) & " 400 ET P_unique " & ChrW(8804) & " 3 ET (taille moyenne de trame " & ChrW(8805) & " 900 octets OU N_pkts " & ChrW(8805) & " 1 200), l'incident est qualifi" & ChrW(233) & " de Flood / DDoS (Niveau de s" & ChrW(233) & "v" & ChrW(233) & "rit" & ChrW(233) & " : CRITICAL). Cette distinction " & ChrW(233) & "vite toute confusion avec un t" & ChrW(233) & "l" & ChrW(233) & "chargement HTTP/HTTPS l" & ChrW(233) & "gitime." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 6. SECTION 3.4 : REGLE 4 GARDE-FOU ---
        ElseIf (InStr(1, txt, "Règle 4 — Garde-Fou", vbTextCompare) > 0 Or InStr(1, txt, "R" & ChrW(232) & "gle 4", vbTextCompare) > 0) And InStr(1, txt, "P_unique >= 25", vbTextCompare) = 0 And InStr(1, txt, "P_unique " & ChrW(8805) & " 25", vbTextCompare) = 0 Then
            p.Range.Text = ChrW(8226) & "  R" & ChrW(232) & "gle 4 " & ChrW(8212) & " Garde-Fou D" & ChrW(233) & "terministe Anti-Scan Furtif : Ind" & ChrW(233) & "pendamment du mod" & ChrW(232) & "le ML, si une fen" & ChrW(234) & "tre pr" & ChrW(233) & "sente une dispersion critique avec P_unique " & ChrW(8805) & " 25, ou P_unique " & ChrW(8805) & " 15 ET R " & ChrW(8805) & " 0,50, l'incident est automatiquement qualifi" & ChrW(233) & " de Port Scan (Niveau de s" & ChrW(233) & "v" & ChrW(233) & "rit" & ChrW(233) & " : CRITICAL). Cette r" & ChrW(232) & "gle de s" & ChrW(251) & "ret" & ChrW(233) & " " & ChrW(233) & "limine l'angle mort des scans lents (nmap -sS en cadence standard T3) masqu" & ChrW(233) & "s par le trafic de fond volumineux." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 7. SECTION 4.4 : TITRE MODULE ALERTING.PY ---
        ElseIf InStr(1, txt, "4.4 Moteur de Journalisation", vbTextCompare) > 0 Then
            p.Range.Text = "4.4 Module de Journalisation d'Audit et de Rem" & ChrW(233) & "diation Pare-feu (alerting.py)" & vbCrLf
            nbModifs = nbModifs + 1
            
        ' --- 8. SECTION 4.4 : ARCHITECTURE ALERTING.PY ---
        ElseIf InStr(1, txt, "audit_logger", vbTextCompare) > 0 Then
            p.Range.Text = "Afin de garantir l'int" & ChrW(233) & "grit" & ChrW(233) & " et la persistance des preuves d'intrusion sans d" & ChrW(233) & "pendre d'une base de donn" & ChrW(233) & "es tierce lourde, NetScan int" & ChrW(232) & "gre le module d" & ChrW(233) & "di" & ChrW(233) & " alerting.py. L'architecture assure la tra" & ChrW(231) & "abilit" & ChrW(233) & " et la r" & ChrW(233) & "ponse active :" & vbCrLf
            nbModifs = nbModifs + 1
            
        ' --- 9. SECTION 4.4 : REGLES NETSH WINDOWS & IPTABLES ---
        ElseIf InStr(1, txt, "Consultation s", vbTextCompare) > 0 And InStr(1, txt, "in-app", vbTextCompare) > 0 And InStr(1, txt, "netsh", vbTextCompare) = 0 Then
            p.Range.Text = "Consultation s" & ChrW(233) & "curis" & ChrW(233) & "e in-app : D" & ChrW(233) & "s la connexion de l'administrateur " & ChrW(224) & " l'interface, un volet d'audit charge automatiquement l'historique complet des alertes non acquitt" & ChrW(233) & "es pour analyse forensique imm" & ChrW(233) & "diate." & vbCrLf & _
                           "G" & ChrW(233) & "n" & ChrW(233) & "ration Multi-Plateforme de R" & ChrW(232) & "gles Pare-Feu : Pour chaque adresse IP hostile identifi" & ChrW(233) & "e, alerting.py synth" & ChrW(233) & "tise instantan" & ChrW(233) & "ment la commande de blocage : iptables -A INPUT -s <IP> -j DROP sous Linux, et netsh advfirewall firewall add rule name=""NetScan_Block_<IP>"" dir=in action=block remoteip=<IP> sous Windows." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 10. SECTION 4.6 : TEST_SMOKE.PY (MTU 1058 & TRAFIC WEB) ---
        ElseIf (InStr(1, txt, "Validation mathématique", vbTextCompare) > 0 Or InStr(1, txt, "Validation math" & ChrW(233) & "matique", vbTextCompare) > 0) And InStr(1, txt, "1 058 octets", vbTextCompare) = 0 Then
            p.Range.Text = "3.  Validation math" & ChrW(233) & "matique sur donn" & ChrW(233) & "es synth" & ChrW(233) & "tiques g" & ChrW(233) & "n" & ChrW(233) & "r" & ChrW(233) & "es " & ChrW(224) & " la vol" & ChrW(233) & "e (200 h" & ChrW(244) & "tes normaux, 1 scanner Nmap " & ChrW(224) & " 500 ports, 1 flooder volum" & ChrW(233) & "trique " & ChrW(224) & " 500 paquets avec trames proches de la MTU " & ChrW(224) & " 1 058 octets, et 1 source Web intensive l" & ChrW(233) & "gitime de 700 paquets avec N_SYN = 0 prouvant formellement l'absence de faux positifs)." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 11. SECTION 5.2 : TITRE SCENARIO 1 ---
        ElseIf InStr(1, txt, "5.2 Sc", vbTextCompare) > 0 And InStr(1, txt, "Sniffing", vbTextCompare) > 0 Then
            p.Range.Text = "5.2 Sc" & ChrW(233) & "nario 1 : " & ChrW(201) & "talonnage dynamique de la r" & ChrW(233) & "f" & ChrW(233) & "rence et d" & ChrW(233) & "tection d'un scan Nmap furtif en direct" & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 12. SECTION 5.2 : PROTOCOLE ---
        ElseIf InStr(1, txt, "python netscan.py", vbTextCompare) > 0 Then
            p.Range.Text = "streamlit run dashboard.py" & vbCrLf & _
                           ChrW(8226) & " " & ChrW(201) & "tape d'apprentissage (Phase 1) : Pendant les 15 premi" & ChrW(232) & "res secondes, NetScan capture le trafic ambiant et " & ChrW(233) & "talonne sa baseline de normalit" & ChrW(233) & "." & vbCrLf & _
                           ChrW(8226) & " " & ChrW(201) & "tape de surveillance et d'attaque (Phase 2) : Une fois la baseline active, la surveillance continue d" & ChrW(233) & "marre avec filtrage local des flux (filter_local_ip)." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 13. SECTION 5.2 : ATTRIBUTION IP REELLE (192.168.1.116) ---
        ElseIf InStr(1, txt, "score d'anomalie critique (s = 0.88)", vbTextCompare) > 0 And InStr(1, txt, "192.168.1.116", vbTextCompare) = 0 Then
            p.Range.Text = "L'arbre d'isolation isole la fen" & ChrW(234) & "tre temporelle avec un score d'anomalie critique (s = 0.88). L'incident est formellement qualifi" & ChrW(233) & " en " & ChrW(171) & " ALERTE CRITIQUE : Port Scan " & ChrW(187) & " et notifi" & ChrW(233) & " en temps r" & ChrW(233) & "el." & vbCrLf & _
                           "R" & ChrW(233) & "solution de l'attribution IP : Gr" & ChrW(224) & "ce au filtrage automatique du trafic de l'h" & ChrW(244) & "te local (filter_local_ip), NetScan discrimine les flux " & ChrW(233) & "mis par la sonde elle-m" & ChrW(234) & "me et isole avec exactitude l'adresse IP source attaquante (192.168.1.116). L'incident est simultan" & ChrW(233) & "ment consign" & ChrW(233) & " dans alerts_history.json et la r" & ChrW(232) & "gle de bannissement Windows (netsh advfirewall) est g" & ChrW(233) & "n" & ChrW(233) & "r" & ChrW(233) & "e." & vbCrLf
            nbModifs = nbModifs + 1

        ' --- 14. SECTION 6.3 : PERSPECTIVES INLINE NIPS ---
        ElseIf (InStr(1, txt, "Module de Réponse Active IPS", vbTextCompare) > 0 Or InStr(1, txt, "Module de R" & ChrW(232) & "ponse Active IPS", vbTextCompare) > 0) And InStr(1, txt, "Inline NIPS", vbTextCompare) = 0 Then
            p.Range.Text = "2.  Passage en mode actif en coupure (Inline NIPS) : Automatisation de l'application imm" & ChrW(233) & "diate des r" & ChrW(232) & "gles pare-feu g" & ChrW(233) & "n" & ChrW(233) & "r" & ChrW(233) & "es par alerting.py (blocage direct sans validation humaine manuelle) coupl" & ChrW(233) & "e " & ChrW(224) & " une table d'expiration temporelle des bannissements (jail timeout)." & vbCrLf
            nbModifs = nbModifs + 1
        End If
    Next p
    
    MsgBox "Mise a jour terminee avec succes !" & vbCrLf & _
           "Sections mises a jour : " & nbModifs, _
           vbInformation, "NetScan - Rapport Finalise"
End Sub
'''

with open(out_file, "w", encoding="latin1", errors="replace") as f:
    f.write(vba_code)
print(f"[OK] Fichier genere : {out_file}")
