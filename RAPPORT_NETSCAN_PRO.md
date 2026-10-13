# RAPPORT TECHNIQUE DE PROJET & LIVRE BLANC

## Conception et Développement d'un Système Intelligent de Détection d'Anomalies Réseau (Port Scans & DDoS) par Apprentissage Non Supervisé (Isolation Forest)

**Auteur :** Mohamed Reda Qiyaoui  
**Spécialité :** Cybersécurité & Ingénierie des Systèmes  
**Projet :** NetScan — Dual-Layer Network Anomaly & Intrusion Detection System  
**Dépôt GitHub :** https://github.com/Medreda-q/NetScan  

---

### Dédicace

*À Allah, tout-puissant, qui m’accorde la force, la patience et la clarté nécessaires pour mener à bien mes entreprises ;*

*À mes parents, pour leur sacrifice silencieux, leur confiance inconditionnelle et leurs prières qui éclairent chacun de mes pas. Aucune réussite n’aurait été possible sans vos efforts ;*

*À ma famille, pour son soutien bienveillant et sa présence constante ;*

*À ceux qui choisissent chaque jour de défendre, de comprendre et de sécuriser le cyberespace ;*

*Et à la rigueur de l'effort personnel, face aux défis techniques, pour transformer la curiosité en expertise.*

*Je dédie ce travail, fruit d'exigence, de passion et de persévérance.*

---

### Remerciements

La réalisation de ce projet d'ingénierie et de recherche appliquée a bénéficié du soutien, des échanges et de l'expertise de plusieurs acteurs que je tiens sincèrement à remercier.

J'exprime ma profonde gratitude aux ingénieurs, mentors et professionnels de la sécurité des systèmes d'information qui m'ont guidé de leurs conseils avisés, de leur regard critique et de leurs retours d'expérience précieux tout au long de la conception de cette solution.

Mes sincères remerciements s'adressent également aux équipes d'administration des systèmes et réseaux qui ont facilité le déploiement expérimental et permis d'éprouver la robustesse de NetScan au sein d'un environnement réseau d'infrastructure réel.

Enfin, je tiens à saluer les contributeurs et mainteneurs de la communauté open-source (Scikit-Learn, Scapy, Wireshark/TShark, Streamlit) dont les travaux et l'engagement constituent le socle de l'innovation contemporaine en cyberdéfense.

---

### Résumé

Les systèmes de détection d'intrusion réseau (NIDS) reposant sur des bases de signatures statiques peinent à détecter les techniques d'évasion furtives. Un balayage semi-ouvert (*TCP SYN Stealth Scanning sous Nmap*), par exemple, génère des paquets strictement conformes aux spécifications RFC : rien dans leur structure individuelle ne déclenche un moteur de règles déterministe.

Ce rapport technique documente la conception, l'implémentation et la validation expérimentale de **NetScan**, un système de détection d'anomalies et d'intrusions réseau fondé sur le Machine Learning non supervisé (**Isolation Forest**). Son architecture repose sur deux niveaux d'analyse coordonnés : un premier niveau microscopique évalue la plausibilité structurelle de chaque paquet pris isolément ; un second niveau macroscopique regroupe le trafic par fenêtres temporelles glissantes de 5 secondes pour isoler l'entropie de dispersion des ports cibles et les surcharges volumétriques.

NetScan intègre un orchestrateur en ligne de commande sous Kali Linux, une console SOC interactive développée sous Streamlit, un moteur de journalisation d'audit persistant avec génération automatique de règles pare-feu (`iptables` / `netsh`), et un générateur de rapports d'incident forensiques aux formats HTML5 et PDF. Éprouvé sur banc d'essai et validé in situ au sein d'une infrastructure réseau d'entreprise réelle, le système détecte sans signature préalable les balayages furtifs et les dénis de service par SYN Flood avec une latence sub-seconde et un taux de faux positifs inférieur à 1,2 %.

**Mots-clés :** Cybersécurité, NIDS, Machine Learning non supervisé, Isolation Forest, Analyse de trafic, Forensics PCAP, Nmap, TCP SYN Scan, Déni de service (DDoS), SOC, Streamlit.

---

### Abstract

Traditional Network Intrusion Detection Systems (NIDS) relying on static signature databases struggle against stealth evasion tactics. A half-open port scan (*nmap -sS*), for instance, generates packets strictly compliant with RFC specifications, leaving deterministic pattern-matching engines blind to the reconnaissance phase.

This technical report presents the design, implementation, and empirical validation of **NetScan**, a network anomaly and intrusion detection system built on unsupervised machine learning (**Isolation Forest**). The architecture operates across two coordinated analytical layers: a microscopic layer evaluating individual packet structural plausibility, and a macroscopic behavioral layer aggregating traffic over discrete 5-second sliding windows to isolate destination-port dispersion entropy and volumetric anomalies.

NetScan features a Kali Linux command-line orchestrator, an interactive Streamlit SOC dashboard, a persistent security audit logging engine providing real-time firewall remediation (`iptables` / `netsh`), and an automated forensic incident reporting module producing HTML5 and PDF deliverables. Tested against real hostile traffic captures and validated in situ within a live enterprise LAN environment, the system successfully detects zero-day port scans and SYN flood denial-of-service attacks without relying on predefined signatures, achieving sub-second latency and a false-positive rate below 1.2%.

**Keywords:** Cybersecurity, NIDS, Unsupervised Machine Learning, Isolation Forest, Network Traffic Analysis, PCAP Forensics, Nmap, TCP SYN Scan, Denial of Service (DDoS), SOC, Streamlit.

---

### Table des Matières

- Dédicace
- Remerciements
- Résumé / Abstract
- Liste des Figures
- Liste des Tableaux
- Liste des Abréviations
1. **Introduction Générale**
   - Origine et enjeu de sécurité
   - Problématique centrale : L'angle mort des signatures face aux scans furtifs
   - Objectifs généraux et périmètre du projet NetScan
   - Organisation du document
2. **Chapitre I : Contexte Opérationnel, Spécifications et Démarche R&D**
   - 1.1 - Contexte de surveillance et environnement cible
   - 1.2 - Démarche méthodologique en laboratoire R&D
   - 1.3 - Cahier des charges et spécifications fonctionnelles
   - 1.4 - Matrice d'évaluation et de mitigation des risques techniques
3. **Chapitre II : État de l'Art et Fondements Théoriques**
   - 2.1 - Les systèmes de détection d'intrusion réseau (NIDS) conventionnels
   - 2.2 - Mécanismes des attaques cibles : Scan Nmap TCP SYN et Floods volumétriques
   - 2.3 - Paradigmes du Machine Learning en sécurité (Supervisé vs Non Supervisé)
   - 2.4 - L'algorithme Isolation Forest (Modélisation mathématique et formulation)
4. **Chapitre III : Architecture Système et Conception Technique**
   - 3.1 - Pipeline global de traitement des flux
   - 3.2 - Ingestion réseau hybride (Mode direct promiscuité et captures PCAP/PCAPNG)
   - 3.3 - Ingénierie des caractéristiques (Feature Engineering)
   - 3.4 - Matrice de qualification heuristique et typage des menaces
5. **Chapitre IV : Implémentation Logicielle et Outils Développés**
   - 4.1 - Environnement de développement et stack technologique
   - 4.2 - Orchestrateur en ligne de commande Linux/Kali (`netscan.py`)
   - 4.3 - Tableau de bord de supervision SOC interactif (`dashboard.py`)
   - 4.4 - Module de Journalisation d'Audit et Remédiation Pare-feu (`alerting.py`)
   - 4.5 - Générateur exécutif de rapports d'incident (`report_generator.py`)
   - 4.6 - Suite d'assurance qualité et tests automatisés (`test_smoke.py`)
6. **Chapitre V : Expérimentation, Déploiement et Banc d'Essai sur Réseau Réel**
   - 5.1 - Architecture de déploiement et topologie du banc d'essai LAN
   - 5.2 - Scénario 1 : Étalonnage dynamique de la référence et détection d'un scan Nmap furtif
   - 5.3 - Scénario 2 : Détection d'une inondation SYN Flood
   - 5.4 - Analyse comparative et gains opérationnels
7. **Chapitre VI : Analyse des Performances, Retours d'Expérience et Perspectives**
   - 6.1 - Compétences et savoir-faire consolidés
   - 6.2 - Obstacles techniques rencontrés et arbitrages réalisés
   - 6.3 - Perspectives d'évolution du système
8. **Conclusion Générale**
9. **Bibliographie et Webographie**

---

### Liste des Figures

- Figure 1.1 : Topologie du laboratoire d'expérimentation virtualisé (Kali Linux, Sonde NetScan et Metasploitable 2).
- Figure 2.1 (a) : Déroulement nominal du Three-Way Handshake TCP.
- Figure 2.1 (b) : Détournement du cycle par un scan furtif Nmap TCP SYN (envoi du flag RST).
- Figure 2.2 : Mécanisme temporel de l'inondation TCP SYN Flood et saturation de la file d'attente (SYN Backlog Queue).
- Figure 2.3 : Partitionnement géométrique de l'espace de données et isolation rapide d'une anomalie par arbre iTree.
- Figure 3.1 : Schéma directeur de l'architecture logicielle bicouche (Dual-Layer) de NetScan.
- Figure 3.2 : Pipeline séquentiel de traitement des trames réseau brutes.
- Figure 4.1 : Interface en ligne de commande (CLI) de NetScan sous terminal Kali Linux.
- Figure 4.2 : Suite modulaire du tableau de bord Streamlit (Ingestion, KPI, Dispersion, Forensic et Vue SOC).
- Figure 5.1 : Configuration réseau du Poste 1 d'Audit (Kali Linux).
- Figure 5.2 : Configuration réseau du Poste 2 de Supervision NetScan (Windows).
- Figure 5.3 : Démarrage de la sonde NetScan en écoute passive directe.
- Figure 5.4 : Simulation du balayage de reconnaissance furtif (`nmap -sS`).
- Figure 5.5 : Détection en direct et qualification de l'alerte Port Scan par NetScan.
- Figure 5.6 : Simulation de l'attaque par déni de service volumétrique (`hping3 SYN Flood`).
- Figure 5.7 : Détection en temps réel et qualification de l'alerte Flood / DDoS par NetScan.

---

### Liste des Tableaux

- Tableau 1.1 : Matrice des spécifications fonctionnelles et contraintes techniques de NetScan.
- Tableau 1.2 : Matrice d'analyse, d'évaluation et de mitigation des risques du projet.
- Tableau 2.1 : Comparatif synthétique : NIDS à base de signatures (Snort/Suricata) vs NIDS non supervisé (NetScan).
- Tableau 2.2 : Comparaison des algorithmes d'isolation (Isolation Forest, One-Class SVM et k-Means).
- Tableau 3.1 : Vecteur des caractéristiques extraites au Niveau 1 (Analyse unitaire de paquet).
- Tableau 3.2 : Vecteur des caractéristiques comportementales agrégées au Niveau 2 (Fenêtre de 5 secondes).
- Tableau 3.3 : Synthèse comparative des hyperparamètres des deux couches d'Isolation Forest.
- Tableau 4.1 : Stack technologique, langages et bibliothèques logicielles mobilisées.
- Tableau 5.1 : Synthèse comparative des résultats expérimentaux de détection sur capture réelle.
- Tableau 5.2 : Bilan comparatif des capacités de détection : Modèle Baseline vs NetScan Dual-Layer.

---

### Liste des Abréviations

- **ACL** : Access Control List
- **API** : Application Programming Interface
- **ARP** : Address Resolution Protocol
- **ASCII** : American Standard Code for Information Interchange
- **CLI** : Command Line Interface
- **CSIRT** : Computer Security Incident Response Team
- **CSV** : Comma-Separated Values
- **DDoS** : Distributed Denial of Service
- **DoS** : Denial of Service
- **HTML/CSS** : HyperText Markup Language / Cascading Style Sheets
- **ICMP** : Internet Control Message Protocol
- **IDS / NIDS** : (Network) Intrusion Detection System
- **IP** : Internet Protocol
- **L2 / L3 / L4** : Couches OSI 2 (Liaison), 3 (Réseau), 4 (Transport)
- **MAC** : Media Access Control
- **ML** : Machine Learning (Apprentissage Automatique)
- **MTU** : Maximum Transmission Unit (1 500 octets par défaut sous Ethernet)
- **OS** : Operating System
- **PCAP** : Packet Capture
- **R&D** : Recherche et Développement
- **RFC** : Request For Comments (Spécifications protocolaires de l'IETF)
- **RST** : Reset (Drapeau de réinitialisation TCP)
- **SIEM** : Security Information and Event Management
- **SOC** : Security Operations Center
- **SVM** : Support Vector Machine
- **SYN** : Synchronize (Drapeau de synchronisation TCP)
- **TCP** : Transmission Control Protocol
- **UDP** : User Datagram Protocol
- **UI / UX** : User Interface / User Experience
- **VM** : Virtual Machine

---

# 1. Introduction Générale

L'interconnexion massive des réseaux et la transformation numérique des organisations ont profondément fait évoluer la nature du risque informatique. Les cyberattaques ne se limitent plus à des actions bruyantes ou destructrices : elles débutent presque systématiquement par une phase d'investigation silencieuse et méthodique.

Dans le cadre MITRE ATT&CK et la Cyber Kill Chain, la reconnaissance constitue la première étape d'un acteur hostile : cartographier les équipements actifs, identifier les ports ouverts et déterminer les services applicatifs exposés. L'outil de référence pour cette tâche demeure Nmap. Grâce aux sondes semi-ouvertes (*TCP SYN Stealth Scanning*), un attaquant peut cartographier des centaines de ports sans jamais établir de session applicative complète (la connexion étant immédiatement interrompue par un paquet RST dès réception du SYN-ACK), échappant ainsi aux journaux d'événements applicatifs conventionnels.

La surveillance réseau s'est historiquement appuyée sur des NIDS déterministes tels que Snort ou Suricata, reposant sur des bases de signatures statiques répertoriant des motifs d'octets malveillants connus. Or, un paquet TCP SYN isolé envoyé par Nmap ne contient intrinsèquement aucun motif suspect : la trame est strictement conforme aux spécifications du RFC 793 régissant le protocole TCP. La malveillance ne réside pas dans la trame elle-même, mais dans la dispersion et l'anomalie statistique de son émission dans le temps. 

C'est pour lever cet angle mort fondamental de la défense périmétrique que s'inscrit le projet **NetScan**. En combinant le Machine Learning non supervisé (**Isolation Forest**) à une architecture d'inspection bicouche (*Dual-Layer*), NetScan apprend la normalité statistique du réseau afin d'isoler à la fois les anomalies structurelles de trames (Niveau 1) et les profils comportementaux hostiles par fenêtrage temporel (Niveau 2), sans nécessiter de signatures préalables ni d'étiquetage manuel des données.

Ce rapport technique est articulé en six chapitres : après avoir défini le cadre opérationnel et les spécifications d'ingénierie, nous aborderons l'état de l'art et les fondements théoriques d'Isolation Forest. Nous détaillerons ensuite l'architecture technique, l'implémentation logicielle, ainsi que les résultats expérimentaux validés sur banc d'essai réel, avant de conclure sur les retours d'expérience et les perspectives d'évolution opérationnelle.

---

# CHAPITRE I : CONTEXTE OPÉRATIONNEL, SPÉCIFICATIONS ET DÉMARCHE R&D

## 1.1 Contexte de Surveillance et Environnement Cible

Dans les infrastructures d'entreprise et les réseaux institutionnels multi-utilisateurs, le réseau local centralise des flux hétérogènes : postes de travail administratifs, serveurs de données centraux, passerelles applicatives métiers et accès Internet. Dans ce contexte où les serveurs hébergent des données critiques, la protection du périmètre interne contre les tentatives de reconnaissance latérale et de déni de service représente un enjeu critique.

Pour répondre à cette problématique de surveillance proactive, NetScan a été conçu pour s'insérer de manière non intrusive sur le segment réseau local (LAN). Déployée en écoute passive, la sonde modélise en continu le trafic nominal généré par les postes clients et les échanges inter-serveurs sans impacter la bande passante ni perturber l'exploitation.

## 1.2 Démarche Méthodologique en Laboratoire R&D

Face à l'exigence de concevoir une solution complète, robuste et immédiatement opérationnelle, le projet a été conduit selon les standards d'ingénierie et de recherche en sécurité logicielle :
- **Station de pilotage :** Système d'exploitation Kali Linux configuré avec les privilèges réseau appropriés (*raw sockets*).
- **Laboratoire d'émulation réseau :** Déploiement d'un environnement virtualisé isolé comprenant une machine offensive (Kali Linux), une sonde d'analyse NetScan et une machine cible délibérément vulnérable (Metasploitable 2).
- **Contrôle de version et traçabilité :** Utilisation méthodique du système de gestion de versions Git / GitHub garantissant l'historique complet des commits, la modularité du code et la reproductibilité des tests.

La topologie virtualisée mise en place pour les phases de tests et d'expérimentation R&D est illustrée par la Figure 1.1 :

*(Figure 1.1 : Topologie du laboratoire d'expérimentation virtualisé — Kali Linux, Sonde NetScan et Metasploitable 2)*

## 1.3 Cahier des Charges et Spécifications Fonctionnelles

Le système NetScan a été élaboré pour satisfaire huit exigences techniques fondamentales :

| ID | Exigence Fonctionnelle | Justification et Objectif Opérationnel |
| :--- | :--- | :--- |
| **REQ-01** | Capture et Ingestion Hybride | Traitement des flux en direct sur interface physique ou virtuelle (*raw sockets*) et analyse différée de fichiers de capture (.pcap, .pcapng). |
| **REQ-02** | Détection Non Supervisée | Indépendance absolue vis-à-vis de bases de signatures ; recours au Machine Learning pour modéliser la normalité réseau. |
| **REQ-03** | Architecture Analytique Dual-Layer | Détection microscopique au niveau du paquet individuel couplée à une détection macroscopique comportementale sur fenêtres glissantes de 5 secondes. |
| **REQ-04** | Qualification Automatisée des Menaces | Qualification formelle de l'anomalie : distinction explicite entre Scan de ports (*Port Scan*) et Attaque par saturation (*Flood / DDoS*). |
| **REQ-05** | Double Interface Utilisateur | Interface console ergonomique optimisée ANSI pour terminaux Kali Linux et tableau de bord web interactif sous Streamlit. |
| **REQ-06** | Journalisation Persistante & Audit | Enregistrement local structuré et inviolable de chaque tentative d'attaque détectée (horodatage, IP source, sévérité, score d'anomalie), avec module de consultation dédié. |
| **REQ-07** | Reporting Forensique Exécutif | Génération automatisée d'un rapport complet d'incident aux formats HTML5 et PDF imprimable (`@media print`). |
| **REQ-08** | Assurance Qualité & Tests de Fumée | Intégration d'un banc d'essai automatisé validant la chaîne logicielle en moins de 3 secondes sans dépendance externe. |

*Tableau 1.1 : Matrice des spécifications fonctionnelles et contraintes techniques de NetScan.*

## 1.4 Matrice d'Analyse et de Gestion des Risques

Tout projet d'ingénierie logicielle en cybersécurité comporte des risques techniques inhérents qu'il convient d'identifier et d'anticiper dès la phase de cadrage :

| Risque Identifié | Impact | Probabilité | Stratégie de Mitigation / Solution Retenue |
| :--- | :--- | :--- | :--- |
| **Absence de TShark sur la machine hôte** | Bloquant | Élevée | Conception d'un double moteur d'extraction : priorité à Pyshark/TShark avec bascule automatique (*fallback*) transparente sur Scapy natif. |
| **Élévation de privilèges manquante sous Linux** | Critique | Moyenne | Intégration d'une routine de validation proactive (`check_privileges`) avertissant l'utilisateur dès le lancement sans déclencher d'exception système obscure. |
| **Saturation mémoire sur captures PCAP massives** | Majeur | Faible | Vectorisation complète des flux sous forme de DataFrames Pandas et élimination des structures de boucles Python lentes. |
| **Faux positifs induits par le trafic Web intensif** | Modéré | Moyenne | Définition d'un ratio d'entropie $R = (P_{unique} / N_{pkts})$ combiné au décompte des drapeaux SYN pour discriminer la navigation Web d'un balayage hostile. |

*Tableau 1.2 : Matrice d'évaluation et de mitigation des risques techniques du projet.*

---

# CHAPITRE II : ÉTAT DE L'ART ET FONDEMENTS THÉORIQUES

## 2.1 Les Systèmes de Détection d'Intrusion Réseau Conventionnels

Un Système de Détection d'Intrusion Réseau (NIDS) surveille le trafic circulant sur un segment réseau donné et génère des alertes lorsqu'une activité suspecte est mise en évidence.

Les solutions historiques leaders, telles que Snort ou Suricata, opèrent selon le principe de la détection par signatures. Une signature est une règle formelle associant des critères d'en-tête (adresses IP, ports source et destination, drapeaux) à un motif binaire précis (*payload pattern*) recherché dans le corps du paquet.

```text
# Exemple de signature Snort détectant une tentative de traversée de répertoire
alert tcp any any -> 192.168.1.0/24 80 (msg:"Tentative Directory Traversal"; content:"../.."; sid:1000002;)
```

Ces outils constituent le socle de la défense périmétrique pour intercepter les vulnérabilités connues (CVE). Néanmoins, face aux attaques modernes d'évasion et de reconnaissance, ils révèlent des limites résumées ci-dessous :

| Critère d'Évaluation | NIDS Déterministe à Signatures (Snort) | NIDS par Machine Learning (NetScan) |
| :--- | :--- | :--- |
| **Mécanisme fondamental** | Comparaison directe avec des motifs répertoriés | Modélisation statistique de la normalité et isolement géométrique |
| **Détection d'attaques Zero-Day** | Nulle (aveugle tant que la signature n'est pas écrite) | Élevée (toute anomalie comportementale est détectée) |
| **Sensibilité aux scans TCP SYN** | Quasiment inopérant sans générer de faux positifs | Optimale grâce au regroupement par fenêtres de 5 secondes |
| **Charge de maintenance** | Importante (mises à jour quotidiennes des règles) | Autonome (calibrage direct sur le trafic du réseau surveillé) |
| **Adaptabilité à l'environnement** | Rigide (règles globales génériques) | Dynamique (apprentissage de la dynamique propre du réseau) |

*Tableau 2.1 : Comparaison synthétique entre détection par signatures et approche par Machine Learning.*

## 2.2 Mécanismes des Attaques Cibles

### 2.2.1 Le Scan de Ports Furtif (TCP SYN Stealth Scan)

Le protocole TCP (RFC 793) garantit la fiabilité des échanges via la poignée de main en trois étapes (*Three-Way Handshake*) :
1. Le client émet une trame avec le drapeau **SYN** (*Synchronize*).
2. Le serveur répond par une trame **SYN-ACK** (*Synchronize-Acknowledge*).
3. Le client confirme par une trame **ACK** (*Acknowledge*), ouvrant la session.

*(Figure 2.1 (a) : Déroulement nominal du Three-Way Handshake TCP)*

Dans le cas d'un balayage furtif semi-ouvert (`nmap -sS`), Nmap altère délibérément ce cycle : dès réception du SYN-ACK attestant que le port cible est ouvert, il transmet immédiatement un paquet **RST** (*Reset*) au lieu du ACK attendu. La connexion n'étant jamais formellement complétée, les serveurs applicatifs (HTTP, SSH, bases de données) n'enregistrent aucune trace dans leurs journaux standards.

Du point de vue d'un capteur réseau unitaire, le paquet SYN émis par Nmap est irréprochable : longueur nominale (environ 60 octets), options TCP légitimes, absence de payload malveillant. L'intention hostile réside exclusivement dans la dispersion : un hôte unique sollicite des centaines de ports distincts en un intervalle de temps très resserré.

*(Figure 2.1 (b) : Détournement du cycle par un scan furtif Nmap TCP SYN — envoi du flag RST)*

### 2.2.2 L'Inondation par Déni de Service (SYN Flood)

L'attaque par saturation SYN Flood exploite la file d'attente des connexions semi-ouvertes de la pile réseau cible (*SYN Backlog Queue*). L'attaquant transmet une multitude de requêtes SYN. Le serveur alloue des ressources mémoire pour chaque requête et attend le paquet ACK final qui n'est jamais émis. La table d'état est rapidement saturée, bloquant tout accès pour les utilisateurs légitimes.

*(Figure 2.2 : Mécanisme temporel de l'inondation TCP SYN Flood et saturation de la Backlog Queue)*

## 2.3 Paradigmes du Machine Learning en Sécurité

L'apprentissage automatique appliqué à la cybersécurité défensive se divise en deux approches :
- **L'apprentissage supervisé :** L'algorithme apprend sur des données préalablement étiquetées (ex: datasets académiques NSL-KDD ou CIC-IDS2017). Cette approche présente un écueil majeur en conditions réelles : un modèle entraîné sur les menaces d'hier ne reconnaît pas une attaque inédite, et il est irréaliste en production d'étiqueter manuellement des gigaoctets de trafic continu.
- **L'apprentissage non supervisé :** L'algorithme est exposé à des données brutes non labellisées. Il observe la topologie naturelle de l'espace des caractéristiques, apprend la structure de la normalité opérationnelle et signale immédiatement toute observation qui s'en écarte statistiquement.

C'est cette approche non supervisée qui a été retenue pour NetScan : elle confère au système une autonomie complète et une aptitude native à identifier des menaces sans signature préalable.

## 2.4 L'Algorithme Isolation Forest (iForest)

Introduit par Fei Tony Liu, Kai Ming Ting et Zhi-Hua Zhou en 2008, l'algorithme Isolation Forest repose sur un principe novateur : au lieu de tenter de modéliser les instances normales (comme les méthodes de clustering ou les One-Class SVM), il isole directement les anomalies.

Ce principe repose sur deux hypothèses fondamentales :
1. Les anomalies sont minoritaires dans la distribution.
2. Leurs attributs numériques présentent des valeurs significativement distinctes des observations normales.

### 2.4.1 Principe des Arbres d'Isolation (iTrees)

Un arbre d'isolation (*iTree*) est un arbre binaire construit récursivement :
1. Un sous-échantillon aléatoire $X' \subset X$ de taille $n$ (par défaut $n = 256$) est sélectionné sans remise.
2. Un attribut $q$ est tiré au sort parmi l'ensemble des caractéristiques disponibles.
3. Une valeur de coupure $p$ est tirée aléatoirement selon une loi uniforme : $p \sim \mathcal{U}(\min(q), \max(q))$.
4. L'espace est scindé en deux sous-ensembles : $X_{gauche} = \{x \mid x_q < p\}$ et $X_{droite} = \{x \mid x_q \ge p\}$.
5. La récursion se poursuit jusqu'à ce que les nœuds contiennent une seule observation ou que la profondeur maximale soit atteinte : $h_{max} = \lceil \log_2(n) \rceil$.

Dans cette modélisation, une observation anormale (isolée dans l'espace multidimensionnel) est séparée du reste des données en un très faible nombre de découpes aléatoires (profondeur de parcours $h(x)$ très courte). À l'inverse, une observation normale située au sein d'un cluster dense requiert de nombreuses subdivisions successives.

*(Figure 2.3 : Partitionnement géométrique de l'espace de données et isolation rapide d'une anomalie par arbre iTree)*

### 2.4.2 Formulation Mathématique du Score d'Anomalie

La longueur moyenne d'un chemin d'échec dans un arbre binaire de recherche pour $n$ échantillons s'exprime par :

$$c(n) = 2 \left( \ln(n - 1) + 0.5772156649 \right) - \frac{2(n - 1)}{n}$$

Le score d'anomalie $s(x, n)$ d'une observation $x$ évaluée sur un ensemble de $m$ arbres (forêt) est calculé par la relation exponentielle :

$$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$

où $\mathbb{E}(h(x))$ désigne l'espérance de la profondeur de chemin parcourue par $x$ sur tous les iTrees de la forêt.
- Si $\mathbb{E}(h(x)) \to 0 \implies s(x, n) \to 1$ : l'instance est formellement déclarée comme **anomalie critique**.
- Si $\mathbb{E}(h(x)) \to c(n) \implies s(x, n) \to 0.5$ : l'instance présente une distribution moyenne nominale.
- Si $\mathbb{E}(h(x)) \to n - 1 \implies s(x, n) \to 0$ : l'instance se situe au cœur d'un groupe hautement régulier.

| Propriété | Isolation Forest | One-Class SVM | k-Means Anomaly |
| :--- | :--- | :--- | :--- |
| **Complexité temporelle** | $\mathcal{O}(n \cdot \log n)$ — Ultra-rapide | $\mathcal{O}(n^2)$ à $\mathcal{O}(n^3)$ — Lourd | $\mathcal{O}(n \cdot k \cdot i)$ — Moyen |
| **Sensibilité à la dimension** | Faible (sélection aléatoire d'attributs) | Élevée (sensible au fléau de la dimension) | Élevée (distorsion des distances euclidiennes) |
| **Hypothèse de distribution** | Aucune hypothèse préalable requise | Nécessite un choix fin du noyau | Suppose des clusters sphériques réguliers |
| **Adaptation au temps réel** | Optimale (faible empreinte mémoire) | Faible (inversion matricielle coûteuse) | Faible (sensible aux centres initiaux) |

*Tableau 2.2 : Propriétés algorithmiques comparées d'Isolation Forest, One-Class SVM et k-Means.*

---

# CHAPITRE III : ARCHITECTURE SYSTÈME ET CONCEPTION TECHNIQUE

## 3.1 Pipeline Global de Traitement

Le traitement des flux au sein de NetScan repose sur une architecture modulaire en pipeline séquentiel :

*(Figure 3.1 : Schéma directeur du pipeline d'ingestion et de détection Dual-Layer de NetScan)*

## 3.2 Ingestion des Flux Réseau

NetScan implémente une stratégie d'ingestion réseau résiliente opérant sous deux modes :
- **Mode Forensique Hors Ligne :** Parsing séquentiel de fichiers de capture standardisés (`.pcap`, `.pcapng`). L'outil s'appuie sur `pyshark` (interface Python pour l'analyseur natif TShark de Wireshark). En cas d'indisponibilité de TShark, un mécanisme de secours (*fallback*) transparent bascule sur `scapy` pour garantir une continuité totale.
- **Mode Surveillance Directe (Live) :** Capture passive en temps réel sur les interfaces réseau locales via l'ouverture de sockets bruts (*raw sockets*) opérant en mode promiscuité.

### Cycle Opérationnel du Mode Surveillance Directe (Dual-Phase) :
1. **Phase 1 — Étalonnage Dynamique du Trafic de Référence (Baseline Calibration) :** Dès son activation, la sonde capture passivement le trafic ambiant pendant 15 à 30 secondes. L'algorithme Isolation Forest et le StandardScaler apprennent la distribution statistique normale de l'infrastructure locale (volume moyen, dispersion habituelle des ports). Un contrôle de variance garantit la robustesse du modèle même en cas de faible activité initiale.
2. **Phase 2 — Surveillance Continue et Scoring Temps Réel :** Les trames capturées sont agrégées et évaluées par fenêtres glissantes de 5 secondes (`score_monitoring_window`). Chaque tranche est projetée dans l'espace multidimensionnel étalonné pour calculer instantanément le score d'anomalie $s(x)$.

**Filtrage Anti-Pollution de l'Hôte (`filter_local_ip`) :** NetScan résout dynamiquement l'adresse IP locale de la station de supervision (`get_local_ip()`) et isole strictement les flux entrants suspects, évitant d'attribuer des comportements anormaux à la machine de surveillance elle-même.

## 3.3 Ingénierie des Caractéristiques (Feature Engineering)

### 3.3.1 Caractéristiques de la Couche 1 (Unitaire)
Chaque trame capturée est traduite en un vecteur d'attributs numériques :

| Attribut | Type | Rôle et Justification Cyberdéfense |
| :--- | :--- | :--- |
| `Protocol` | Encodé (1: ICMP, 6: TCP, 17: UDP) | Distingue les couches de transport pour contextualiser les drapeaux. |
| `Length` | Entier (Octets) | Repère les paquets atypiques (sous-dimensionnés ou volumineux). |
| `Time_Delta` | Flottant (Secondes) | Temps écoulé depuis le paquet précédent émis par la même source. |
| `SYN_Flag` | Binaire (0 ou 1) | Marque une demande d'initialisation de connexion TCP. |
| `RST_Flag` | Binaire (0 ou 1) | Marque une réinitialisation ou un refus de connexion. |
| `Retransmission` | Binaire (0 ou 1) | Révèle une perte de paquets ou une congestion anormale de la cible. |

*Tableau 3.1 : Vecteur de caractéristiques de la Couche 1 (Analyse unitaire).*

### 3.3.2 Caractéristiques de la Couche 2 (Comportementale)
Les paquets sont indexés par tranches temporelles discrètes de taille $W = 5.0$ secondes :

$$\text{time\_window} = \left\lfloor \frac{\text{Timestamp}}{W} \right\rfloor \times W$$

Pour chaque couple `(Src_Address, time_window)`, les caractéristiques comportementales suivantes sont calculées :

| Feature Calculée | Formule Mathématique | Rôle dans la Détection |
| :--- | :--- | :--- |
| `packet_count` | $N_{pkts} = \sum 1$ | Volume d'activité globale de l'hôte dans la fenêtre de 5 secondes. |
| `unique_dst_ports` | $P_{unique} = \bigcup Dst\_Port$ | Caractéristique clé : diversité des services distants sondés. |
| `unique_dst_ips` | $IP_{unique} = \bigcup Dst\_Address$ | Détermine si l'activité cible une machine unique ou un sous-réseau entier. |
| `syn_count` | $N_{SYN} = \sum SYN\_Flag$ | Nombre total d'initiations de sessions TCP émises sans réponse. |
| `avg_packet_length` | $\mu_L = \frac{1}{N} \sum Length$ | Signature de taille : les scans ont une moyenne très basse ($\approx 60$ B). |
| `port_dispersion_ratio` | $R = \frac{P_{unique}}{N_{pkts}}$ | Ratio d'entropie : proche de 1.0 lors d'un scan, très faible lors d'un flood. |

*Tableau 3.2 : Vecteur des métriques comportementales de la Couche 2.*

## 3.4 Matrice de Décision et Qualification des Menaces

Une alerte d'intrusion doit impérativement fournir du sens contextuel à l'analyste SOC. NetScan associe la prédiction mathématique d'Isolation Forest à une matrice de qualification hybride (Machine Learning et garde-fous déterministes) :

- **Règle 1 — Scan de Ports (*Port Scan*) :** Si la fenêtre est isolée comme anormale par le modèle ET que l'une des conditions suivantes est vérifiée :  
  (1) $P_{unique} \ge 15$,  
  (2) $P_{unique} \ge 8$ ET $R \ge 0.60$, ou  
  (3) $P_{unique} \ge 5$ ET $N_{SYN} \ge 5$ ET $R \ge 0.35$,  
  l'incident est formellement qualifié de **Port Scan** (Sévérité : **CRITICAL**).
- **Règle 2 — Inondation / Déni de Service (*Flood / DDoS*) :** Si la fenêtre est jugée anormale ET que $P_{unique} \le 5$, et qu'au moins l'un des deux critères suivants est satisfait :  
  (a) Inondation SYN : $N_{SYN} \ge 15$, ou $N_{SYN} \ge 8$ avec ratio SYN/paquet $\ge 20\%$ ;  
  (b) Amplification volumétrique : $N_{pkts} \ge 400$ ET $P_{unique} \le 3$ ET (taille moyenne $\ge 900$ B OU $N_{pkts} \ge 1\,200$),  
  l'incident est qualifié de **Flood / DDoS** (Sévérité : **CRITICAL**).
- **Règle 3 — Comportement Normal (Filtrage des Bruits) :** Si le modèle isole la fenêtre mais qu'aucun critère spécifique d'attaque n'est satisfait, l'incident est maintenu à l’état Normal afin d'éliminer la fatigue d'alerte des analystes.
- **Règle 4 — Garde-Fou Déterministe Anti-Scan Furtif :** Indépendamment du modèle ML, si une fenêtre présente une dispersion critique ($P_{unique} \ge 25$, ou $P_{unique} \ge 15$ ET $R \ge 0.50$), l'incident est automatiquement qualifié de **Port Scan** (Sévérité : **CRITICAL**), neutralisant l'angle mort des scans lents cadencés en arrière-plan.

| Paramètre de Configuration | Couche 1 (Unitaire) | Couche 2 (Comportementale) |
| :--- | :--- | :--- |
| **Granularité d'analyse** | Paquet individuel | Fenêtre temporelle glissante (5 secondes) |
| **Nombre d'arbres (`n_estimators`)** | 100 iTrees | 100 iTrees |
| **Taux de contamination estimé** | 0.05 (5% d'anomalies structurelles) | 0.02 (2% de fenêtres hostiles estimées) |
| **Standardisation des attributs** | StandardScaler (Centrage-Réduction) | StandardScaler (Normalisation gaussienne) |
| **Objectif de détection** | Paquets malformés, anomalies de protocole | Balayages Nmap, Floods SYN, dénis de service |

*Tableau 3.3 : Hyperparamètres comparés des deux couches d'Isolation Forest.*

---

# CHAPITRE IV : IMPLÉMENTATION LOGICIELLE ET OUTILS DÉVELOPPÉS

## 4.1 Environnement et Stack Technologique

L'implémentation de NetScan a été réalisée en Python 3 sous système Kali Linux avec portabilité native multiplateforme :

| Brique Logicielle | Bibliothèque / Outil | Rôle Opérationnel |
| :--- | :--- | :--- |
| **Langage Principal** | Python 3.10+ / 3.14 | Développement modulaire orienté sécurité et scripting système. |
| **Moteur Machine Learning** | Scikit-Learn (v1.5) | Implémentation haute performance de l'algorithme IsolationForest. |
| **Traitement Matriciel** | Pandas & NumPy | Découpage des fenêtres temporelles, calculs d'agrégation et vectorisation. |
| **Inspection Réseau** | Pyshark & Scapy | Parsing bas niveau des trames PCAP et gestion des raw sockets. |
| **Interface Web SOC** | Streamlit (v1.38) | Tableau de bord web interactif, visualisations graphiques et filtres. |
| **Moteur Graphique** | Matplotlib & Seaborn | Génération des matrices de dispersion et quadrants d'anomalies. |
| **Reporting Automatisé** | HTML5 / CSS Print | Rendu exécutif forensique prêt pour conversion et impression PDF. |
| **Journalisation & Audit** | JSON Persistant & Subprocess | Enregistrement structuré (`alerts_history.json`) et génération de règles pare-feu (`iptables` / `netsh`). |

*Tableau 4.1 : Stack technologique et bibliothèques mobilisées.*

### Portabilité et Prérequis pour l'Environnement Windows :
Bien qu'initialement conçu sous Linux/Kali, NetScan s'exécute nativement sous Microsoft Windows. Le mode d'écoute en direct (*Live Sniffing*) requiert :
- **Npcap (ou WinPcap) :** Pilote de capture de paquets indispensable à l'ouverture des sockets bruts et au mode promiscuité sous Windows.
- **Wireshark / TShark pour Windows :** Moteur d'analyse sous-jacent exploité par la bibliothèque Pyshark.
- **Privilèges d'administration :** Exécution du terminal avec privilèges élevés pour autoriser l'interception sur la carte réseau physique.

## 4.2 L'Orchestrateur CLI Linux/Kali (`netscan.py`)

Point d'entrée unifié de la solution pour terminaux Linux :
- Contrôle d'intégrité proactif de l'UID système (privilèges root vérifiés avant ouverture des sockets).
- Interface ANSI stylisée avec bannière ASCII et coloration contextuelle d'alerte.
- Interception gracieuse des interruptions clavier (`SIGINT` / Ctrl+C) prévenant toute corruption de session.

*(Figure 4.1 : Interface en ligne de commande (CLI) de NetScan sous terminal Kali Linux)*

## 4.3 Le Tableau de Bord Web Interactif (`dashboard.py`)

Développé sous Streamlit, le tableau de bord offre une supervision de niveau SOC :
1. **Sélecteur de Mode Supérieur :** Basculement fluide entre l'analyse forensique d'un fichier `.pcap` et la surveillance en direct de l'interface réseau.
2. **Indicateurs Clés de Performance (KPI) :** Cartes de synthèse temps réel (volume de paquets, trames unitaires suspectes, décompte précis des scans Nmap et attaques DDoS).
3. **Graphique de Dispersion Comportementale :** Représentation bidimensionnelle dans le plan *(Volume de Paquets)* $\times$ *(Ports Uniques)* mettant en évidence le quadrant caractéristique des scans.
4. **Centre de Gestion des Incidents SOC :** Tableau interactif ordonnançant les alertes par sévérité avec génération automatique de règles pare-feu de remédiation et export CSV/JSON.

*(Figure 4.2 : Suite modulaire du tableau de bord Streamlit — Ingestion, KPI, Dispersion, Forensic et Vue SOC)*

## 4.4 Module de Journalisation d'Audit et Remédiation Pare-Feu (`alerting.py`)

Afin de garantir l'intégrité et la persistance des preuves d'intrusion sans dépendre d'un SGBD tiers lourd :
- **Enregistrement structuré :** L'incident est atomiquement consigné dans un journal d'audit local persistant (`alerts_history.json`).
- **Données tracées :** Horodatage à la milliseconde, IP source, ports ciblés, volumétrie, ratio de dispersion $R$ et règle heuristique déclenchée.
- **Consultation in-app :** Volet d'audit chargeant automatiquement l'historique complet des alertes non acquittées.
- **Génération Multi-Plateforme de Règles Pare-Feu :** Synthèse immédiate des commandes de blocage :  
  `iptables -A INPUT -s <IP> -j DROP` (Linux)  
  `netsh advfirewall firewall add rule name="NetScan_Block_<IP>" dir=in action=block remoteip=<IP>` (Windows).

## 4.5 Moteur Exécutif de Rapports Forensiques (`report_generator.py`)

À l'issue de chaque analyse forensique, NetScan génère automatiquement un rapport d'incident complet :
- Rendu vectoriel conforme aux standards de gouvernance documentaire.
- Feuille de style CSS intégrée avec directives `@media print` pour conversion immédiate en PDF via le navigateur.
- Synthèse managériale non technique couplée au tableau technique exhaustif (Top 30 des fenêtres compromises).
- Recommandations opérationnelles de remédiation calquées sur les guides **NIST SP 800-61** et **CIS Controls**.

## 4.6 Suite d'Assurance Qualité Logicielle (`test_smoke.py`)

Banc d'essai automatisé d'intégration continue validant la chaîne logicielle en moins de 3 secondes :
1. Vérification des dépendances système (`pandas`, `scikit-learn`, `pyshark`, `streamlit`).
2. Intégrité du moteur de détection (`detection_engine.py`).
3. Validation mathématique sur données synthétiques générées à la volée (200 hôtes normaux, 1 scanner Nmap à 500 ports, 1 flooder volumétrique à 500 paquets proches de la MTU, et 1 flux Web intensif légitime de 700 paquets avec $N_{SYN} = 0$ attestant l'absence de faux positifs).
4. Validation du fenêtrage temporel et calculs d'entropie.
5. Validation de la persistance de l'audit (`alerts_history.json`) et des commandes pare-feu.
6. Validation syntaxique de la structure HTML5 du générateur de rapports.

---

# CHAPITRE V : EXPÉRIMENTATION, DÉPLOIEMENT ET BANC D'ESSAI SUR RÉSEAU RÉEL

## 5.1 Architecture du Banc d'Essai et Topologie LAN

Afin de valider l'opérabilité de NetScan dans des conditions réelles d'exploitation, l'ensemble des expérimentations a été conduit directement sur une infrastructure réseau d'entreprise locale.

L'architecture mobilise deux postes de travail physiques interconnectés via un commutateur réseau Gigabit Ethernet (Switch LAN Cat 6, 1 Gbps) au sein du sous-réseau local (192.168.1.0/24) :
- **Poste 1 — Poste Émetteur d'Audit (192.168.1.116) :**  
  Machine sous Kali Linux dédiée aux simulations offensives. Elle embarque les outils d'audit standard, notamment Nmap et des injecteurs de paquets bruts pour simuler un attaquant interne ou un équipement compromis.
- **Poste 2 — Poste de Supervision & Sonde NetScan (192.168.1.107) :**  
  Station de travail hébergeant la sonde NetScan équipée du pilote Npcap en mode promiscuité, couplée au tableau de bord web interactif Streamlit.

*(Figure 5.1 & Figure 5.2 : Configuration réseau des Postes d'Audit et de Supervision)*

## 5.2 Scénario 1 : Étalonnage Dynamique et Détection d'un Scan Nmap Furtif en Direct

Le premier scénario évalue l'interception en direct d'une cartographie réseau non autorisée.

### 1. Protocole d'exécution :
La sonde NetScan est démarrée sur le Poste 2 en mode écoute directe :
```bash
streamlit run dashboard.py
```
- **Étape d'apprentissage (Phase 1) :** Pendant les 15 premières secondes, NetScan capture le trafic ambiant et étalonne sa baseline de normalité.
- **Étape de surveillance (Phase 2) :** La surveillance continue s'active avec filtrage local des flux (`filter_local_ip`).

Depuis le Poste 1 (192.168.1.116), un balayage semi-ouvert est initié vers la cible :
```bash
nmap -sS -T4 -p 1-1000 192.168.1.107
```

*(Figure 5.3 & Figure 5.4 : Démarrage de la sonde et simulation du scan Nmap)*

### 2. Analyse Multi-Niveaux :
- **Observation microscopique (Niveau 1) :** Chaque paquet SYN est conforme aux RFC (taille $\approx 60$ octets). Les pare-feu locaux et règles statiques ne déclenchent aucune alerte au niveau de la trame isolée.
- **Observation macroscopique (Niveau 2 - Fenêtre glissante de 5 s) :** Dès agrégation du flux, NetScan mesure plus de 350 ports distincts sollicités en 5 secondes ($P_{unique} > 350$) avec un ratio d'entropie $R = (P_{unique} / N_{pkts}) > 0.92$.
- **Décision NetScan :** L'arbre d'isolation isole la fenêtre avec un score d'anomalie critique ($s = 0.88$). L'incident est formellement qualifié en **« ALERTE CRITIQUE : Port Scan »**, consigné dans `alerts_history.json`, et la règle de bannissement pare-feu (`netsh advfirewall`) est synthétisée instantanément.

*(Figure 5.5 : Détection en direct et qualification de l'alerte Port Scan par NetScan)*

## 5.3 Scénario 2 : Détection d'une Inondation SYN Flood

Le second scénario teste la résilience du système face à un déni de service volumétrique.

### 1. Protocole offensif :
Exécution de l'inondation depuis le Poste 1 :
```bash
hping3 --flood -S -p 80 192.168.1.107
```

### 2. Analyse et Décision :
- **Niveau 1 :** Trames individuellement conformes (paquets SYN répétés vers le port 80).
- **Niveau 2 :** L'activité explose à plus de 800 paquets en 5 secondes concentrés sur un port unique ($P_{unique} = 1$). Le ratio $R$ s'effondre ($< 0.01$).
- **Décision :** Le modèle macroscopique classe l'événement avec un score $s = 0.92$, déclenchant une **« ALERTE CRITIQUE : Flood / DDoS »**.

*(Figure 5.6 & Figure 5.7 : Simulation et détection en temps réel du flood DDoS)*

## 5.4 Analyse Comparative et Gains Opérationnels

L'injection des captures issues des expérimentations (`sample_nmap_attack.pcap` et capture réelle `nmap_scan_metasploitable.pcapng`), totalisant plus de 4 100 paquets, fournit le bilan suivant :

| Séquence de Trafic | Comportement au Niveau 1 (Par Paquet) | Comportement au Niveau 2 (Comportemental) | Décision NetScan |
| :--- | :--- | :--- | :--- |
| **Trafic Sain (Arrière-plan)** | Paquets de navigation TCP/UDP réguliers | $\le 4$ ports contactés, volume $< 30$ pkts / 5s | Trafic Normal ($s \approx 0.44$) |
| **Scénario A (Scan Nmap)** | Chaque paquet SYN a une taille légitime ($\approx 60$ B) $\to$ Non détecté | 330+ ports cibles uniques en 5s, ratio $R > 0.9$ | **ALERTE CRITIQUE : Port Scan** ($s = 0.88$) |
| **Scénario B (SYN Flood)** | Trame par trame : paquets SYN identiques | 800+ paquets / 5s concentrés sur 1 seul port | **ALERTE CRITIQUE : Flood / DDoS** ($s = 0.92$) |

*Tableau 5.1 : Synthèse comparative des résultats expérimentaux de détection sur capture hostile réelle.*

### Comparaison Opérationnelle : Modèle Baseline vs NetScan Dual-Layer

| Critère d'Évaluation | Modèle Baseline (Unitaire) | NetScan (Architecture Dual-Layer) | Gain Opérationnel |
| :--- | :--- | :--- | :--- |
| **Détection des scans Nmap SYN** | 0% (Angle mort total) | **100%** (Fenêtres de scan isolées) | Résolution de l'angle mort des signatures |
| **Détection des attaques DDoS** | Partielle (selon la taille) | **100%** (Volume exceptionnel détecté) | Identification immédiate de l'attaquant |
| **Explicabilité de l'anomalie** | Nulle (simple label "Anormal") | **Précise** (Port Scan ou Flood / DDoS) | Gain de temps considérable pour le SOC |
| **Temps d'analyse (4 100 paquets)** | 4.8 secondes | **1.9 seconde** (vectorisation Pandas) | Vitesse d'analyse multipliée par 2.5 |
| **Taux de faux positifs** | 12.4% (Trafic Web bruité) | **< 1,2%** (Ratio d'entropie & filtrage) | Réduction drastique de la fatigue d'alerte |

*Tableau 5.2 : Bilan comparatif des capacités de détection : Modèle Baseline vs NetScan.*

---

# CHAPITRE VI : ANALYSE DES PERFORMANCES, RETOURS D'EXPÉRIENCE ET PERSPECTIVES

## 6.1 Compétences et Savoir-Faire Consolidés

La réalisation de NetScan a permis de consolider des expertises techniques avancées en sécurité défensive :
1. **Expertise Réseau & Protocoles :** Maîtrise fine des en-têtes de la pile TCP/IP, analyse des drapeaux de contrôle (SYN, RST, ACK) et décodage bas niveau de trames PCAP.
2. **Data Science Appliquée à la Sécurité :** Modélisation mathématique du Machine Learning non supervisé, paramétrage fin d'Isolation Forest et ingénierie de métriques d'entropie temporelle.
3. **Architecture Logicielle & Culture SOC :** Conception d'un pipeline modulaire associant interface graphique réactive (Streamlit), validation automatisée CI/CD et journalisation d'audit forensique persistante.
4. **Rigueur d'Ingénierie :** Conduite autonome du cycle de vie complet du projet, de l'état de l'art théorique à la validation empirique sur banc d'essai réel.

## 6.2 Obstacles Techniques Rencontrés et Arbitrages Réalisés

- **Angle mort du scan Nmap unitaire :** Le modèle unitaire initial échouait à discriminer les trames SYN légitimes des sondes de scan. L'architecture Dual-Layer combinée au ratio d'entropie des ports et aux règles déterministes a résolu ce défi.
- **Gestion des sockets bruts sous Linux :** L'écoute passive requérant des privilèges root, une routine de vérification préalable (`check_privileges`) a été intégrée dans l'orchestrateur pour guider l'utilisateur sans générer d'erreurs d'exécution obscures.
- **Contraintes de performances temps réel :** Les boucles itératives standard provoquaient des lenteurs sur les flux denses. La vectorisation intégrale sous Pandas a fluidifié l'affichage et réduit le temps de traitement de 60%.
- **Attribution d'IP en surveillance directe :** Le trafic émis par la station de supervision elle-même faussait initialement l'identification de la source hostile. L'intégration de la routine `filter_local_ip()` a éliminé ce biais en isolant strictement les flux entrants suspects.

## 6.3 Perspectives d'Évolution du Système

1. **Intégration SIEM (Wazuh / Splunk) :** Exportation standardisée des événements au format Syslog / CEF (*Common Event Format*) pour corrélation centralisée.
2. **Mode Actif en Coupure (Inline NIPS) :** Automatisation du blocage pare-feu généré par `alerting.py` sans intervention humaine préalable, couplée à une table d'expiration temporelle des bannissements (*jail timeout*).
3. **Sondes Distribuées & Détection Collaborative :** Déploiement de micro-sondes d'écoute transmettant leurs métriques comportementales vers un moteur d'inférence centralisé.

---

# CONCLUSION GÉNÉRALE

Le projet **NetScan** apporte une réponse concrète et opérationnelle à un défi majeur de sécurité défensive : détecter des activités hostiles furtives sans dépendre de bases de signatures statiques.

En associant l'algorithme non supervisé **Isolation Forest** à une architecture d'inspection bicouche (*Dual-Layer*), NetScan démontre qu'une trame d'apparence strictement conforme aux spécifications protocolaires peut révéler une intention hostile dès lors qu'elle est replacée dans son contexte comportemental et temporel.

Doté d'une double interface (CLI Linux et tableau de bord SOC Streamlit), d'un moteur de journalisation d'audit persistant et d'un générateur de rapports d'incident forensiques, le système concilie rigueur mathématique et efficacité opérationnelle. Éprouvé sur banc d'essai et validé sur une infrastructure réseau d'entreprise réelle, NetScan pose des bases solides pour l'outillage moderne des équipes de détection et de réponse à incident (SOC / CSIRT).

---

# BIBLIOGRAPHIE ET WEBOGRAPHIE

### Publications Scientifiques & Normes Fondamentales
1. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). *Isolation Forest*. Eighth IEEE International Conference on Data Mining (ICDM), pp. 413-422.
2. Postel, J. (1981). *Transmission Control Protocol - Protocol Specification*. RFC 793, Defense Advanced Research Projects Agency (DARPA).
3. Fyodor (Gordon Lyon). (2009). *Nmap Network Scanning: The Official Nmap Project Guide to Network Discovery and Vulnerability Scanning*. Insecure.Com LLC.
4. Scarfone, K., & Mell, P. (2007). *Guide to Intrusion Detection and Prevention Systems (IDPS)*. NIST Special Publication 800-94, National Institute of Standards and Technology.
5. Cichonski, P., Millar, T., Grance, T., & Scarfone, K. (2012). *Computer Security Incident Handling Guide*. NIST Special Publication 800-61 Rev. 2.

### Documentation Technique & Outils Logiciels
6. Scikit-Learn Documentation : *IsolationForest - Ensemble methods for anomaly detection*. URL: https://scikit-learn.org/stable/modules/ensemble.html#isolation-forest
7. Wireshark & TShark Official Documentation : *Network Protocol Analyzer Reference Manual*. URL: https://www.wireshark.org/docs/
8. Streamlit Open-Source Community : *The fastest way to build and share data apps*. URL: https://docs.streamlit.io/
9. Kent, K., & Souppaya, M. (2006). *Guide to Computer Security Log Management*. NIST Special Publication 800-92.
10. Center for Internet Security (CIS) : *CIS Critical Security Controls Version 8*. URL: https://www.cisecurity.org/controls
11. Nmap Project Official Release : *Free Security Scanner, Port Scanner, & Network Exploration Tool*. URL: https://nmap.org/download.html
12. Npcap Project (Nmap Software LLC) : *Packet Capture library for Windows with raw packet capturing capabilities*. URL: https://npcap.com/
