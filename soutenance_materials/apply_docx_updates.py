# -*- coding: utf-8 -*-
import docx
import shutil
import os

docx_path = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedReda_Qiyaoui.docx"
backup_path = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedReda_Qiyaoui_Backup.docx"
updated_path = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedReda_Qiyaoui_Updated.docx"

# 1. Sauvegarde de sécurité
shutil.copy2(docx_path, backup_path)
print(f"[OK] Backup cree : {backup_path}")

# 2. Chargement du document
doc = docx.Document(docx_path)

# Dictionnaire de correspondances
replacements = {
    # 1. Sommaire 4.4
    "4.4 - Moteur de Journalisation Sécurisée et Historique des Incidents (alerts_history.json)":
        "4.4 - Module de Journalisation d'Audit et de Remédiation Pare-feu (alerting.py & alerts_history.json)",
    
    # 2. Sommaire 5.2
    "5.2 - Scénario 1 : Détection d'un scan Nmap furtif":
        "5.2 - Scénario 1 : Étalonnage dynamique de la référence et détection d'un scan Nmap furtif en direct",
    
    # 3. Section 3.2 Ingestion
    "•  Mode Surveillance Directe (Live) : Capture passive en temps réel sur les interfaces réseau locales via l'ouverture de sockets bruts (raw sockets) opérant en mode promiscuité.":
        "•  Mode Surveillance Directe (Live) : Capture passive en temps réel sur les interfaces réseau locales via l'ouverture de sockets bruts (raw sockets) opérant en mode promiscuité.\n"
        "Cycle Opérationnel du Mode Surveillance Directe (Dual-Phase Surveillance) :\n"
        "1. Phase 1 — Étalonnage Dynamique du Trafic de Référence (Baseline Calibration) : Dès l'activation de la sonde, NetScan capture passivement le trafic ambiant pendant 15 à 30 secondes. L'algorithme Isolation Forest et le StandardScaler apprennent la distribution statistique normale du sous-réseau communal (volume moyen, dispersion habituelle des ports). Un contrôle de variance garantit la robustesse du modèle même en cas de réseau inactif.\n"
        "2. Phase 2 — Surveillance Continue et Scoring Temps Réel : Les trames capturées sont agrégées et évaluées par fenêtres glissantes de 5 secondes (score_monitoring_window). Chaque tranche est projetée dans l'espace multidimensionnel étalonné pour calculer instantanément le score d'anomalie s(x).\n"
        "Filtrage Anti-Pollution de l'Hôte (filter_local_ip) : NetScan identifie dynamiquement l'adresse IP locale de la station de supervision (get_local_ip()) et isole strictement les flux entrants suspects, évitant d'imputer des comportements anormaux à la machine de supervision elle-même.",

    # 4. Section 4.4 Titre
    "4.4 Moteur de Journalisation Sécurisée et Historique des Incidents":
        "4.4 Module de Journalisation d'Audit et de Remédiation Pare-feu (alerting.py)",

    # 5. Section 4.4 Texte
    "Conformément aux exigences de traçabilité des systèmes d'information administratifs, NetScan intègre un mécanisme autonome de journalisation persistante (audit_logger). Lorsqu'une fenêtre réseau franchit le seuil critique d'anomalie :":
        "Afin de garantir l'intégrité et la persistance des preuves d'intrusion sans dépendre d'une base de données tierce lourde, NetScan intègre le module dédié alerting.py. L'architecture assure la traçabilité et la réponse active :",

    # 6. Section 4.4 Remédiation pare-feu
    "Consultation sécurisée in-app :\xa0Dès la connexion de l'administrateur à l'interface, un volet d'audit charge automatiquement l'historique complet des alertes non acquittées pour analyse forensique immédiate.":
        "Consultation sécurisée in-app : Dès la connexion de l'administrateur à l'interface, un volet d'audit charge automatiquement l'historique complet des alertes non acquittées pour analyse forensique immédiate.\n"
        "Génération Multi-Plateforme de Règles Pare-Feu : Pour chaque adresse IP hostile identifiée, alerting.py synthétise instantanément la commande de blocage : iptables -A INPUT -s <IP> -j DROP sous Linux, et netsh advfirewall firewall add rule name=\"NetScan_Block_<IP>\" dir=in action=block remoteip=<IP> sous Windows.",

    # 7. Section 5.2 Titre
    "5.2 Scénario 1 : Détection en direct d'un scan Nmap furtif (Live Sniffing)":
        "5.2 Scénario 1 : Étalonnage dynamique de la référence et détection d'un scan Nmap furtif en direct",

    # 8. Section 5.2 Protocole
    "python netscan.py":
        "streamlit run dashboard.py\n"
        "• Étape d'apprentissage (Phase 1) : Pendant les 15 premières secondes, NetScan capture le trafic ambiant et étalonne sa baseline de normalité.\n"
        "• Étape de surveillance et d'attaque (Phase 2) : Une fois la baseline active, la surveillance continue démarre avec filtrage local des flux (filter_local_ip).",

    # 9. Section 5.2 Décision & Attribution IP
    "L'arbre d'isolation isole la fenêtre temporelle avec un score d'anomalie critique (s = 0.88). L'incident est formellement qualifié en « ALERTE CRITIQUE : Port Scan « et notifié en temps réel (interception opérationnelle sur scan rapide -T4 par l’IA et scan furtif standard -sS par le garde-fou).":
        "L'arbre d'isolation isole la fenêtre temporelle avec un score d'anomalie critique (s = 0.88). L'incident est formellement qualifié en « ALERTE CRITIQUE : Port Scan » et notifié en temps réel.\n"
        "Résolution de l'attribution IP : Grâce au filtrage automatique du trafic de l'hôte local (filter_local_ip), NetScan discrimine les flux émis par la sonde elle-même et isole avec exactitude l'adresse IP source attaquante (192.168.1.116). L'incident est simultanément consigné dans alerts_history.json et la règle de bannissement Windows (netsh advfirewall) est générée."
}

def update_paragraph(p, new_text):
    # Preserver les runs et le formatage de style si possible
    p.text = new_text

count = 0
for p in doc.paragraphs:
    cur_text = p.text.strip()
    for target, replacement in replacements.items():
        if target in cur_text or cur_text == target:
            update_paragraph(p, replacement)
            count += 1
            print(f"[MODIF] Paragraphe mis a jour ({count}) : {target[:40]}...")
            break

# Aussi vérifier dans les tableaux
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                cur_text = p.text.strip()
                for target, replacement in replacements.items():
                    if target in cur_text:
                        p.text = p.text.replace(target, replacement)
                        count += 1
                        print(f"[MODIF TABLE] Cellule mise a jour : {target[:40]}...")

# Sauvegarder dans le fichier original et la copie mise à jour
doc.save(updated_path)
print(f"[OK] Fichier enregistre avec succes dans : {updated_path}")

try:
    doc.save(docx_path)
    print(f"[OK] Fichier principal {docx_path} mis a jour directement !")
except Exception as e:
    print(f"[INFO] Document principal ouvert dans Word, copie disponible dans {updated_path}: {e}")
