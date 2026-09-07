# 🎓 GUIDE COMPLET DE SOUTENANCE — STAGE D'INITIATION (DUT Cybersécurité)
**Projet : NetScan — Système de Détection d'Anomalies Réseau par Machine Learning**  
**Étudiant : Mohamed Reda QIYAOUI**  
**Date : Soutenance de Stage d'Initiation — Septembre 2026**

---

## 📋 Table des Matières
1. [Conseils Clés pour Réussir votre Soutenance](#1-conseils-clés-pour-réussir-votre-soutenance)
2. [Structure Recommandée des Slides (10 à 12 Slides)](#2-structure-recommandée-des-slides)
3. [Script & Discours Mot à Mot (En Français)](#3-script--discours-mot-à-mot)
4. [Scénario de Démonstration en Direct (3 Minutes Chrono)](#4-scénario-de-démonstration-en-direct)
5. [Les 10 Questions Pièges du Jury & Leurs Réponses Parfaites](#5-les-10-questions-pièges-du-jury)
6. [Fiche Récapitulative des Notions Clés](#6-fiche-récapitulative-des-notions-clés)

---

## 1. Conseils Clés pour Réussir votre Soutenance

> [!IMPORTANT]
> Pour un **Stage d'Initiation**, le jury n'évalue pas seulement la complexité du code. Il évalue :
> 1. **Votre compréhension des bases** : Savez-vous ce qu'est un paquet TCP, un flag SYN, et comment fonctionne un port scan ?
> 2. **Votre clarté d'expression** : Êtes-vous capable de vulgariser l'IA sans réciter des formules par cœur ?
> 3. **Le fonctionnement de votre outil** : Montrer une application qui tourne en direct sans bug vaut 100 pages de texte.

- **Temps alloué** : Généralement 10 à 15 minutes d'exposé + 5 à 10 minutes de questions.
- **Posture** : Regardez tous les membres du jury, parlez calmement, ne lisez jamais vos diapositives.
- **Le secret** : Vos slides doivent contenir des schémas et des chiffres clés, pas de longs paragraphes.

---

## 2. Structure Recommandée des Slides

- **Slide 1 — Page de Garde** : Titre du projet (*NetScan*), Nom, Encadrant(s), Logo de l'établissement, mention **Stage d'Initiation** et date : *Septembre 2026*.
- **Slide 2 — Contexte & Cadre du Stage d'Initiation** : Entreprise / service d'accueil, durée du stage, missions confiées.
- **Slide 3 — La Problématique Réseau** : Pourquoi les pare-feux et IDS classiques (à signatures) échouent face aux scans furtifs (Nmap).
- **Slide 4 — Objectifs du Projet NetScan** : Détecter sans signature grâce au Machine Learning non supervisé, en différé (.pcap) et en temps réel.
- **Slide 5 — L'Architecture Dual-Layer (Le Cœur du Sujet)** :
  - *Niveau 1* : Analyse microscopique par paquet (Taille + Timestamp).
  - *Niveau 2* : Analyse macroscopique par fenêtre temporelle (Comportement de l'hôte).
- **Slide 6 — L'Algorithme : Isolation Forest** : Pourquoi cet algorithme ? (Principe d'isolation des anomalies dans l'espace des données).
- **Slide 7 — Mode Temps Réel : Calibrate-Then-Monitor** : Phase 1 (Apprentissage du trafic normal pendant 2 min) $\rightarrow$ Phase 2 (Surveillance active continue).
- **Slide 8 — Centre de Notification & Traçabilité SOC** : Historique persistant des incidents, sévérité, et recommandations firewall automatiques.
- **Slide 9 — Démonstration de l'Outil (Streamlit)** : Transition vers la démo live ou captures d'écran annotées.
- **Slide 10 — Compétences Acquises & Bilan du Stage d'Initiation** : Ce que le stage vous a apporté techniquement et professionnellement.
- **Slide 11 — Perspectives d'Évolution** : Améliorations futures (réponse active IPS, notification Discord/Telegram, intégration SIEM).
- **Slide 12 — Conclusion & Remerciements** : Synthèse finale et ouverture vers les questions du jury.

---

## 3. Script & Discours Mot à Mot

### Introduction (Slides 1 & 2)
> *"Bonjour chers membres du jury. Je me présente, Mohamed Reda QIYAOUI, étudiant en DUT. J'ai l'honneur de vous présenter aujourd'hui le bilan de mon stage d'initiation, intitulé : **NetScan — Conception et implémentation d'un système intelligent de détection d'anomalies réseau par apprentissage non supervisé**."*

### Problématique (Slide 3)
> *"Dans le domaine de la cybersécurité, les outils traditionnels de détection comme Snort ou les pare-feux reposent sur des bases de données de signatures connues.  
> Or, face à une attaque inconnue ou à un scan de reconnaissance furtif comme `nmap -sS`, ces outils sont souvent aveugles. Pourquoi ? Parce que chaque paquet SYN envoyé par un attaquant est individuellement tout à fait légitime et conforme aux normes RFC.  
> La question centrale de mon projet a donc été : **Comment détecter une intrusion furtive sans aucune signature préalable ?**"*

### La Solution & Architecture (Slides 4, 5 & 6)
> *"Pour répondre à ce défi, j'ai conçu **NetScan**, une solution basée sur l'apprentissage automatique non supervisé via l'algorithme **Isolation Forest**.  
> L'originalité de NetScan réside dans son architecture à double niveau :  
> 1. **Le Niveau 1 (Microscopique)** examine chaque trame individuellement pour repérer les anomalies de format, retransmissions anormales ou paquets surdimensionnés.  
> 2. **Le Niveau 2 (Macroscopique / Comportemental)** regroupe les paquets par fenêtres de temps (ex: 5 secondes) pour observer le comportement global de chaque adresse IP : combien de ports distincts a-t-elle contactés ? Combien de paquets SYN sans ACK ?  
> C'est ce Niveau 2 qui permet de démasquer instantanément un scan Nmap : une machine qui tente de joindre 500 ports différents en 5 secondes est isolée immédiatement par le modèle mathématique."*

### Le Temps Réel & Le Centre de Notification (Slides 7 & 8)
> *"Au-delà de l'analyse de fichiers Wireshark (.pcap), j'ai doté NetScan d'un moteur temps réel basé sur le principe **Calibrate-Then-Monitor** :  
> L'outil observe le réseau pendant 2 minutes pour apprendre l'activité normale de l'environnement, puis passe en surveillance continue passive sans bloquer le trafic.  
> Enfin, toutes les alertes sont centralisées dans un **Notification Center** qui attribue un niveau de sévérité (Critique, Élevé, Moyen) et propose à l'administrateur une règle de remédiation firewall immédiate (`iptables`)."*

---

## 4. Scénario de Démonstration en Direct (3 Minutes Chrono)

> 💡 **Règle d'or** : Lancez votre application **avant** de commencer à parler (`streamlit run dashboard.py`). Laissez l'onglet prêt dans votre navigateur.

### Étape 1 : Montrer l'accueil & Charger l'échantillon (30 secondes)
1. Ouvrez `http://localhost:8501`.
2. Présentez les **deux modes principaux** en haut de l'écran :
   - **`Analyse de Capture (Fichier PCAP)`** (Forensic & Graphiques)
   - **`Surveillance Réseau en Direct (Live)`** (Sniffing d'interface & Détection continue)
3. Glissez-déposez le fichier de capture de test (`sample_nmap_attack.pcap`) dans la zone d'importation. Le bandeau d'alerte rouge apparaît aussitôt :  
   *"Dès l'importation de cette capture de 11 614 paquets, NetScan analyse le trafic et isole instantanément les attaques sans signatures préalables."*

### Étape 2 : L'onglet Comportemental (Niveau 2) — L'effet "WAOUH" (1 minute)
1. Cliquez sur l'onglet **`Analyse Comportementale (Niveau 2)`**.
2. Montrez le graphique de dispersion :
   - Le quadrant **en haut à gauche** (Beaucoup de ports uniques, volume modéré) : *"Voici la signature mathématique exacte du scan Nmap."*
   - Le quadrant **en bas à droite** : *"Ici, nous avons une tentative de Flood / Déni de service."*
3. Expliquez la standardisation de la fenêtre temporelle (5 secondes) :  
   *"L'analyse regroupe le trafic par fenêtres optimales de 5 secondes, ce qui isole précisément les rafales de sondes Nmap et les pics de volume."*

### Étape 3 : Le Centre de Notification SOC (1 minute)
1. Cliquez sur le 4ème onglet **`Centre d'Alertes`**.
2. Si vous n'avez pas encore d'alertes, cliquez sur **`Charger Incidents Démo (Nmap)`**.
3. Montrez une carte d'alerte rouge `CRITICAL` :
   *"L'outil identifie l'IP source `10.0.2.15`, précise qu'elle a scanné 526 ports en 5 secondes, et génère automatiquement la commande de mitigation firewall pour le SOC : `iptables -A INPUT -s 10.0.2.15 -j DROP`."*
4. Montrez les boutons d'export CSV / JSON pour l'audit.

---

## 5. Les 10 Questions Pièges du Jury & Leurs Réponses Parfaites

### Q1 : "Pourquoi avez-vous choisi Isolation Forest plutôt qu'un autre algorithme comme les k-means ou SVM ?"
> **Réponse** : *"Isolation Forest est spécifiquement conçu pour la détection d'anomalies : au lieu de modéliser les points normaux (ce qui est lourd en calcul), il isole directement les points anormaux par des découpages aléatoires. Comme les attaques ont des caractéristiques très différentes de la norme (ex: 500 ports ciblés), elles sont isolées près de la racine de l'arbre en très peu d'étapes. C'est un algorithme non supervisé très rapide et adapté au temps réel."*

### Q2 : "Pourquoi votre outil ne bloque-t-il pas directement les paquets au lieu de simplement alerter ?"
> **Réponse** : *"C'est un choix de conception fondamental. NetScan est un IDS (système de détection) et non un IPS (système de prévention en coupure). En environnement de production, bloquer automatiquement sur la base d'un modèle non supervisé comporte un risque de faux positif qui pourrait interrompre un service critique. NetScan alerte donc l'analyste SOC et lui fournit la commande exacte pour agir en toute connaissance de cause."*

### Q3 : "Que se passe-t-il si la carte réseau est inactive pendant les 2 minutes de calibration ?"
> **Réponse** : *"Si le trafic est quasi nul ou sans variance, scikit-learn lèverait une exception mathématique (division par zéro). Pour parer à cela, j'ai implémenté une sécurité dans la fonction `calibrate_baseline()` : elle bascule automatiquement sur un profil neutre standard représentatif d'un trafic de fond, avec un micro-bruit gaussien. L'outil ne plante jamais et reste prêt à détecter toute attaque survenant après."*

### Q4 : "Si Wireshark / TShark n'est pas installé sur la machine de test, est-ce que votre outil fonctionne ?"
> **Réponse** : *"Oui, absolument. J'ai conçu un mécanisme de secours (fallback) : NetScan tente d'abord d'utiliser PyShark pour les performances. Si le binaire TShark est absent du système, il bascule de manière transparente sur la bibliothèque native Scapy en Python pur."*

### Q5 : "Qu'est-ce que le paramètre 'contamination' dans le modèle ?"
> **Réponse** : *"La contamination correspond à la proportion estimée d'anomalies dans le jeu de données. Pour la couche 1 (par paquet), je l'ai fixée à 5% (bruit réseau classique). Pour la couche 2 (comportement par fenêtre), je l'ai fixée à 10% car lors d'une attaque active, la proportion de fenêtres malveillantes est plus élevée."*

### Q6 : "Comment différenciez-vous mathématiquement un scan de port d'un déni de service (DDoS) ?"
> **Réponse** : *"Grâce au ratio de diversité des ports : `unique_dst_ports / packet_count`. Si une machine envoie 500 paquets vers 500 ports différents (ratio proche de 1.0), il s'agit d'un scan de port. Si elle envoie 2 000 paquets vers un seul et même port (ratio très faible proche de 0), c'est une attaque volumétrique ou un flood."*

### Q7 : "Pourquoi utiliser deux bibliothèques de capture : pyshark et scapy ?"
> **Réponse** : *"PyShark est un wrapper au-dessus du moteur C de Wireshark (TShark), ce qui le rend rapide sur de très gros fichiers. Mais il nécessite une installation tierce. Scapy est 100% Python, extrêmement portable et autonome. Les combiner offre le meilleur des deux mondes : vitesse et résilience."*

### Q8 : "Avez-vous testé votre outil sur des attaques réelles ?"
> **Réponse** : *"Oui, j'ai validé la détection sur la capture médico-légale `sample_nmap_attack.pcap` contenant un véritable scan SYN agressif lancé par l'outil Nmap. Les 4 fenêtres d'attaque ont été détectées avec 100% de succès par la Couche 2."*

### Q9 : "Qu'avez-vous appris durant ce stage d'initiation ?"
> **Réponse** : *"Ce stage m'a permis d'approfondir l'analyse protocolaire TCP/IP, de maîtriser le traitement de données massives en Python avec Pandas, et d'appliquer concrètement l'intelligence artificielle à la résolution d'un problème réel de sécurité réseau, tout en concevant une interface utilisateur intuitive."*

### Q10 : "Quelles améliorations pourriez-vous apporter à l'avenir ?"
> **Réponse** : *"Deux axes majeurs : premièrement, l'intégration d'un webhook pour recevoir des alertes instantanées sur Discord ou Telegram. Deuxièmement, le calcul de l'entropie de Shannon sur les requêtes DNS pour détecter les canaux cachés d'exfiltration de données (DNS Tunneling)."*

---

## 6. Fiche Récapitulative des Notions Clés

| Terme | Définition Simple pour le Jury |
|---|---|
| **Pcap** | Fichier de capture contenant l'enregistrement brut des trames ayant circulé sur le réseau. |
| **TCP SYN Scan** | Technique de scan furtif (half-open) envoyant des paquets SYN pour cartographier les services sans finaliser la connexion. |
| **Isolation Forest** | Algorithme d'apprentissage non supervisé qui détecte les anomalies en mesurant la facilité à isoler un point par découpage récursif. |
| **Windowing (Fenêtrage)** | Agrégation temporelle des paquets par tranches de 5s pour calculer des moyennes comportementales par adresse IP. |
| **SOC** | *Security Operations Center* : centre de supervision où les analystes surveillent les alertes et appliquent les mesures défensives. |
| **IPS vs IDS** | Un IDS (NetScan) observe et alerte ; un IPS bloque activement le trafic au risque d'interrompre des flux légitimes. |

---
*Bonne chance pour votre soutenance Mohamed Reda ! Avec cette préparation, votre projet est prêt pour obtenir la note maximale.*
