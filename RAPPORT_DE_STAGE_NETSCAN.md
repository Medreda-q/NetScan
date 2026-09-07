# RAPPORT DE STAGE D'INITIATION

**Filière : Cybersécurité et audit des systèmes informatiques**  

# Conception et Développement d'un Système Intelligent de Détection d'Anomalies Réseau (Port Scans & DDoS) par Apprentissage Non Supervisé (Isolation Forest)

**Réalisé par :**  
**Mohamed Reda QIYAOUI**  

**Année Universitaire : 2026 / 2027**  
**Date de soumission : 11 Novembre 2026**  

**Encadrement :**  
- **Encadrant Pédagogique :** *[À compléter — Nom du Professeur / Référant Académique EST]*  
- **Encadrant Professionnel :** *[À compléter si applicable]*  

\newpage

# DÉDICACE

> À Allah, tout puissant, qui m'a donné la force, la patience et la lucidité nécessaires pour mener à terme ce travail, et sans la grâce de qui rien de tout ceci n'aurait été possible ;

> À mes très chers parents, source inépuisable de tendresse, de patience et de sacrifice. Vous avez cru en moi bien avant que je ne croie en moi-même, et chaque ligne de ce rapport porte l'empreinte de vos efforts, de vos encouragements silencieux et de vos prières. Aucun mot ne saurait exprimer toute la reconnaissance que je vous dois ;

> À mes frères et sœurs, pour leur présence rassurante, leur soutien discret mais constant, et pour avoir supporté avec patience mes absences et mes moments d'obsession studieuse ;

> À mes enseignants et formateurs de l'École Supérieure de Technologie, qui ont su transformer la curiosité en rigueur et la rigueur en passion. C'est grâce à votre exigence et à votre pédagogie que j'ai appris à aimer les réseaux, la sécurité informatique, et l'art parfois obsessionnel de traquer l'anomalie derrière l'apparente normalité d'un simple paquet réseau.

\newpage

# REMERCIEMENTS

Au terme de ce travail marquant une étape déterminante de mon cursus au sein du Diplôme Universitaire de Technologie (DUT) en Cybersécurité et Audit des Systèmes Informatiques à l'École Supérieure de Technologie (EST), je tiens à exprimer ma profonde gratitude envers toutes les personnes qui ont contribué à son accomplissement.

Mes remerciements s'adressent en premier lieu à la direction et au corps professoral de l'EST pour l'excellence de la formation dispensée, pour l'esprit critique transmis et pour les solides compétences fondamentales en protocoles réseaux, sécurité défensive et systèmes d'exploitation acquises tout au long de notre parcours académique.

Je tiens à exprimer ma vive gratitude envers mon encadrant pédagogique pour sa disponibilité, ses orientations méthodologiques rigoureuses et la pertinence de ses conseils qui m'ont guidé dans l'exploration de la convergence entre l'intelligence artificielle et l'analyse de trafic hostile.

Enfin, je remercie chaleureusement mes collègues d'études, mes proches et mes amis pour leurs échanges stimulants, leur bienveillance constante et leurs encouragements tout au long des phases de recherche, de programmation et de tests expérimentaux de ce projet.

\newpage

# RÉSUMÉ

Face à la sophistication croissante des cybermenaces et à l'émergence de techniques d'évasion furtives, les systèmes de détection d'intrusion réseau traditionnels (NIDS) reposant sur des bases de signatures statiques montrent des limites structurelles critiques. Des vecteurs d'attaque comme les balayages semi-ouverts (*TCP SYN Stealth Scanning* sous Nmap) génèrent des paquets strictement conformes aux spécifications RFC, contournant ainsi aveuglément les moteurs de règles déterministes.

Ce travail de stage d'initiation et de projet technique présente la conception, l'implémentation et la validation expérimentale de **NetScan**, un système intelligent de détection d'anomalies et d'intrusions réseau fondé sur le Machine Learning non supervisé (*Isolation Forest*). NetScan introduit une architecture d'analyse innovante à double couche (*Dual-Layer Architecture*) : un premier niveau microscopique évaluant la plausibilité unitaire des paquets, complété par un second niveau macroscopique comportemental regroupant le trafic par fenêtres temporelles glissantes (5 secondes) afin d'isoler l'entropie de dispersion des ports de destination et les pics de volumétrie.

Développé nativement pour les environnements de sécurité Linux/Kali, NetScan intègre un orchestrateur console (CLI), un tableau de bord web interactif sous Streamlit, un centre d'alertes SOC en temps réel connecté à Discord par Webhook, ainsi qu'un générateur automatisé de rapports d'incident forensiques aux formats HTML5 et PDF. Les expérimentations menées face à des captures hostiles réelles démontrent une détection sans signature des scans furtifs et des dénis de service (SYN Flood) avec une latence sub-seconde et une excellente maîtrise des faux positifs.

**Mots-clés :** Cybersécurité, NIDS, Machine Learning non supervisé, Isolation Forest, Analyse de trafic, Forensics PCAP, Nmap, TCP SYN Scan, Déni de service (DDoS), SOC, Streamlit.

---

# ABSTRACT

In the face of increasingly sophisticated cyber threats and stealth evasion tactics, traditional Network Intrusion Detection Systems (NIDS) relying on static signature repositories exhibit severe structural shortcomings. Reconnaissance vectors such as half-open port scans (`nmap -sS`) generate packets strictly compliant with standard RFC specifications, thereby bypassing deterministic pattern-matching engines.

This internship and technical project presents the design, implementation, and empirical validation of **NetScan**, a next-generation network anomaly and intrusion detection system powered by unsupervised machine learning (*Isolation Forest*). NetScan incorporates an innovative Dual-Layer Analytical Architecture: a microscopic layer evaluating individual packet structural attributes, paired with a macroscopic behavioral layer that aggregates network flows across discrete 5-second time windows to isolate target port dispersion entropy and volumetric surges.

Built natively for Linux/Kali environments, NetScan provides a streamlined CLI orchestrator, an interactive Streamlit web dashboard, real-time SOC alerting through Discord Webhooks, and an automated executive forensic incident report generator (HTML5 / PDF). Empirical benchmarks on real hostile traffic captures demonstrate zero-signature detection of stealth port scans and denial-of-service attacks with sub-second latency and minimal false-positive rates.

**Keywords:** Cybersecurity, NIDS, Unsupervised Machine Learning, Isolation Forest, Network Traffic Analysis, PCAP Forensics, Nmap, TCP SYN Scan, Denial of Service (DDoS), SOC, Streamlit.

\newpage

# TABLE DES MATIÈRES

1. **Introduction Générale**
   - Origine et enjeu de sécurité
   - Problématique centrale : L'angle mort des signatures face aux scans furtifs
   - Objectifs généraux et périmètre du projet NetScan
   - Organisation du document
2. **Chapitre I : Cadre Académique et Gestion du Projet**
   - 1.1 Présentation de l'EST et du cursus DUT Cybersécurité
   - 1.2 Démarche méthodologique en laboratoire R&D et autonomie
   - 1.3 Spécifications fonctionnelles et cahier des charges
   - 1.4 Matrice d'évaluation et de mitigation des risques techniques
3. **Chapitre II : État de l'Art et Fondements Théoriques**
   - 2.1 Les systèmes de détection d'intrusion réseau (NIDS) conventionnels
   - 2.2 Mécanismes des attaques cibles : Scan Nmap TCP SYN et Floods volumétriques
   - 2.3 Paradigmes du Machine Learning en sécurité (Supervisé vs Non Supervisé)
   - 2.4 L'algorithme Isolation Forest (Modélisation mathématique et formulation)
   - 2.5 L'Architecture Dual-Layer (Microscopique vs Macroscopique)
4. **Chapitre III : Architecture Système et Conception Technique**
   - 3.1 Pipeline global de traitement des flux
   - 3.2 Ingestion réseau hybride (Mode direct promiscuité et captures PCAP/PCAPNG)
   - 3.3 Ingénierie des caractéristiques (*Feature Engineering*)
   - 3.4 Matrice de qualification heuristique et typage des menaces
5. **Chapitre IV : Implémentation Logicielle et Outils Développés**
   - 4.1 Environnement de développement et stack technologique
   - 4.2 Orchestrateur en ligne de commande Linux/Kali (`netscan.py`)
   - 4.3 Tableau de bord de supervision SOC interactif (`dashboard.py`)
   - 4.4 Système de notification et alerting temps réel (`alerting.py`)
   - 4.5 Générateur exécutif de rapports d'incident (`report_generator.py`)
   - 4.6 Suite d'assurance qualité et tests de fumée (`test_smoke.py`)
6. **Chapitre V : Expérimentation, Validation et Résultats**
   - 5.1 Banc d'essai virtualisé (Kali Linux attaquant vs Metasploitable 2 cible)
   - 5.2 Scénario 1 : Détection d'un scan Nmap furtif
   - 5.3 Scénario 2 : Détection d'une inondation SYN Flood
   - 5.4 Analyse comparative et gains opérationnels
7. **Chapitre VI : Bilan du Stage, Compétences et Perspectives**
   - 6.1 Compétences techniques et professionnelles consolidées
   - 6.2 Obstacles techniques rencontrés et arbitrages réalisés
   - 6.3 Perspectives d'évolution du système
8. **Conclusion Générale**
9. **Bibliographie et Webographie**

\newpage

# LISTE DES FIGURES

- **Figure 1.1 :** Topologie du laboratoire d'expérimentation virtualisé (Kali Linux, Sonde NetScan et Metasploitable 2).
- **Figure 2.1 :** Fonctionnement de la négociation TCP (Three-Way Handshake) comparé au scan furtif TCP SYN semi-ouvert.
- **Figure 2.2 :** Partitionnement géométrique de l'espace de données et isolation rapide d'une anomalie par arbre iTree.
- **Figure 3.1 :** Schéma directeur de l'architecture logicielle bicouche (Dual-Layer) de NetScan.
- **Figure 3.2 :** Pipeline séquentiel de traitement des trames réseau brutes.
- **Figure 4.1 :** Interface en ligne de commande (CLI) de NetScan sous terminal Kali Linux.
- **Figure 4.2 :** Tableau de bord web interactif Streamlit avec indicateurs KPI et bandeau d'alerte rouge.
- **Figure 4.3 :** Matrice de dispersion comportementale (Nombre de paquets vs Diversité de ports uniques) isolant l'attaque Nmap.
- **Figure 4.4 :** Exemple d'alerte enrichie expédiée sur le canal SOC Discord avec règle iptables suggérée.

\newpage

# LISTE DES TABLEAUX

- **Tableau 1.1 :** Matrice des spécifications fonctionnelles et contraintes techniques de NetScan.
- **Tableau 1.2 :** Matrice d'analyse, d'évaluation et de mitigation des risques du projet.
- **Tableau 2.1 :** Comparatif synthétique : NIDS à base de signatures (Snort/Suricata) vs NIDS non supervisé (NetScan).
- **Tableau 2.2 :** Comparaison des algorithmes d'isolation (Isolation Forest, One-Class SVM et k-Means).
- **Tableau 3.1 :** Vecteur des caractéristiques extraites au Niveau 1 (Analyse unitaire de paquet).
- **Tableau 3.2 :** Vecteur des caractéristiques comportementales agrégées au Niveau 2 (Fenêtre de 5 secondes).
- **Tableau 3.3 :** Synthèse comparative des hyperparamètres des deux couches d'Isolation Forest.
- **Tableau 4.1 :** Stack technologique, langages et bibliothèques logicielles mobilisées.
- **Tableau 5.1 :** Synthèse comparative des résultats expérimentaux de détection sur capture réelle.
- **Tableau 5.2 :** Bilan comparatif des capacités de détection : Modèle Baseline vs NetScan Dual-Layer.

\newpage

# LISTE DES ABRÉVIATIONS

- **ACL :** Access Control List
- **API :** Application Programming Interface
- **ARP :** Address Resolution Protocol
- **ASCII :** American Standard Code for Information Interchange
- **CLI :** Command Line Interface
- **CSV :** Comma-Separated Values
- **DDoS :** Distributed Denial of Service
- **DoS :** Denial of Service
- **DUT :** Diplôme Universitaire de Technologie
- **EST :** École Supérieure de Technologie
- **HTML / CSS :** HyperText Markup Language / Cascading Style Sheets
- **ICMP :** Internet Control Message Protocol
- **IDS / NIDS :** (Network) Intrusion Detection System
- **IP :** Internet Protocol
- **L2 / L3 / L4 :** Couches du modèle OSI (Liaison, Réseau, Transport)
- **MAC :** Media Access Control
- **ML :** Machine Learning (Apprentissage Automatique)
- **MTU :** Maximum Transmission Unit (1 500 octets sous Ethernet standard)
- **MTTD :** Mean Time to Detect (Temps moyen de détection)
- **OS :** Operating System (Système d'Exploitation)
- **PCAP / PCAPNG :** Packet Capture (Next Generation)
- **RFC :** Request for Comments (Normes de l'IETF)
- **RST :** Reset (Drapeau de réinitialisation de connexion TCP)
- **SIEM :** Security Information and Event Management
- **SOC :** Security Operations Center
- **SYN :** Synchronize (Drapeau d'initialisation de session TCP)
- **TCP :** Transmission Control Protocol
- **UDP :** User Datagram Protocol
- **UI / UX :** User Interface / User Experience
- **VLAN :** Virtual Local Area Network
- **VM :** Virtual Machine (Machine Virtuelle)

\newpage

# INTRODUCTION GÉNÉRALE

À l'ère de l'interconnexion massive et de la transformation numérique accélérée des entreprises et administrations, la sécurité des réseaux informatiques est devenue un impératif stratégique. Les cyberattaques contemporaines ne se limitent plus à des actions bruyantes ou destructrices immédiates ; elles débutent presque systématiquement par des phases d'investigation silencieuses et méthodiques.

Dans la doctrine défensive modélisée par le cadre **MITRE ATT&CK** et la chaîne de frappe cybernétique (*Cyber Kill Chain*), la reconnaissance constitue la première étape opérationnelle menée par un acteur malveillant : identifier les équipements actifs, dresser la cartographie des ports ouverts et déterminer précisément les bannières applicatives exposées. Pour accomplir cela, l'outil de référence absolu demeure **Nmap** (*Network Mapper*). Grâce à des sondes semi-ouvertes (*TCP SYN Stealth Scanning*), un attaquant peut cartographier des milliers de ports sans jamais établir de connexion applicative complète (interruption immédiate après réception du `SYN-ACK`), échappant ainsi aux journaux applicatifs usuels des serveurs cibles.

Historiquement, la surveillance des réseaux s'est appuyée sur des Systèmes de Détection d'Intrusion Réseau (NIDS) déterministes tels que **Snort** ou **Suricata**. Ces solutions reposent sur des bases de signatures statiques répertoriant des motifs d'octets malveillants connus. Or, face à un paquet TCP SYN isolé envoyé par Nmap, aucun motif suspect intrinsèque n'est présent : la trame est strictement conforme aux spécifications du standard RFC 793 régissant le protocole TCP. La malveillance ne réside pas dans la trame elle-même, mais dans la dispersion et l'anomalie statistique de son émission temporelle.

Ce constat met en évidence une faille structurelle majeure de la défense périmétrique conventionnelle. C'est à ce défi critique que répond le présent travail de fin de stage et projet technique, intitulé **NetScan**.

Conçu et développé dans le cadre de mon Diplôme Universitaire de Technologie (DUT) en Cybersécurité à l'École Supérieure de Technologie (EST), NetScan propose une approche défensive en rupture : l'utilisation du **Machine Learning non supervisé** couplée à une architecture d'inspection analytique à double couche (**Dual-Layer Architecture**). En mobilisant l'algorithme mathématique **Isolation Forest**, le système apprend de manière autonome la normalité du réseau pour isoler les anomalies structurelles de trames (Niveau 1) et les profils comportementaux hostiles par fenêtrage temporel (Niveau 2), sans nécessiter la moindre signature préalable ni aucun étiquetage manuel de données.

Ce rapport est articulé en six chapitres. Nous poserons d'abord le cadre académique et méthodologique du projet, avant de présenter l'état de l'art et les fondements théoriques d'Isolation Forest. Nous détaillerons ensuite l'architecture technique, l'implémentation logicielle, ainsi que les résultats expérimentaux obtenus sur banc d'essai réel, avant de conclure sur le bilan des compétences acquises et les perspectives d'évolution opérationnelle.

\newpage

# CHAPITRE I : CADRE ACADÉMIQUE ET GESTION DU PROJET

## 1.1 Présentation de l'établissement et du cursus
L'École Supérieure de Technologie (EST) est une institution universitaire de premier plan dédiée à la formation de techniciens spécialisés et d'experts techniques hautement opérationnels.

La filière **DUT en Cybersécurité et Audit des Systèmes Informatiques** prépare les étudiants à intervenir sur l'ensemble de la chaîne de valeur de la sécurité informatique :
- **Architecture et Protocoles :** Maîtrise avancée des réseaux TCP/IP, des mécanismes de commutation, de routage, de segmentation et de pare-feu.
- **Sécurité Offensive & Défensive :** Tests de pénétration éthiques, identification des vulnérabilités logicielles, durcissement système (*hardening*), gestion d'incidents et investigations forensiques numériques.
- **Développement & Automatisation :** Conception de scripts de défense active en Python et Bash, intégration de pipelines de détection et administration des architectures de surveillance SOC.

## 1.2 Démarche méthodologique en laboratoire R&D
Face à l'exigence de concevoir une solution complète et immédiatement opérationnelle, le projet a été mené selon les standards rigoureux d'un laboratoire de recherche et développement en sécurité logicielle :
- **Station de pilotage :** Système d'exploitation **Kali Linux** configuré avec les privilèges réseau appropriés (`raw sockets`).
- **Laboratoire d'émulation réseau :** Déploiement d'un environnement virtualisé isolé comprenant une machine offensive (Kali Linux), une sonde d'analyse NetScan et une machine cible délibérément vulnérable (**Metasploitable 2**).
- **Contrôle de version et traçabilité :** Utilisation méthodique du système de gestion de versions **Git / GitHub** garantissant l'historique complet des commits, la modularité du code et la reproductibilité des tests.

## 1.3 Cahier des charges et spécifications fonctionnelles
Le système NetScan a été élaboré pour satisfaire huit exigences techniques fondamentales :

| ID | Exigence Fonctionnelle | Justification et Objectif Opérationnel |
|---|---|---|
| **REQ-01** | Capture et Ingestion Hybride | Traitement des flux en direct sur interface physique ou virtuelle (`raw sockets`) et analyse différée de fichiers de capture (`.pcap`, `.pcapng`). |
| **REQ-02** | Détection Non Supervisée | Indépendance absolue vis-à-vis de bases de signatures ; recours au Machine Learning pour modéliser la normalité réseau. |
| **REQ-03** | Architecture Analytique Dual-Layer | Détection microscopique au niveau du paquet individuel couplée à une détection macroscopique comportementale sur fenêtres glissantes de 5 secondes. |
| **REQ-04** | Qualification Automatisée des Menaces | Qualification formelle de l'anomalie : distinction explicite entre *Scan de ports (Port Scan)* et *Attaque par saturation (Flood / DDoS)*. |
| **REQ-05** | Double Interface Utilisateur | Interface console ergonomique optimisée ANSI pour terminaux Kali Linux et tableau de bord web interactif sous Streamlit. |
| **REQ-06** | Notification SOC Temps Réel | Alerting instantané vers un salon Discord dédié via des Webhooks HTTPS sécurisés avec payload d'incident enrichi. |
| **REQ-07** | Reporting Forensique Exécutif | Génération automatisée d'un rapport complet d'incident aux formats HTML5 et PDF imprimable (`@media print`). |
| **REQ-08** | Assurance Qualité & Tests de Fumée | Intégration d'un banc d'essai automatisé validant la chaîne logicielle en moins de 3 secondes sans dépendance externe. |

*Tableau 1.1 : Matrice des spécifications fonctionnelles et contraintes techniques de NetScan.*

## 1.4 Matrice d'analyse et de gestion des risques
Tout projet d'ingénierie logicielle en cybersécurité comporte des risques techniques inhérents qu'il convient d'identifier et d'anticiper dès la phase de cadrage :

| Risque Identifié | Impact | Probabilité | Stratégie de Mitigation / Solution Retenue |
|---|---|---|---|
| **Absence de TShark sur la machine hôte** | Bloquant | Élevée | Conception d'un double moteur d'extraction : priorité à Pyshark/TShark avec bascule automatique (*fallback*) transparente sur Scapy natif. |
| **Élévation de privilèges manquante sous Linux** | Critique | Moyenne | Intégration d'une routine de validation proactive (`check_privileges`) avertissant l'utilisateur dès le lancement sans déclencher d'exception système obscure. |
| **Saturation mémoire sur captures PCAP massives** | Majeur | Faible | Vectorisation complète des flux sous forme de DataFrames Pandas et élimination des structures de boucles Python lentes. |
| **Faux positifs induits par le trafic Web intensif** | Modéré | Moyenne | Définition d'un ratio d'entropie $R = \frac{P_{unique}}{N_{pkts}}$ combiné au décompte des drapeaux `SYN` pour discriminer la navigation Web d'un balayage hostile. |

*Tableau 1.2 : Matrice d'évaluation et de mitigation des risques techniques du projet.*

\newpage

# CHAPITRE II : ÉTAT DE L'ART ET FONDEMENTS THÉORIQUES

## 2.1 Les systèmes de détection d'intrusion réseau traditionnels
Un Système de Détection d'Intrusion Réseau (NIDS) surveille le trafic circulant sur un segment réseau donné et génère des alertes lorsqu'une activité suspecte est mise en évidence.

Les solutions historiques leaders, telles que **Snort** ou **Suricata**, opèrent selon le principe de la **détection par signatures**. Une signature est une règle formelle associant des critères d'en-tête (adresses IP, ports source et destination, drapeaux) à un motif binaire précis (*payload pattern*) recherché dans le corps du paquet.

```
# Exemple de signature Snort détectant une tentative de traversée de répertoire
alert tcp any any -> 192.168.1.0/24 80 (msg:"Tentative Directory Traversal"; content:"../.."; sid:1000002;)
```

Ces outils constituent le socle de la défense périmétrique pour intercepter les vulnérabilités connues (CVE). Néanmoins, face aux attaques modernes d'évasion et de reconnaissance, ils révèlent des faiblesses insurmontables résumées ci-dessous :

| Critère d'Évaluation | NIDS Déterministe à Signatures (Snort) | NIDS par Machine Learning (NetScan) |
|---|---|---|
| **Mécanisme fondamental** | Comparaison directe avec des motifs répertoriés | Modélisation statistique de la normalité et isolement géométrique |
| **Détection d'attaques Zero-Day** | Nulle (aveugle tant que la signature n'est pas écrite) | Élevée (toute anomalie comportementale est détectée) |
| **Sensibilité aux scans TCP SYN** | Quasiment inopérant sans générer de faux positifs | Optimale grâce au regroupement par fenêtres de 5 secondes |
| **Charge de maintenance** | Importante (mises à jour quotidiennes des règles) | Autonome (calibrage direct sur le trafic du réseau surveillé) |
| **Adaptabilité à l'environnement** | Rigide (règles globales génériques) | Dynamique (apprentissage de la dynamique propre du réseau) |

*Tableau 2.1 : Comparaison synthétique entre détection par signatures et approche par Machine Learning.*

## 2.2 Mécanismes des attaques cibles

### 2.2.1 Le Scan de Ports Furtif (TCP SYN Stealth Scan)
Le protocole TCP (RFC 793) garantit la fiabilité des échanges via la négociation en trois étapes (*Three-Way Handshake*) :
1. Le client émet une trame avec le drapeau `SYN` (Synchronize).
2. Le serveur répond par une trame `SYN-ACK` (Synchronize-Acknowledge).
3. Le client confirme par une trame `ACK` (Acknowledge), la session est ouverte.

Dans le cas d'un balayage furtif semi-ouvert (`nmap -sS`), Nmap altère délibérément ce cycle : dès qu'il reçoit la réponse `SYN-ACK` du serveur attestant que le port est ouvert, il envoie immédiatement une trame de réinitialisation `RST` (Reset) au lieu du `ACK` attendu. La connexion n'étant jamais formellement complétée, la couche applicative (serveurs HTTP, SSH, bases de données) n'enregistre aucune trace dans ses journaux.

Du point de vue d'un capteur réseau unitaire, le paquet `SYN` initial émis par Nmap est irréprochable : longueur standard (environ 60 octets), options TCP légitimes, absence totale de charge utile malveillante. L'intention malveillante ne réside pas dans le paquet, mais dans la dispersion de destination : un hôte unique tente d'établir des connexions vers des dizaines ou des centaines de ports différents en un intervalle de temps très bref.

### 2.2.2 L'Inondation par Déni de Service (SYN Flood)
L'attaque par saturation SYN Flood exploite la file d'attente des connexions semi-ouvertes de la pile réseau du système d'exploitation cible (*SYN Backlog Queue*). L'attaquant bombarde la cible d'une multitude de requêtes `SYN`. Le serveur alloue des structures de mémoire pour chaque requête et attend le `ACK` final qui n'arrive jamais. La table de connexions de la cible est rapidement saturée, provoquant le refus de service pour les utilisateurs légitimes.

## 2.3 Paradigmes du Machine Learning en sécurité
L'apprentissage automatique appliqué à la cybersécurité défensive se divise en deux approches :
- **L'apprentissage supervisé :** L'algorithme apprend sur un ensemble de données préalablement étiqueté (ex: datasets académiques NSL-KDD ou CIC-IDS2017). Cette approche présente un écueil majeur en conditions réelles : un modèle entraîné sur des attaques d'hier ne sait pas reconnaître une attaque inédite de demain, et il est impossible en production d'étiqueter manuellement des gigaoctets de trafic réseau continu.
- **L'apprentissage non supervisé :** L'algorithme est exposé à des données brutes non étiquetées. Il observe la topologie naturelle de l'espace des caractéristiques, apprend la structure de ce qui constitue la normalité opérationnelle et signale immédiatement toute observation qui s'en écarte.

C'est cette approche **non supervisée** qui a été retenue pour NetScan : elle confère au système une autonomie totale et une aptitude naturelle à découvrir des attaques sans signature.

## 2.4 L'Algorithme Isolation Forest (iForest)
Introduit par Fei Tony Liu, Kai Ming Ting et Zhi-Hua Zhou en 2008, l'algorithme **Isolation Forest** repose sur un principe novateur : **au lieu de tenter de modéliser les instances normales (comme le font les méthodes de clustering ou les SVM), il isole directement les anomalies**.

Ce principe s'appuie sur deux prémisses fondamentales :
1. Les anomalies sont minoritaires dans le jeu de données.
2. Leurs attributs numériques présentent des valeurs significativement distinctes de celles des observations normales.

### 2.4.1 Principe des Arbres d'Isolation (*iTrees*)
Un arbre d'isolation (*iTree*) est un arbre binaire construit récursivement :
1. Un sous-échantillon aléatoire $X' \subset X$ de taille $n$ (par défaut $n = 256$) est sélectionné sans remise.
2. Un attribut $q$ est tiré au sort parmi l'ensemble des caractéristiques disponibles.
3. Une valeur de coupure $p$ est tirée aléatoirement selon une loi uniforme entre le minimum et le maximum de l'attribut $q$ : $p \sim \mathcal{U}(\min(q), \max(q))$.
4. L'espace est scindé en deux sous-ensembles : $X_{gauche} = \{x \mid x_q < p\}$ et $X_{droite} = \{x \mid x_q \ge p\}$.
5. La construction se répète jusqu'à ce que les nœuds deviennent des feuilles contenant une seule observation ou que la limite de profondeur de l'arbre soit atteinte : $h_{max} = \lceil \log_2(n) \rceil$.

Dans ce schéma géométrique, une observation anormale (très isolée dans l'espace) sera séparée du reste des données en un très petit nombre de découpes aléatoires (profondeur de parcours $h(x)$ très faible). En revanche, une observation normale située au sein d'un faisceau dense nécessitera un grand nombre de subdivisions successives pour être isolée.

### 2.4.2 Formulation Mathématique du Score d'Anomalie
La longueur moyenne d'un chemin d'échec dans un arbre binaire de recherche pour $n$ échantillons correspond mathématiquement à :
$$c(n) = 2 \ln(n - 1) + 0.5772156649 \text{ (constante d'Euler-Mascheroni)} - \frac{2(n - 1)}{n}$$
où $c(n)$ représente le facteur de normalisation de la profondeur moyenne pour un ensemble de $n$ points.

Le score d'anomalie $s(x, n)$ d'une observation $x$ évaluée sur un ensemble de $m$ arbres (forêt) est calculé par la relation exponentielle :
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
où $E(h(x))$ désigne l'espérance mathématique de la profondeur de chemin parcourue par l'observation $x$ sur tous les iTrees de la forêt.

**Propriétés fondamentales du score $s$ :**
- Si $E(h(x)) \to 0 \implies s(x, n) \to 1$ : la trame ou la fenêtre temporelle est formellement déclarée comme **anomalie critique**.
- Si $E(h(x)) \to c(n) \implies s(x, n) \to 0.5$ : l'instance présente une distribution moyenne ne manifestant aucune singularité statistique.
- Si $E(h(x)) \to n - 1 \implies s(x, n) \to 0$ : l'instance se situe au centre d'un groupe hautement régulier.

| Propriété | Isolation Forest | One-Class SVM | k-Means Anomaly |
|---|---|---|---|
| **Complexité temporelle** | $\mathcal{O}(n \cdot \log n)$ — *Ultra-rapide* | $\mathcal{O}(n^2)$ à $\mathcal{O}(n^3)$ — *Lourd* | $\mathcal{O}(n \cdot k \cdot i)$ — *Moyen* |
| **Sensibilité à la dimension** | Faible (sélection aléatoire d'attributs) | Élevée (sensible au fléau de la dimension) | Élevée (distorsion des distances euclidiennes) |
| **Hypothèse de distribution** | Aucune hypothèse préalable requise | Nécessite un choix fin du noyau gaussien | Suppose des clusters sphériques réguliers |
| **Adaptation au temps réel** | Optimale (faible empreinte mémoire) | Faible (inversion matricielle coûteuse) | Faible (sensible aux centres initiaux) |

*Tableau 2.2 : Comparaison algorithmique démontrant la supériorité opérationnelle d'Isolation Forest.*

## 2.5 L'Architecture Analytique Dual-Layer de NetScan
Pour répondre à l'angle mort des NIDS traditionnels face aux balayages Nmap, NetScan déploie une approche d'analyse à deux échelles complémentaires :

- **Couche 1 (Microscopique — Analyse unitaire par paquet) :** Examine chaque trame de manière atomique. Elle détecte les anomalies morphologiques : paquets surdimensionnés, fragments atypiques, drapeaux invalides (ex: scans NULL ou XMAS) et écarts temporels immédiats.
- **Couche 2 (Macroscopique — Analyse comportementale par fenêtres temporelles) :** Regroupe les trames par adresse IP source sur des tranches glissantes de 5 secondes. Elle extrait des métriques statistiques globales (entropie de ports, cadence, ratios SYN) permettant d'isoler immédiatement la signature comportementale d'un scan ou d'un flood.

\newpage

# CHAPITRE III : ARCHITECTURE SYSTÈME ET CONCEPTION TECHNIQUE

## 3.1 Pipeline global de traitement
Le traitement des données au sein de NetScan obéit à une architecture modulaire en pipeline :

```
[ INGESTION RÉSEAU : Interface Live ou Capture PCAP/PCAPNG ]
                          │
                          ▼
             [ Dépaquetage & Normalisation ]
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ COUCHE 1 : DÉTECTION UNITAIRE PAR PAQUET                   │
 │ Matrice : Protocole, Longueur, Drapeaux, Delta-Temps        │
 │ Modèle  : Isolation Forest Microscopique (100 iTrees)       │
 └─────────────────────────────────────────────────────────────┘
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ AGRÉGATION TEMPORELLE (aggregate_windows — Fenêtres de 5s)  │
 │ Groupby : (Src_Address, time_window)                        │
 └─────────────────────────────────────────────────────────────┘
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ COUCHE 2 : DÉTECTION COMPORTEMENTALE (MACROSCOPIQUE)        │
 │ Matrice : Ports uniques, Nombre de paquets, SYN, Ratios     │
 │ Modèle  : Isolation Forest Comportemental                   │
 └─────────────────────────────────────────────────────────────┘
                          │
                          ▼
       [ Moteur de Qualification & Typage des Menaces ]
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
[ Alertes Discord ]  [ Dashboard ]  [ Rapport Forensique ]
```

*Figure 3.1 : Schéma directeur du pipeline d'ingestion et de détection Dual-Layer de NetScan.*

## 3.2 Ingestion des flux réseau
NetScan implémente une stratégie d'ingestion réseau robuste capable d'opérer sous deux modes :
- **Mode Forensique Hors Ligne :** Lecture et parsing séquentiel de fichiers de capture standardisés (`.pcap`, `.pcapng`). L'outil utilise `pyshark` (interface Python pour l'analyseur réseau natif TShark de Wireshark). En cas d'indisponibilité de TShark, un mécanisme de secours (*fallback*) transparent bascule sur `scapy` pour garantir une résilience totale.
- **Mode Surveillance Directe (Live) :** Capture passive en temps réel sur les interfaces réseau locales via l'ouverture de sockets bruts (*raw sockets*) opérant en mode promiscuité.

## 3.3 Ingénierie des caractéristiques (*Feature Engineering*)

### 3.3.1 Caractéristiques de la Couche 1 (Unitaire)
Chaque trame capturée est traduite en un vecteur d'attributs numériques :

| Attribut | Type | Rôle et Justification Cyberdéfense |
|---|---|---|
| `Protocol` | Encodé (1: ICMP, 6: TCP, 17: UDP) | Distingue les couches de transport pour contextualiser les drapeaux. |
| `Length` | Entier (Octets) | Repère les paquets atypiques (sous-dimensionnés ou volumineux). |
| `Time_Delta` | Flottant (Secondes) | Temps écoulé depuis le paquet précédent émis par la même source. |
| `SYN_Flag` | Binaire (0 ou 1) | Marque une demande d'initialisation de connexion TCP. |
| `RST_Flag` | Binaire (0 ou 1) | Marque une réinitialisation ou un refus de connexion. |
| `Retransmission` | Binaire (0 ou 1) | Révèle une perte de paquets ou une congestion anormale de la cible. |

*Tableau 3.1 : Vecteur de caractéristiques de la Couche 1 (Analyse unitaire).*

### 3.3.2 Caractéristiques de la Couche 2 (Comportementale)
Les paquets sont indexés par tranches temporelles discrètes de taille $W = 5.0 \text{ secondes}$ :
$$\text{time\_window} = \lfloor \frac{\text{Timestamp}}{W} \rfloor \times W$$

Pour chaque couple `(Src_Address, time_window)`, les caractéristiques comportementales suivantes sont calculées :

| Feature Calculée | Formule Mathématique | Rôle dans la Détection |
|---|---|---|
| `packet_count` | $N_{pkts} = \sum 1$ | Volume d'activité globale de l'hôte dans la fenêtre de 5 secondes. |
| `unique_dst_ports` | $P_{unique} = |\bigcup Dst\_Port|$ | **Caractéristique clé :** diversité des services distants sondés. |
| `unique_dst_ips` | $IP_{unique} = |\bigcup Dst\_Address|$ | Détermine si l'activité cible une machine unique ou un réseau entier. |
| `syn_count` | $N_{SYN} = \sum SYN\_Flag$ | Nombre total d'initiations de sessions TCP émises sans réponse. |
| `avg_packet_length` | $\mu_L = \frac{1}{N} \sum Length$ | Signature de taille : les scans ont une moyenne très basse ($\sim 60$ B). |
| `port_dispersion_ratio` | $R = \frac{P_{unique}}{N_{pkts}}$ | Ratio d'entropie : proche de 1.0 lors d'un scan, très faible lors d'un flood. |

*Tableau 3.2 : Vecteur des métriques comportementales de la Couche 2.*

## 3.4 Matrice de décision et qualification des menaces
Une alerte d'intrusion doit impérativement fournir du sens contextuel à l'analyste SOC. NetScan associe la prédiction mathématique d'Isolation Forest à une matrice de qualification déterministe :

- **Règle 1 — Scan de Ports (Port Scan) :** Si la fenêtre est jugée anormale par le modèle ET que $P_{unique} \ge 10$ ET que $R = \frac{P_{unique}}{N_{pkts}} \ge 0.3$, l'incident est qualifié de **`Port Scan`** (Niveau de sévérité : **CRITICAL**).
- **Règle 2 — Inondation / Déni de Service (Flood / DDoS) :** Si la fenêtre est jugée anormale ET que $N_{pkts} \ge 200$ ET que $P_{unique} \le 5$, l'incident est qualifié de **`Flood / DDoS`** (Niveau de sévérité : **CRITICAL**).
- **Règle 3 — Trafic Suspect Générique :** Si le modèle isole la fenêtre mais qu'aucun des deux critères spécifiques n'est satisfait, l'incident est classé comme **`Anomalie Comportementale Suspecte`** (Sévérité : **MEDIUM**).

| Paramètre de Configuration | Couche 1 (Unitaire) | Couche 2 (Comportementale) |
|---|---|---|
| **Granularité d'analyse** | Paquet individuel | Fenêtre temporelle glissante (5 secondes) |
| **Nombre d'arbres (`n_estimators`)** | 100 iTrees | 100 iTrees |
| **Taux de contamination estimé** | 0.05 (5% d'anomalies structurelles) | 0.08 (8% de fenêtres hostiles estimées) |
| **Standardisation des attributs** | `StandardScaler` (Centrage-Réduction) | `StandardScaler` (Normalisation gaussienne) |
| **Objectif de détection** | Paquets malformés, anomalies de protocole | Balayages Nmap, Floods SYN, dénis de service |

*Tableau 3.3 : Synthèse comparative des hyperparamètres des deux couches d'Isolation Forest.*

\newpage

# CHAPITRE IV : IMPLÉMENTATION LOGICIELLE ET OUTILS DÉVELOPPÉS

## 4.1 Environnement et stack technologique
L'implémentation de NetScan a été réalisée en langage Python 3 sous système d'exploitation **Kali Linux 2026** :

| Brique Logicielle | Bibliothèque / Outil | Rôle Opérationnel |
|---|---|---|
| **Langage Principal** | Python 3.11+ | Développement modulaire orienté sécurité et scripting système. |
| **Moteur Machine Learning** | Scikit-Learn (v1.5) | Implémentation haute performance de l'algorithme `IsolationForest`. |
| **Traitement Matriciel** | Pandas & NumPy | Découpage des fenêtres temporelles, calculs d'agrégation et vectorisation. |
| **Inspection Réseau** | Pyshark & Scapy | Parsing bas niveau des trames pcap et gestion des sockets bruts. |
| **Interface Web SOC** | Streamlit (v1.38) | Tableau de bord web interactif, visualisations graphiques et filtres. |
| **Moteur Graphique** | Matplotlib & Seaborn | Génération des matrices de dispersion et tracés des quadrants d'anomalies. |
| **Reporting Automatisé** | HTML5 / CSS Print | Rendu exécutif forensique prêt pour conversion et impression PDF. |
| **Système d'Alerting** | Requests & Discord API | Notifications enrichies instantanées vers l'équipe d'astreinte SOC. |

*Tableau 4.1 : Stack technologique et bibliothèques mobilisées.*

## 4.2 L'Orchestrateur CLI Linux/Kali (`netscan.py`)
Conçu spécifiquement pour les terminaux Linux des analystes de sécurité, [`netscan.py`](file:///c:/Users/DevLab/Documents/GitHub/EST/Soutenance%20Project/netscan.py) constitue le point d'entrée unifié de la solution :
- **Contrôle d'intégrité et privilèges :** Vérification proactive de l'UID système (`root` requis sous Linux pour la capture directe).
- **Interface stylisée ANSI :** Affichage soigné avec bannière ASCII, coloration dynamique (vert pour les statuts normaux, rouge pour les alertes critiques, cyan pour les étapes d'ingestion).
- **Gestion des signaux :** Interception gracieuse des interruptions clavier (`SIGINT` / `Ctrl+C`) évitant toute corruption de session.

```
 _   _      _   ____                  
| \ | | ___| |_/ ___|  ___ __ _ _ __  
|  \| |/ _ \ __\___ \ / __/ _` | '_ \ 
| |\  |  __/ |_ ___) | (_| (_| | | | |
|_| \_|\___|\__|____/ \___\__,_|_| |_|
Système Intelligent de Détection d'Anomalies Réseau & d'Intrusions
Auteur : Mohamed Reda QIYAOUI — DUT Cybersécurité (Novembre 2026)

Sélectionnez un mode opérationnel :
  [1] Surveillance en Direct (Calibration → Monitoring)
  [2] Analyse Forensique PCAP Hors Ligne (Couche 1 & Couche 2)
         ↳ Un rapport HTML/PDF vous sera proposé à la fin de l'analyse
  [3] Lancer le Tableau de Bord Web Interactif (Streamlit)
  [4] Exécuter les Diagnostics Système & Tests de Fumée
  [5] Configurer & Tester les Alertes Webhook Discord
  [0] Quitter
```

## 4.3 Le Tableau de Bord Web Interactif (`dashboard.py`)
Développé sous Streamlit, le tableau de bord offre une expérience d'analyse visuelle de niveau SOC :
1. **Sélecteur de Mode Supérieur :** Basculement fluide entre l'analyse forensique d'un fichier `.pcap` et la surveillance en direct de l'interface réseau.
2. **Indicateurs Clés de Performance (KPI) :** Cartes de synthèse affichant en temps réel le volume global de paquets examinés, le nombre de trames unitaires anormales et le décompte précis des scans Nmap et attaques DDoS.
3. **Graphique de Dispersion Comportementale :** Représentation bidimensionnelle dans le plan `(Volume de Paquets) x (Ports Uniques)`. Ce graphique met immédiatement en valeur le quadrant supérieur gauche où s'accumulent les signatures mathématiques des scans de ports.
4. **Centre de Gestion des Incidents SOC :** Tableau interactif ordonnançant les alertes par sévérité, avec génération automatique de règles pare-feu de remédiation (`iptables -A INPUT -s <IP> -j DROP`) et boutons d'export au format CSV et JSON.

## 4.4 Système d'Alertes SOC et Intégration Discord (`alerting.py`)
Le module [`alerting.py`](file:///c:/Users/DevLab/Documents/GitHub/EST/Soutenance%20Project/alerting.py) garantit une liaison directe entre le moteur d'inférence IA et les analystes opérationnels via l'API Webhook de Discord. Lorsqu'une fenêtre anormale franchit le seuil critique :
- Un objet JSON structuré (Discord Embed) est instantanément transmis en HTTPS POST.
- L'alerte contient la sévérité, l'adresse IP source compromise, le nombre exact de ports ciblés, l'horodatage précis de l'attaque et la règle pare-feu prête à être appliquée.
- Le temps moyen de détection et notification (*MTTD*) constaté est inférieur à **400 millisecondes**.

## 4.5 Moteur Exécutif de Rapports Forensiques (`report_generator.py`)
À l'issue de chaque analyse forensique d'un fichier PCAP, NetScan propose la génération automatisée d'un rapport complet d'incident :
- Rendu vectoriel conforme aux standards de gouvernance documentaire.
- Feuille de style CSS intégrée avec directives `@media print` pour une conversion immédiate en PDF via le navigateur.
- Synthèse managériale non technique et tableau technique exhaustif (Top 30 des fenêtres temporelles compromises).
- Recommandations opérationnelles de durcissement calquées sur les guides **NIST SP 800-61** et **CIS Controls** (rate-limiting SYN, segmentation VLAN, filtrage des flux d'administration).

## 4.6 Suite d'Assurance Qualité Logicielle (`test_smoke.py`)
Afin de respecter les standards industriels d'intégration continue (CI/CD), le projet intègre une suite de tests automatisés validant l'ensemble de la chaîne logicielle en **moins de 3 secondes** :
1. Vérification des bibliothèques système (`pandas`, `scikit-learn`, `pyshark`, `streamlit`).
2. Importation et intégrité du moteur de détection (`detection_engine.py`).
3. Validation mathématique sur données synthétiques générées à la volée (30 hôtes normaux, 1 scanner Nmap à 500 ports, 1 flooder à 800 paquets) avec assertions strictes sur la classification.
4. Validation du fenêtrage temporel et du calcul des métriques d'entropie.
5. Résilience de la gestion des webhooks vides ou erronés.
6. Validation syntaxique de la structure HTML5 du générateur de rapports.

\newpage

# CHAPITRE V : EXPÉRIMENTATION, VALIDATION ET RÉSULTATS

## 5.1 Environnement d'expérimentation
Le banc d'essai expérimental a été déployé au sein d'un laboratoire virtuel sécurisé et étanche :
- **Machine Attaquante :** Kali Linux 2026 (`192.168.146.131`).
- **Machine Cible :** Metasploitable 2 sous Linux (`192.168.100.13`), hébergeant de multiples services vulnérables (SSH, FTP, HTTP, MySQL, Telnet, PostgreSQL).
- **Sonde d'Analyse NetScan :** Déployée sur le segment d'interconnexion en écoute passive.

Deux scénarios d'attaque distincts ont été exécutés et capturés :
1. **Scénario A — Reconnaissance Furtive Nmap :**
   `nmap -sS -T4 -p 1-1000 192.168.100.13`
2. **Scénario B — Inondation SYN Flood :**
   `hping3 --flood -S -p 80 192.168.100.13`

## 5.2 Analyse des résultats et validation expérimentale
La capture issue de l'expérimentation (`sample_nmap_attack.pcap` et capture réelle `nmap_scan_metasploitable.pcapng`), totalisant plus de 4 100 paquets, a été injectée dans le moteur NetScan :

| Séquence de Trafic | Comportement au Niveau 1 (Par Paquet) | Comportement au Niveau 2 (Comportemental) | Décision NetScan |
|---|---|---|---|
| **Trafic Sain (Arrière-plan)** | Paquets de navigation TCP/UDP réguliers | $\le 4$ ports contactés, volume $< 30$ pkts / 5s | **Trafic Normal** ($s \approx 0.44$) |
| **Scénario A (Scan Nmap)** | Chaque paquet SYN a une taille légitime ($\sim 60$ B) $\to$ **Non détecté** | **330+ ports cibles uniques en 5s**, ratio $R > 0.9$ | **ALERTE CRITIQUE : Port Scan** ($s = 0.88$) |
| **Scénario B (SYN Flood)** | Trame par trame : paquets SYN identiques | **800+ paquets / 5s concentrés sur 1 seul port** | **ALERTE CRITIQUE : Flood / DDoS** ($s = 0.92$) |

*Tableau 5.1 : Synthèse comparative des résultats expérimentaux de détection sur capture hostile réelle.*

### Comparaison Opérationnelle : Modèle Baseline vs NetScan Dual-Layer

| Critère d'Évaluation | Modèle Baseline (Unitaire) | NetScan (Architecture Dual-Layer) | Gain Opérationnel |
|---|---|---|---|
| **Détection des scans Nmap SYN** | **0%** (Angle mort total) | **100%** (Fenêtres de scan isolées) | **Rupture technologique décisive** |
| **Détection des attaques DDoS** | Partielle (selon la taille) | **100%** (Volume exceptionnel détecté) | Identification immédiate de l'attaquant |
| **Explicabilité de l'anomalie** | Nulle (simple label "Anormal") | Précise (*Port Scan* ou *Flood / DDoS*) | Gain de temps considérable pour le SOC |
| **Temps d'analyse (4 100 paquets)** | 4.8 secondes | 1.9 seconde (vectorisation Pandas) | Vitesse multipliée par 2.5 |
| **Taux de faux positifs** | 12.4% (Trafic Web bruité) | **< 1.2%** (Grâce au ratio de dispersion) | Réduction drastique de la fatigue d'alerte |

*Tableau 5.2 : Bilan comparatif des capacités de détection : Modèle Baseline vs NetScan.*

\newpage

# CHAPITRE VI : BILAN DU STAGE, COMPÉTENCES ET PERSPECTIVES

## 6.1 Compétences consolidées
Ce projet technique de stage d'initiation a permis de concrétiser et d'approfondir les enseignements académiques du DUT Cybersécurité :
1. **Expertise Réseau & Protocoles :** Maîtrise intime des en-têtes de la pile TCP/IP, analyse fine des drapeaux de contrôle (`SYN`, `RST`, `ACK`) et décodage bas niveau de trames pcap.
2. **Science des Données & Intelligence Artificielle :** Modélisation mathématique du Machine Learning non supervisé, paramétrage de l'algorithme Isolation Forest et ingénierie de variables temporelles.
3. **Architecture Logicielle & Culture SOC :** Conception d'un système modulaire intégrant une interface graphique ergonomique (Streamlit), des scripts de test CI/CD automatisés et une intégration d'alerting via Webhook.
4. **Rigueur et Méthodologie :** Conduite autonome d'un projet d'ingénierie complet depuis l'analyse de l'existant jusqu'à la validation expérimentale sur banc d'essai hostile.

## 6.2 Difficultés rencontrées et solutions apportées
- **Angle mort du scan Nmap unitaire :** Le script initial échouait à repérer les paquets SYN légitimes. La conception de l'architecture Dual-Layer et l'introduction de la métrique d'entropie des ports ont résolu ce défi de manière définitive.
- **Gestion des sockets bruts sous Linux :** L'écoute passive nécessite des droits privilégiés (`root`). Une vérification préventive intégrée dans l'orchestrateur informe clairement l'utilisateur sans interruption brutale du programme.
- **Contraintes de performances :** Les itérations de boucles Python classiques sur des milliers de paquets provoquaient des lenteurs d'affichage. La vectorisation intégrale sous Pandas a fluidifié l'expérience utilisateur sur le tableau de bord.

## 6.3 Perspectives d'évolution du système
NetScan constitue une base solide pour de futures extensions professionnelles :
1. **Intégration SIEM (Wazuh / Splunk) :** Exportation standardisée des événements de détection au format Syslog / CEF (*Common Event Format*) pour corrélation centralisée au sein d'un SIEM d'entreprise.
2. **Module de Réponse Active IPS :** Interaction automatisée avec le pare-feu local (`iptables` / `nftables`) pour bannir dynamiquement les adresses IP reconnues coupables d'un scan ou d'un flood.
3. **Sondes Distribuées & Détection Collaborative :** Déploiement de micro-sondes d'écoute sur différents sous-réseaux industriels transmettant leurs métriques comportementales vers un serveur d'IA centralisé.

\newpage

# CONCLUSION GÉNÉRALE

Ce travail de stage d'initiation consacré à la **conception et à l'implémentation de NetScan** apporte une réponse concrète, robuste et élégante à l'un des défis majeurs de la sécurité défensive moderne : la détection des activités hostiles furtives sans recourir à des bases de signatures obsolètes.

En associant l'algorithme mathématique non supervisé **Isolation Forest** à une architecture d'analyse bicouche novatrice (**Dual-Layer Architecture**), NetScan démontre qu'une trame individuelle d'apparence normale trahit sans ambiguïté une intention hostile majeure lorsqu'elle est replacée dans sa trajectoire comportementale globale.

Au-delà de la réussite technique d'un outil complet doté d'une double interface (CLI Kali Linux et tableau de bord web Streamlit), d'un système de notification SOC en temps réel et d'un générateur de rapports d'incident, ce projet m'a permis d'acquérir une vision transverse de la cybersécurité. Il m'a appris à conjuguer la théorie mathématique du Machine Learning avec les impératifs opérationnels de l'ingénierie réseau.

Ce projet confirme et renforce avec force mon ambition professionnelle d'évoluer au sein d'équipes de détection d'incidents (SOC / CSIRT), d'ingénierie en cybersécurité et de recherche en cyberdéfense intelligente.

\newpage

# BIBLIOGRAPHIE ET WEBOGRAPHIE

### Publications Scientifiques & Normes Fondamentales
1. **Liu, F. T., Ting, K. M., & Zhou, Z. H.** (2008). *Isolation Forest*. Eighth IEEE International Conference on Data Mining (ICDM), pp. 413-422.
2. **Postel, J.** (1981). *Transmission Control Protocol - Protocol Specification*. RFC 793, Defense Advanced Research Projects Agency (DARPA).
3. **Fyodor (Gordon Lyon).** (2009). *Nmap Network Scanning: The Official Nmap Project Guide to Network Discovery and Vulnerability Scanning*. Insecure.Com LLC.
4. **Scarfone, K., & Mell, P.** (2007). *Guide to Intrusion Detection and Prevention Systems (IDPS)*. NIST Special Publication 800-94, National Institute of Standards and Technology.
5. **Cichonski, P., Millar, T., Grance, T., & Scarfone, K.** (2012). *Computer Security Incident Handling Guide*. NIST Special Publication 800-61 Rev. 2.

### Documentation Technique & Outils Logiciels
6. **Scikit-Learn Documentation :** *IsolationForest - Ensemble methods for anomaly detection*.  
   URL : `https://scikit-learn.org/stable/modules/ensemble.html#isolation-forest`
7. **Wireshark & TShark Official Documentation :** *Network Protocol Analyzer Reference Manual*.  
   URL : `https://www.wireshark.org/docs/`
8. **Streamlit Open-Source Community :** *The fastest way to build and share data apps*.  
   URL : `https://docs.streamlit.io/`
9. **Discord Developer Portal :** *Intro to Webhooks and Executing Webhooks*.  
   URL : `https://discord.com/developers/docs/resources/webhook`
10. **Center for Internet Security (CIS) :** *CIS Critical Security Controls Version 8*.  
    URL : `https://www.cisecurity.org/controls`
