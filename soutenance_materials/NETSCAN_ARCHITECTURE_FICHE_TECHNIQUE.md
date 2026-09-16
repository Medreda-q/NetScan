# NETSCAN — FICHE TECHNIQUE & CARTOGRAPHIE LOGICIELLE
**Document de Soutenance remis aux Membres du Jury**  
*École Supérieure de Technologie (EST) — Tétouan | DUT Cybersécurité (2025 / 2026)*  
**Candidat :** Mohamed Reda QIYAOUI  
**Projet :** Système Intelligent de Détection d'Anomalies Réseau par Machine Learning Non Supervisé  

---

## 1. CARTOGRAPHIE DES FICHIERS & RÔLES TECHNIQUES

Le projet NetScan est conçu selon une architecture modulaire en couches strictes (Capture ➔ Analyse IA ➔ Surveillance SOC ➔ Réponse active) :

| Fichier Source | Rôle Principal & Responsabilité | Fonctions & Classes Clés | Entrées / Sorties |
| :--- | :--- | :--- | :--- |
| **`netscan.py`**<br>`netscan.bat`<br>`netscan.sh` | **Orchestrateur & Lanceur Unifié (CLI)**<br>Point d'entrée du système. Gère l'auto-diagnostic, la vérification des privilèges administrateur (Npcap/root) et l'installation automatique des dépendances. | `check_system_drivers()`<br>`interactive_menu()`<br>`main()` | **In :** Drapeaux CLI (`--live`, `--pcap`, `--dashboard`, `--check`)<br>**Out :** Lancement des sous-modules |
| **`detection_engine.py`** | **Cœur Algorithmique & Moteur IA**<br>Implémente le double niveau Isolation Forest (Layer 1 unitaire & Layer 2 fenêtré 5s), le ratio mathématique de diversité portuaire et la boucle temps réel « Calibrate-Then-Monitor ». | `Layer1_PerPacket_Model`<br>`Layer2_Behavioral_Window`<br>`calibrate_session()`<br>`classify_threat()` | **In :** Flux réseau brut (Npcap/libpcap) ou fichier `.pcap`<br>**Out :** Scores d'anomalie, classification (Scan vs Flood) |
| **`dashboard.py`** | **Tableau de Bord SOC Interactif (Streamlit)**<br>Interface graphique de supervision en temps réel : visualisation des métriques réseau, inspection forensic de fichiers PCAP uploadés et audit trail. | `render_kpi_metrics()`<br>`plot_live_traffic()`<br>`display_threat_timeline()` | **In :** Trames capturées en streaming & exports CSV/JSON<br>**Out :** Interface web SOC haute résolution |
| **`alerting.py`** | **Module SIEM & Réponse Active (SOAR)**<br>Formatage et expédition d'alertes webhook Discord temps réel (< 300ms) et génération automatique des commandes de confinement pare-feu. | `send_discord_alert()`<br>`generate_firewall_rule()`<br>`log_audit_event()` | **In :** Anomalies confirmées par le moteur de détection<br>**Out :** Webhooks Discord + règles `iptables` / `netsh` |
| **`report_generator.py`** | **Générateur de Rapports NIST / CIS**<br>Génération en 1 clic de rapports d'incident exécutifs et forensiques détaillés, téléchargeables et imprimables en formats HTML et PDF. | `build_incident_report()`<br>`export_pdf()`<br>`format_nist_guidelines()` | **In :** Données de l'incident et métriques d'attaque<br>**Out :** Rapports exécutifs conformes NIST SP 800-61 |
| **`test_smoke.py`**<br>`test_detection_pcap.py` | **Suite de Tests Automatisés & Intégrité**<br>Validation de la résilience du code, de l'absence de régression, de la boucle asyncio Windows et de la précision sur capture réelle. | `test_asyncio_loop()`<br>`test_layer1_detection()`<br>`test_layer2_accuracy()` | **In :** Jeux d'essais unitaires & `sample_nmap_attack.pcap`<br>**Out :** Taux de succès des tests (100% validé) |
| **`sample_nmap_attack.pcap`**<br>`sample_analyzed_packets.csv` | **Jeux de Données Forensiques de Référence**<br>Captures réelles d'attaques Nmap SYN furtives et inondations SYN Flood réalisées en laboratoire virtualisé (Kali Linux ➔ Metasploitable 2). | Captures réseau brutes et trames labellisées | **Rôle :** Benchmark et validation expérimentale |

---

## 2. FLUX D'INTERACTION ENTRE LES COMPOSANTS (PIPELINE GLOBAL)

Voici la chronologie d'exécution montrant comment chaque fichier communique avec les autres :

```
                                  [ UTILISATEUR / ANALYSTE SOC ]
                                                │
                                                ▼
                                          netscan.py
                       (Validation des pilotes Npcap & Choix du Mode)
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
     [ MODE 1 : FORENSIC OFFLINE ]                                 [ MODE 2 : STREAMING TEMPS RÉEL ]
       sample_nmap_attack.pcap                                        Npcap (Win) / libpcap (Linux)
                 │                                                             │
                 └──────────────────────────────┬──────────────────────────────┘
                                                ▼
                                       detection_engine.py
           ┌────────────────────────────────────┴────────────────────────────────────┐
           ▼                                                                         ▼
 [ Phase 1 : Calibration (120s) ]                                         [ Phase 2 : Surveillance Continue (5s) ]
  Calcul de la baseline normale                                            Extraction du Vecteur 5D
  Ajustement du StandardScaler                                             Scoring Isolation Forest (L1 & L2)
           │                                                                         │
           └────────────────────────────────────┬────────────────────────────────────┘
                                                ▼
                             [ Ratio = unique_ports / packets ]
                              ├── Ratio > 0.5   ==>  Port Scan
                              └── Ratio <= 0.5  ==>  DDoS / Flood
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
            alerting.py                                                   dashboard.py
  - Webhooks Discord (< 300 ms)                                 - Visualisation des flux en direct
  - Confinement Firewall automatique                            - Audit trail persistant (JSON/CSV)
    (iptables / netsh)                                                         │
                 │                                                             ▼
                 └──────────────────────────────┬──────────────────────────────┘
                                                ▼
                                       report_generator.py
                          - Rapport Forensic Exécutif (HTML / PDF)
                          - Recommandations NIST SP 800-61 & CIS Controls
```

---

## 3. COMMENT PRÉSENTER CE DOCUMENT AU JURY (DISCOURS RECOMMANDÉ)

> *"Messieurs les membres du jury, vous avez devant vous la cartographie logicielle complète de NetScan. Comme vous pouvez le constater, ce projet ne se limite pas à un simple algorithme isolé : c'est une architecture modulaire complète en 5 briques :*
> 1. *L'orchestrateur `netscan.py` qui sécurise la capture bas niveau et gère la compatibilité Windows/Linux.*
> 2. *Le moteur IA `detection_engine.py` qui héberge le double Isolation Forest et la signature mathématique.*
> 3. *Le module de réponse active `alerting.py` qui génère automatiquement les règles pare-feu de confinement.*
> 4. *Le tableau de bord SOC `dashboard.py` sous Streamlit pour les analystes.*
> 5. *Le générateur `report_generator.py` qui structure les incidents selon le standard NIST SP 800-61.*
> 
> *Voyons maintenant en détail comment ces composants s'articulent en temps réel..."*
