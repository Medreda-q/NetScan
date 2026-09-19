# -*- coding: utf-8 -*-
import docx
import shutil

p_updated = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedReda_Qiyaoui_Updated.docx"
p_main = r"C:\Users\DevLab\Desktop\Soutenance\Rapport_MohamedReda_Qiyaoui.docx"

doc = docx.Document(p_updated)

updates = {
    308: "•  Règle 1 — Scan de Ports (Port Scan) : Si la fenêtre est jugée anormale par le modèle ET que l'une des conditions suivantes est vérifiée : (1) P_unique ≥ 15, (2) P_unique ≥ 8 ET R ≥ 0,60, ou (3) P_unique ≥ 5 ET N_SYN ≥ 5 ET R ≥ 0,35, l'incident est formellement qualifié de Port Scan (Niveau de sévérité : CRITICAL).",
    309: "•  Règle 2 — Inondation / Déni de Service (Flood / DDoS) : Si la fenêtre est jugée anormale ET que P_unique ≤ 5, et qu'au moins l'un des deux critères suivants est satisfait : (a) Inondation SYN : N_SYN ≥ 15, ou N_SYN ≥ 8 avec un ratio SYN/paquet ≥ 20% ; (b) Amplification volumétrique : N_pkts ≥ 400 ET P_unique ≤ 3 ET (taille moyenne de trame ≥ 900 octets OU N_pkts ≥ 1 200), l'incident est qualifié de Flood / DDoS (Niveau de sévérité : CRITICAL). Cette distinction évite toute confusion avec un téléchargement HTTP/HTTPS légitime.",
    312: "•  Règle 4 — Garde-Fou Déterministe Anti-Scan Furtif : Indépendamment du modèle ML, si une fenêtre présente une dispersion critique avec P_unique ≥ 25, ou P_unique ≥ 15 ET R ≥ 0,50, l'incident est automatiquement qualifié de Port Scan (Niveau de sévérité : CRITICAL). Cette règle de sûreté élimine l'angle mort des scans lents (nmap -sS en cadence standard T3) masqués par le trafic de fond volumineux.",
    361: "3.  Validation mathématique sur données synthétiques générées à la volée (200 hôtes normaux, 1 scanner Nmap à 500 ports, 1 flooder volumétrique à 500 paquets avec trames proches de la MTU à 1 058 octets, et 1 source Web intensive légitime de 700 paquets avec N_SYN = 0 prouvant formellement l'absence de faux positifs).",
    432: "2.  Passage en mode actif en coupure (Inline NIPS) : Automatisation de l'application immédiate des règles pare-feu générées par alerting.py (blocage direct sans validation humaine manuelle) couplée à une table d'expiration temporelle des bannissements (jail timeout)."
}

for idx, text in updates.items():
    doc.paragraphs[idx].text = text
    print(f"[OK] P{idx} mis a jour avec succes.")

doc.save(p_updated)
doc.save(p_main)
print(f"[OK] Enregistre dans {p_updated} et {p_main}")
